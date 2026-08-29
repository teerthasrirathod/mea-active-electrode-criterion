#!/usr/bin/env python3
"""
verify_all.py — independent re-derivation of every DERIVED ledger row.

Written from scratch on 10 Aug 2026. Deliberately does NOT import or reuse
build_electrode_matrix.py / fit_threshold.py / ttx_floor.py. If this script
agrees with them, the numbers are reproduced by two independent
implementations. If it disagrees, one of them is wrong and we find out now.

Rows tested:
  A1  recording duration (proxy: max spike time; descriptor states 600 s)
  A3  Channel = <well>_<electrode>, 8x8 grid, 64/well
  B2  nae reproduced by spike count >= 100
  B3  nae NOT reproduced by spike count >= 101  (the off-by-one)
  B5  nae ratio at 5/min vs 10/min
  C1  human electrodes producing >= 1 spike at DIV 66
  C2  rat electrodes producing >= 1 spike at DIV 35
  C6  TTX noise ceiling, recomputed from the raw TTX spike file
  C7  contamination of published nae against that ceiling
"""

import re
import sys
from pathlib import Path

import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parent.parent
OUT = []


def say(s=""):
    print(s)
    OUT.append(str(s))


def load_spikes(path):
    df = pd.read_csv(path)
    df.columns = [c.strip() for c in df.columns]
    df["Channel"] = df["Channel"].astype(str).str.strip()
    return df


def spike_counts(path):
    """electrode -> spike count, for every electrode appearing in the file."""
    df = load_spikes(path)
    return df["Channel"].value_counts(), df["Time"].max(), len(df)


def div_of(path):
    m = re.search(r"DIV(\d+)_spikes\.csv$", path.name)
    return int(m.group(1)) if m else None


def load_noisy(path):
    """DIV -> set of noisy channel names. Wide file, one column per DIV."""
    df = pd.read_csv(path, dtype=str)
    out = {}
    for col in df.columns:
        div = int(str(col).strip().replace("DIV", ""))
        vals = {str(v).strip() for v in df[col].dropna() if str(v).strip()}
        out[div] = vals
    return out


def load_nae(path):
    """published nae -> dict[(well, div)] = value"""
    df = pd.read_csv(path)
    df.columns = [c.strip().strip('"') for c in df.columns]
    out = {}
    for _, row in df.iterrows():
        well = str(row["well"]).strip().strip('"')
        for col in df.columns:
            if col.startswith("divDIV"):
                div = int(col.replace("divDIV", ""))
                val = row[col]
                if pd.isna(val):
                    continue
                try:
                    out[(well, div)] = int(float(val))
                except (TypeError, ValueError):
                    continue
    return out


