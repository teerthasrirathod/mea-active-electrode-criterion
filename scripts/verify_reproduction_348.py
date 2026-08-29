"""
verify_reproduction_348.py — H1, recomputed over every published cell.

WHAT CHANGED AND WHY
--------------------
H1 was frozen as "336/336 published values reproduced exactly" across
hPSC_MEA1 (114), hPSC_MEA2 (114) and Rat_MEA1 (108). The rat plate is
12 wells x 10 timepoints = 120 cells; 12 carry bare `NA` and were dropped from
the test as unrecorded.

`scripts/verify_rat_na_cells.py` established that those 12 are not missing
recordings. Every one of the 12 wells was recorded -- 63-64 electrodes
producing spikes, 2,254-2,929 detected spikes -- and the rule returns exactly
zero for each. **Bare `NA` in this table means zero active electrodes.**

So the 12 are reproducible, and excluding them understated the result. This
recomputes H1 over all 348 published cells with `NA` read as 0, and recomputes
the adjacent-threshold figures (frozen as 307 and 303 of 336) on the same basis,
because those are denominated in 336 too.

INDEPENDENCE
------------
Written from the published method description without reference to
`verify_all.py`, so the two implementations stay independent -- the standard
§2.4 states and that H1 must meet.

SEARCH SPACE
------------
Printed with the result. §2.4 said only "candidate values of k were scanned"
while §3.1 claimed the rule is unique; a uniqueness claim needs its space
stated.

INPUTS
------
Per-electrode counts come from `data/derived/<plate>_electrode_counts.csv`
where the repo already has them, and are built from the published spike files
where it does not. Building writes the same CSV shape, so the next run is fast
and the intermediate is inspectable rather than hidden in memory.

USAGE
-----
    python scripts/verify_reproduction_348.py
Writes notes/reproduction_348.txt. Run from the repo root.
"""

import collections
import csv
import glob
import os
import sys

K_MIN, K_MAX = 1, 400
OUT = "notes/reproduction_348.txt"
DERIVED = "data/derived"

PLATES = [
    ("hPSC_MEA1", "data/hPSC_MEA1", "hPSC_20517_MEA1"),
    ("hPSC_MEA2", "data/hPSC_MEA2", "hPSC_20517_MEA2"),
    ("Rat_MEA1", "data/Rat_MEA1", "Rat_190617_MEA1"),
]


def clean(s):
    return s.strip().strip('"').strip()


def read_nae(path):
    """-> ({(well, div): int|None}, [div]). None means published as NA."""
    rows = list(csv.reader(open(path, newline="")))
    hdr = [clean(h) for h in rows[0]]
    divs = [h[len("divDIV"):] for h in hdr if h.startswith("divDIV")]
    first = hdr.index("divDIV" + divs[0])
    out = {}
    for r in rows[1:]:
        if not r:
            continue
        well = clean(r[0])
        for i, d in enumerate(divs):
            v = clean(r[first + i])
            out[(well, d)] = None if v.upper() in ("", "NA", "NAN") else int(v)
    return out, divs


def read_noisy(path):
    """-> {div: {channel}}. Entries carry stray whitespace; strip all."""
    if not os.path.exists(path):
        return {}
    rows = list(csv.reader(open(path, newline="")))
    hdr = [clean(h) for h in rows[0]]
    out = collections.defaultdict(set)
    for r in rows[1:]:
        for h, v in zip(hdr, r):
            v = clean(v)
            if v and v.upper() not in ("NA", "NAN"):
                out[h.replace("DIV", "")].add(v)
    return out


def counts_from_derived(path):
    """-> {(div, well): {electrode: n_spikes}} from the repo's derived CSV."""
    per = collections.defaultdict(dict)
    with open(path, newline="") as fh:
        for row in csv.DictReader(fh):
            per[(clean(row["div"]), clean(row["well"]))][clean(row["electrode"])] = \
                int(row["n_spikes"])
    return per


def counts_from_spikes(root, stem, divs, plate):
    """Parse the published spike files; also write the derived CSV."""
    per = collections.defaultdict(dict)
    rows = []
    for d in divs:
        p = f"{root}/spikes/{stem}_DIV{d}_spikes.csv"
        if not os.path.exists(p):
            continue
        c = collections.Counter()
        with open(p, newline="") as fh:
            rd = csv.reader(fh)
            next(rd)
            for row in rd:
                if row:
                    c[clean(row[0])] += 1
        for ch, n in c.items():
            w, _, e = ch.partition("_")
            per[(d, w)][e] = n
            rows.append((d, w, e, n))
    os.makedirs(DERIVED, exist_ok=True)
    out = f"{DERIVED}/{plate}_electrode_counts.csv"
    with open(out, "w", newline="", encoding="utf-8") as fh:
        wr = csv.writer(fh)
        wr.writerow(["div", "well", "electrode", "n_spikes"])
        wr.writerows(rows)
    return per, out


