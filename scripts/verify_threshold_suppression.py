#!/usr/bin/env python3
"""
verify_threshold_suppression.py -- independent second implementation of M4/A2b.

WHY
---
§2.4 claims the reproduction procedure was "implemented twice, independently"
and that "reported figures are those on which both agree". H1 meets that
standard. When M4 and A2b were added on 16 August 2026 they did not: they came
from a single implementation, written once, in a scratch directory.

This is the second implementation. It is deliberately written a different way:

  * spike counts accumulated with collections.Counter over the raw Channel
    column rather than pandas value_counts;
  * every plate expanded to a dense fixed-length vector of nominal electrodes,
    with absent channels entered as explicit zeros, rather than operating on the
    present-channels-only series;
  * ranks computed by explicit comparison counting rather than np.percentile;
  * percentiles taken with the 'lower' interpolation convention rather than the
    default linear one.

Those choices are not arbitrary. Each is a place the first implementation could
have been quietly wrong: zero-padding changes every percentile if any channel is
absent, and interpolation convention changes a percentile whenever the rank
falls between two samples. If both implementations agree despite differing on
all four, the numbers are not artefacts of either.

Exits non-zero on any disagreement outside the stated tolerance.
"""
from collections import Counter
from pathlib import Path
import csv
import re
import sys

ROOT = Path(__file__).resolve().parents[1]

PLATES = {
    "hPSC_MEA1": ("data/hPSC_MEA1/spikes", "hPSC_", "_MEA1_DIV", 384,
                  "data/hPSC_MEA1/spikes/noisy_electrodes_hPSC_MEA1.csv"),
    "hPSC_MEA2": ("data/hPSC_MEA2/spikes", "hPSC_", "_MEA2_DIV", 384,
                  "data/hPSC_MEA2/spikes/noisy_electrodes_hPSC_MEA2.csv"),
    "Rat_MEA1": ("data/Rat_MEA1/spikes", "Rat_", "_MEA1_DIV", 768,
                 "data/Rat_MEA1/spikes/noisy_electrodes_Rat_MEA1.csv"),
}

# ---- what the draft and claim set assert, transcribed by hand from the text --
EXPECT_M4 = {
    #            flagged, bottom-decile, top-decile, median spikes/min
    "hPSC_MEA1": (47, 36, 2, 2.70),
    "Rat_MEA1": (44, 40, 2, 2.65),
}
EXPECT_M4_POOLED = (91, 76, 4)
EXPECT_A2B = {
    # plate -> div -> (p25, p50, p75, p90) ratio to DIV 45, silent count
    "hPSC_MEA1": {51: (0.88, 0.47, 0.20, 0.14, 0),
                  56: (0.86, 0.43, 0.16, 0.09, 0)},
    "hPSC_MEA2": {51: (0.79, 0.44, 0.17, 0.16, 0),
                  56: (0.80, 0.42, 0.16, 0.14, 0)},
}
# floor claim, DIV 42 onward, spikes per 600 s. Corrected from (30, 33) on
# 16 Aug: hPSC_MEA2 runs 29-34 over that window, and the narrower range had been
# read off hPSC_MEA1 alone.
EXPECT_FLOOR = (29, 34)
FLOOR_FROM_DIV = 42

# TOLERANCE, AND WHY IT IS THIS SIZE
# ----------------------------------
# The two implementations use different percentile conventions -- numpy's
# default linear interpolation in threshold_suppression.py, the 'lower' sample
# convention here. On these distributions that shifts individual ratios by up to
# 0.017 (hPSC_MEA2 DIV 51 p25: 0.773 vs 0.790). It changes no conclusion: p25
# lands in 0.77-0.88 either way and p90 in 0.09-0.16 either way.
#
# So a tolerance of 0.005 would be asserting a precision the data does not
# carry. 0.02 is the honest figure and it is stated in the draft alongside the
# table rather than hidden here.
TOL_RATIO = 0.02
TOL_RATE = 0.005      # rates are exact to 2 dp; no convention dependence

fails = []
notes = []


def check(ok, label, got, want):
    line = f"  {'PASS' if ok else 'FAIL'}  {label:<52} got {got!s:<22} want {want!s}"
    print(line)
    if not ok:
        fails.append(f"{label}: got {got}, want {want}")


def counts_for(plate):
    """{div: [count per nominal electrode, absent channels as 0]} plus the
    channel-id list, built with Counter and explicit zero padding."""
    sdir, pre, mid, nominal, _ = PLATES[plate]
    per_div = {}
    ids = set()
    for f in sorted((ROOT / sdir).glob(f"{pre}*{mid}*_spikes.csv")):
        d = int(re.search(r"DIV(\d+)_spikes", f.name).group(1))
        c = Counter()
        with open(f, newline="", encoding="utf-8") as fh:
            r = csv.reader(fh)
            hdr = next(r)
            ci = [i for i, h in enumerate(hdr) if h.strip().lower() == "channel"][0]
            for row in r:
                if row:
                    c[row[ci].strip()] += 1
        per_div[d] = c
        ids |= set(c)
    return per_div, sorted(ids), nominal


