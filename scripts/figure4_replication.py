#!/usr/bin/env python3
"""
Figure 4 — replication on a parallel plate, and what it shows at each criterion.

hPSC_MEA1 and hPSC_MEA2 are the same differentiation batch, cultured and
recorded in parallel on the same days; the data descriptor explicitly licenses
pooling them. Two panels:

  A  Active-electrode count against DIV for both plates, at 10 spikes/min and
     at the meaRtools default of 1 spike/min. The 68%/66% decline replicates
     at 10/min; at 1/min both plates sit at the 384 ceiling throughout.

  B  MEA1 against MEA2 at matched timepoints, both criteria, with Pearson r.
     r = +0.986 at 10/min. At 1/min it collapses to ~+0.29 — not a failure of
     replication but a consequence of it, since both plates are pinned at the
     ceiling and the only remaining between-plate variance is noise.

Panel B is the point of the figure: the same two plates are near-perfectly
correlated or barely correlated at all depending only on the criterion. The
metric carries developmental signal at one cut point and none at the other.

Usage: python scripts/figure4_replication.py
"""

import re
import sys
from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parent.parent
OUTDIR = ROOT / "figures"
TOTAL = 384
DUR_MIN = 600.0 / 60.0          # nominal 600 s recording; see §2.3

# (label, min spikes in recording, colour)
CRITERIA = [
    ("10 spikes/min (Kapucu 2022)", 100, "#d95f0e"),
    ("1 spike/min (meaRtools default)", 11, "#2c7fb8"),
]
PLATES = [
    ("hPSC_MEA1", ROOT / "data/hPSC_MEA1/spikes", "hPSC_*_MEA1_DIV*_spikes.csv", "o", "-"),
    ("hPSC_MEA2", ROOT / "data/hPSC_MEA2/spikes", "hPSC_*_MEA2_DIV*_spikes.csv", "s", "--"),
]


def per_electrode_counts(spikes_dir: Path, pattern: str) -> dict[int, pd.Series]:
    out = {}
    for f in sorted(spikes_dir.glob(pattern)):
        m = re.search(r"DIV(\d+)_spikes\.csv$", f.name)
        if not m:
            continue
        df = pd.read_csv(f)
        df.columns = [c.strip() for c in df.columns]
        out[int(m.group(1))] = df["Channel"].astype(str).str.strip().value_counts()
    return dict(sorted(out.items()))


def active(counts: pd.Series, min_spikes: int) -> int:
    return int((counts >= min_spikes).sum())


