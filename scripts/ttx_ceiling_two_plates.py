#!/usr/bin/env python3
"""
ttx_ceiling_two_plates.py — C6, the clean test.

The noise ceiling was measured on ONE plate: hPSC_MEA3TTX_DIV29, 192 silenced
electrodes, max 17.70 spikes/min. Every contamination percentage in C7 inherits
the assumption that this transfers.

Rat_MEA2TTX_DIV22 is the independent test: a different species, a different
culture age, a different plate, same 48-well format, same detector, TTX at the
same 1 uM. If the ceiling reproduces, C6 becomes PRIMARY. If it does not, C7's
numbers need rescaling and we find out now rather than in review.

Pre-registered before running (same discipline as the C3 demotion):
    ceiling within  +/-30%  of 17.70  ->  C6 PRIMARY, transfers
    ceiling within  +/-2x                ->  C6 SUPPORTED, state the range
    ceiling beyond  2x                   ->  C6 FAILS, rescale C7 and say so
"""

from pathlib import Path

import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parent.parent
DUR_MIN = 10.0
OUT = []


def say(s=""):
    print(s)
    OUT.append(str(s))


def plate(label, folder, spikes, explog, elec_per_well):
    base = ROOT / folder
    df = pd.read_csv(base / spikes)
    df.columns = [c.strip() for c in df.columns]
    df["Channel"] = df["Channel"].astype(str).str.strip()
    log = pd.read_csv(base / explog)
    log.columns = [c.strip() for c in log.columns]
    log["Well"] = log["Well"].astype(str).str.strip()
    log["Treatment"] = log["Treatment"].astype(str).str.strip()

    counts = df["Channel"].value_counts()
    groups = log.groupby("Treatment")["Well"].apply(list).to_dict()
    res = {}
    for treat, wells in groups.items():
        if treat in ("ExcludedWell", "nan"):
            continue
        rates = []
        for w in wells:
            wc = counts[counts.index.str.startswith(w + "_")]
            r = list(wc.values / DUR_MIN)
            r += [0.0] * (elec_per_well - len(r))
            rates += r
        res[treat] = np.array(rates, dtype=float)

    say("=" * 76)
    say(f"  {label}")
    say("=" * 76)
    say(f"  max spike time {df['Time'].max():.4f} s   "
        f"wells {', '.join(f'{k}={len(v)}' for k, v in sorted(groups.items()))}")
    say("")
    say("  group          n_elec   median      p95      p99      max")
    for treat in sorted(res):
        v = res[treat]
        say(f"  {treat:<13} {len(v):>7}  {np.median(v):>7.2f} "
            f"{np.percentile(v,95):>8.2f} {np.percentile(v,99):>8.2f} {v.max():>8.2f}")
    return res.get("TTX"), res


def main():
    say("C6 — does the TTX noise ceiling reproduce on a second, independent plate?")
    say("")
    say("Pre-registered before running:")
    say("   within +/-30% of 17.70  -> C6 PRIMARY")
    say("   within +/-2x            -> C6 SUPPORTED, state the range")
    say("   beyond 2x               -> C6 FAILS, rescale C7")
    say("")

    a, _ = plate("hPSC_MEA3TTX_DIV29  (human, DIV 29, 48-well)",
                 "data/hPSC_MEA3_Pharmacology/hPSC_MEA3TTX_DIV29",
                 "hPSC_120618_MEA3TTX_DIV29_spikes.csv",
                 "hPSC_120618_MEA3TTX_DIV29_expLog.csv", 16)
    say("")
    b, _ = plate("Rat_MEA2TTX_DIV22   (rat, DIV 22, 48-well)",
                 "data/Rat_MEA2_Pharmacology/Rat_MEA2TTX_DIV22",
                 "Rat_50618_MEA2TTX_DIV22_spikes.csv",
                 "Rat_50618_MEA2TTX_DIV22_expLog.csv", 16)

    say("")
    say("=" * 76)
    say("VERDICT")
    say("=" * 76)
    say("")
    say("                      n    median     p95     p99      MAX (the ceiling)")
    say(f"  human MEA3   {len(a):>8}  {np.median(a):>8.2f} {np.percentile(a,95):>7.2f} "
        f"{np.percentile(a,99):>7.2f} {a.max():>12.2f}")
    say(f"  rat   MEA2   {len(b):>8}  {np.median(b):>8.2f} {np.percentile(b,95):>7.2f} "
        f"{np.percentile(b,99):>7.2f} {b.max():>12.2f}")
    say("")
    ratio = b.max() / a.max()
    say(f"  ceiling ratio rat/human = {ratio:.2f}x")
    say("")
    if 0.7 <= ratio <= 1.3:
        say("  ** C6 -> PRIMARY. ** The ceiling reproduces across species, culture")
        say("  age and plate. It is a property of the detector, not of one plate.")
    elif 0.5 <= ratio <= 2.0:
        say("  ** C6 -> SUPPORTED. ** Same order, not identical. Report the range,")
        say("  not a single number, and recompute C7 at both ends.")
    else:
        say("  ** C6 FAILS. ** The ceiling does not transfer. C7 must be rescaled")
        say("  and the transfer stated as a limitation.")

    pooled = np.concatenate([a, b])
    say("")
    say(f"  pooled silenced electrodes: n={len(pooled)}  median "
        f"{np.median(pooled):.2f}  p99 {np.percentile(pooled,99):.2f}  "
        f"max {pooled.max():.2f} /min")
    say(f"  active-electrode criterion = 10.00 /min")
    say(f"  fraction of ALL silenced electrodes that the criterion would score "
        f"ACTIVE: {int((pooled>=10).sum())}/{len(pooled)} "
        f"({100*(pooled>=10).mean():.2f}%)")
    say("")
    say("  The criterion sits inside the distribution of rates produced by")
    say("  electrodes whose sodium channels are pharmacologically blocked,")
    say("  on two independent plates.")

    (ROOT / "notes" / "ttx_ceiling_two_plates.txt").write_text(
        "\n".join(OUT), encoding="utf-8")
    say("")
    say("written: notes/ttx_ceiling_two_plates.txt")


if __name__ == "__main__":
    main()
