#!/usr/bin/env python3
"""
day3_threshold_landscape.py

The Day 3 headline figure. Replaces the TTX-contamination curve as the
lead result, because this one depends on no transferred assumption:
it is arithmetic on published spike times against two DOCUMENTED criteria.

  meaRtools default : 1 spike / 60 s   (shipped `parameters` object documents
                      elec_min_rate : num 0.0167 spikes/s; vignette: "a lenient
                      1 spike in 60s"). Implemented as >= 11 spikes over the
                      recording span; the documentation is given to three
                      significant figures and does not distinguish 0.0167 from
                      1/60, which would give >= 10. This figure is IDENTICAL
                      under either -- see notes/criterion-ambiguity.md and
                      scripts/verify_criterion_boundary.py.
  Kapucu et al. 2022: >10 spikes / min (descriptor Methods, verbatim)

Both are published. Neither is wrong. They disagree by up to 109x on the
same electrodes.
"""

import re
from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parent.parent

# 28 Aug 2026: MEA-ToolBox at 6 spikes/min added. §2.5 documents FOUR criteria
# and this figure showed three, so §3.2's table said "four documented sources"
# above three rows. 6 spikes/min = 60 spikes over the ~600 s recording, by the
# same arithmetic as the other three. Found by the Methods-against-Results loop
# audit, notes/LOOPS-M2R-28AUG.md L-3.
CRITERIA = [
    ("meaRtools default, 1 spike/min", 11, "#2c7fb8"),
    ("5 spikes/min", 50, "#7fcdbb"),
    ("MEA-ToolBox, 6 spikes/min", 60, "#41ae76"),
    ("Kapucu 2022, 10 spikes/min", 100, "#d95f0e"),
]


def counts(spikes_dir, pattern):
    out = {}
    for f in sorted(spikes_dir.glob(pattern)):
        m = re.search(r"DIV(\d+)_spikes\.csv$", f.name)
        if not m:
            continue
        df = pd.read_csv(f)
        df.columns = [c.strip() for c in df.columns]
        out[int(m.group(1))] = df["Channel"].astype(str).str.strip().value_counts()
    return out


def main():
    plates = [
        ("hPSC_MEA1 (human)", ROOT / "data/hPSC_MEA1/spikes",
         "hPSC_*_MEA1_DIV*_spikes.csv", 384),
        ("hPSC_MEA2 (human, parallel replicate)", ROOT / "data/hPSC_MEA2/spikes",
         "hPSC_*_MEA2_DIV*_spikes.csv", 384),
        ("Rat_MEA1 (rat)", ROOT / "data/Rat_MEA1/spikes",
         "Rat_*_MEA1_DIV*_spikes.csv", 768),
    ]
    plates = [p for p in plates if list(p[1].glob(p[2]))]

    fig, axes = plt.subplots(2, len(plates), figsize=(6.5 * len(plates), 9),
                             gridspec_kw={"height_ratios": [2, 1]},
                             squeeze=False)

    for col, (label, sdir, pat, total) in enumerate(plates):
        c = counts(sdir, pat)
        divs = sorted(c)
        ax = axes[0][col]
        for name, k, colr in CRITERIA:
            y = [int((c[d] >= k).sum()) for d in divs]
            ax.plot(divs, y, "o-", color=colr, label=name, lw=2, ms=5)
        ax.axhline(total, ls=":", c="grey", lw=1)
        ax.text(divs[-1], total, f" {total} electrodes on plate",
                va="bottom", ha="right", fontsize=8, color="grey")
        ax.set_title(label, fontsize=12, weight="bold")
        ax.set_ylabel("electrodes scored ACTIVE")
        ax.set_ylim(0, total * 1.10)
        ax.grid(alpha=.3)
        if col == 0:
            ax.legend(fontsize=9, loc="lower left")

        ax2 = axes[1][col]
        ratio = []
        for d in divs:
            n1 = int((c[d] >= 11).sum())
            n10 = int((c[d] >= 100).sum())
            ratio.append(n1 / n10 if n10 else np.nan)
        ax2.plot(divs, ratio, "s-", color="#525252", lw=2, ms=5)
        ax2.axhline(1, ls="--", c="k", lw=1)
        ax2.set_yscale("log")
        ax2.set_xlabel("DIV")
        ax2.set_ylabel("ratio\n(1/min : 10/min)")
        ax2.grid(alpha=.3, which="both")
        mx = np.nanmax(ratio)
        ax2.annotate(f"max {mx:.0f}x", xy=(divs[int(np.nanargmax(ratio))], mx),
                     xytext=(8, -2), textcoords="offset points",
                     fontsize=9, weight="bold")

    fig.suptitle(
        "The same electrodes, four published criteria for “active”",
        fontsize=14, weight="bold", y=0.985)
    fig.text(0.5, 0.935,
             "Under the analysis package's own documented default, essentially every electrode is active at every timepoint "
             "and the developmental\ntrajectory disappears. Under the study's criterion it declines. Neither choice is an error; "
             "both are published. Spike times are identical.",
             ha="center", fontsize=9.5, color="#444444")
    fig.tight_layout(rect=[0, 0, 1, 0.925])
    out = ROOT / "figures" / "day3_threshold_landscape.png"
    fig.savefig(out, dpi=160)
    print("written:", out)


if __name__ == "__main__":
    main()