def plate_report(label, spikes_dir, nae_path, pattern, noisy_path):
    say("=" * 72)
    say(f"PLATE {label}")
    say("=" * 72)

    files = sorted(spikes_dir.glob(pattern), key=lambda p: div_of(p))
    counts_by_div = {}
    durations = {}
    for f in files:
        vc, tmax, ntot = spike_counts(f)
        d = div_of(f)
        counts_by_div[d] = vc
        durations[d] = (tmax, ntot)

    # ---- A1 : duration proxy -------------------------------------------
    tmaxes = [durations[d][0] for d in sorted(durations)]
    say("")
    say("A1  max spike time across recordings: "
        f"min={min(tmaxes):.4f}s  max={max(tmaxes):.4f}s  n={len(tmaxes)}")
    say("    descriptor states 10 min recordings -> 600 s. Max spike time is a")
    say("    LOWER bound only; it is consistent with 600 s, it does not prove it.")

    # ---- A3 : channel format -------------------------------------------
    all_ch = set()
    for vc in counts_by_div.values():
        all_ch.update(vc.index)
    wells = sorted({c.split("_")[0] for c in all_ch})
    elecs = sorted({c.split("_")[1] for c in all_ch})
    bad = [c for c in all_ch if not re.fullmatch(r"[A-H]\d+_[1-8][1-8]", c)]
    say("")
    say(f"A3  wells={len(wells)} {wells}")
    say(f"    distinct electrode IDs={len(elecs)}  range {min(elecs)}-{max(elecs)}")
    say(f"    channels violating <well>_[1-8][1-8]: {len(bad)}  {bad[:5]}")
    say(f"    total distinct channels = {len(all_ch)}")

    # ---- A6 : is the noisy list per-recording or carried forward? --------
    noisy = load_noisy(noisy_path)
    sets = [frozenset(v) for v in noisy.values()]
    say("")
    say(f"A6  noisy-electrode list: {len(noisy)} DIV columns, "
        f"{len(set(sets))} distinct sets, union={len(set().union(*sets))} electrodes")
    if len(set(sets)) == 1:
        say("    IDENTICAL across every DIV -> carried forward, NOT recomputed "
            "per recording.")
    else:
        say("    varies by DIV -> at least partly per-recording.")
        for d in sorted(noisy):
            say(f"      DIV {d:>3}: {sorted(noisy[d])}")

    # ---- B2 / B3 : threshold reproduction -------------------------------
    published = load_nae(nae_path)
    results = {}
    for excl in (False, True):
        say("")
        say(f"B2/B3  noisy electrodes excluded = {excl}")
        for k in (100, 101, 99):
            hits = tot = 0
            diffs = []
            for (well, div), pub in published.items():
                if div not in counts_by_div:
                    continue
                vc = counts_by_div[div]
                drop = noisy.get(div, set()) if excl else set()
                n = sum(1 for ch, c in vc.items()
                        if ch.split("_")[0] == well and c >= k
                        and ch not in drop)
                tot += 1
                if n == pub:
                    hits += 1
                else:
                    diffs.append((well, div, pub, n))
            results[(excl, k)] = (hits, tot, diffs)
            say(f"       criterion >= {k:>3} spikes : {hits}/{tot} reproduced exactly")
        d100 = results[(excl, 100)][2]
        if d100:
            say(f"       >=100 mismatches (well,div,published,mine): {d100[:8]}")

    # ---- B5 : threshold sensitivity -------------------------------------
    # meaRtools' shipped `parameters` data object -- the one the vignette loads
    # -- documents the default as `elec_min_rate : num 0.0167`. That is R's
    # str() display at three significant figures, not necessarily the stored
    # value: str(1/60) prints `0.0167` as well. See notes/criterion-ambiguity.md.
    #
    # The package removes an electrode when `meanfiringrate < elec_min_rate`
    # (R/spikes.R), so ACTIVE is >=, not >. And `meanfiringrate <- nspikes /
    # (end - beg)`, so the divisor is the measured span, not a nominal 600 s --
    # which is M2, confirmed from the package source rather than inferred.
    #
    #   active  <=>  nspikes >= elec_min_rate * span,  span 599.689-599.997 s
    #     reading 0.0167  ->  threshold 10.0148-10.0199  ->  count >= 11
    #     reading (1/60)  ->  threshold  9.9948- 9.9999  ->  count >= 10
    #
    # >= 11 is used here because 0.0167 is what the documentation shows. The
    # choice is reported, not hidden: scripts/verify_criterion_boundary.py
    # confirms the B5 range and endpoints are IDENTICAL under both readings
    # (381-384, 384 -> 382). Only H3's 1/min r moves, +0.289 vs +0.126.
    #
    # (The earlier comment here read "rate > 0.0167 means count > 10.02, i.e.
    # count >= 11". Right answer, wrong reason: it read the filter as strict
    # and used a nominal 600 s. Corrected 25 Aug 2026.)
    #
    # Kapucu 2022 criterion = 10 spikes/min, implemented as count >= 100
    say("")
    say("B5  active-electrode count under three published criteria")
    say("    meaRtools default 1/min (>=11; >=10 under the (1/60) reading -- see")
    say("      notes/criterion_boundary.txt) | Axion-era 5/min (>=50) | Kapucu 10/min (>=100)")
    say("      DIV    n@1/min   n@5/min  n@10/min   1/min:10/min")
    for d in sorted(counts_by_div):
        vc = counts_by_div[d]
        n1 = int((vc >= 11).sum())
        n5 = int((vc >= 50).sum())
        n10 = int((vc >= 100).sum())
        ratio = (n1 / n10) if n10 else float("inf")
        say(f"     {d:>4}   {n1:>8}  {n5:>8}  {n10:>8}   {ratio:>10.2f}x")

    # ---- C1 / C2 : electrodes producing >=1 spike -----------------------
    say("")
    last = max(counts_by_div)
    vc_last = counts_by_div[last]
    say(f"C1/C2  DIV {last}: electrodes with >=1 detected spike = {len(vc_last)}")
    say(f"       expected total electrodes = {len(wells)} wells x 64 = {len(wells)*64}")

    return counts_by_div, published, wells, noisy


