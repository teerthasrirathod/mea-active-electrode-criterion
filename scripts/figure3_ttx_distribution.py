#!/usr/bin/env python3
"""
figure3_ttx_distribution.py — Figure 3.

Firing rates of pharmacologically silenced electrodes, on two plates and two
species, against the 10 spikes/min active-electrode criterion.

Grouping and rate logic are reused verbatim from ttx_ceiling_two_plates.py so
the figure cannot drift from the numbers in the claim set. The script asserts
against those numbers and refuses to draw if any of them moves.

DESIGN DECISIONS, and why
-------------------------
1. **The 216.40/min rat outlier is drawn, labelled, and explained.** Limitation
   2 says report percentiles and never a maximum -- so the maximum is NOT the
   headline. But hiding it would be worse than featuring it: it is the point at
   which a pre-registered test failed, and a figure that quietly clipped it
   would be doing the thing this paper is about. It gets an annotation naming
   the well and the failure.

2. **Untreated electrodes are shown alongside.** Silenced rates alone say
   nothing about whether 10/min is a sensible cut. Against untreated medians of
   70 and 6 spikes/min the separation is visible, and so is the fact that the
   criterion sits at the TOP of the noise rather than clear of it.

3. **Every electrode is a point.** No box plot, no violin. n = 192 and 224 are
   small enough to show whole, and a box plot would summarise away exactly the
   tail behaviour that made the transfer test fail.

4. **Percentile markers, not error bars.** These are not estimates with
   sampling error; they are order statistics of a measured set.

Input : data/{hPSC_MEA3,Rat_MEA2}_Pharmacology/...
Output: figures/figure3_ttx_distribution.png (+ .pdf)
"""

from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt          # noqa: E402
import numpy as np                       # noqa: E402
import pandas as pd                      # noqa: E402

ROOT = Path(__file__).resolve().parent.parent
OUTDIR = ROOT / "figures"
DUR_MIN = 10.0
CRITERION = 10.0

PLATES = [
    ("hPSC_MEA3TTX  ·  human, DIV 29",
     "data/hPSC_MEA3_Pharmacology/hPSC_MEA3TTX_DIV29",
     "hPSC_120618_MEA3TTX_DIV29_spikes.csv",
     "hPSC_120618_MEA3TTX_DIV29_expLog.csv", 16),
    ("Rat_MEA2TTX  ·  rat, DIV 22",
     "data/Rat_MEA2_Pharmacology/Rat_MEA2TTX_DIV22",
     "Rat_50618_MEA2TTX_DIV22_spikes.csv",
     "Rat_50618_MEA2TTX_DIV22_expLog.csv", 16),
]

C_TTX = "#c1442e"
C_UNT = "#9aa4ad"
C_CRIT = "#1b6ca8"


def rates(folder, spikes, explog, elec_per_well):
    """Identical logic to ttx_ceiling_two_plates.py — do not diverge."""
    base = ROOT / folder
    df = pd.read_csv(base / spikes)
    df.columns = [c.strip() for c in df.columns]
    df["Channel"] = df["Channel"].astype(str).str.strip()
    log = pd.read_csv(base / explog)
    log.columns = [c.strip() for c in log.columns]
    log["Well"] = log["Well"].astype(str).str.strip()
    log["Treatment"] = log["Treatment"].astype(str).str.strip()

    counts = df["Channel"].value_counts()
    out = {}
    for treat, wells in log.groupby("Treatment")["Well"].apply(list).items():
        if treat in ("ExcludedWell", "nan"):
            continue
        r, tags = [], []
        for w in wells:
            wc = counts[counts.index.str.startswith(w + "_")]
            vals = list(wc.values / DUR_MIN)
            vals += [0.0] * (elec_per_well - len(vals))
            r += vals
            tags += [w] * elec_per_well
        out[treat] = (np.array(r, float), tags)
    return out


