# Audit decisions log

**Opened 12 August 2026**, at the start of the line-by-line pass described in
`START-HERE.md` §6. One row per review comment. The pass does not live only in
a chat.

**Every line in the manuscript resolves to one of three categories.** The
category determines what happens next, so it is recorded explicitly rather than
inferred:

| category | meaning | what follows |
|---|---|---|
| **Traced** | comes from a named claim row and a script | check against the row; a mismatch is a bug, not a style question |
| **Choice** | a structural or rhetorical decision | defensible, not derived, **TSRB's to overrule** |
| **Cut** | cannot be defended | remove, then check nothing downstream depended on it |

**A section that produces no Cut has not been audited, it has been admired.**

**Standing procedure for each comment**, so it can be relied on without asking:

1. Check whether the same statement appears elsewhere in `draft/`. A comment on
   one span is usually a comment on two.
2. Check whether `CLAIM-SET-FROZEN.md` governs the span. If it does, the claim
   set is amended in the same pass, not later.
3. Run `scripts/verify_draft_claims.py`.
4. State which parts of the change are Traced and which are Choice, so it is
   clear what is TSRB's to overrule.

**Default on a comment: act, then explain.** Exceptions, per agreement of
12 Aug: a comment that says "think", "comment", "thoughts", or asks a question
gets reasoning and proposed text *first*, and no edit until agreed.

---

## 2026-08-29 — the front door

**One file, and it is the keystone the apparatus was missing.** `scripts/check.py`
runs the staleness test and all four checkers and returns a single verdict.

**The rule it enforces: a partial run is never green.** A checker that times out,
crashes, is missing or is skipped makes the verdict INCOMPLETE, not PASS. Exit 0
only when every one ran to completion and reported nothing; 1 on failure; 2 on
incomplete. There is no wording in the file that lets an unrun check read as a
passing one.

It exists because of what happened the night before: one checker was run for six
hours and the other three were not, and the moment they were run they found two
more defects. Nothing was wrong with the checkers. There was no single place to
invoke them, so **"0 failures" meant "0 failures in the one I happened to run"
and read exactly like "0 failures in the paper"** — this manuscript's own subject,
committed against the manuscript.

### Both failure paths were watched before the file was trusted

An injected `§9.9` in §5 produced **three simultaneous failures** — the
cross-reference check, the partition checker's dangling-reference test, and
staleness — and exit 1. `--quick` produces INCOMPLETE and exit 2. Only then was
the green path believed.

### It found a real defect on its first honest run

`[0b]` never existed. `START-HERE.md` and `build_manuscript_pdf.py` had both been
claiming for weeks that *"verify_draft_claims.py [0b] checks it"* about whether
the PDF is current. Nothing was checking it, and `MANUSCRIPT.pdf` went stale four
times on 28 August alone. The false claim has been corrected where it was made.

The first version tested staleness by mtime and raised a **false alarm** after a
no-op recompile. Rewritten to compare content: `build_manuscript_pdf.py` already
records `sha256[:16]` of the markdown it consumed in `notes/pdf-toolchain.txt`,
so the exact question — was this PDF built from this text — is answerable, and
the proxy was replaced with the answer. The inputs with no recorded hash (header,
figures, the build script) stay on mtime and are **reported separately as the
weaker test**, rather than being silently mixed in with the strong one.

That rewrite immediately surfaced a provenance gap: every recent PDF was built in
the cloud container and only the PDF was committed back, never
`notes/pdf-toolchain.txt`. **The record on the device did not describe the PDF
beside it.** Both are now committed together.

### Where the apparatus stands

42 scripts, 10 of them verifiers, 2,907 lines of verifier code against 10,173
shipped words. 20 claim rows, 7 withdrawn. 94 cross-references, all resolving.
139 papers in the corpus the style decisions are measured against.

**The one thing still true of it: `verify_all.py` does not finish inside a
45-second shell.** `check.py` gives it 1,800 seconds and reports honestly when it
is skipped. It is not skipped by default.

**Cut count: 0.** The §1/§4 duplication remains the standing proposed cut.

---

## 2026-08-29, small hours — the loop audit, and the format

### The loop audit, four passes

TSRB's instruction: a paper questions and answers itself, and a loop opened in
one section closes in another. Eleven loops closed. Ledger:
`notes/LOOPS-M2R-28AUG.md`.

**The mechanical scan was tried and abandoned.** 45 obligation markers; three of
the eighteen "forward promises" were real, the rest being *below* used as a
comparison operator. In a paper about thresholds the discourse vocabulary and
the arithmetic vocabulary are the same words. **Loops are not findable by
pattern.**

**Two findings stand out.** §4.1 wrote that the malfunction records "document
essentially none", where §3.7 reports an upper bound and says in terms that it
is "a bound and not a reading". §1 states it correctly. **A paper about a metric
that silently converts one kind of quantity into another had done exactly that
to its own evidence, two sections apart.** And §0 and §1 both assert that one
pipeline states two values in a single paper, a string that appeared nowhere
else in the body: a claim in the abstract whose only support was an entry in the
reference list.

**One finding was withdrawn and one was mine.** L-7 claimed the distribution met
the pre-registered transfer tier; the pre-registration is fixed on 17.70, the
ceiling, and applying its band to medians is the post-hoc move this paper
criticises. And at ~01:00, closing L-8, I wrote into §5 that three analyses were
never implemented twice; `second_implementation.txt` shows all six were. **A
negative asserted about the project's own work without opening the artefact that
records it.** Both corrected, both recorded rather than quietly fixed.

### Running one checker is not running the checkers

`verify_draft_claims.py` had been run all night and the other three had not.
Running them surfaced two more defects, both the same class as `[6]`: substring
tests defeated by formatting rather than by content. `claim_map` failed on
`381–384` because the register pass replaced the en dash with the word "to";
`check_paper_partition` called §2.1 hollow for a phrase that was in §2.1, wrapped
across two lines, because it normalises whitespace on the citing side and not on
the target. **Three formatting-defeats-substring bugs in one night.** Both fixed
at the mechanism: alternatives are declared explicitly in `claim_map`, and both
sides are normalised in the partition check.

`verify_all.py` does not complete inside the device shell's 45-second limit. Its
last full run is the 16 August artefact that `claim_map` traces against. Not a
failure; not a fresh run either.

### The format

**The paper and its status are now two files.** The Snapshot block and the
open-items list moved to `notes/STATUS.md`. They had gone stale inside the
document three times in one day, which is what a status block inside the
artefact it describes will always do. `MANUSCRIPT.md` is now the paper.

**Presentation moved into the build script.** `compile_manuscript.py` emits
plain markdown so the file stays readable and `number_reading.py` keeps working;
`build_manuscript_pdf.py` replaces the front matter with a typeset title block.
Table of contents removed — a 25-page paper was spending two pages on one.
Margin 3.1 cm rather than 2.4: at 11 pt the old measure ran near 100 characters,
and the register rebuild had just moved the median paragraph to 95 words.
Running head, heading hierarchy through `titlesec`, `microtype`, widow and orphan
penalties, tables one size down.

**The typeface was deliberately not changed.** The `newunicodechar` mappings are
calibrated to Latin Modern, and on 13 August a missing glyph silently deleted
every ≥ in the manuscript. A font swap reopens that failure for a cosmetic gain.

**Two bugs found by looking at the render rather than the log.** The title block
came out reading "emphin vitro" — a doubled backslash — and the author lines ran
into the date, because inside a `center` environment `\vspace` does not end a
line. And `-V indent=false` had switched indentation **on**, since pandoc treats
any non-empty value as true; indented paragraphs are now a stated choice rather
than an accident.

**The figure number lived in two places.** `figure4_replication.png` carried
"Figure 4" drawn into the image while its caption said "Figure 2", because the
figures were renumbered into citation order and the PNG was not rebuilt. The
number now lives only in the caption. Same rule the claim set uses everywhere
else: one source, not two that can disagree.

### Verifier

`verify_draft_claims` 0 failures, `claim_map` 0, `check_paper_partition` 0
problems. 23 pages.

**Cut count: 0.** The §1/§4 duplication is still the standing proposed cut.

---

## 2026-08-28, late — register, architecture, and a broken cross-reference set

TSRB read the §1 and §3 register rebuilds and said the result was still "the book
chapter with removed numbers". She was right, and saying so produced the two
largest findings of the day.

