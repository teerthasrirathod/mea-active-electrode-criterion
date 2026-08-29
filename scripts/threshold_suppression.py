#!/usr/bin/env python3
"""
threshold_suppression.py -- M4 and A2b, from published files only.

WHY THIS SCRIPT EXISTS
----------------------
On 16 August 2026 the numbers in draft §3.6 and §3.6.1 were computed in a
sandbox scratch directory by two throwaway scripts that were never saved. The
manuscript therefore asserted a numbered result that nothing in this repository
could regenerate -- the identical defect found in the same session for
hPSC_MEA2's nae table (audit row S2-1). This script closes that.

WHAT IT PRODUCES
----------------
M4  -- the flagged ("noisy") electrodes sit at the BOTTOM of the firing-rate
       distribution for their own recording day, not the top, with a minor mode
       of two electrodes per plate at the top.

A2b -- on the anomalous recording days the active-electrode count collapses
       while NO electrode falls silent, and the loss is confined to the upper
       part of the distribution; the lower tail rests on a floor that does not
       move and that floor matches the pharmacologically silenced rate.

DEFINITIONS, STATED BECAUSE THEY DECIDE THE NUMBERS
---------------------------------------------------
* rate            spikes per 600 s recording, converted to spikes/min as
                  count / 10. The recovered analysis duration (599.688-599.997 s,
                  derive_duration.py) differs from 600 s by <0.06% and is not
                  used here; using it would change no reported digit.
* present         a channel appearing at least once in that day's spike file.
                  A channel absent from the file produced no detected spikes.
* silent          nominal electrodes minus present. Reported explicitly so
                  "no electrode fell silent" is a measurement, not an absence.
* percentile-within-day
                  rank of an electrode's count among ALL present electrodes on
                  that plate that day, as a percentage. Bottom decile is <=10,
                  top decile >=90. Same convention as characterise_noisy.py.
* baseline        DIV 45, the last timepoint before the DIV 48/51/56 collapse.

Reads only published files. Writes notes/threshold_suppression.txt.
"""
from pathlib import Path
import re
import sys

import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
OUT = []


def say(s=""):
    OUT.append(s)
    print(s)


# --------------------------------------------------------------- plate config
PLATES = [
    ("hPSC_MEA1", "data/hPSC_MEA1/spikes", "hPSC_*_MEA1_DIV*_spikes.csv",
     "data/hPSC_MEA1/spikes/noisy_electrodes_hPSC_MEA1.csv", 384),
    ("hPSC_MEA2", "data/hPSC_MEA2/spikes", "hPSC_*_MEA2_DIV*_spikes.csv",
     "data/hPSC_MEA2/spikes/noisy_electrodes_hPSC_MEA2.csv", 384),
    ("Rat_MEA1", "data/Rat_MEA1/spikes", "Rat_*_MEA1_DIV*_spikes.csv",
     "data/Rat_MEA1/spikes/noisy_electrodes_Rat_MEA1.csv", 768),
]

# Silenced-electrode reference, hPSC_MEA3TTX DIV 29, from
# ttx_ceiling_two_plates.py. Quoted here so the floor comparison is explicit.
TTX_HUMAN_MEDIAN = 3.30      # spikes/min
TTX_HUMAN_P95 = 5.14
TTX_HUMAN_P99 = 9.43
TTX_HUMAN_MAX = 17.70


def div_of(p):
    m = re.search(r"DIV(\d+)_spikes", str(p))
    return int(m.group(1)) if m else None


def load_counts(spikes_dir, pattern):
    """{div: Series(channel -> spike count)} from published spike-time files."""
    out = {}
    for f in sorted((ROOT / spikes_dir).glob(pattern), key=div_of):
        df = pd.read_csv(f, usecols=["Channel"])
        out[div_of(f)] = df["Channel"].value_counts()
    return out


def load_noisy(path):
    """{div: set(channel)} from the published noisy-electrode file."""
    df = pd.read_csv(ROOT / path)
    out = {}
    for col in df.columns:
        m = re.search(r"(\d+)", str(col))
        if not m:
            continue
        out[int(m.group(1))] = {
            str(v).strip() for v in df[col].dropna() if str(v).strip()
        }
    return out


def pct_within(value, arr):
    """Percentage of arr strictly below value. 0 = lowest, 100 = highest."""
    return 100.0 * float((arr < value).sum()) / len(arr)


