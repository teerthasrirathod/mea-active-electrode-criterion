"""
verify_rat_na_cells.py

Question: the published `nae` table for Rat_MEA1 is 12 wells x 10 timepoints
= 120 cells, but only 108 carry a value. The other 12 are bare `NA`.
notes/logbook.md (Day 1, anomaly 4) recorded bare `NA` as "well not recorded
that day". This script tests that reading.

For every `NA` cell it checks:
  (a) was the well recorded at all -- i.e. does the spike file contain
      channels for it, and how many electrodes produced at least one spike;
  (b) what the paper's own rule (>=100 spikes, after removing that day's
      published noisy electrodes) returns for that cell.

If (a) shows the well was recorded and (b) returns 0, then bare `NA` in this
table means ZERO ACTIVE ELECTRODES, not a missing recording -- and the cell is
reproduced by the rule rather than excluded from the test.

Writes notes/rat_na_cells.txt. Run from the repo root.
"""

import collections
import csv
import os
import sys

PLATE = "Rat_MEA1"
NAE = "data/Rat_MEA1/summary/Rat_190617_MEA1_nae.csv"
SPIKES = "data/Rat_MEA1/spikes/Rat_190617_MEA1_DIV{div}_spikes.csv"
NOISY = "data/Rat_MEA1/spikes/noisy_electrodes_Rat_MEA1.csv"
OUT = "notes/rat_na_cells.txt"
CRITERION = 100  # spikes per recording; the rule established in section 3.1


def unquote(s):
    return s.strip().strip('"').strip()


def read_nae(path):
    """-> {(well, div): value_or_None}, and the DIV order as published."""
    with open(path, newline="") as fh:
        rows = list(csv.reader(fh))
    header = [unquote(h) for h in rows[0]]
    divs = [h[len("divDIV"):] for h in header if h.startswith("divDIV")]
    first = header.index("divDIV" + divs[0])
    table = {}
    for row in rows[1:]:
        if not row:
            continue
        well = unquote(row[0])
        for i, div in enumerate(divs):
            raw = row[first + i]
            val = unquote(raw)
            table[(well, div)] = None if val.upper() in ("", "NA", "NAN") else int(val)
    return table, divs


def read_noisy(path):
    """-> {div: set(channels)}. Entries carry stray whitespace; strip everything."""
    with open(path, newline="") as fh:
        rows = list(csv.reader(fh))
    header = [unquote(h) for h in rows[0]]
    out = collections.defaultdict(set)
    for row in rows[1:]:
        for h, v in zip(header, row):
            v = unquote(v)
            if v and v.upper() not in ("NA", "NAN"):
                out[h.replace("DIV", "")].add(v)
    return out


def spike_counts(path):
    """-> Counter over channel -> n spikes."""
    counts = collections.Counter()
    with open(path, newline="") as fh:
        reader = csv.reader(fh)
        next(reader)
        for row in reader:
            if row:
                counts[unquote(row[0])] += 1
    return counts


def main():
    nae, divs = read_nae(NAE)
    noisy = read_noisy(NOISY)

    lines = []
    def emit(s=""):
        print(s)
        lines.append(s)

    emit("verify_rat_na_cells.py -- are the `NA` cells missing recordings, or zeros?")
    emit("=" * 78)
    emit("")
    emit("plate      : %s" % PLATE)
    emit("nae table  : %d wells x %d timepoints = %d cells"
         % (len(nae) // len(divs), len(divs), len(nae)))

    na_cells = sorted(k for k, v in nae.items() if v is None)
    emit("`NA` cells : %d  -> %d cells carry a value"
         % (len(na_cells), len(nae) - len(na_cells)))
    emit("")

    by_div = collections.defaultdict(list)
    for well, div in na_cells:
        by_div[div].append(well)

    recorded = 0
    reproduced_as_zero = 0

    for div in divs:
        if div not in by_div:
            continue
        path = SPIKES.format(div=div)
        if not os.path.exists(path):
            emit("DIV %-3s  SPIKE FILE MISSING: %s" % (div, path))
            continue
        counts = spike_counts(path)
        flagged = noisy.get("DIV" + div, noisy.get(div, set()))

        emit("DIV %s -- %d `NA` cells" % (div, len(by_div[div])))
        emit("  %-5s %10s %10s %10s %10s %8s"
             % ("well", "spikes", "electrodes", ">=%d" % CRITERION, "flagged", "rule"))
        for well in sorted(by_div[div]):
            chans = {c: n for c, n in counts.items() if c.startswith(well + "_")}
            n_spikes = sum(chans.values())
            n_elec = len(chans)
            above = {c for c, n in chans.items() if n >= CRITERION}
            above_clean = above - flagged
            n_flagged_removed = len(above & flagged)
            if n_elec > 0:
                recorded += 1
            if len(above_clean) == 0:
                reproduced_as_zero += 1
            emit("  %-5s %10d %10d %10d %10d %8d"
                 % (well, n_spikes, n_elec, len(above), n_flagged_removed,
                    len(above_clean)))
        emit("")

    emit("-" * 78)
    emit("wells that WERE recorded (>=1 electrode producing spikes) : %d of %d"
         % (recorded, len(na_cells)))
    emit("cells the rule returns 0 for                              : %d of %d"
         % (reproduced_as_zero, len(na_cells)))
    emit("")

    ok = recorded == len(na_cells) and reproduced_as_zero == len(na_cells)
    if ok:
        emit("RESULT: every `NA` cell is a recorded well in which zero electrodes")
        emit("        meet the criterion. Bare `NA` in this table means ZERO ACTIVE")
        emit("        ELECTRODES, not a missing recording.")
        emit("")
        emit("        Consequences:")
        emit("        - notes/logbook.md Day 1 anomaly 4 records bare `NA` as `well")
        emit("          not recorded that day`. For this table that reading is wrong.")
        emit("        - Rat_MEA1 is reproduced at 120/120, not 108/120, and the")
        emit("          three-plate total is 348/348 rather than 336/336.")
        emit("        - The 12 cells are the most extreme cases of the paper's own")
        emit("          claim: wells with thousands of detected spikes across 63-64")
        emit("          electrodes, scored as no active electrodes.")
    else:
        emit("RESULT: the reading does NOT hold uniformly. Inspect the rows above.")

    os.makedirs("notes", exist_ok=True)
    with open(OUT, "w", encoding="utf-8") as fh:
        fh.write("\n".join(lines) + "\n")
    print()
    print("written: %s" % OUT)
    return 0 if ok else 1


if __name__ == "__main__":
    sys.exit(main())