def dense(counter, ids, nominal):
    """Fixed-length vector: every observed channel id, absent entered as 0,
    padded to the nominal electrode count."""
    v = [counter.get(ch, 0) for ch in ids]
    v += [0] * (nominal - len(v))
    return sorted(v)


def pctile_lower(sorted_v, p):
    """'lower' convention: the largest sample at or below rank p."""
    if not sorted_v:
        return float("nan")
    k = int(p / 100.0 * (len(sorted_v) - 1))
    return float(sorted_v[k])


def rank_pct(value, vec):
    """Percentage of vec strictly below value, by explicit counting."""
    below = sum(1 for x in vec if x < value)
    return 100.0 * below / len(vec)


def noisy_for(plate):
    _, _, _, _, npath = PLATES[plate]
    out = {}
    with open(ROOT / npath, newline="", encoding="utf-8") as fh:
        rows = list(csv.reader(fh))
    hdr = rows[0]
    for j, h in enumerate(hdr):
        m = re.search(r"(\d+)", h)
        if not m:
            continue
        s = set()
        for row in rows[1:]:
            if j < len(row) and row[j].strip():
                s.add(row[j].strip())
        out[int(m.group(1))] = s
    return out


def main():
    print("verify_threshold_suppression.py -- independent check of M4 and A2b")
    print("")

    # ------------------------------------------------------------------ M4 --
    print("M4  flagged-electrode position")
    pooled_n = pooled_bottom = pooled_top = 0
    for plate in ("hPSC_MEA1", "Rat_MEA1"):
        per_div, _, _ = counts_for(plate)
        noisy = noisy_for(plate)
        ranks, rates = [], []
        for d, c in per_div.items():
            present = list(c.values())
            for ch in noisy.get(d, set()):
                if ch in c:
                    ranks.append(rank_pct(c[ch], present))
                    rates.append(c[ch] / 10.0)
        n = len(ranks)
        bottom = sum(1 for r in ranks if r <= 10)
        top = sum(1 for r in ranks if r >= 90)
        rates.sort()
        med = (rates[n // 2] if n % 2 else (rates[n // 2 - 1] + rates[n // 2]) / 2)
        exp_n, exp_b, exp_t, exp_med = EXPECT_M4[plate]
        check(n == exp_n, f"{plate} flagged and present", n, exp_n)
        check(bottom == exp_b, f"{plate} in bottom decile", bottom, exp_b)
        check(top == exp_t, f"{plate} in top decile", top, exp_t)
        check(abs(med - exp_med) <= TOL_RATE,
              f"{plate} median flagged rate", f"{med:.3f}", exp_med)
        pooled_n += n
        pooled_bottom += bottom
        pooled_top += top

    en, eb, et = EXPECT_M4_POOLED
    check(pooled_n == en, "pooled flagged", pooled_n, en)
    check(pooled_bottom == eb, "pooled in bottom decile", pooled_bottom, eb)
    check(pooled_top == et, "pooled in top decile", pooled_top, et)
    print("")

    # ----------------------------------------------------------------- A2b --
    print("A2b  distribution across the anomalous days")
    for plate, exp in EXPECT_A2B.items():
        per_div, ids, nominal = counts_for(plate)
        base = dense(per_div[45], ids, nominal)
        for div, (e25, e50, e75, e90, esilent) in exp.items():
            vec = dense(per_div[div], ids, nominal)
            silent = sum(1 for x in vec if x == 0)
            check(silent == esilent, f"{plate} DIV {div} electrodes silent",
                  silent, esilent)
            for p, e in ((25, e25), (50, e50), (75, e75), (90, e90)):
                got = pctile_lower(vec, p) / pctile_lower(base, p)
                check(abs(got - e) <= TOL_RATIO,
                      f"{plate} DIV {div} p{p} ratio to DIV 45",
                      f"{got:.3f}", e)
    print("")

    # --------------------------------------------------------------- floor --
    print(f"A2b  bottom-decile floor from DIV {FLOOR_FROM_DIV} onward")
    lo, hi = EXPECT_FLOOR
    for plate in ("hPSC_MEA1", "hPSC_MEA2"):
        per_div, ids, nominal = counts_for(plate)
        vals = [pctile_lower(dense(c, ids, nominal), 10)
                for d, c in sorted(per_div.items()) if d >= FLOOR_FROM_DIV]
        check(lo <= min(vals) and max(vals) <= hi,
              f"{plate} bottom decile within [{lo}, {hi}]",
              f"{min(vals):.0f}-{max(vals):.0f}", f"{lo}-{hi}")
        early = [pctile_lower(dense(c, ids, nominal), 10)
                 for d, c in sorted(per_div.items()) if d < FLOOR_FROM_DIV]
        notes.append(f"{plate}: bottom decile before DIV {FLOOR_FROM_DIV} runs "
                     f"{min(early):.0f}-{max(early):.0f} spikes/600 s, which is "
                     f"why the floor claim is scoped to the late phase")
    print("")

    for n in notes:
        print(f"  note: {n}")
    print("")
    print("=" * 64)
    print(f"{len(fails)} disagreement(s) between the two implementations")
    if fails:
        for f in fails:
            print(f"  - {f}")
    print("=" * 64)
    return 1 if fails else 0


if __name__ == "__main__":
    sys.exit(main())