### The register pass could not have found it

`VOICE-BASELINE-26AUG.md` measures paragraph length, sentence length, hedging,
signposting and person. **None of those metrics can see a heading.** The prose
inside §1.2 was moved into the field's range while the heading above it still
read like a chapter's. So the architecture was measured the same way the prose
had been, against the same 139 cached papers: `ARCHITECTURE-BASELINE-28AUG.md`.

**Headings that name the paper rather than its subject: 1 of 138 papers carries
any, and that one carries exactly one. This manuscript carried five.** Section
*count* was never the problem (17 subsections against a field median of 19).
The five were §1.2, §1.3, §1.4, §3.4 and §4.5.

### §2's cross-references had all been broken for a day

Found while planning the re-heading. The 27 August edit restructured
`draft/02-methods.md` from twelve numbered subsections to **five unnumbered
ones**, and dropped the number from the H1 as well, so §2 alone read `# Methods`
while every other section read `# N. Title`.

**The rest of the manuscript went on citing §2.1 through §2.8 — nineteen
references in the shipped text — and not one of those headings existed.** §7's
own heading read *"Sources for the four criteria of §2.4"*. A reader following
any of them landed nowhere.

It survived a compile, a PDF build and a verifier reporting 0 failures, because
nothing compared references against headings. Same class as `[5e]` and `[6]`:
**the check that would have caught it did not exist.**

**`[7]` written, then made to fail on purpose** before anything was closed
against it. A probe injecting `§9.9` and `§2.11` into §5 produced two named
failures with the exact address and exit 1; removing the probe returned 0.

### The repair — Choice, and it is TSRB's to overrule

§2 was renumbered **in document order**, which is the numbering the prose flow
already implies but not the numbering the prose had been carrying:

| | | |
|---|---|---|
| 2.1 | Dataset and detection pipeline | unchanged |
| 2.2 | Inputs used, and what could not be read | unchanged |
| 2.3 | Recovering the duration the analysis used | **was cited as 2.5** |
| 2.4 | Reproducing the published active-electrode count | **was cited as 2.3** |
| 2.5 | Recounting under other documented criteria | **was cited as 2.4** |
| 2.6 | Pharmacologically silenced electrodes | unchanged |
| 2.7 | Bounding recorded hardware failure | unchanged |
| 2.8 | Code and data availability | unchanged |

The alternative was to restore the original order, which would have required
moving the duration derivation after the criteria table and breaking the
sentence *"With the duration in hand, the reproduction is a direct test."*
**The permutation was applied simultaneously through a placeholder** so no value
could collide with another mid-substitution, and five live script docstrings
citing §2.3 and §2.5 were corrected with it. Dated notes in `notes/` were left
alone: they record what was true when written.

### Register and architecture, applied

| | before | after | field |
|---|---:|---:|:---:|
| bold paragraph lead-ins | 34 | **0** | 0 |
| pull-quote blocks in prose | 4 | **1** | 0 |
| median paragraph, words | 51.5 | **95** | 119 (102–145) |
| em dashes per 1,000 | 3.6 | **0.7** | target 2.0 |
| headings naming the paper | 5 | **0** | 0 |
| subsections | 17 | **19** | 19 (14–25) |
| Results subsections | 8 | **7** | 5 (4–7) |
| maximum heading depth | 3 | **2** | 2 (2–3) |

§1's four subsection headings were removed and the Introduction now runs as
continuous prose, which is the field norm. §3.4 was renamed to its finding.
§3.6.1 was folded into §3.6 and its two references repaired. §4.5's four
non-claims were moved rather than cut: three close §4.1, and the chronic-array
scope merged into §5's own scope paragraph, which already said the same thing.

**Every change was checked, not trusted.** §3, §4 and §5 each had their numeric
token multiset compared before and after. §3: identical. §4 and §5 combined: the
only differences are the section numbers that were deliberately retired, `4.5`
twice and `3.6.1` once, with `3.6` gaining one.

### Still open

- **§1 and §4 say the same three things.** The former §1.4 and the former §4.5
  both stated that no study did anything improper, that the count is not useless,
  and that no standard value is proposed. Both were kept, unheaded. **A paper
  says them once. This is a proposed Cut and it is TSRB's ruling**, not one to
  take at 01:00.
- **First person sits at 1.7 per 1,000 against a field median of 8.9.** The
  field's figure is dominated by multi-author *we*; a single-author paper using
  *I* will land lower. Whether 1.7 is low enough to still read as agentless is a
  judgement, not a measurement.
- **Part C of `CITATION-MAP-26AUG.md` remains open.** Headings were compared
  against the corpus. Section *ordering* was not, and the format-match against
  Cotterill 2016 has still not been done.

### Verifier

0 failures, 1 warning (em dash, now 0.7 per 1,000 and below target — the warning
threshold should probably be retired). `[7]`: 23 distinct cross-references, all
resolving.

**Cut count: 0.** One cut is proposed above and not taken.

---

## 2026-08-28 — S1: the shipping blockers

**Approved as a list before any edit**, per `ADDRESSING.md`. Six proposals, one
ruling, then applied. Two findings surfaced during the work that were not in the
list; the second is still open.

### The checker was made to fail before anything was closed against it

`[6]` had two defects and both were required. The **pattern** matched a keyword
vocabulary (`CITE|MODEL|TODO|S7 CROSS-REF|XX|REFERENCES`); the two live
placeholders open `*[State funding` and `*[Kapucu, Narkilahti`, are free prose,
and close on a different line, so a line-by-line scan had to anchor on the
opening `*[`. The **severity** sent them to `warn()` against an exit of
`1 if fails else 0`, so a corrected pattern alone still exited 0.

Both changed, then run: **it failed on exactly those two lines and nothing
else.** No false positive. Only then was §6 written.

`[5e]` had the same shape and was fixed with it. It counted the string `CHECK`
across the whole file including the draft-provenance header, whose own sentence
instructs that CHECK items be resolved — a check firing on the instruction about
the thing rather than the thing. It now counts the shipped body, after the head
separator `compile_manuscript.py` strips, and a CHECK is a failure.

### The four citations — Traced

Resolved against the indexed records, 28 Aug, not against memory.

| entry | what was open | outcome |
|---|---|---|
| Cotterill 2016 | authors, volume, pages, DOI | nothing was wrong. `doi:10.1152/jn.00093.2016`, PMID 27098024 |
| Kapucu 2022 | full author list, byline truncated | **resolved.** The indexed record carries these five and no others. `9(1), 120`, PMID 35354837 |
| meaRtools | package version, vignette date | **1.0.4, CRAN 1 May 2019**, vignette `meaRtoolsGeneralUsage.Rmd`; the prose sentence quoted in full |
| MEA-NAP | authors, year, volume, pages, DOI | *Cell Reports Methods* 4(11), 100901; twenty authors listed |

**Noted for §4.4, not acted on today.** Stephen Eglen is an author on three of
the four sources — Cotterill 2016, meaRtools and MEA-NAP — and Ole Paulsen on
two. meaRtools also carries an Axion BioSystems co-author. Under R4 this is not
an observation about anyone's conduct: it strengthens the claim, because the
documented values differ by an order of magnitude even across an overlapping
authorship.

### The author line — Choice, and the pattern was already on record

AUD-5. The byline is generated, exactly like the title, and a value that lives
only in `compile_manuscript.py` is a value nothing checks — the failure that let
the wrong title ship for two days. So the four fields live in an `AUTHORS`
constant, are mirrored in `01-introduction.md`'s title block, and `[5b]` now
checks the generator, the draft record **and** `MANUSCRIPT.md` for each.

### Figures — Traced, with one defect found

Callouts added for Figures 2 and 3 (AUD-6). While placing them: the numbering
ran against citation order. Figure 2 was anchored to §3.5 and Figure 3 to §3.3,
so the built PDF showed Figure 3 first. **Swapped**: replication is Figure 2
(§3.3), the silenced-electrode distribution is Figure 3 (§3.5). `§2.8`'s script
table and `build_manuscript_pdf.py` changed in the same edit. AUD-7 needed no
separate ruling — `figure2_criteria_spread.py` plots the 23 surveyed criteria
and left with Paper 2; the build script already records that.

### AUD-16 — the snapshot block was lying, and it was lying about this pass