def n_at(desc, k):
    """How many electrodes reached k spikes. `desc` is sorted descending, so
    this is a binary search for the first entry below k."""
    lo, hi = 0, len(desc)
    while lo < hi:
        mid = (lo + hi) // 2
        if desc[mid] >= k:
            lo = mid + 1
        else:
            hi = mid
    return lo


def build_cells(emit):
    cells = []
    for plate, root, stem in PLATES:
        nae, divs = read_nae(glob.glob(f"{root}/summary/*_nae.csv")[0])
        noisy = read_noisy(f"{root}/spikes/noisy_electrodes_{plate}.csv")
        d_csv = f"{DERIVED}/{plate}_electrode_counts.csv"
        if os.path.exists(d_csv):
            per = counts_from_derived(d_csv)
            emit(f"  {plate:<11} counts from {d_csv}")
        else:
            per, made = counts_from_spikes(root, stem, divs, plate)
            emit(f"  {plate:<11} counts built from spike files -> {made}")
        for (well, div), pub in nae.items():
            elec = per.get((div, well), {})
            if not elec:
                continue
            flagged = noisy.get("DIV" + div, noisy.get(div, set()))
            desc = sorted((n for e, n in elec.items()
                           if f"{well}_{e}" not in flagged), reverse=True)
            cells.append({"plate": plate, "well": well, "div": div,
                          "pub": pub, "desc": desc})
    return cells


def main():
    lines = []

    def emit(s=""):
        print(s, flush=True)
        lines.append(s)

    emit("verify_reproduction_348.py -- H1 over every published cell")
    emit("=" * 74)
    emit(f"search space   k = {K_MIN}..{K_MAX} spikes per recording, step 1")
    emit("NA convention  bare `NA` in the published nae table is read as 0")
    emit("               (established by scripts/verify_rat_na_cells.py)")
    emit("")
    emit("INPUTS")
    cells = build_cells(emit)
    emit("")

    scores_all, scores_nn = {}, {}
    for k in range(K_MIN, K_MAX + 1):
        ha = ta = hn = tn = 0
        for c in cells:
            got = n_at(c["desc"], k)
            pub = c["pub"]
            ta += 1
            if got == (0 if pub is None else pub):
                ha += 1
            if pub is not None:
                tn += 1
                if got == pub:
                    hn += 1
        scores_all[k] = (ha, ta)
        scores_nn[k] = (hn, tn)

    best = max(scores_all, key=lambda k: scores_all[k][0])
    hit, tot = scores_all[best]
    perfect = [k for k in scores_all if scores_all[k][0] == tot]

    emit("PER PLATE, at the best threshold")
    emit(f"  {'plate':<12}{'cells':>7}{'NA':>5}{'reproduced':>14}")
    gh = gt = gna = 0
    for plate, _, _ in PLATES:
        sub = [c for c in cells if c["plate"] == plate]
        h = sum(1 for c in sub
                if n_at(c["desc"], best) == (0 if c["pub"] is None else c["pub"]))
        na = sum(1 for c in sub if c["pub"] is None)
        gh += h
        gt += len(sub)
        gna += na
        emit(f"  {plate:<12}{len(sub):>7}{na:>5}{f'{h}/{len(sub)}':>14}")
    emit(f"  {'TOTAL':<12}{gt:>7}{gna:>5}{f'{gh}/{gt}':>14}")
    emit("")

    emit(f"BEST THRESHOLD  >= {best} spikes per recording")
    emit(f"  reproduced    {hit}/{tot}  ({100.0 * hit / tot:.2f}%)")
    emit(f"  unique        {'YES' if len(perfect) == 1 else 'NO ' + str(perfect)}"
         f"  -- only k reaching {tot}/{tot} in {K_MIN}..{K_MAX}")
    emit("")

    emit("ADJACENT THRESHOLDS")
    emit(f"  {'k':>5}{'over 348':>12}{'over 336 (frozen basis)':>27}")
    for k in range(best - 2, best + 3):
        if k < K_MIN:
            continue
        a, _ = scores_all[k]
        b, _ = scores_nn[k]
        mark = "   <-- the rule" if k == best else ""
        emit(f"  {k:>5}{a:>12}{b:>27}{mark}")
    emit("")

    emit("WHAT REPLACES WHAT, if H1 is amended")
    emit(f"  frozen   336/336 exact; >={best + 1} reproduces "
         f"{scores_nn[best + 1][0]} of 336; >={best - 1} reproduces "
         f"{scores_nn[best - 1][0]}")
    emit(f"  amended  {hit}/{tot} exact; >={best + 1} reproduces "
         f"{scores_all[best + 1][0]} of {tot}; >={best - 1} reproduces "
         f"{scores_all[best - 1][0]}")
    emit("")
    emit("  Every sentence in draft/ carrying 336, 307 or 303 is on the sweep,")
    emit("  as is the all-336 regex in scripts/verify_draft_claims.py [5b].")

    os.makedirs("notes", exist_ok=True)
    open(OUT, "w", encoding="utf-8").write("\n".join(lines) + "\n")
    print(f"\nwritten: {OUT}")
    return 0 if (hit == tot and len(perfect) == 1) else 1


if __name__ == "__main__":
    sys.exit(main())
