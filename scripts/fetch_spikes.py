#!/usr/bin/env python3
"""
fetch_spikes.py — download the per-electrode spike-time files for one plate
from the TUNI Comparative MEA dataset on GIN, and report their structure.

Why this exists
---------------
Every metric analysed on Day 1 came from the meaRtools summary CSVs, which are
*per well*. They can tell you that a well lost 23 active electrodes; they cannot
tell you *which* electrodes, or whether the same electrode came back a week later.
The `*_spikes*.csv` files carry spike times per electrode, which is the resolution
the question actually needs.

These files are small (kB-MB, not GB). Downloading the whole folder is fine.

Usage
-----
    python scripts/fetch_spikes.py                  # hPSC_MEA1, the default
    python scripts/fetch_spikes.py --plate Rat_MEA1
    python scripts/fetch_spikes.py --list-only      # discover, download nothing

    # also pull the meaRtools summary CSVs, so Day 1's result becomes
    # reproducible from this repo rather than from your Downloads folder:
    python scripts/fetch_spikes.py --folder hPSC_MEA1_meaRtools_output

Dataset: Kapucu et al., Scientific Data 9, 93 (2022).
Data under CC BY 4.0. G-Node DOI 10.12751/g-node.wvr3jf
"""

from __future__ import annotations

import argparse
import json
import re
import sys
import urllib.error
import urllib.request
from pathlib import Path

REPO = "https://gin.g-node.org/NeuroGroup_TUNI/Comparative_MEA_dataset"
UA = {"User-Agent": "mea-reanalysis/0.2 (academic reuse; contact via GIN)"}

# Plate folder -> the subfolder holding spike times, noise levels and exp logs.
SUBFOLDER = "{plate}_spikes_noise_explogs"

PROJECT = Path(__file__).resolve().parent.parent


def get(url: str, timeout: int = 120) -> bytes:
    req = urllib.request.Request(url, headers=UA)
    with urllib.request.urlopen(req, timeout=timeout) as r:
        return r.read()


def _entries(url: str, prefix: str) -> list[str]:
    """Names of the immediate children of a GIN directory, or [] if unreachable."""
    try:
        html = get(url).decode("utf-8", errors="replace")
    except Exception:  # noqa: BLE001
        return []
    pat = re.compile(r'href="[^"]*?/src/(?:branch/)?master/'
                     + re.escape(prefix) + r'/([^"/?#]+)"')
    return sorted(set(pat.findall(html)))


def _whats_actually_there(plate: str, sub: str, listing: str, code: int) -> str:
    """Build a message that answers 'then what IS there?' by walking up."""
    lines = [f"HTTP {code} for {listing}", ""]

    subs = _entries(f"{REPO}/src/master/Data/{plate}", f"Data/{plate}")
    if subs:
        lines.append(f"Plate '{plate}' exists. Its subfolders are:")
        lines += [f"    {s}" for s in subs]
        lines.append("")
        lines.append(f"Re-run with:  --plate {plate} --folder <one of the above>")
        return "\n".join(lines)

    plates = _entries(f"{REPO}/src/master/Data", "Data")
    if plates:
        lines.append(f"Plate '{plate}' does not exist. /Data actually contains:")
        lines += [f"    {p}" for p in plates]
        lines.append("")
        lines.append("Re-run with:  --plate <one of the above> --list-only")
        return "\n".join(lines)

    lines.append("Could not list /Data either — check the network or the repo URL.")
    return "\n".join(lines)


def discover(plate: str, sub: str) -> tuple[list[str], str]:
    """Return (filenames, listing_url) for a folder inside a plate.

    Parses the GIN (Gitea) directory listing rather than guessing filenames,
    so a naming convention that differs from expectation cannot silently
    produce an empty download. Day 1 already found one filename typo in this
    dataset ("electordes"); assume there are others.
    """
    listing = f"{REPO}/src/master/Data/{plate}/{sub}"
    try:
        html = get(listing).decode("utf-8", errors="replace")
    except urllib.error.HTTPError as e:
        # Folder does not exist under that name. Walk up the tree and report
        # what IS there, rather than dying on a 404. The pharmacology plates do
        # not follow the "<plate>_spikes_noise_explogs" convention, and the
        # plate names themselves were inferred rather than verified.
        raise SystemExit(_whats_actually_there(plate, sub, listing, e.code))

    # Gitea renders one <a href=".../src/branch/master/<path>"> per entry.
    pat = re.compile(
        r'href="[^"]*?/src/(?:branch/)?master/Data/'
        + re.escape(plate) + "/" + re.escape(sub) + r'/([^"/?#]+)"'
    )
    names = sorted(set(pat.findall(html)))

    if not names:
        # Fall back to any file-looking link on the page, then filter.
        loose = re.compile(r'href="[^"]*?/([^"/?#]+\.(?:csv|txt|xlsx?))"', re.I)
        names = sorted(set(loose.findall(html)))

    if not names:
        # The subfolder guess was wrong. Rather than fail with an opaque error,
        # list what subfolders the plate actually has. The pharmacology plates
        # do not follow the "<plate>_spikes_noise_explogs" convention.
        try:
            top = get(f"{REPO}/src/master/Data/{plate}").decode("utf-8", "replace")
            subs = sorted(set(re.findall(
                r'href="[^"]*?/src/(?:branch/)?master/Data/'
                + re.escape(plate) + r'/([^"/?#]+)"', top)))
        except Exception:  # noqa: BLE001
            subs = []
        msg = [f"No files found in {listing}"]
        if subs:
            msg.append(f"\n'{plate}' actually contains:")
            msg += [f"    {s}" for s in subs]
            msg.append(f"\nRe-run with:  --plate {plate} --folder <one of the above>")
        else:
            snippet = re.sub(r"\s+", " ", html)[:400]
            msg.append(f"\nAnd the plate folder could not be listed either.")
            msg.append(f"First 400 chars of the response:\n  {snippet}")
        raise SystemExit("\n".join(msg))
    return names, listing