def main():
    data = {}
    for label, folder, sp, lg, npw in PLATES:
        data[label] = rates(folder, sp, lg, npw)

    # Guard against silent drift from the frozen numbers.
    h = data[PLATES[0][0]]["TTX"][0]
    r = data[PLATES[1][0]]["TTX"][0]
    assert len(h) == 192 and len(r) == 224, f"n = {len(h)}, {len(r)}; expected 192, 224"
    for v, exp in ((h, (3.30, 5.14, 9.43, 17.70)), (r, (3.20, 5.47, 13.37, 216.40))):
        got = (np.median(v), np.percentile(v, 95), np.percentile(v, 99), v.max())
        assert all(abs(a - b) < 0.01 for a, b in zip(got, exp)), f"{got} != {exp}"

    pooled = np.concatenate([h, r])
    p99 = np.percentile(pooled, 99)
    n_over = int((pooled >= CRITERION).sum())

    fig, axes = plt.subplots(2, 1, figsize=(8.0, 5.4), sharex=True)
    rng = np.random.default_rng(20260811)

    for ax, (label, _, _, _, _) in zip(axes, PLATES):
        groups = data[label]
        ttx, tags = groups["TTX"]
        unt = np.concatenate([v for k, (v, _) in groups.items() if k != "TTX"])

        # Untreated, behind, muted. Zeros nudged so a log axis can show them.
        ax.scatter(np.clip(unt, 0.1, None), rng.normal(1.72, .075, len(unt)),
                   s=13, color=C_UNT, alpha=.55, lw=0, zorder=2)
        ax.scatter(np.clip(ttx, 0.1, None), rng.normal(1.0, .075, len(ttx)),
                   s=15, color=C_TTX, alpha=.75, lw=0, zorder=3)

        for val, name, dy in ((np.median(ttx), "median", 0),
                              (np.percentile(ttx, 99), "p99", 0)):
            ax.plot([val, val], [0.80, 1.20], color="#4a1f16", lw=1.5, zorder=5)
            ax.text(val, 0.70, f"{name}\n{val:.2f}", ha="center", va="top",
                    fontsize=6.9, color="#4a1f16", linespacing=1.2)

        ax.axvline(CRITERION, color=C_CRIT, ls="--", lw=1.5, zorder=4)
        ax.set_xscale("log")
        ax.set_xlim(0.07, 4000)
        ax.set_ylim(0.42, 2.15)
        ax.set_yticks([1.0, 1.72])
        ax.set_yticklabels(["TTX\n(silenced)", "untreated"], fontsize=8)
        ax.tick_params(axis="y", length=0)
        for s in ("left", "right", "top"):
            ax.spines[s].set_visible(False)
        ax.grid(axis="x", alpha=.14, zorder=0)
        ax.text(0.075, 2.05, label, fontsize=9, va="top", fontweight="bold",
                color="#333")
        ax.text(CRITERION * 1.18, 2.02, "criterion\n10 spikes/min", fontsize=7.4,
                color=C_CRIT, va="top", linespacing=1.2)

    # The failed transfer test, named rather than clipped.
    worst = r.max()
    bad_well = data[PLATES[1][0]]["TTX"][1][int(np.argmax(r))]
    axes[1].annotate(
        f"{worst:.1f}/min — well {bad_well}\npre-registered transfer test FAILED here\n"
        f"(rat max {worst:.1f} vs human 17.7, 12.2×; 222 of 224 fall below 17.7)",
        xy=(worst, 0.93), xytext=(430, 0.68), fontsize=6.9, color="#4a1f16",
        ha="center", va="center", linespacing=1.35,
        bbox=dict(fc="white", ec="none", pad=1.5),
        arrowprops=dict(arrowstyle="->", color="#4a1f16", lw=.9,
                        connectionstyle="arc3,rad=0.25"))

    axes[1].set_xlabel("Firing rate per electrode (spikes / min, log scale)",
                       fontsize=9.5, labelpad=6)

    fig.text(0.012, 0.012,
             f"Pooled across both plates, n = {len(pooled)} silenced electrodes: "
             f"99th percentile = {p99:.2f} spikes/min, against a criterion of "
             f"{CRITERION:.0f}.  {n_over} of {len(pooled)} "
             f"({100*n_over/len(pooled):.2f}%) would be scored active.",
             fontsize=7.8, color="#4a1f16", va="bottom")

    fig.tight_layout(rect=(0, 0.055, 1, 1))
    OUTDIR.mkdir(exist_ok=True)
    for ext in ("png", "pdf"):
        fig.savefig(OUTDIR / f"figure3_ttx_distribution.{ext}", dpi=300,
                    bbox_inches="tight")

    print(f"human TTX n={len(h)}  median {np.median(h):.2f}  p99 {np.percentile(h,99):.2f}  max {h.max():.2f}")
    print(f"rat   TTX n={len(r)}  median {np.median(r):.2f}  p99 {np.percentile(r,99):.2f}  max {r.max():.2f}")
    print(f"pooled n={len(pooled)}  p99 {p99:.2f}  >= {CRITERION:g}/min: {n_over} ({100*n_over/len(pooled):.2f}%)")
    print(f"worst rat electrode in well {bad_well}")
    print("written: figures/figure3_ttx_distribution.{png,pdf}")


if __name__ == "__main__":
    main()