The hard-coded "Known open items" list asserted that the author line was
outstanding, that Figures 2 and 3 had no callout, that §6 was bracketed
instructions and that §7 carried six CHECK items. All four had just been closed.
Rewritten to the true state, with a "Closed on 28 August" line so the change is
visible rather than silent. **The item is its own illustration**: a status list
that is generated but not checked drifts exactly the way the criterion in this
paper drifts.

### §6's generative-AI declaration — restored, and rewritten as prose

**Surfaced outside the approved list, ruled on the same day.** The 27 August edit
replaced a five-part disclosure with a single paragraph. The decoupling it
performed was necessary — the old text carried survey material and referred to
§2.10.1 and §2.12, which no longer exist. What it also removed: that the model
implemented the analysis and verification scripts, what the model did *not* do,
that it is not an author and is not eligible to be one, and that five claims were
withdrawn under tests written before their outcomes were known.

`[5c]` failed on three counts. §6's own opening paragraph requires "the full
extent of use, not the minimum defensible amount", and its drafting note says
"Do not trim this section to look better."

**TSRB's ruling: restore it, but as prose.** The five bolded blocks the previous
version used are the same device the register rebuild is removing everywhere
else — a bolded lead-in carries the point alone and lets the paragraph stop at
three sentences. The restored section is two paragraphs of 130 and 95 words,
inside the field's 100–140 band, and carries everything the five blocks carried:
which scripts the model implemented, that it drafted the text against a claim set
fixed in advance, that it is not an author and is not eligible to be one, what it
did not decide, and that the five withdrawn claims are recorded rather than
removed.

**One checker change came with it, and it is a change of category, not a
convenience.** `[5c]` matched the literal `takes full responsibility`; the voice
ruling put the sentence in the first person, so the pattern was testing a
grammatical choice rather than the disclosure. Widened to `takes? full
responsibility`, which accepts either person and no longer encodes the voice
decision. **The distinction matters here more than usual**: this is a check being
edited on the same day it failed, and the test is whether the edit follows a
decision already taken or exists to silence the failure. It follows the ruling.

The snapshot block was updated in the same pass so the open-items list does not
re-acquire the defect AUD-16 was raised for.

### Verifier

`[6]` none. `[5e]` none. `[5b]` author fields present in all three places.
3 failures, all `[5c]`. Em dash density 3.6 → 3.3 per 1,000.

**Final state after the §6 restoration: 0 failures, 1 warning** — the em dash
pass, 3.2 per 1,000 against a target of 2.0, deferred to worklist 8b.

**Cut count: 0.** This pass added and resolved; it did not audit prose. The
register rebuild is where cuts belong.

---

## 2026-08-17 — TSRB's read-through: decomposition and beat structure

**A different instrument, and it found what the scripts could not.** TSRB read
the paper whole and worked two passes over it: **atomic decomposition** of the
claim sentence — take each term, ask what it means, ask whether the paper
supplies it — and a **beat map**, the paper's structure against screenplay
convention with positions measured in words rather than estimated.

**Everything below was found by reading. Nothing was found by a checker.** The
checkers were then extended so that each finding cannot recur silently.

### E-1 — the title described a paper that no longer exists. **Found by TSRB.**

`MANUSCRIPT.md` carried *"…: a reanalysis and a survey"* **two days after the
survey moved to `paper2/`**.

**Three failures stacked.** The title was never in `draft/` — it lives in a
`TITLE` constant in `compile_manuscript.py`, so correcting the draft and passing
the verifier changed nothing a reader sees. The verifier's title check confirmed
that the decision was *flagged as pending*, which is not a check on the title.
And the session had logged the residue as *"S4's worklist"*, filing the most
visible sentence in the document under a heading meaning **later**.

**Fixed.** Title decided (candidate 2), carried identically in the compile
constant, the draft's decision block and `CLAIM-SET-FROZEN.md` §2; candidate 3
withdrawn for naming Paper 2; the verifier now checks the **built** `MANUSCRIPT.md`
H1 and fails if it names a survey. Teeth-tested.

### E-2 — M1 was asserted in Results and Discussion and stated nowhere in Methods

Found by decomposition, confirmed by grep: §3.6 states the detector rule and
cites *"(§2.1)"*. **§2.1 did not contain it. §2 did not contain it.** A frozen
claim row, load-bearing for M4 and for §4.2, was never introduced.

`check_paper_partition.py` passed because §2.1 exists. **It was checking the
address, not the delivery.** New section `[5b]` verifies that a cited section
contains what the citation promises — statuses `HOLLOW` and `DANGLING`. Verified
by removing M1 again in a scratch copy: two `HOLLOW` findings.

**Fixed.** M1 now stated in §2.1 as part of the acquisition chain, in the
descriptor's terms, with both consequences named. §4.2 cites it instead of
repeating it.

### E-3 — the paper never defined "active electrode" or "thresholded". **Cut-equivalent: two missing definitions.**

Decomposition question 2: *what is an active electrode?* §1.1 offers a gloss —
electrodes that "detect little or nothing are set aside, and the remainder…" —
which says what they are *for*, not what they *are*. **S6, which documented the
term's instability, left with the survey**, so a term whose ambiguity was
evidenced three days ago is now simply used.

Question 5: *threshold → thresholded, what is this?* The paper performs the
operation throughout and never states it. **Both now defined at the head of
§2.3**, including the transformation itself: a continuous quantity is compared
to a cut point, yields one bit per electrode, and the bits are summed.

### E-4 — H2 and M3 were in tension and the paper never staged the encounter

**The deepest finding of the session.** §3.2's headline is that **382–384 of 384
electrodes are active at 1 spike/min**. §3.5 measures pharmacologically silenced
electrodes at a **median of 3.30 spikes/min**.

**A silenced electrode fires at three times the criterion that makes the decline
vanish.** §4.2 stated the fact and never connected it to H2, so a reader was
invited to read 382/384 as reassurance about electrode health — which §3.5 says
it cannot be.

**Fixed in §3.5**, where the encounter now happens explicitly: what §3.2 shows
is criterion-dependence, which survives intact; what it does not show, and must
not be read as showing, is that the electrodes are healthy. **No rate threshold
on this pipeline can separate a working electrode from a silent one.**

### E-5 — §3.3 asserted what §3.6.1 later withdrew. **Cut.**

*"Two physically separate plates cannot independently produce the same
three-timepoint depression."* Decompose *independently*: same differentiation
batch, same incubator, same media schedule, same recording days. **Physically
separate, and independent in no stronger sense.** §3.6.1 conceded exactly this
forty lines later; §3.3 stood uncorrected. Rewritten to state what is excluded —
an accident confined to one plate — and what is not: a shared cause.

### E-6 — §3.7 stated a bound as a reading. **Cut.**

§2.7 is careful: `InactiveChannels` was **unreachable** and was *bounded* from
channel presence. §3.7's pull-quote said the record *"contains essentially
nothing at any timepoint"*. **The record was never read.** Rewritten to say what
it can at most hold, and to name itself as a bound.

### E-7 — four more, from the same read

- **§3.1** juxtaposed 336/336 with 216/222 — three plates against two, in one
  sentence. Now 222/222 → 216/222, like against like.
- **§3.5** opened *"every event detected on a silenced electrode is a false
  positive"* and retracted the *every* eight lines later for well A4. The
  qualifier is now in the opening sentence.
- **§3.6** claimed real spikes have *"an amplitude set by the biology rather
  than by the channel"*. Recorded amplitude also depends on impedance and
  distance — a degrading electrode records **smaller** spikes, which strengthens
  the argument. Corrected.
- **§3.6** stated two detector behaviours as fact that are **consequences of the
  rule, not measurements** — measuring them needs amplitudes, and the `.h5`
  files are unreachable. Now marked as inference.
- **§3.6** contained *"We refer to this below as adaptive-threshold
  suppression"* — a coinage sentence, **contrary to the decision logged on
  16 Aug** ("no 'we term this' sentence"). Removed; the phrase does its work
  descriptively, as decided.

### E-8 — §4.1 was a scene with no function. **Cut, 363 → ~200 words.**

The beat map put the paper's final image at **59%** (§3.7's pull-quote) with
**39% of runtime remaining**. §4.1 opened that remainder by restating §3 from the
top: four numbers already spent, no new evidence, and a drafting note conceding
the coupling (*"§3.2 and §4.1 must stay in agreement"*). **A section that must be
kept in sync with another section is a section that repeats it.**

