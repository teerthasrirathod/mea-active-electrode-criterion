# The claim set and the audit trail

Two working files, deposited with the paper rather than rewritten for it. They
are the record of what the paper was allowed to say and of what happened when
each line of it was read back.

| file | what it is |
|---|---|
| `CLAIM-SET-FROZEN.md` | Every claim the paper was permitted to make, frozen on 10 August 2026 before the writing began, each with the ledger row and the script behind it. Section 4 lists the claims **withdrawn** under it, with the reason each died and the date. |
| `audit-decisions.md` | One row per review comment from the line-by-line pass: the span, the defect named, what changed, what was swept, and which of three categories it fell into. |

**The rule the claim set carries is that nothing entered the paper that was not
already on that page.** A sentence produced during drafting was either wrong or
required the set to be amended, with evidence, a ledger row and a dated note.
Five claims were withdrawn under that rule. They are listed rather than deleted,
because a set of surviving claims says little on its own about how hard the
survivors were tested.

`scripts/claim_map.py` maps each row of the claim set to the script and the
artefact that produce its number, and fails if a claim is asserted with nothing
behind it or if a row is added without being mapped. Its recorded output is
`artefacts/claim_map_output.txt`.

## Reading them

Both files were written for the working repository and cite files that are not
deposited here: the manuscript source under `draft/`, the assumption ledger, the
open-ends register, the day-by-day logbook. Those references are left as they
were written. Editing them to suit a public reader would make the record a
document about the record.

Dates are the dates the decisions were taken, not the deposit date. Struck-through
text marks a position that was superseded, and it is kept struck rather than
removed for the same reason the withdrawn claims are kept.
