#!/usr/bin/env python3
"""
derive_duration.py — settle A1 exactly, from files already on disk.

The .h5 attribute DurationInSec is unreachable: GIN does not serve HTTP range
requests, so reading it costs 21 GB per file. But the duration is recoverable
from the published outputs by arithmetic.

meaRtools' mean firing rate by active electrodes is, per well per DIV:

    MFR = (1 / n_active) * sum_over_active( spikes_i / duration_seconds )
        = total_spikes_on_active / (n_active * duration_seconds)

Every term but the duration is known to full precision:

    total_spikes_on_active   from the published spike-time CSVs
    n_active                 published in nae.csv, and reproduced 336/336 by us across three plates
    MFR                      published to 15 significant figures

so

    duration = total_spikes_on_active / (n_active * MFR)

Solved independently in every well-DIV cell. If the answers agree, the duration
is derived, not assumed, and B3's integer boundary is decided.

WHY THIS MATTERS FOR B3
-----------------------
Kapucu's stated rule is ">10 spikes per minute", i.e. count > duration/6.

    duration = 600.000  ->  count > 100.000  ->  >= 101   (implemented: >= 100)
                            the stated and implemented rules DIFFER. B3 stands.

    duration = 599.700  ->  count >  99.950  ->  >= 100   (implemented: >= 100)
                            the stated and implemented rules AGREE. B3 EVAPORATES.

Observed max spike times run 599.7377-599.9980 s, which spans that boundary.
So B3 genuinely turns on this number and cannot be asserted without it.
"""

import re
from pathlib import Path

import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parent.parent
OUT = []


def say(s=""):
    print(s)
    OUT.append(str(s))


def wide(path):
    df = pd.read_csv(path)
    df.columns = [c.strip().strip('"') for c in df.columns]
    out = {}
    for _, row in df.iterrows():
        w = str(row["well"]).strip().strip('"')
        for c in df.columns:
            if c.startswith("divDIV"):
                v = row[c]
                if pd.isna(v):
                    continue
                try:
                    out[(w, int(c.replace("divDIV", "")))] = float(v)
                except (TypeError, ValueError):
                    pass
    return out


def load_noisy(p):
    df = pd.read_csv(p, dtype=str)
    return {int(str(c).strip().replace("DIV", "")):
            {str(v).strip() for v in df[c].dropna() if str(v).strip()}
            for c in df.columns}


def solve(label, spikes_dir, pattern, nae_p, mfr_p, noisy_p):
    say("=" * 74)
    say(f"A1 — duration solved from published MFR   {label}")
    say("=" * 74)

    nae, mfr, noisy = wide(nae_p), wide(mfr_p), load_noisy(noisy_p)

    counts = {}
    for f in sorted(spikes_dir.glob(pattern)):
        m = re.search(r"DIV(\d+)_spikes\.csv$", f.name)
        if not m:
            continue
        df = pd.read_csv(f)
        df.columns = [c.strip() for c in df.columns]
        counts[int(m.group(1))] = df["Channel"].astype(str).str.strip().value_counts()

    rows = []
    for (w, div), n_act in nae.items():
        if div not in counts or (w, div) not in mfr:
            continue
        f = mfr[(w, div)]
        if not np.isfinite(f) or f <= 0 or n_act <= 0:
            continue
        vc = counts[div]
        drop = noisy.get(div, set())
        active = [c for ch, c in vc.items()
                  if ch.split("_")[0] == w and c >= 100 and ch not in drop]
        if len(active) != int(round(n_act)):
            continue                      # only use cells where nae reproduces
        tot = float(sum(active))
        rows.append({"well": w, "div": div, "nae": int(n_act),
                     "spikes": tot, "mfr": f,
                     "duration": tot / (n_act * f)})

    if not rows:
        say("  no usable cells — nothing concluded")
        return None

    d = pd.DataFrame(rows)
    v = d["duration"].values
    say("")
    say(f"  cells solved independently: {len(v)}")
    say(f"  duration  min    = {v.min():.9f} s")
    say(f"            median = {np.median(v):.9f} s")
    say(f"            max    = {v.max():.9f} s")
    say(f"            spread = {v.max() - v.min():.3e} s")
    say(f"            sd     = {v.std(ddof=1):.3e} s")
    say("")
    say(f"  distance from 600.000000: {abs(np.median(v) - 600.0):.3e} s")
    return v


def verdict(all_v):
    v = np.concatenate([x for x in all_v if x is not None])
    med = float(np.median(v))
    say("=" * 74)
    say("VERDICT — A1 and B3")
    say("=" * 74)
    say("")
    say(f"  {len(v)} independent solutions, pooled across both plates")
    say(f"  derived duration = {med:.9f} s   (spread {v.max()-v.min():.2e} s)")
    say("")
    exact = abs(med - 600.0) < 1e-6
    if exact:
        say("  -> 600.000000 s exactly. A1 is DERIVED-exact, not merely nominal.")
    else:
        say(f"  -> NOT exactly 600 s. Deviation {med - 600.0:+.6f} s.")
    say("")
    thr = med / 6.0
    say(f"  Kapucu's stated rule '>10 spikes/min' means count > duration/6")
    say(f"                                             = {thr:.6f}")
    say(f"  so the stated rule admits an electrode at count >= {int(np.floor(thr)) + 1}")
    say(f"  the implemented rule, derived from 336/336 published values, is >= 100")
    say("")
    if int(np.floor(thr)) + 1 == 100:
        say("  ** B3 EVAPORATES. ** Stated and implemented rules agree at this")
        say("  duration. The off-by-one was an artefact of assuming 600.000 s.")
        say("  WITHDRAW B3.")
    else:
        say(f"  ** B3 STANDS. ** Stated rule = >= {int(np.floor(thr)) + 1}, "
            f"implemented = >= 100.")
        say("  The written criterion and the executed criterion differ by one")
        say("  spike, and only a derivation could have shown it.")


def main():
    a = solve("hPSC_MEA1 (human)",
              ROOT / "data/hPSC_MEA1/spikes", "hPSC_*_MEA1_DIV*_spikes.csv",
              ROOT / "data/hPSC_MEA1/summary/hPSC_20517_MEA1_nae.csv",
              ROOT / "data/hPSC_MEA1/summary/hPSC_20517_MEA1_meanfiringrate_by_active_electordes.csv",
              ROOT / "data/hPSC_MEA1/spikes/noisy_electrodes_hPSC_MEA1.csv")
    b = solve("Rat_MEA1 (rat)",
              ROOT / "data/Rat_MEA1/spikes", "Rat_*_MEA1_DIV*_spikes.csv",
              ROOT / "data/Rat_MEA1/summary/Rat_190617_MEA1_nae.csv",
              ROOT / "data/Rat_MEA1/summary/Rat_190617_MEA1_meanfiringrate_by_active_electordes.csv",
              ROOT / "data/Rat_MEA1/spikes/noisy_electrodes_Rat_MEA1.csv")
    if a is not None or b is not None:
        verdict([a, b])
    (ROOT / "notes" / "duration_derivation.txt").write_text(
        "\n".join(OUT), encoding="utf-8")
    say("")
    say("written: notes/duration_derivation.txt")


if __name__ == "__main__":
    main()