def reproduced_at(counts_by_div, published, noisy, k):
    """Well-timepoint cells whose published nae is reproduced at >= k spikes,
    with that day's flagged electrodes excluded. Same rule as B2/B3 above;
    factored out so the three-plate H1 total is regenerated, not assembled."""
    hits = 0
    for (well, div), pub in published.items():
        if div not in counts_by_div:
            continue
        vc = counts_by_div[div]
        drop = noisy.get(div, set())
        n = sum(1 for ch, c in vc.items()
                if ch.split("_")[0] == well and c >= k and ch not in drop)
        if n == pub:
            hits += 1
    return hits


def cells(published):
    return len(published)


def ttx_ceiling():
    say("")
    say("=" * 72)
    say("C6  TTX NOISE CEILING — recomputed from raw spike times")
    say("=" * 72)
    base = ROOT / "data/hPSC_MEA3_Pharmacology/hPSC_MEA3TTX_DIV29"
    spikes = base / "hPSC_120618_MEA3TTX_DIV29_spikes.csv"
    explog = base / "hPSC_120618_MEA3TTX_DIV29_expLog.csv"

    df = load_spikes(spikes)
    log = pd.read_csv(explog)
    log.columns = [c.strip() for c in log.columns]
    log["Well"] = log["Well"].astype(str).str.strip()
    log["Treatment"] = log["Treatment"].astype(str).str.strip()

    groups = log.groupby("Treatment")["Well"].apply(list).to_dict()
    say("")
    say("expLog treatment groups: "
        + ", ".join(f"{k}={len(v)}" for k, v in sorted(groups.items())))

    tmax = df["Time"].max()
    say(f"max spike time in TTX file = {tmax:.4f} s "
        f"(descriptor: TTX response recorded for 10 minutes = 600 s)")
    DUR_MIN = 10.0

    df["well"] = df["Channel"].str.split("_").str[0]
    counts = df["Channel"].value_counts()

    # electrode census must include zero-spike electrodes
    ELEC_PER_WELL = 16  # 48-well CytoView -> 16 electrodes/well
    rows = []
    for treat, wells in groups.items():
        if treat in ("ExcludedWell", "nan"):
            continue
        for w in wells:
            wc = counts[counts.index.str.startswith(w + "_")]
            rates = list(wc.values / DUR_MIN)
            rates += [0.0] * (ELEC_PER_WELL - len(rates))
            for r in rates:
                rows.append((treat, w, r))
    rr = pd.DataFrame(rows, columns=["treatment", "well", "rate"])

    say("")
    say("  group          n_elec   median      p95      p99      max")
    ceiling = None
    for treat, g in rr.groupby("treatment"):
        v = g["rate"].values
        say(f"  {treat:<13} {len(v):>6}  {np.median(v):>7.2f} "
            f"{np.percentile(v,95):>8.2f} {np.percentile(v,99):>8.2f} "
            f"{v.max():>8.2f}")
        if treat == "TTX":
            ceiling = v.max()
    say("")
    say(f"  -> noise ceiling (max rate on a silenced electrode) = {ceiling:.2f} spikes/min")
    say(f"  -> active criterion is 10 spikes/min; ceiling/criterion = {ceiling/10:.2f}x")
    n_ttx_active = int((rr[rr.treatment == "TTX"]["rate"] >= 10).sum())
    n_ttx = int((rr.treatment == "TTX").sum())
    say(f"  -> silenced electrodes scored ACTIVE by the criterion: {n_ttx_active}/{n_ttx}")
    return ceiling