Rewritten to carry only what §3 cannot say about itself: that the conversion is
one of **kind, not degree**, and that the metric is answering a different
question than the one it appears to answer.

### What the beat map showed that the line-by-line did not

Measured in words, not estimated: catalyst at **32%**, midpoint at **44%**,
"all is lost" — the failed pre-registered test — at **46%**, climax at **53%**,
final image at **59%**.

- **The midpoint does not reach back.** §3.5 recontextualises §3.2 and §3.2 was
  never revisited. E-4 is the fix.
- **Nine working setup–payoffs**, three of them reframing rather than merely
  fulfilling: §2.6→§3.5 (the failed test), §3.3→§3.6.1, §3.5→§3.6.1.
- **One broken**: §3.6 paid off a setup that was never planted. E-2.

**Cut count: 5** (E-3 two definitions absent, E-5, E-6, E-7 coinage, E-8), plus
E-2 a missing Methods statement and E-4 an unstaged tension.

**Method note, recorded because it changes how this session should be run.**
Cross-domain framing generated the §4.1 finding and also produced one
overstatement in the same message — *"the antagonist is available from 17%"*,
when M1 was not in §2 at all. **The rule adopted: no metaphorical claim is kept
unless it reduces to a statement about a named file and line.** The reduction is
what found E-2.

---

## 2026-08-17 — §4 and §5 line audit

**Overdue since 14 August, and deliberately run after the strip** so the
sections being audited were the ones that will actually post. TSRB's ordering.

### D-1 — the paper had no reference section. **Cut-equivalent: a missing section.**

`draft/` ran 00–06. **There was no reference list.** The only thing standing in
for one was a bracketed editorial note at the end of §4.4 reading
*"REFERENCES — assembled in `notes/BIBLIOGRAPHY.md`…"*, which is scaffolding,
not a section.

**Nothing was watching for it.** `verify_draft_claims.py`'s placeholder pattern
covered `CITE`, `MODEL`, `TODO`, `S7 CROSS-REF` and `XX` — **not `REFERENCES`**.
The paper could have reached pre-flight with two in-text citations and nowhere
for a reader to resolve them.

**Changed.** `draft/07-references.md` created; `compile_manuscript.py` extended
to 00–07; new verifier section **[5e]** checking the file exists and that every
name cited in the body appears in it; `REFERENCES` added to the placeholder
pattern. Six CHECK items now surface as a warning rather than sitting silent in
`BIBLIOGRAPHY.md`.

**The list is short because the strip made it short** — two papers, four pieces
of tool documentation, one methods source. That is a real gain from the
decoupling.

### D-2 — §4.2 overstated the order of magnitude. **Cut.**

*"a criterion set an order of magnitude lower — as three of the four documented
sources set it — sits inside the noise distribution"*.

The four criteria are **1, 5, 6 and 10 spikes/min**. Only meaRtools' 1/min is an
order of magnitude below 10. **The conclusion was right and the characterisation
was wrong**: all three do sit below the silenced p99 of 9.69, but not because
they are an order of magnitude lower. Rewritten to state the three values and
the p99 directly, which is both true and stronger.

### D-3 — three survey invocations survived the strip in prose. **Cut.**

None contained a number, so **nothing was checking for them**:

- §4.3 — *"a survey of this kind does not earn the authority to set a
  convention"* → now *"a reanalysis of one dataset does not earn the authority
  to set a convention for a field"*, which is the true reason and a better one.
- §5 — *"The survey result, which concerns the field rather than one dataset,
  does not share this limitation."* → rewritten to make the same point about
  **S5**, which is Paper 1's and does not depend on the sample.
- §5 header — instructions to fill *"the model name and version used for
  classification, and the S7 cross-reference"*. Both were stale: the model name
  was filled 12 Aug and the classification left with the survey.

`check_paper_partition.py` gained a **[3b] survey METHOD PROSE** section.
**A partition leaks through ordinary English, not through statistics.**

### D-4 — §4.4 said the same thing twice, and it was my doing

Paragraph 1, rewritten during the strip, ends *"a burst-detection algorithm has
a name and a citation, whereas the activity criterion is a bare number"*.
Paragraph 2 then opened *"an algorithm has a name and a citation, while a
threshold has neither"*. **The repetition was introduced by the strip edit and
survived it.** Paragraph 2 rewritten to carry only the self-concealing argument,
which is the part that is actually distinct.

### D-5 — §4 and §5 checked and sound

- §4.1 — 336/336, 68%, 382–384 of 384, r = +0.986, −68%/−66%, 18 of 19, 19 of
  19: all traced.
- §4.2 — 416, 9.69, 4 of 416 (0.96%): traced. The pre-registered failure is
  stated as a failure.
- §4.3 — six recommendations, none exceeding the data. Item 4 (state the
  criterion where the count enters a denominator) now rests on **M2**, the
  data-dependent denominator, rather than on the survey's propagation figure.
- §4.5 — the four "does not claim" bullets survive intact, including the chronic
  *in vivo* framing settled under A1 on 12 Aug.
- §5 — every surviving limitation has a referent in Paper 1. The two that left
  (retrieval coverage, classification) are in `paper2/05-limitations.md`.

**Cut count: 3** (D-2 characterisation, D-3 three invocations, D-4 repetition),
plus D-1 which is a missing section rather than a cut.

### Still open on Paper 1

**Four partition residues remain, all in `01-introduction.md`** — §1.2 still
names the survey as one of two pillars. **That is S4's worklist and the checker
will stay red until §1 is rewritten**, which is the correct signal.

Also open: the abstract pass, six CHECK items in the references, the six
single-implementation claims (H2, H3, H4, M2, M3, A1), the em dash pass at
8.0/1000 against a 4.15 field maximum, the title decision, and pre-flight.

---

## 2026-08-17 — Session 3, the strip

**Both papers built full-fledged, at TSRB's instruction — no shortcuts, Paper 2
a manuscript rather than a holding pen.** `check_paper_partition.py` went from
**73 problems to 0**.

### T-1 — the checker was written before the move, deliberately

`scripts/check_paper_partition.py` was written first, run against the
un-stripped tree to produce a 73-item worklist, and watched from red to green.
**A checker written afterwards only ever confirms what was already believed.**
It asserts four things nothing else in the repo does: no survey section survives
in Paper 1, every moved section landed in Paper 2, no survey figure or
classification disclosure remains, and no cross-reference dangles in *either*
paper.

### T-2 — the move was done by script, and the reconciliation caught a real gap

`scripts/strip_survey.py` slices on headings and **reconciles the multiset of
body lines** before and after, so a dropped paragraph cannot hide behind an
added blank. A plain line count would not have done: two errors can cancel.

**It failed on first run** — one line unaccounted — then on the second reported
five, which turned out to be the deliberately renumbered headings. Titles are
now checked separately, so a renumber cannot conceal a retitle. **308 lines
moved, every line accounted for.**

### T-3 — my own checker made yesterday's Figure 2 mistake

`check_paper_partition.py` v1 keyed on section **numbers**. The moment Paper 1
was renumbered to close the gaps, §2.8 became *"Code and data availability"* and
§4.2 became *"What the criterion cannot do"* — so it reported Paper 1's own
surviving sections as survey residue and the genuinely moved ones as missing.

**Identical to the Figure 2 anchor defect found on 16 Aug**, one day later, in a
file written to prevent exactly this kind of error. Now keyed on titles. **A
number is a position; a title is an identity.**

### T-4 — Paper 2's verifier, and a pattern that should have been copied

The survey checks migrated to `scripts/verify_paper2_claims.py` as
`DECOUPLING.md` required — *"must move to a Paper 2 verifier rather than be
deleted"*. Sections [1], [2], the audit write-up, the S1 interval rule and the
classification disclosure all moved; `verify_draft_claims.py` carries a pointer
so a reader cannot think they were dropped.

**One defect, and it is instructive.** The withdrawn-claim patterns were
**retyped from memory rather than copied**, and immediately lost a detail that
had been reasoned about carefully: the original writes `[^,.;]{0,40}` for the
meaRtools rule *specifically* so a list naming both tools does not match.
Retyped as `[^.]{0,40}` it allowed the comma and flagged Paper 2's own correct
sentence as a resurrected dead claim. **A checked artefact is copied, not
retyped.**

### T-5 — two false passes, found by looking rather than by running