# ------------------------------------------------------------------------ M4
def m4_flagged_position(name, counts, noisy):
    say("=" * 74)
    say(f"M4  where do flagged electrodes sit?   {name}")
    say("=" * 74)
    say("")

    ranks, rates, n_obs = [], [], 0
    for div, vc in sorted(counts.items()):
        n_obs += len(vc)
        arr = vc.values.astype(float)
        for ch in noisy.get(div, set()):
            if ch in vc.index:
                ranks.append(pct_within(float(vc[ch]), arr))
                rates.append(float(vc[ch]) / 10.0)

    ranks = np.array(ranks)
    rates = np.array(rates)
    bottom = int((ranks <= 10).sum())
    top = int((ranks >= 90).sum())
    plate_med = np.median(np.concatenate(
        [c.values.astype(float) for c in counts.values()]))

    say(f"  electrode-DIV observations           {n_obs}")
    say(f"  flagged and present in the spike file {len(ranks)}")
    say(f"  in the BOTTOM decile of their own day  {bottom}"
        f"  ({100.0 * bottom / len(ranks):.0f}%)")
    say(f"  in the TOP decile of their own day     {top}"
        f"  ({100.0 * top / len(ranks):.0f}%)")
    say(f"  median rate of flagged electrodes      {np.median(rates):.1f} spikes/min")
    say(f"  plate-wide median, all electrodes      {plate_med:.0f} spikes/600 s"
        f"  = {plate_med / 10.0:.1f} spikes/min")
    say(f"  ratio, typical electrode : flagged     "
        f"{plate_med / 10.0 / np.median(rates):.0f}x")
    say("")
    return bottom, top, len(ranks), float(np.median(rates))


# ----------------------------------------------------------------------- A2b
def a2b_distribution(name, counts, n_nominal, baseline_div, anomaly_divs):
    say("=" * 74)
    say(f"A2b  distribution across the anomalous days   {name}")
    say("=" * 74)
    say("")
    say(f"  {'DIV':>4} {'present':>8} {'silent':>7} {'p10':>7} {'p25':>7}"
        f" {'p50':>7} {'p75':>7} {'p90':>7} {'>=100':>7}")
    for div, vc in sorted(counts.items()):
        arr = np.sort(vc.values.astype(float))
        silent = n_nominal - len(arr)
        q = [np.percentile(arr, p) for p in (10, 25, 50, 75, 90)]
        say(f"  {div:>4} {len(arr):>8} {silent:>7} "
            + " ".join(f"{v:>7.0f}" for v in q)
            + f" {int((arr >= 100).sum()):>7}")
    say("")

    base = np.sort(counts[baseline_div].values.astype(float))
    say(f"  ratio to DIV {baseline_div} at each percentile (1.00 = unchanged)")
    say(f"  {'DIV':>4} {'p25':>7} {'p50':>7} {'p75':>7} {'p90':>7} {'silent':>8}")
    ratios = {}
    for div in anomaly_divs:
        arr = np.sort(counts[div].values.astype(float))
        r = [np.percentile(arr, p) / np.percentile(base, p)
             for p in (25, 50, 75, 90)]
        ratios[div] = r
        say(f"  {div:>4} " + " ".join(f"{v:>7.2f}" for v in r)
            + f" {n_nominal - len(arr):>8}")
    say("")

    floor = [np.percentile(np.sort(vc.values.astype(float)), 10)
             for _, vc in sorted(counts.items())]
    say(f"  bottom decile across ALL {len(floor)} recordings of this plate:")
    say(f"    min {min(floor):.0f}  max {max(floor):.0f} spikes/600 s"
        f"   =  {min(floor) / 10.0:.1f} to {max(floor) / 10.0:.1f} spikes/min")
    say(f"    silenced reference (TTX, human plate): median "
        f"{TTX_HUMAN_MEDIAN:.2f} spikes/min")
    say("")
    return ratios, (min(floor) / 10.0, max(floor) / 10.0)


def main():
    say("threshold_suppression.py -- M4 and A2b from published files")
    say("")

    loaded = {}
    for name, sdir, pat, npath, nel in PLATES:
        loaded[name] = (load_counts(sdir, pat), load_noisy(npath), nel)

    # ---- M4, on the two plates the flag was characterised on (A6b) ----------
    tot_bottom = tot_top = tot_n = 0
    for name in ("hPSC_MEA1", "Rat_MEA1"):
        counts, noisy, _ = loaded[name]
        b, t, n, _ = m4_flagged_position(name, counts, noisy)
        tot_bottom += b
        tot_top += t
        tot_n += n

    say("=" * 74)
    say("M4  pooled across hPSC_MEA1 and Rat_MEA1")
    say("=" * 74)
    say("")
    say(f"  flagged electrode-recordings   {tot_n}")
    say(f"  in the bottom decile           {tot_bottom}"
        f"  ({100.0 * tot_bottom / tot_n:.0f}%)")
    say(f"  in the top decile              {tot_top}")
    say("")

    # ---- A2b, on the two parallel human plates -----------------------------
    for name in ("hPSC_MEA1", "hPSC_MEA2"):
        counts, _, nel = loaded[name]
        a2b_distribution(name, counts, nel, 45, (48, 51, 56, 59))

    (ROOT / "notes" / "threshold_suppression.txt").write_text(
        "\n".join(OUT) + "\n", encoding="utf-8")
    say("written: notes/threshold_suppression.txt")
    return 0


if __name__ == "__main__":
    sys.exit(main())
