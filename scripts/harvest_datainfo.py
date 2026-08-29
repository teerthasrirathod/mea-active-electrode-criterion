#!/usr/bin/env python3
"""
harvest_datainfo.py — settle A1 (exactly) and A7b, without downloading 21 GB files.

Each published .h5 carries a /DataInfo group holding:
    DurationInSec, SamplingFrequencyInHz, DIV, Plate type,
    ExcludedWells, InactiveChannels

That group is a few kilobytes. HDF5 is chunked and indexed, so with HTTP range
requests h5py can seek straight to it. Same trick as stream_h5.py, applied to
every recording in a plate.

What it settles:

  A1  DurationInSec, exactly. B3 (the > vs >= off-by-one) is an integer-boundary
      claim and needs 600.000, not "about ten minutes".

  A7b InactiveChannels per DIV. If the list changes between recordings it was
      regenerated; if identical it was carried forward. Either answer closes the
      row, and it does not require contacting the original authors.

  BONUS — A7a says InactiveChannels is the study's own record of electrodes
      "not recorded due to malfunctioning electrodes during acquisition". That
      is the only direct measure of hardware failure in the entire release. If
      it grows across DIV, that is interface attrition measured by the people
      who ran the experiment. If it does not, that is a strong independent
      result. Either way it is the original question this project set out to ask.

Run:
    python -m pip install fsspec aiohttp requests h5py
    python scripts/harvest_datainfo.py --plate hPSC_MEA1
    python scripts/harvest_datainfo.py --plate Rat_MEA1
"""

import argparse
import json
import sys
from pathlib import Path

import numpy as np

ROOT = Path(__file__).resolve().parent.parent
REPO = "https://gin.g-node.org/NeuroGroup_TUNI/Comparative_MEA_dataset"


def as_text(v):
    if isinstance(v, bytes):
        return v.decode("utf-8", errors="replace").strip()
    if isinstance(v, np.ndarray):
        return [as_text(x) for x in v.tolist()]
    if isinstance(v, (list, tuple)):
        return [as_text(x) for x in v]
    if isinstance(v, (np.integer,)):
        return int(v)
    if isinstance(v, (np.floating,)):
        return float(v)
    return v


def read_datainfo(url, block_size=1 << 20):
    """Read only /DataInfo. Same access pattern as stream_h5.py, which is
    already known to work against GIN from this machine."""
    import fsspec
    import h5py
    handle = fsspec.open(url, mode="rb", block_size=block_size)
    with handle as fh:
        with h5py.File(fh, "r") as f:
            g = f["/DataInfo"]
            rec = {k: as_text(v) for k, v in g.attrs.items()}
            for ds in ("ExcludedWells", "InactiveChannels"):
                rec[ds] = as_text(g[ds][()]) if ds in g else None
            return rec


def h5_names(plate):
    """Discover the .h5 filenames in a plate folder from the GIN listing."""
    import urllib.request
    import re
    url = f"{REPO}/src/master/Data/{plate}"
    req = urllib.request.Request(url, headers={"User-Agent": "mea-reanalysis"})
    html = urllib.request.urlopen(req, timeout=120).read().decode("utf-8", "replace")
    names = sorted(set(re.findall(r'>([A-Za-z0-9_\-]+\.h5)<', html)))
    return names


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--plate", default="hPSC_MEA1")
    ap.add_argument("--files", nargs="*", default=None,
                    help="explicit .h5 filenames; otherwise discovered from GIN")
    args = ap.parse_args()

    names = args.files or h5_names(args.plate)
    if not names:
        print(f"no .h5 found for {args.plate}; pass --files explicitly")
        return 1
    print(f"{len(names)} recordings in {args.plate}\n")

    recs = []
    for i, n in enumerate(names, 1):
        url = f"{REPO}/raw/master/Data/{args.plate}/{n}"
        try:
            r = read_datainfo(url)
        except Exception as e:                      # noqa: BLE001
            print(f"  [{i}/{len(names)}] {n}: FAILED {type(e).__name__}: {e}")
            continue
        r["file"] = n
        recs.append(r)
        inact = r.get("InactiveChannels") or []
        if isinstance(inact, str):
            inact = [inact]
        print(f"  [{i}/{len(names)}] {n}  DIV={r.get('DIV')}  "
              f"dur={r.get('DurationInSec')}  fs={r.get('SamplingFrequencyInHz')}  "
              f"inactive={len(inact)}")

    out = ROOT / "notes" / f"datainfo_{args.plate}.json"
    out.write_text(json.dumps(recs, indent=2, default=str), encoding="utf-8")

    if not recs:
        print("\n" + "=" * 66)
        print("NO RECORDINGS READ — NOTHING IS CONCLUDED")
        print("=" * 66)
        print("  A1 and A7b are UNCHANGED. Do not record any result from this run.")
        print("  Fix the transport first, then re-run.")
        return 2

    # ---- A1 -------------------------------------------------------------
    durs = sorted({r.get("DurationInSec") for r in recs if r.get("DurationInSec") is not None})
    print("\n" + "=" * 66)
    print("A1 — recording duration, exactly")
    print("=" * 66)
    print(f"  distinct DurationInSec values: {durs}")
    if len(durs) == 1 and abs(float(durs[0]) - 600.0) < 1e-6:
        print("  -> exactly 600.000 s. A1 PRIMARY-exact. **B3 is unblocked.**")
    else:
        print("  -> NOT a clean 600.000. B3's integer boundary must be recomputed")
        print("     against the true duration before it can be claimed.")

    # ---- A7b ------------------------------------------------------------
    print("\n" + "=" * 66)
    print("A7b — was InactiveChannels regenerated per recording?")
    print("=" * 66)
    sets, order = [], []
    for r in recs:
        v = r.get("InactiveChannels") or []
        if isinstance(v, str):
            v = [v]
        s = frozenset(x for x in v if x)
        sets.append(s)
        order.append((r.get("DIV"), len(s)))
    uniq = len(set(sets))
    print(f"  {len(sets)} recordings, {uniq} distinct InactiveChannels sets")
    if uniq == 1:
        print("  -> IDENTICAL across every recording: CARRIED FORWARD.")
        print("     It is a plate-level property, not a per-recording measurement,")
        print("     and cannot evidence attrition over DIV.")
    else:
        print("  -> VARIES: regenerated per recording. It IS a per-recording")
        print("     hardware record and CAN be tracked over DIV.")
    print("\n  DIV vs count of inactive channels:")
    for div, n in sorted(order, key=lambda t: (t[0] is None, t[0])):
        print(f"    DIV {div}: {n}")
    ns = [n for _, n in order]
    ds = [d for d, _ in order if d is not None]
    if len(ds) == len(ns) and len(ds) > 2:
        r = float(np.corrcoef([float(d) for d in ds], ns)[0, 1])
        print(f"\n  correlation with DIV: r = {r:+.3f}")
        print("  A7a: this is the dataset's OWN record of electrodes not recorded")
        print("  due to malfunction. Rising = hardware attrition. Flat = none.")

    print(f"\nwritten: {out}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