**Paper 1's [5c] "analysis use" check went on passing against a disclaimer.**
Its pattern was `eligibility screening and criterion extraction`, correct while
Paper 1 contained the survey. After the strip the only remaining match was the
new sentence saying the model did **not** do that work here — the check was
confirming the presence of a denial. Repointed to
`implemented the analysis scripts`.

**Paper 2's completeness check went green on placeholders.** It tested only that
the file existed and was non-empty, so creating stub abstract and introduction
files reported the paper complete while both said *"NOT WRITTEN"* on line three.
Placeholders now report **PENDING**, which is not a pass.

**Both are the A6b class: a check satisfied by the wrong thing.** Neither would
have been caught by running the suite, because both were green.

### T-6 — Figure 2 would have left a hole

The criteria-spread figure belonged to §3.9, which moved. **Paper 1 would have
shipped with Figures 1, 3 and 4 and no Figure 2** — a gap a reader reads as a
missing figure, not as a decoupling. Remaining figures renumbered 1, 2, 3;
§2.8's script table updated; Paper 2 inherits it as its own Figure 1.

### Result

| | Paper 1 | Paper 2 |
|---|:---:|:---:|
| words (compiled body) | **7,926** | 3,689 |
| verifier | 0 failures, 1 warning | 0 failures, 2 pending |
| partition | \multicolumn — **0 problems** | |
| claim map | 12 rows | 8 rows |

**Paper 1 is 7,926 words against the 7,000–7,500 target.** §1 has not yet been
rewritten (S4), which is where the remaining reduction comes from.

**Still open:** Paper 2's abstract and introduction are placeholders carrying
their own reasoning; both are blocked on the pilot-versus-fresh-draw decision in
`paper2/README.md`. Paper 1's §4/§5 line audit, the em dash pass and pre-flight
remain.

---

## 2026-08-16 — Reproducibility audit, called after S2

**TSRB stopped the session**, judging the pace and the level of uncertainty
unsafe to continue on, and asked for everything possible to establish that the
project is reproducible and repeatable before wrapping. **The judgement was
correct.** Full write-up in `notes/REPRODUCIBILITY-AUDIT-16AUG.md`. Five errors
found in material written earlier the same day, all in the new material, none in
the 10 August work.

### R-1 — §3.6.1's numbers were produced by no script. **Same defect as S2-1, four hours later.**

The §3.6.1 table came from throwaway scripts written to a sandbox scratch
directory and never saved. **This session had flagged exactly this failure mode
as the day's most urgent finding (S2-1) and then reproduced it in the same
sitting.** Fixed: `scripts/threshold_suppression.py`.

### R-2 — unit error, false ratio in the manuscript. **Cut.**

§3.6 said a flagged electrode fires at *"roughly a fortieth"* of the typical
rate. Flagged medians are spikes/min; plate medians as reported by
`characterise_noisy.py` are spikes per 600 s. **True ratios 4× and 13×.** The
trap is now recorded in the M4 row so the conversion is not skipped again.

### R-3 — floor claim generalised from a partial printout. **Cut, twice.**

*"On every recording of the experiment"* was false — the bottom decile falls
from 56 and 62 at DIV 3 to the low thirties by DIV 42. Rescoped to DIV 42–66.
**The replacement range was then also wrong**, 30–33 read off `hPSC_MEA1` alone;
`hPSC_MEA2` runs 29–34. Now stated as 29–34 across both plates.

### R-4 — the ratio table is over-precise. **Choice: state the convention.**

The two implementations disagree by up to 0.017 on individual ratios because
they use different percentile conventions. The pattern holds under both; the
second decimal does not. §3.6.1 now declares the convention and the tolerance
instead of implying exactness.

### R-5 — `verify_draft_claims.py` was not checking the reanalysis. **Tooling, closed.**

Its docstring and `START-HERE.md` §3 both claimed it checks every number in
`draft/` against the source CSVs. It checked the survey and the wording rules
and **almost none of the reanalysis figures** — the gap that let `hPSC_MEA2` go
a week unreproduced. New section **[0]**, 35 checks. **Verified to have teeth by
re-running against the pre-fix artefact from `HEAD`: 5 failures, exit 1.**
`START-HERE.md` §3 corrected, with the false sentence quoted so the correction
is visible rather than silent.

### R-6 — rule 4 was too narrow, and this session broke the repo. **Rule rewritten.**

`git status` is **not** read-only: it refreshes the index stat cache, takes
`.git/index.lock`, and the sandbox cannot delete it. Rule 4 read *"commit from
PowerShell, never from the sandbox"*, which reads as a rule about committing.
This session obeyed that scrupulously and then ran `git status`, `git diff`,
`git log` and `git show` freely all day. **Third occurrence of O7/O14, first one
caused by a session that was following the rule as written.** Rule 4 now says no
git command from the sandbox at all, lists the read-safe exceptions, and gives
the recovery command. Lock cleared by TSRB in session.

### R-7 — A2b now meets the §2.3 standard it was failing

`scripts/verify_threshold_suppression.py` is a genuinely independent second
implementation — different counting, different percentile convention, dense
zero-padded vectors, ranks by explicit comparison. **It found R-3 and R-4 on its
first run: five disagreements. After correction, zero.**

### R-8 — the PDF, 17 Aug. **Three defects from one traceback.**

The rebuild failed with a bare `FileNotFoundError: [WinError 2]`. **Neither
pandoc nor xelatex is on PATH on the Windows machine.**