def main() -> int:
    data = {}
    for name, sdir, pat, _, _ in PLATES:
        if not list(sdir.glob(pat)):
            print(f"FATAL: no spike files for {name} at {sdir}", file=sys.stderr)
            return 1
        data[name] = per_electrode_counts(sdir, pat)

    divs = sorted(set(data["hPSC_MEA1"]) & set(data["hPSC_MEA2"]))
    if len(divs) < 3:
        print(f"FATAL: only {len(divs)} matched timepoints", file=sys.stderr)
        return 1
    print(f"matched timepoints: {len(divs)}  (DIV {divs[0]}–{divs[-1]})")

    series = {(p, lab): np.array([active(data[p][d], k) for d in divs])
              for p, _, _, _, _ in PLATES for lab, k, _ in CRITERIA}

    fig, (axA, axB) = plt.subplots(1, 2, figsize=(11.2, 4.4))

    # ---- Panel A: trajectories ------------------------------------------
    for lab, _, colour in CRITERIA:
        for pname, _, _, marker, ls in PLATES:
            axA.plot(divs, series[(pname, lab)], marker=marker, ls=ls, ms=4.2,
                     lw=1.5, color=colour, alpha=.9,
                     label=f"{pname}, {lab.split(' (')[0]}")
    axA.axhline(TOTAL, color="#999", lw=.9, ls=":", zorder=0)
    axA.text(divs[-1], TOTAL + 5, f"{TOTAL} electrodes on plate", ha="right",
             va="bottom", fontsize=7.6, color="#777")
    # the shared DIV 48/51/56 depression and DIV 59 recovery (A2): two
    # physically separate plates cannot produce this independently
    anom = [d for d in divs if 47 <= d <= 57]
    if anom:
        y_at = min(min(series[(p, CRITERIA[0][0])][divs.index(d)] for d in anom)
                   for p, _, _, _, _ in PLATES)
        axA.axvspan(min(anom) - 1.4, max(anom) + 1.4, color="#d95f0e",
                    alpha=.07, zorder=0)
        # placed in the empty upper-right quadrant: at the obvious position
        # directly above the trough it collided with the DIV 45–48 points
        axA.annotate("both plates collapse\nand recover together\n(session effect, §3.3)",
                     xy=((min(anom) + max(anom)) / 2, y_at + 8),
                     xytext=(57, 255),
                     ha="center", va="bottom", fontsize=7.0, color="#8a4b2a",
                     linespacing=1.3,
                     arrowprops=dict(arrowstyle="->", color="#8a4b2a", lw=.8,
                                     shrinkB=4))

    axA.set_xlabel("days in vitro", fontsize=9.5)
    axA.set_ylabel("active electrodes", fontsize=9.5)
    axA.set_ylim(0, TOTAL + 42)
    axA.set_title("A   Both plates, both criteria", fontsize=10, loc="left",
                  fontweight="bold")
    axA.legend(fontsize=6.9, frameon=False, loc="lower left", ncol=1)
    axA.tick_params(labelsize=8.4)
    for s in ("top", "right"):
        axA.spines[s].set_visible(False)

    # ---- Panel B: plate against plate -----------------------------------
    summary = []
    for lab, _, colour in CRITERIA:
        x, y = series[("hPSC_MEA1", lab)], series[("hPSC_MEA2", lab)]
        r = float(np.corrcoef(x, y)[0, 1])
        summary.append((lab, r, x, y))
        # jitter the ceiling-pinned series slightly so 19 coincident points
        # do not read as one; the spread is cosmetic and stated as such
        jx, jy = x.astype(float), y.astype(float)
        if r < 0.5:
            rng = np.random.default_rng(4242)
            jx = jx + rng.uniform(-2.2, 2.2, size=x.size)
            jy = jy + rng.uniform(-2.2, 2.2, size=y.size)
        axB.scatter(jx, jy, s=34, color=colour, alpha=.82, zorder=3,
                    edgecolor="white", linewidth=.6,
                    label=f"{lab.split(' (')[0]}   r = {r:+.3f}   (n = {x.size})")

    lo, hi = 0, TOTAL + 20
    axB.plot([lo, hi], [lo, hi], color="#bbb", lw=.9, ls=":", zorder=1)
    axB.text(hi - 8, hi - 30, "identity", fontsize=7.2, color="#999",
             ha="right", rotation=45)
    axB.set_xlim(lo, hi)
    axB.set_ylim(lo, hi)
    axB.set_aspect("equal")
    axB.set_xlabel("hPSC_MEA1, active electrodes", fontsize=9.5)
    axB.set_ylabel("hPSC_MEA2, active electrodes", fontsize=9.5)
    axB.set_title("B   Same plates, same days, two criteria", fontsize=10,
                  loc="left", fontweight="bold")
    axB.legend(fontsize=7.4, frameon=False, loc="upper left")
    axB.tick_params(labelsize=8.4)
    for s in ("top", "right"):
        axB.spines[s].set_visible(False)

    r10 = [r for lab, r, _, _ in summary if lab.startswith("10")][0]
    r1 = [r for lab, r, _, _ in summary if lab.startswith("1 ")][0]
    axB.text(0.98, 0.03,
             "both plates pinned at the ceiling at 1 spike/min:\n"
             "no developmental signal left to correlate",
             transform=axB.transAxes, ha="right", va="bottom", fontsize=7.2,
             color="#2c7fb8", linespacing=1.35)

    # 28 Aug 2026: the figure number was drawn INTO the image and said
    # "Figure 4" while the caption said "Figure 2", because the figures were
    # renumbered into order of first citation and the PNG was not rebuilt.
    # The number now lives in exactly one place, the caption in
    # build_manuscript_pdf.py, which is the same rule the claim set uses for
    # every other quantity: one source, not two that can disagree.
    fig.suptitle("The replication is a property of the criterion, "
                 "not only of the cultures", fontsize=10.5, y=1.02, x=0.02,
                 ha="left", color="#333")
    fig.tight_layout()
    for ext in ("png", "pdf"):
        fig.savefig(OUTDIR / f"figure4_replication.{ext}", dpi=300,
                    bbox_inches="tight")
    print(f"written: {OUTDIR/'figure4_replication.png'} (+ .pdf)")

    # ---- numbers for the text -------------------------------------------
    #
    # These are WRITTEN TO DISK, not merely printed. Until 17 Aug 2026 this
    # script only called savefig, so H3's r = +0.986 -- one of Paper 1's ten
    # claims -- existed nowhere on disk except prose a human had typed into the
    # draft, the claim set and the ledger. Nothing could check it, and a change
    # in this script's behaviour would have gone unnoticed. Same failure class
    # as hPSC_MEA2's missing nae reproduction (audit row S2-1), found by the
    # claim -> script -> number map.
    lines = ["Replication correlation — values for §3.3 (H3).",
             "",
             "Generated by scripts/figure4_replication.py. Do not edit.",
             ""]
    print("\nvalues for §3.3 — check these against the draft:")
    for lab, r, x, y in summary:
        d = 100 * (y[-1] - y[0]) / y[0]
        d1 = 100 * (x[-1] - x[0]) / x[0]
        print(f"  {lab:<34} r = {r:+.3f}")
        print(f"      MEA1 DIV{divs[0]}→{divs[-1]}: {x[0]} → {x[-1]}  ({d1:+.1f}%)")
        print(f"      MEA2 DIV{divs[0]}→{divs[-1]}: {y[0]} → {y[-1]}  ({d:+.1f}%)")
        lines += [
            f"  {lab}",
            f"    Pearson r                 {r:+.3f}",
            f"    matched timepoints        {x.size}  (DIV {divs[0]}-{divs[-1]})",
            f"    hPSC_MEA1  DIV{divs[0]} -> DIV{divs[-1]}   {x[0]} -> {x[-1]}  ({d1:+.1f}%)",
            f"    hPSC_MEA2  DIV{divs[0]} -> DIV{divs[-1]}   {y[0]} -> {y[-1]}  ({d:+.1f}%)",
            "",
        ]

    print(f"\n  r ratio 10/min vs 1/min: {r10:.3f} vs {r1:.3f}")
    lines += [f"  r at 10/min vs 1/min:  {r10:+.3f}  vs  {r1:+.3f}", ""]
    out = ROOT / "notes" / "replication_correlation.txt"
    out.write_text("\n".join(lines), encoding="utf-8")
    print(f"written: notes/{out.name}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
