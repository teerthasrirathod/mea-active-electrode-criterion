#!/usr/bin/env python3
"""
duration_consistency.py — what exactly did derive_duration.py recover?

The pooled solve gave 599.9942 s, but the largest spike time observed on the
human plate is 599.9980 s. A spike cannot land after the recording stops, so the
pooled number is not simply "the recording duration". Three candidates:

  H1  true recording duration, constant, and the pooled median is just noisy
  H2  meaRtools' internal rec.time = (last spike - first spike) on the well/plate
      -- sjemea sets rec.time from the spike range unless told otherwise
  H3  rec.time = (0, last spike), i.e. just the last spike time

H2 and H3 are not the recording length. They are what the ANALYSIS used, which
is what B3 actually turns on -- B3 compares the *written* rule to the *executed*
one, and the executed one used whatever meaRtools believed the duration was.

Solving per DIV and comparing against the spike-time span decides between them.
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


def run(label, spikes_dir, pattern, nae_p, mfr_p, noisy_p):
    say("=" * 92)
    say(f"  {label}")
    say("=" * 92)
    nae, mfr, noisy = wide(nae_p), wide(mfr_p), load_noisy(noisy_p)

    say("")
    say("  DIV   derived_dur    span(all)   last(all)   first(all)   "
        "dur-span    dur-last")
    rows = []
    for f in sorted(spikes_dir.glob(pattern)):
        m = re.search(r"DIV(\d+)_spikes\.csv$", f.name)
        if not m:
            continue
        div = int(m.group(1))
        df = pd.read_csv(f)
        df.columns = [c.strip() for c in df.columns]
        df["Channel"] = df["Channel"].astype(str).str.strip()
        vc = df["Channel"].value_counts()
        t = df["Time"].values
        first, last = float(t.min()), float(t.max())
        span = last - first

        ds = []
        for (w, d), n_act in nae.items():
            if d != div or (w, d) not in mfr:
                continue
            fr = mfr[(w, d)]
            if not np.isfinite(fr) or fr <= 0 or n_act <= 0:
                continue
            drop = noisy.get(div, set())
            act = [c for ch, c in vc.items()
                   if ch.split("_")[0] == w and c >= 100 and ch not in drop]
            if len(act) != int(round(n_act)):
                continue
            ds.append(sum(act) / (n_act * fr))
        if not ds:
            continue
        dur = float(np.median(ds))
        rows.append({"div": div, "dur": dur, "span": span,
                     "last": last, "first": first})
        say(f"  {div:>4}  {dur:>12.6f} {span:>12.6f} {last:>11.6f} "
            f"{first:>12.6f} {dur-span:>10.6f} {dur-last:>11.6f}")

    if not rows:
        return None
    d = pd.DataFrame(rows)

    say("")
    say("  --- which hypothesis fits? (closer to zero wins)")
    say(f"    H1  |derived - 600.000|      median abs = "
        f"{np.median(np.abs(d.dur - 600.0)):.6f} s")
    say(f"    H2  |derived - (last-first)| median abs = "
        f"{np.median(np.abs(d.dur - d.span)):.6f} s")
    say(f"    H3  |derived - last|         median abs = "
        f"{np.median(np.abs(d.dur - d['last'])):.6f} s")
    say("")
    viol = int((d.dur < d["last"] - 1e-9).sum())
    say(f"  recordings where derived duration < last spike time (impossible "
        f"if it is the true length): {viol}/{len(d)}")
    return d


def main():
    a = run("hPSC_MEA1 (human)",
            ROOT / "data/hPSC_MEA1/spikes", "hPSC_*_MEA1_DIV*_spikes.csv",
            ROOT / "data/hPSC_MEA1/summary/hPSC_20517_MEA1_nae.csv",
            ROOT / "data/hPSC_MEA1/summary/hPSC_20517_MEA1_meanfiringrate_by_active_electordes.csv",
            ROOT / "data/hPSC_MEA1/spikes/noisy_electrodes_hPSC_MEA1.csv")
    b = run("Rat_MEA1 (rat)",
            ROOT / "data/Rat_MEA1/spikes", "Rat_*_MEA1_DIV*_spikes.csv",
            ROOT / "data/Rat_MEA1/summary/Rat_190617_MEA1_nae.csv",
            ROOT / "data/Rat_MEA1/summary/Rat_190617_MEA1_meanfiringrate_by_active_electordes.csv",
            ROOT / "data/Rat_MEA1/spikes/noisy_electrodes_Rat_MEA1.csv")

    say("")
    say("=" * 92)
    say("WHAT THIS MEANS FOR B3")
    say("=" * 92)
    say("")
    say("  B3 compares the WRITTEN rule ('>10 spikes per minute') against the")
    say("  EXECUTED one (>=100 spikes). The executed rule used whatever duration")
    say("  meaRtools believed the recording was. So the number that decides B3")
    say("  is meaRtools' rec.time, NOT the true wall-clock recording length.")
    say("")
    say("  If rec.time is the spike-time span, it differs per recording, which")
    say("  means the effective spike-count criterion ALSO differs per recording")
    say("  -- and that is a sharper finding than the off-by-one ever was.")
    (ROOT / "notes" / "duration_consistency.txt").write_text(
        "\n".join(OUT), encoding="utf-8")
    say("")
    say("written: notes/duration_consistency.txt")


if __name__ == "__main__":
    main()