> **R-8 was written and committed (`d17a35c`) asserting they had been there on
> 13 August and had since gone. False — seventh error of the audit.** pandoc has
> never been installed on Windows: no `pandoc.exe` on `C:\` or `%LOCALAPPDATA%`,
> nothing in `winget list`, no non-Python pins in `requirements.txt`, no PDF
> entry in the logbook. **`MANUSCRIPT.pdf` has always been built in the sandbox.**
> The evidence sat in `build_manuscript_pdf.py` line 26 — a comment about the
> sandbox being unable to delete files it creates — and was read past. A
> timestamp and a Windows traceback were turned into a story about a vanished
> toolchain. Same reflex as *"roughly a fortieth"*: confident causal account,
> committed before anyone tried to falsify it.

**R-8a. Unreadable failure.** `build_manuscript_pdf.py` now preflights, names
the missing program, gives install locations, and says which artefact is still
trustworthy.

**R-8b. A four-day-stale PDF was committed** beside a current `MANUSCRIPT.md`,
with `START-HERE.md` §2 pointing readers at it — no M4, wrong §2.4 provenance,
survey still integrated. New verifier section **[0b]**: **missing is a WARN,
stale is a FAIL.** Verified on a backdated copy — `STALE by 81.7 h`. Deleting a
stale artefact is a legitimate route to green; a missing one misleads nobody.

**R-8c. The §3 renumbering silently misplaced Figure 2.** *(Sixth error of the
audit.)* Figures anchor to section **numbers**; inserting §3.6/§3.6.1 shifted
the survey sections down one, so Figure 2's `3.8` anchor — written for *"What
the criterion is, when stated"* — came to point at *"How often the field states
the criterion"*. **It would not have errored**, because §3.8 still existed. The
build would have placed the figure under the wrong subsection and reported
success. Every `FIGURES` entry now carries an `expect` heading-text string and
the build refuses to run on a mismatch.

**R-8d. The real gap, once the false story is removed.** The sandbox is the PDF
toolchain and always was. What is missing is any record of **what** builds it:
`requirements.txt` pins the analysis stack because the analysis was treated as
the reproducible part, while the PDF was treated as a convenience — but rule 10
exists precisely because typesetting fails silently. The sandbox is ephemeral
and its versions are not pinned anywhere. `build_manuscript_pdf.py` now writes
`notes/pdf-toolchain.txt` recording pandoc, xelatex and pdftotext versions plus
the source hash it built from, so drift is visible rather than discovered in a
rendered character.

**No Windows rebuild is required**; that instruction described a build that has
never existed.

### R-9 — the claim → script → number map, and the eighth error

**Built 17 Aug at TSRB's instruction**, as `scripts/claim_map.py`. This is the
general form of S2-1: fixing `hPSC_MEA2`'s missing reproduction answered one
instance and never asked what else was asserted with nothing behind it.

**Asking it found a second immediately. H3's r = +0.986 — one of Paper 1's ten
claims — was produced by `figure4_replication.py`, which only called `savefig`.**
The number existed nowhere on disk: not in `notes/`, not in any script output,
only in prose typed by hand into the draft, the claim set, the ledger and the
logbook. Nothing could check it, and a change in that script would have gone
unnoticed indefinitely. It now writes `notes/replication_correlation.txt`.

**Result across all twenty rows: 10 TRACED, 2 PRIMARY, 8 SURVEY, 0 unsourced.**

**The map also guards itself.** It fails if a row is added to
`CLAIM-SET-FROZEN.md` without being mapped — the same failure one level up, an
unwatched claim. Both behaviours verified: removing H3's artefact gives
`H3 UNSOURCED ... FAIL`; adding an unmapped `M5` gives
`CLAIM ROWS NOT IN THIS MAP: M5`.

**Cut count for the audit: 3** (R-2 wording, R-3 twice). **Eight errors found in
one day's new material and its surrounding machinery.** S2 reported a Cut count
of 2 and was wrong to feel finished.

---

## 2026-08-16 — Session 2, §3 Results

**Scope.** §3.1–3.6 checked against the CSVs, plus the standing decision on the
threshold-scaling mechanism. Evidence assembled in
`notes/S2-threshold-scaling.md` **before** the decision, so the decision was made
against evidence rather than recollection.

### S2-1 — no script reproduced `hPSC_MEA2`'s `nae` table. **34% of H1 had nothing behind it.**

**Found while answering "which script produces this" for §3.1.**

**Defect.** Every script that reads a published `nae` file — `verify_all.py`,
`characterise_noisy.py`, `derive_duration.py`, `duration_consistency.py`,
`fit_threshold.py`, `day2_threshold_analysis.py`, `block_d_plot.py` — covered
`hPSC_MEA1` and `Rat_MEA1` only. §2.12 lists `verify_all.py` as *"independent
reproduction of published `nae`"*, and it was, **for two plates of three**.
**H1 is 336/336 and 114 of those values were produced by nothing.**

**Checked by hand first.** `hPSC_MEA2` reproduces at 114/114 (≥100), 102 (≥101),
103 (≥99). Three-plate totals **336, 307, 303** — matching §3.1's stated 336,
307 and 303 exactly, including both adjacent-threshold figures.

**Changed.** `verify_all.py` now runs three plates and prints an `H1 TOTAL`
block that regenerates the headline rather than leaving it to be assembled by
hand. `reproduced_at()` factored out of the B2/B3 loop so the total uses the
same rule, not a second implementation of it. `plate_report()` returns its noisy
sets so the total can apply the exclusion.

**Why this was the most urgent thing found today.** The repo goes public with H1
as its first claim. A reader could not have regenerated a third of it.

**Category.** **Traced.** Acted under the act-then-explain default.

### S2-2 — the threshold-scaling mechanism becomes M4. **Adjudicated by TSRB: adopt.**

**Was.** §5, as a limitation, with the mechanism spelled out in full; and §4.5,
in passing.

**Finding.** It is not a limitation. A limitation constrains what this analysis
can conclude, and this constrains nothing — §5 already establishes that H1's
exactness does not depend on knowing the flag rule. It is a **mechanism claim
about the metric**, the same category as M1, M2 and M3, and it belongs in
`CLAIM-SET-FROZEN.md` §3.4 with them.

**Evidence, all of it re-run this session.** Flagged electrodes sit in the bottom
decile of their own recording day: 36 of 47 (`hPSC_MEA1`, 77%), 40 of 44
(`Rat_MEA1`, 91%), 76 of 91 pooled (84%); medians 2.7 and 2.6 spikes/min against
plate-wide medians of 100 and 342 spikes per 600 s; minor mode exactly two
electrodes per plate. Detector rule documented (A5b): stage 1 at 4.5 × each
channel's own noise SD, stage 2 rank-matched. Kapucu's account of the flag's
provenance obtained independently and matching mode for mode.

**Changed.** New claim row **M4** in `CLAIM-SET-FROZEN.md` §3.4. New **§3.6** in
`03-results.md`. §5's paragraph reduced to the limitation that actually remains —
the provenance rests on correspondence and cannot be verified from the deposited
files — and now points at §3.6 rather than restating it. §4.5 gains the
inversion argument.

**Preserved deliberately.** Both boundaries. It is a documented rule plus a
distribution the rule predicts, **not a controlled demonstration**; and the flag
is a bench judgement, not a calibrated instrument. Both are stated in §3.6
itself rather than left to §5, because a result that needs its caveats read
elsewhere is a result stated too strongly.

**Category.** **Traced** as to the measurement, **Choice** as to promotion.

### S2-3 — A2b: the anomalous days show the predicted signature. **New.**

**Finding, from per-electrode distributions, new this session.** On DIV 51 and
56 the active-electrode count falls by roughly two thirds on both plates while
**not one electrode on either plate stops producing spikes** — 384 of 384,
both days, both plates. The loss is confined to the top: against DIV 45, the
lower quartile retains 79–88% while p90 retains 9–14%. **The distribution does
not shift; it collapses onto a floor that does not move** — bottom decile at
30–31 spikes per 600 s on *every* recording of the experiment, i.e. 3.0–3.1
spikes/min against a silenced median of 3.30 (M3).

**Why it matters.** §3.3 said the DIV 48/51/56 collapse was *"a property of
those recording sessions rather than of either culture"* and stopped. A2b says
what property, and it is the property M4 predicts.

**Stated limit, in the claim row and in the draft.** Spike times alone cannot
separate *"the threshold rose"* from *"the cultures were quieter that day"*.
Amplitudes would; the `.h5` files are unreachable. **The claim is the structural
one — no electrode silenced, residual floor matches the silenced floor — with M4
as a sufficient rather than demonstrated explanation.**

**Category.** **Traced** as to the distributions; the attribution to M4 is
explicitly flagged as sufficient-not-demonstrated in both the claim row and §3.6.1.

### S2-4 — the name. **Choice, and TSRB's to overrule.**

TSRB asked to decide it in session rather than pick from the list. Decided:
**"adaptive-threshold suppression", lower case, used descriptively and never
formally coined.**

**Reasoning.**

- **The paper's own style does not name phenomena, it states them.** Every §3
  heading is a declarative sentence — *"The published active-electrode count is
  reproduced exactly by a spike-count rule"*, *"What the analysis divided by"*.
  A capitalised coinage would be stylistically foreign, so the heading
  *"A channel that gets noisier reads as quiet"* carries the phenomenon and the
  phrase carries the back-references.
- **"Adaptive threshold" is the field's own term for this detector**, used
  verbatim by one of the surveyed papers (PMC8885486: *"the adaptive threshold
  method"*). Borrowing it costs nothing and claims nothing.
- **It states the direction.** *Threshold scaling*, the working term, does not,
  and collides with the rate-criterion scaling §3.2 is about.
- **It scopes the claim honestly** to per-channel adaptive detectors, which is
  the boundary the evidence supports.
- **No "we term this" sentence.** Formally coining a term for a mechanism
  demonstrated on one dataset by inference is the kind of overreach this project
  has avoided everywhere else. Written as description, it reads as description
  on first encounter and as a name by the third. If the field picks it up it
  becomes a term; if not, nothing was overclaimed.

**Overrule path.** If a name is wanted with more edge, *the noise–quiet
inversion* is the alternative and the change is three occurrences.

**Category.** **Choice.**

### S2-5 — §3.1–3.5 checked, and §3.6-as-was

All figures re-derived from source this session and matching the draft: the
336/307/303 reproduction and the 216/222 without exclusion; the six and two
electrode-recordings the exclusion removes; §3.2's 384/355/321 and 382/201/103
and the 1.20×–8.53× ratio range; §3.4's 222 estimates, 599.689 s minimum and the
three-candidate table; §3.5's two TTX rows, the 12.2× transfer failure and the
pooled p99 of 9.69; §3.7's bounds of 0, 0 and 0–3 of 768. `hPSC_MEA2`'s
DIV 45/48/51/56/59 row — 189/124/60/55/132 — independently confirmed.

**One wording defect.** §5 said *"roughly three quarters"* of flagged electrodes
fall in the bottom decile. The measurement is **77% and 91%, 84% pooled**. The
draft understated its own result. Corrected in the move to §3.6.

**Renumbering.** §3.6 and §3.6.1 inserted; survey sections §3.7–3.9 became
§3.8–3.10; two stale cross-references in `05-limitations.md` swept. **Session 3
deletes §3.8–3.10 and renumbers again**, so these numbers are deliberately not
invested in.

---

## 2026-08-16 — Session 1, §2 Methods

**Rows are numbered `S1-n`, not continuing the `A` series.** The `A` rows are
TSRB's review comments. These are findings from a script-tracing pass, which is
a different instrument, and the `B` prefix is unavailable because the ledger
already uses B2, B3, B5, B6, B8 for claim rows.

**Scope.** §2.1–2.7 and §2.11–2.12. §2.8–2.10 skipped; they leave in session 3.
**Question asked of every factual span: which script produces this, and does it
still?** All six scripts named in §2.12 for the reanalysis were re-run from a
clean copy of the tree.

**Environment note, because it strengthens the answer.** The re-run used
Python 3.10.12 / numpy 2.2.6 / pandas 2.3.3 / scipy 1.15.3. `requirements.txt`
pins Python 3.13.15 / numpy 2.5.1 / scipy 1.18.0, the versions the published
results were produced with. `verify_all.py` reproduced
`notes/verify_all_results.txt` **byte-for-byte** across that gap, and
`derive_duration.py`, `duration_consistency.py`, `ttx_ceiling_two_plates.py`,
`bound_inactive.py` and `figure4_replication.py` each reproduced their stored
values exactly. **The results are not interpreter-dependent.** That is a
stronger reproducibility claim than the paper currently makes and it was free.

### S1-1 — §2.4 attributes the Pearson correlation to a script that does not compute it. **Traced defect: a bug.**

**Span.** `02-methods.md` §2.4: *"Agreement between plates was quantified by
Pearson correlation of active-electrode counts across matched timepoints
(`day3_threshold_landscape.py`)."*

**Defect.** `day3_threshold_landscape.py` contains no correlation of any kind —
no `corrcoef`, no `pearson`. It builds the threshold landscape and Figure 1.
**r = +0.986 is produced by `figure4_replication.py:127`**, which was not cited
anywhere in §2. H3 is one of Paper 1's ten claims and its Methods pointed at
the wrong file.

**Changed.** §2.4 now names both scripts and attributes each to what it does.
Re-ran `figure4_replication.py`: r = +0.986 at 10/min, r = +0.289 at 1/min,
MEA1 321→103 (−67.9%), MEA2 315→108 (−65.7%). Unchanged.

**Category.** **Traced.** A mismatch here is a bug, not a style question, so it
was fixed under the act-then-explain default.

### S1-2 — §2.12 claims to list every figure-generating script and omits three. **Traced defect: a false sentence.**

**Span.** `02-methods.md` §2.12: *"Scripts regenerate every reported figure from
those inputs:"* followed by a six-row table.

**Defect.** The table omitted `figure2_criteria_spread.py`,
`figure3_ttx_distribution.py` and `figure4_replication.py` — the scripts that
build Figures 2, 3 and 4. All three exist and all three run. The sentence
asserting completeness was therefore false, and a reader taking §2.12 as the
availability statement could not have regenerated three of the four figures.

**Changed.** Three rows added. Figure 1 was already covered by
`day3_threshold_landscape.py`, which does produce it.

**Note for session 3.** `figure2_criteria_spread.py` builds Figure 2, which
`DECOUPLING.md` assigns to Paper 2. Its row leaves with the strip, and the two
`d3_*` rows with it.

**Category.** **Traced.**

### S1-3 — §2.4's Axion provenance overstates the evidence on two counts. **Proposed, not acted on.**

**Span.** `02-methods.md` §2.4, the 5 spikes/min row: *"value named identically
by four independent studies using the tool (PMC11002531, PMC8885486,
PMC13190290, PMC11217373)."*

**What the cached full texts actually say**, read verbatim this session:

| record | names the Neural Metrics Tool? | wording of the criterion |
|---|:---:|---|
| PMC11002531 | yes | *"active electrodes required at least five spikes/min"* |
| PMC8885486 | yes (*"Axion Neural Metric Tool"*) | *"a minimum of five spikes a minute"* |
| PMC13190290 | yes (*"v2.5.1"*) | *"at least 5 spikes per min"* |
| PMC11217373 | **no — names AxIS Navigator** | *"an average of 5 spikes per min"* |

**Two defects, and the second is the serious one.**

1. *"using the tool"* — three of four name the Neural Metrics Tool.
   PMC11217373 names Maestro Pro, Axion plates and **AxIS Navigator software**.
   Same manufacturer, different named tool. This is the same failure class as
   the withdrawn EPA attribution: a criterion attributed to a named tool on
   evidence that does not establish the tool.
2. *"named identically"* — **it is not.** Three state a **minimum**; PMC11217373
   states an **average**. A minimum and an average over electrodes are different
   rules that can select different electrodes from the same data. **This paper's
   entire thesis is that the field states this criterion inconsistently, and its
   own Methods flattens four statements into "identically".** The value is
   identical. The rule is not.

**Why it was not acted on.** `CLAIM-SET-FROZEN.md` S5 says only that four
independent papers *confirm the value* at 5/min, which is true and untouched.
The overstatement lives in the Methods wording, not the claim, so correcting it
is a wording decision against a frozen row and it is TSRB's.

**Proposed replacement for the provenance cell:**

> value stated at 5 spikes/min by four independent studies using Axion
> instrumentation, three of which name the Neural Metrics Tool (PMC11002531,
> PMC8885486, PMC13190290); the fourth names AxIS Navigator and states the
> value as an average rather than a minimum (PMC11217373)

**ADJUDICATED 16 Aug — fix both, full replacement.** §2.4's provenance cell now
reads as proposed. *"named identically"* is **Cut**; *"using the tool"* is
narrowed to the three records that support it, and PMC11217373 is kept in the
row with its actual software and its actual rule stated. The row is longer and
survives a reader opening all four papers, which the old one did not.

**Category.** **Cut** (the words *"named identically"*), inside a Traced row.

### S1-4 — §2.11 Statistics is entirely survey machinery, and `DECOUPLING.md` does not assign it. **Structural, awaiting adjudication.**

**Span.** All of §2.11.

**Finding.** Three sentences: proportions with 95% CIs under a
finite-population correction against the estimated eligible population;
intervals reported throughout, never bare point estimates; pattern-matched
quantities reported as lower bounds. **Every one of those governs the survey
only.** After the strip, Paper 1 reports no proportion with a confidence
interval — H1 is 336/336 exact, H2–H4 are counts and percentage changes, M1–M3
and A1–A2 are counts, bounds and percentiles. Nothing in §2.11 has a referent
left.

**Why it matters now rather than in session 3.** `DECOUPLING.md`'s *what goes
where* table lists §2.1–2.7 and §2.8–2.10 and **stops**. §2.11 and §2.12 are
not assigned to either paper. Session 3 is scoped to move §2.8–2.10; §2.11
would survive by default into a Paper 1 that has no use for it.

**Two options, both defensible.**

- **Move §2.11 whole to `paper2/`.** Cleanest. Paper 1 then has no Statistics
  subsection, which is honest — it performs no inferential statistics.
- **Keep one sentence, rewritten.** Paper 1 does report a Pearson r and a set
  of percentiles, and could state that percentiles rather than extrema are used
  for silenced-electrode distributions — but §2.6 already says that, so the
  sentence would be a duplicate.

**ADJUDICATED 16 Aug — move §2.11 whole to `paper2/`.** `DECOUPLING.md` updated
in the same pass: §2.11 added to the *what goes where* table and to the session 3
strip list with the reasoning, and §2.12 recorded as **splitting** rather than
moving — the two `d3_*` rows and `figure2_criteria_spread.py` leave, the rest
stay. Session 3 now executes this rather than rediscovering it.

**Category.** **Cut** from Paper 1. Nothing is deleted; §2.11 moves intact.

### S1-5 — the verifier's placeholder check has a hole. **Tooling defect, found while tracing §2.12.**

**Finding.** `[6] unresolved placeholders` reports **PASS none** while four
placeholders sit in `draft/`:

```
draft/02-methods.md:262   *[repository]*, *[Zenodo DOI]*
draft/06-declarations.md:49-50   *[repository]*, *[Zenodo DOI]*
```

The regex is `\[(CITE|MODEL|TODO|S7 CROSS-REF|XX)`. It never matched
`[repository]` or `[Zenodo DOI]`. `START-HERE.md` §7 item 6 tracks these as
pre-flight items, so they are not forgotten — **but the verifier is reporting
zero when the true count is four, and the pre-flight step that resolves them is
the last thing before posting.** A6b's lesson was that a check reporting clean
is worse than no check.

**Not fixed this session** — it is a one-line regex change plus a re-run, and it
belongs with the pre-flight work rather than mid-audit. **Logged so it cannot be
lost.**

**Category.** Tooling. Not a manuscript row.

### S1-6 — spans checked and found sound

Recorded so the pass is not re-run over them.

- **§2.1 plate table** — 6 wells / 384 channels / 19 DIV for `hPSC_MEA1`,
  12 wells / 768 / 10 DIV for `Rat_MEA1`, confirmed by `verify_all.py` A3.
  `hPSC_MEA2` confirmed at 19 spike files and 384 channels.
- **§2.1 simultaneity** — *"recorded simultaneously on the same plate in a
  single 10-minute recording"* is traced: the `expLog` for
  `hPSC_MEA3TTX_DIV29` carries Control=2, ExcludedWell=24, NoTreatment=10,
  TTX=12 within one file, max spike time 599.9948 s.
- **§2.3 double implementation** — *"implemented twice, independently"* still
  holds. `day2_threshold_analysis.py`, the exploratory implementation, still
  lands on 100 spikes per 600 s = 10 spikes/min, agreeing with `verify_all.py`.
- **§2.5 duration recovery** — 222 independent solutions across both plates,
  min 599.6888 s, pooled 599.99416 s. Matches §3.6 exactly.
- **§2.6 pre-registered rule** — the rule is stated as pre-registered and it
  **failed**: rat/human ceiling ratio 12.23×, beyond the 2× bound. §2.6 says so
  and points at §3. Sound, and the honesty is load-bearing.
- **§2.7 bound** — max 3 of 768, 0.39%, on the worst rat recording. Matches §3.
- **§2.2** — the `.h5` exclusion and its two downstream consequences (§2.5,
  §2.7) are consistent and correctly cross-referenced.

---

## 2026-08-13

### A2 — table alignment

**Span.** `MANUSCRIPT.md`, the §2.1 plate table, and by extension every table
in the manuscript.

**Comment from TSRB.** *"always follow centre alignments for data and numbers
within the table also while table"* — read as two requests: centre the data
cells, and centre the table on the page.

**Acted, per the act-then-explain default.** The comment landed on
`MANUSCRIPT.md`, which is **generated**, so fixing it there would have been
undone by the next compile. The change went into `draft/` instead.

**Changed.**

- `draft/02-methods.md`, `draft/03-results.md` — ten data tables now carry
  `:---:` on their numeric columns.
- `scripts/manuscript-header.tex` — `\LTleft`/`\LTright` set to `\fill`, which
  centres pandoc's longtables on the page. Alignment within a column comes from
  the markdown; centring of the table does not, and cannot.
- `START-HERE.md` rule 9 — recorded, or the next compile drifts.

**Preserved deliberately.** Prose columns stay left: *species*
(*"human hPSC-derived cortical"*), *provenance*, *upper bound on failed
electrodes*, and the two wholly prose tables (script → produces, and the
snapshot header). Centring running text degrades readability; the comment asked
for data and numbers, and that is what moved.

**Category.** **Choice**, and TSRB's to overrule — including the prose-column
carve-out, which is a reading of the comment rather than the comment itself.

### A2b — glyph loss found while verifying A2. **Cut-equivalent: a false number.**

Not a review comment. Found by rendering the page to check the alignment,
which is the only reason it was found at all.

**`≥` was being dropped from the PDF in all eight places it appears.** Latin
Modern has no glyph for U+2265 and **xelatex discards it silently** — no
warning, no error, no box. The built PDF read *"reproduced at 100 spikes"* for
*"≥100 spikes"*, *"101 spikes reproduces 307"* for *"≥101"*, and *"100 leaves
no residual"* for *"≥100"*. H1's rule is a threshold; the PDF stated it as a
bare count. **Anyone reading the PDF would have read a different claim from
the one the claim set makes.**

**Changed.** `\newunicodechar` mappings for `≥ ≤ ≈ ≠ ±` in
`scripts/manuscript-header.tex`; `build_manuscript_pdf.py` now diffs the
source's non-ASCII character set against the built PDF's text layer and
**exits non-zero** rather than shipping a PDF with dropped characters;
`START-HERE.md` rule 10.

**Why it is logged here rather than as housekeeping.** The verifier passed, the
draft was correct, and the PDF looked clean. The defect existed only in the
artefact a reader would actually receive, which is a class of error nothing in
the repository was checking for. **The lesson is that "0 failures" describes
`draft/`, not the PDF.**

**Verifier.** 0 failures, 1 warning (em dash pass, deferred under 8b). Glyph
check: 0 lost.

---

## 2026-08-12

### A1 — §4 scope disclaimer: chronic implants

**Span.** `04-discussion.md`, the "what this paper does not claim" list:
*"It says nothing about chronically implanted arrays, where electrode failure is
well documented and mechanistically distinct."*

**Defect named by TSRB.** The wording implies the restriction is principled when
the truth is that the work has not been done. Requested a change in tonality and
reasoning, noting an intention to work on chronic *in vivo* implants after this
paper.

**Finding.** The objection is stronger than a tone problem. The old wording
implies the boundary is a matter of kind, which is quietly self-serving. The
conflation identified in this paper follows from defining "active" by a rate
threshold, and nothing in that is specific to culture, so a chronic recording
would carry the same ambiguity with genuine electrode loss present in addition
to it rather than in place of it. **Restating the boundary as untested rather
than principled is a harder limitation, not a softer one**, which is what §5's
own governing principle asks for.

**Changed.**

- `04-discussion.md` — bullet rewritten; scope-not-principle reasoning added;
  closes *"an open question, and one we intend to take up."*
- `05-limitations.md` — the same defect was present and worse (*"Nothing here
  bears on that literature"*). Rewritten to match, **without** the forward
  clause: Limitations states the limitation, it does not advertise.
- `CLAIM-SET-FROZEN.md` §5.4 — amended to require the untested framing.

**Preserved deliberately.** The concession that chronic arrays genuinely do
fail, by gliosis, encapsulation and mechanical failure. `CLAIM-SET-FROZEN.md`
§5.4 mandates it, and it is what protects the paper from an *in vivo* reviewer.
Trading it for forward-looking language would swap protection for ambition.

**Category.** Mostly **Choice**. One sentence is flagged for overrule: *"A
chronic recording would therefore carry the same ambiguity, with genuine
electrode loss present in addition to it rather than in place of it."* That is
an inference from the structure of the metric, not a measurement. Both
paragraphs survive without it.

**Verifier.** 0 failures. Em dash density 7.6 → 7.3; `05-limitations.md` reached
3.5 per 1,000, the first draft file under the 4.15 field maximum.

**Cut count: 0.** Noted, not excused. See the header.

---

### A0 — housekeeping swept in the same pass

Not review comments; recorded so the pass is not re-run over them.

- **§4 drafting note** demanded "a chapter and page, not a whole-textbook
  citation" for the two `[CITE]` markers. Stale: Niedermeyer's proved
  unobtainable and the replacement is deliberately cited whole. Updated.
- **A6b closure propagated** to `05-limitations.md` limitation 1,
  `CLAIM-SET-FROZEN.md` §5.1 and its header, `OPEN-ENDS.md` O4 and the ledger.
  The manuscript had been asserting the noisy-electrode flag was undefined after
  it had been defined.
- **`[MODEL AND VERSION]` filled in all three slots: "Claude Opus 5,
  Anthropic".** Confirmed by TSRB across every session; constant throughout, so
  §6's "used throughout this work" and §2.10.1's single-pass claim take the same
  string. The placeholder asked for a model *and* a version; the desktop app
  exposes only the model name, so the model name is the complete available
  answer and nothing was invented to look more precise. **`START-HERE.md` §7
  item 1 closed in the same pass.**
- **Placeholder count reached zero.** `verify_draft_claims.py`: 0 failures,
  1 warning, and the only remaining warning is the em dash pass deferred under
  8b. Every citation and every placeholder in `draft/` is now resolved.