def contamination(counts_by_div, ceiling, label):
    say("")
    say("=" * 72)
    say(f"C7  CONTAMINATION of published nae — {label}")
    say("=" * 72)
    say(f"  ceiling transferred from MEA3 = {ceiling:.2f} spikes/min "
        f"= {ceiling*10:.1f} spikes / 600 s")
    thr = ceiling * 10.0
    say("")
    say("   DIV   scored_active   above_ceiling   within_noise   %within")
    for d in sorted(counts_by_div):
        vc = counts_by_div[d]
        act = vc[vc >= 100]
        above = int((act > thr).sum())
        within = len(act) - above
        pct = 100.0 * within / len(act) if len(act) else float("nan")
        say(f"  {d:>4}   {len(act):>13}   {above:>13}   {within:>12}   {pct:>6.1f}%")


def main():
    hp_counts, hp_pub, hp_wells, hp_noisy = plate_report(
        "hPSC_MEA1 (human, 12-well, 64 elec/well)",
        ROOT / "data/hPSC_MEA1/spikes",
        ROOT / "data/hPSC_MEA1/summary/hPSC_20517_MEA1_nae.csv",
        "hPSC_*_MEA1_DIV*_spikes.csv",
        ROOT / "data/hPSC_MEA1/spikes/noisy_electrodes_hPSC_MEA1.csv",
    )
    # hPSC_MEA2 added 16 Aug 2026, session 2. Until then no script in this
    # repository reproduced this plate's published nae table, so 114 of H1's
    # 336 values -- 34% of the paper's first claim -- had nothing behind them.
    hp2_counts, hp2_pub, hp2_wells, hp2_noisy = plate_report(
        "hPSC_MEA2 (human, 12-well, 64 elec/well, parallel replicate)",
        ROOT / "data/hPSC_MEA2/spikes",
        ROOT / "data/hPSC_MEA2/summary/hPSC_20517_MEA2_nae.csv",
        "hPSC_*_MEA2_DIV*_spikes.csv",
        ROOT / "data/hPSC_MEA2/spikes/noisy_electrodes_hPSC_MEA2.csv",
    )
    rat_counts, rat_pub, rat_wells, rat_noisy = plate_report(
        "Rat_MEA1 (rat, 12-well, 64 elec/well)",
        ROOT / "data/Rat_MEA1/spikes",
        ROOT / "data/Rat_MEA1/summary/Rat_190617_MEA1_nae.csv",
        "Rat_*_MEA1_DIV*_spikes.csv",
        ROOT / "data/Rat_MEA1/spikes/noisy_electrodes_Rat_MEA1.csv",
    )
    ceiling = ttx_ceiling()
    contamination(hp_counts, ceiling, "hPSC_MEA1")
    contamination(rat_counts, ceiling, "Rat_MEA1")

    say("")
    say("=" * 72)
    say("H1 TOTAL across all three plates")
    say("=" * 72)
    say("")
    say("  Reproduction of the published nae tables is claimed at 336/336.")
    say("  Per-plate totals at each candidate criterion, summed here so the")
    say("  headline number is regenerated rather than assembled by hand:")
    say("")
    plates = ((hp_counts, hp_pub, hp_noisy),
              (hp2_counts, hp2_pub, hp2_noisy),
              (rat_counts, rat_pub, rat_noisy))
    for k in (99, 100, 101):
        tot = sum(reproduced_at(c, p, nz, k) for c, p, nz in plates)
        n = sum(cells(p) for p in (hp_pub, hp2_pub, rat_pub))
        mark = "   <-- H1" if k == 100 else ""
        say(f"    >= {k:3d} spikes : {tot}/{n} reproduced exactly{mark}")

    (ROOT / "notes" / "verify_all_results.txt").write_text(
        "\n".join(OUT), encoding="utf-8")
    say("")
    say("written: notes/verify_all_results.txt")


if __name__ == "__main__":
    main()