ANNEX_HINT = re.compile(rb"^\s*(/annex/|\.\./\.git/annex/|[0-9a-f]{40}\s*$)")


def download(plate: str, sub: str, names: list[str], dest: Path) -> list[dict]:
    dest.mkdir(parents=True, exist_ok=True)
    records = []

    for i, name in enumerate(names, 1):
        url = f"{REPO}/raw/master/Data/{plate}/{sub}/{name}"
        out = dest / name
        rec = {"name": name, "url": url}

        if out.exists() and out.stat().st_size > 0:
            rec["status"] = "already present"
            rec["bytes"] = out.stat().st_size
            print(f"[{i:>3}/{len(names)}] {name:<52} skipped (present)")
            records.append(rec)
            continue

        try:
            blob = get(url)
        except urllib.error.HTTPError as e:
            rec["status"] = f"HTTP {e.code}"
            print(f"[{i:>3}/{len(names)}] {name:<52} FAILED  HTTP {e.code}")
            records.append(rec)
            continue
        except Exception as e:  # noqa: BLE001 - want the reason, whatever it is
            rec["status"] = f"error: {e}"
            print(f"[{i:>3}/{len(names)}] {name:<52} FAILED  {e}")
            records.append(rec)
            continue

        # A git-annex pointer is a few hundred bytes of path, not data.
        if len(blob) < 1024 and ANNEX_HINT.search(blob.strip()):
            rec["status"] = "git-annex pointer, not file content"
            print(f"[{i:>3}/{len(names)}] {name:<52} ANNEX POINTER ({len(blob)} B)")
            records.append(rec)
            continue

        out.write_bytes(blob)
        rec["status"] = "downloaded"
        rec["bytes"] = len(blob)
        print(f"[{i:>3}/{len(names)}] {name:<52} {len(blob):>12,} B")
        records.append(rec)

    return records


def describe(dest: Path, records: list[dict]) -> None:
    """Report the actual structure. Written before the format is known, so it
    reports rather than assumes."""
    csvs = [r for r in records if r.get("bytes") and r["name"].lower().endswith(".csv")]
    if not csvs:
        print("\nNo CSVs landed — nothing to describe.")
        return

    print("\n" + "=" * 72)
    print("STRUCTURE OF THE FIRST CSV (verbatim, first 6 lines)")
    print("=" * 72)
    first = dest / csvs[0]["name"]
    with first.open("r", encoding="utf-8", errors="replace") as fh:
        for n, line in enumerate(fh):
            if n >= 6:
                break
            print(f"  {line.rstrip()[:200]}")

    try:
        import pandas as pd
    except ImportError:
        print("\n(pandas not importable — skipping the parsed summary)")
        return

    print("\n" + "=" * 72)
    print("PARSED SUMMARY")
    print("=" * 72)
    for r in csvs[:3]:
        p = dest / r["name"]
        try:
            df = pd.read_csv(p, nrows=5000)
        except Exception as e:  # noqa: BLE001
            print(f"  {r['name']}: could not parse — {e}")
            continue
        print(f"\n  {r['name']}")
        print(f"    shape (first 5000 rows): {df.shape}")
        print(f"    columns: {list(df.columns)[:15]}")
        print(f"    dtypes:  {dict(list(df.dtypes.astype(str).items())[:15])}")


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--plate", default="hPSC_MEA1")
    ap.add_argument("--folder", default=None,
                    help="subfolder inside the plate; default <plate>_spikes_noise_explogs")
    ap.add_argument("--list-only", action="store_true")
    ap.add_argument("--dest", default=None,
                    help="default: data/<plate>/<short folder name> under the project root")
    args = ap.parse_args()

    sub = args.folder or SUBFOLDER.format(plate=args.plate)
    # Destination name. The pharmacology plates nest one level deeper —
    # Data/<plate>/<condition>/<condition>_spikes_noise_explogs — so several
    # folders share the same suffix. Key off the condition folder in that case,
    # otherwise Baseline and TTX would both land in "spikes/" and clobber each
    # other.
    if "/" in sub:
        short = sub.split("/")[0]
    elif sub.endswith("_spikes_noise_explogs"):
        short = "spikes"
    elif sub.endswith("_meaRtools_output"):
        short = "summary"
    else:
        short = sub
    dest = Path(args.dest) if args.dest else PROJECT / "data" / args.plate / short

    print(f"Plate      : {args.plate}")
    print(f"Folder     : {sub}")
    print(f"Destination: {dest}\n")

    names, listing = discover(args.plate, sub)
    print(f"Found {len(names)} file(s) at {listing}\n")
    for n in names:
        print(f"  - {n}")
    print()

    if args.list_only:
        return 0

    records = download(args.plate, sub, names, dest)

    inv = PROJECT / "notes" / f"inventory_{args.plate}_{short}.json"
    inv.parent.mkdir(parents=True, exist_ok=True)
    inv.write_text(json.dumps(
        {"plate": args.plate, "folder": sub, "listing": listing, "files": records},
        indent=2), encoding="utf-8")

    ok = sum(1 for r in records if r.get("status") in ("downloaded", "already present"))
    print(f"\n{ok}/{len(records)} file(s) available in {dest}")
    print(f"Inventory written to {inv}")

    describe(dest, records)
    return 0


if __name__ == "__main__":
    sys.exit(main())
