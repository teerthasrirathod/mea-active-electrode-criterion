# FROZEN CLAIM SET

> **SPLIT 12 August 2026 — read `notes/DECOUPLING.md` before using this page.**
> The reanalysis and the survey are now two papers. **Paper 1 keeps H1–H4, S5,
> M1–M3, A1–A2. Paper 2 takes S1–S4, S6–S8, P1.** S5 moves to Paper 1 because it
> is documented tool defaults, not a survey result, and it is what lets Paper 1
> make a field-level claim without the sample. **No claim was withdrawn, added
> or altered by the split** — the set below stands exactly as frozen, and is
> partitioned rather than revised.

**Frozen 10 August 2026, after D3 closed. Amended same day** to add S7 and S8, the two pre-registered analyses that had not been run when this page was first written — see the open-ends register. ~~Every gate is shut except A6b, which
needs Tampere and is a stated limitation either way.~~

**Amended 12 August 2026: every gate is now shut.** A6b was answered by
F. E. Kapucu (personal communication, 12 Aug) and moves `OPEN` → `PRIMARY`
(pers. comm.) in the ledger; O4 is closed. **No claim on this page changed as a
result.** H1's 336/336 is arithmetic on the published lists and never depended
on why an electrode was on one. What changed is limitation 1 below, which is now
a disclosed-and-answered limitation rather than an open one. **A7b remains the
only open ledger row and is bounded to 0–3 channels per recording, so nothing is
waiting on it.**

**How to use this document.** Nothing goes in the paper that is not on this page.
If drafting produces a sentence that is not here, either it is wrong or this page
needs amending — and amending requires evidence, a ledger row, and a dated note
saying what changed. **Do not amend it because a sentence would be more
exciting.** Three claims died today for exactly that reason.

Every claim below carries its ledger row. Every number is reproducible from
published files by a script in `scripts/`.

---

## 1. The paper in one sentence

> The number of active electrodes is not a measurement of electrode function. It
> is the firing-rate distribution counted against a threshold that the field
> chooses arbitrarily, does not usually report, and — when it does report it —
> spans three orders of magnitude.

## 2. Title — DECIDED 17 August 2026

> **An undeclared free parameter underneath *in vitro* microelectrode array
> metrics**

Candidate 2, unchanged. **The only candidate that survived the decoupling
untouched, because it never named the survey.**

| | candidate | status |
|---|---|---|
| 1 | *The active-electrode count is a thresholded restatement of firing rate* | true and available; states the finding rather than the problem |
| 2 | *An undeclared free parameter underneath in vitro MEA metrics* | **CHOSEN** |
| 3 | *What "active electrode" means: a reanalysis and a survey* | **WITHDRAWN 17 Aug — describes Paper 2** |

> **How this was nearly missed.** The drafted title read *"The active-electrode
> count is a thresholded restatement of firing rate: **a reanalysis and a
> survey**"* — a subtitle added at drafting on 11 Aug that was never a claim-set
> candidate. It survived the entire strip. `verify_draft_claims.py` checked that
> the title decision was still *flagged as pending*, which passed, and had no
> opinion about whether the candidates still described the paper. **The most
> visible sentence in the document was the last thing anything was checking.**
> The verifier now fails if any title candidate names a survey.

---

## 3. THE CLAIMS — everything the paper asserts

### 3.1 Headline — the metric is arithmetic on a free parameter

**H1. The published active-electrode count is exactly reproduced by a spike-count
rule.** `nae` = electrodes with ≥100 spikes in the recording, after removing that
day's noisy-electrode list. **348/348 published values reproduced exactly** across
`hPSC_MEA1` (114), `hPSC_MEA2` (114) and `Rat_MEA1` (120) — three plates, two
species, zero misses. **≥100 is unique over every integer from 1 to 400.**
*(B2, A6c, A6d. `verify_all.py`, `verify_reproduction_348.py`)*

> **AMENDED 19 August 2026. Previously 336/336 over 108 rat cells.**
> `Rat_MEA1` publishes 120 well–timepoint values, 12 of them bare `NA` at DIV 2
> and DIV 7. Those 12 were treated as unrecorded and dropped. **New ledger row
> A6d:** all 12 wells *were* recorded — 63–64 electrodes producing spikes, 2,254
> to 2,929 detected — and the rule returns exactly zero for each, so bare `NA`
> in this table denotes **zero active electrodes**, not a missing recording.
> Established by `verify_rat_na_cells.py` (exit 0, `notes/rat_na_cells.txt`) and
> reproduced independently by `verify_reproduction_348.py` (exit 0,
> `notes/reproduction_348.txt`).
>
> **The result did not change; the convention did.** Run on the old basis, the
> new implementation returns the frozen numbers exactly — 336/336, ≥101 → 307,
> ≥99 → 303, and 222/222 → 216/222. Two independent implementations, both
> conventions, identical answers.
>
> **Consequent figures, all recomputed rather than rescaled:** ≥101 reproduces
> **319 of 348** (was 307 of 336); ≥99 reproduces **314** (was 303); the
> noisy-exclusion necessity test is **234/234 → 227/234** (was 222/222 →
> 216/222).
>
> **Two numbers deliberately unchanged.** §3.4's *"222 independent estimates"*
> stays 222 — the duration recovery inverts a mean firing rate and a cell with
> no active electrodes has no `n_active` to divide by. §3.2's `315 → 108` is
> `hPSC_MEA2`'s electrode count at DIV 66, not a cell count.
>
> **And it repairs a sentence that was wrong.** §3.1's *"the exclusion removes
> six electrode-recordings on `hPSC_MEA1` and two on `Rat_MEA1`"* is six and
> **one** on the 108-cell basis; the second rat one is `B2_32` at DIV 7, inside
> an `NA` cell. One sentence had already adopted the 120-cell basis while the
> rest of the paragraph used 108. It is correct as written under this
> amendment.

**H2. Under the analysis package's own documented default, the developmental
decline does not exist.** At meaRtools' `elec_min_rate` (1 spike/min), **381–384
of 384 electrodes are active at every one of nineteen timepoints**. At the
study's 10 spikes/min the same spike times give 321 → 103, a 68% fall.
*(B4′, B5. `day3_threshold_landscape.py`)*

**H3. H2 replicates on a parallel plate.** `hPSC_MEA2`, same differentiation
batch, recorded in parallel, descriptor explicitly licenses pooling.
**Pearson r = +0.986** across 19 timepoints at 10/min. Decline: MEA1 −68%,
MEA2 −66%. At 1/min: −0.5% and **0.0%**. *(A10)*

**H4. On the rat plate the two criteria differ by up to 109×** at DIV 2. *(B5)*

> **Footnote worth keeping:** at 1/min the between-plate correlation collapses to
> r = +0.29, because both plates sit pinned at the 384 ceiling. The metric
> carries no signal at all under the package default — the same point from the
> other direction.

### 3.2 The field has no convention — the survey

**S1. Fewer than half of eligible papers state the criterion.** Pre-registered
survey, **n = 100 drawn from a measured population of 457**, seed 20260810,
reproducible. **23 of 51 eligible papers state one: 45.1%, 95% CI 33.0–57.2%.**
**Always report the interval, never the point estimate.** *(D3)*

**S2. Among those that do, stated rates span 0.042 to 60 spikes/min — 1,429×.**
From *"at least 30 spikes in 12 h"* to *"spike rate above 1 Hz"*. *(D3)*

**S3. There is no modal convention.** The most common value (5/min) accounts for
**5 of 23**. **No value reaches a quarter of the papers that state one.** *(D3)*

**S4. One in five stated criteria is not a firing-rate rule at all** — a
75th-percentile-of-the-plate rule, an SNR rule, two raw spike counts, and one
paper using *"spike frequency > 0"*. **A percentile rule cannot be converted to
spikes/min even in principle.** *(D3)*

**S5. Four independent sources, four different values, none citing the others:**
meaRtools **1/min**, Axion Neural Metric Tool **5/min**, MEA-ToolBox **6/min**
(0.1 Hz), Kapucu **10/min**. MEA-NAP states **0.6/min and 6/min in the same
paper**, switched per dataset. *(B6, B6b)*

> **AMENDED 19 August 2026 — the Axion row is now primary, and `D3` is gone
> from the citation.** The 5/min value was evidenced by four user studies, one of
> which reported it as an *average* rather than a minimum. Both vendor documents
> have since been retrieved and are open: the **Neural Metric Tool User Guide
> v4.1 (July 2023) documents no default** — the criterion is a field the user
> fills in — and **Axion states 5 spikes/min in its own application note**
> (Streeter, Sullivan, Millard; Methods). **New ledger row B6b.**
>
> This matters beyond provenance. S5 sits in Paper 1 because it rests on tool
> documentation rather than on the survey, and it was cited to `D3`, which *is*
> the survey. Paper 2 is now out of Paper 1's only field-level claim.
>
> **The four sources, the four values and the 10× span are unchanged.** What
> changed is that they are no longer four of a kind: two are tool defaults, one
> is a vendor's stated value over a tool that has no default, one is a study's
> choice.

> **AMENDED 11 Aug 2026 under pre-registered rule R4 of
> `scripts/o2_epa_criterion.py`.** The 5/min row previously read *"US EPA NFA"*.
> That attribution was never primary-confirmed. The run retrieved **zero**
> EPA-authored full texts: Frank et al. 2017, both editions of the Shafer
> protocol chapter, the 2019 Shafer book chapter and both Brown papers all
> return `isOpenAccess = N`. R4, fixed before the run, directs dropping the row
> and using the Axion Neural Metrics Tool value, which four independent papers
> confirm at 5/min. **Four sources and four values are unchanged; only the
> attribution moved, and it moved from unsourced to four-way sourced.**
>
> **State the reason precisely.** The EPA sources are *closed access*, not
> silent. **Nothing in this paper may say or imply that the EPA does not state a
> criterion** — that is a different claim and it has not been tested. O2 is
> closed as *unreachable*, not as *answered*.

**S6. "Active electrode" carries at least four incompatible meanings** in this
literature: electrodes exceeding an activity criterion; the physical electrodes
on the array (*"59 titanium nitride active electrodes"*); fEPSP-responsive
channels; and electrodes whose spikes merely clear the detection threshold with
no rate rule. *(D3, from the rejects)*


**S7. Only a quarter of eligible papers state both a threshold and a recording
duration.** 13 of 51 (**25.5%**). Of the 23 that state a threshold, only **13
(57%) also state a duration**. *(D3, pre-registered analysis 3)*

> Why this matters and why it is novel: **"10 spikes/min" and "100 spikes" are
> the same rule only for a 600 s recording.** A raw spike count without a
> duration is not reproducible at all, and a rate without a duration cannot be
> checked against a raw count. **Three of the criteria found are raw counts**
> (*"at least one spike"*, *"more than two action potentials"*, *"30 spikes in
> 12 h"*), so for those papers the duration is not a nicety — it is the whole
> rule. No existing critique appears to make this point.

**S8. Nearly a third of eligible papers feed the active-electrode count into a
normalised or graph-theoretic metric, and half of those never define it.**
15 of 51 (**29.4%**) use it as a denominator (per-active-electrode rates,
weighted mean firing rate) or in a graph/percentage-of-active rule. **7 of those
15 (47%) state no criterion at all** — the parameter propagates into a reported
result that nobody can reconstruct. *(D3, pre-registered analysis 4)*

### 3.3 The parameter propagates

**P1. Active-electrode counts feed downstream metrics that are then reported as
biology**, in papers that never define the term:
- graph **node count** — *"Nodes were defined as the number of active electrodes
  participating in at least one edge"* (PMC12929631)
- **primary maturation readout**, R² > 0.9 (PMC11440061)
- **network-burst definitions** — *">35% of the active electrodes"* (PMC10672180),
  *">30% of the active electrodes"* (PMC8418338)
- MEA-NAP defines graph **"network size"** as the active-electrode count

### 3.4 Mechanism — why the count moves when nothing fails

**M1. The spike detector applies no absolute amplitude criterion at any stage.**
Stage 1 thresholds at **4.5 times the estimated noise standard deviation of each
channel**; stage 2 (SWTTEO) is **rank-matched to stage 1's count**, so it must
return that many events. Nothing in the pipeline can reject a recording for being
noise. *(A5b, descriptor Methods verbatim)*

> **Stated in §2.1 from 17 August 2026.** Until then M1 was asserted in §3.6 and
> §4.2 — Results and Discussion — and **appeared nowhere in Methods**, while
> §3.6 cited *"(§2.1)"* for it. The cited section existed, so
> `check_paper_partition.py` passed; it was checking the address, not the
> delivery. **A claim that two sections rest on was never introduced.**
> The checker now verifies that a cited section contains what the citation
> promises (`[5b]`, statuses `HOLLOW` and `DANGLING`).

**M2. The rate denominator is data-dependent.** meaRtools' firing rate divides by
the **plate-wide span from first to last spike**, not the recording duration —
matched to 0.000000 s in 29/29 recordings. A quieter plate inflates its own
rates. **On these plates the effect is negligible (<0.06%); state the mechanism,
not an effect size.** *(B8)*

**M3. The criterion sits at the 99th percentile of pharmacologically silenced
electrodes.** Pooled across two TTX plates, **n = 416** silenced electrodes:
p99 = **9.69 spikes/min** against a criterion of 10. **4 of 416 (0.96%)** silenced
electrodes would be scored active. *(C7′)*

**M4. A channel that gets noisier reads as quiet — adaptive-threshold
suppression.** *(added 16 Aug 2026, session 2. Was a limitation in §5 and a
passing remark in §4.5; it is a mechanism, and it belongs here with M1–M3.)*

Stage 1 of the detector thresholds at **4.5 × each channel's own estimated noise
SD**, and stage 2 is rank-matched to stage 1 *(M1, A5b)*. That threshold is
therefore **self-normalising**, with two consequences that pull opposite ways:

- **the false-positive rate is invariant to absolute noise level** — a noisier
  channel does not emit more spurious events, because its bar rose with its
  noise;
- **the true-positive rate is not** — real spikes have an amplitude set by the
  biology, so a higher bar excludes more of them, and stage 2 cannot restore
  what stage 1 dropped.

**So elevated noise suppresses a channel's detected count while leaving its
noise output unchanged, and under a rate criterion that channel is counted as an
electrode that stopped working.**

**Measured, from spike times alone.** Electrodes the study flagged noisy sit in
the bottom decile of firing rate for their own recording day: **36 of 47** on
`hPSC_MEA1` (77%), **40 of 44** on `Rat_MEA1` (91%), **76 of 91 pooled (84%)**.
Median flagged rates **2.70 and 2.65 spikes/min** against **plate median rates of
9.9 and 33.4 spikes/min** — a flagged electrode fires at about a quarter of the
typical rate on the human plate and a thirteenth on the rat plate. The minor mode
is **exactly two electrodes per plate** at the top, matching the glitch and
post-hoc outlier passes. *(A6b, `characterise_noisy.py`,
`threshold_suppression.py`)*

> **Unit trap, recorded because it produced a false sentence on 16 Aug.** The
> flagged medians are **spikes/min**; `characterise_noisy.py` reports plate
> medians as **spikes per 600 s** (99 and 334 over all electrodes; 100 and 342
> over unflagged only). Dividing one by the other gives a spurious ~40× and the
> draft carried *"roughly a fortieth"* for several hours. **Always convert
> before comparing.** The true ratios are 4× and 13×.

**Corroborated independently.** Kapucu (pers. comm.) gives the flag's provenance
as visual inspection at acquisition for noise, glitches *"which would cause
misdetection of spikes"* and baseline drift, plus a later outlier pass over
*"extremely high spiking activity"*. **Neither party knew the other's answer**;
the stated provenance matches the measured bimodality mode for mode.

**Scope, and it is narrow.** The mechanism is documented for this detector and
inferred for this dataset. **It is not a controlled demonstration** — no spikes
were added to a channel to watch its count fall. It is a documented rule plus a
distribution that the rule predicts. Write it that way.

> **HAZARD — do not let M4 revive a withdrawn claim.** *"16–53% of
> counted-active electrodes fire within noise"* died on 10 Aug as an artefact of
> the ceiling statistic. M4 needs **no within-noise fraction at all**; it rests
> on the bottom-decile counts and the flagged-electrode medians. **Any sentence
> of the form "N% of active electrodes are noise" is the withdrawn claim
> returning and must be cut.**

### 3.5 What the dataset's own records show

**A1. The study's own hardware-failure record shows no attrition.** Upper bound
on `InactiveChannels`: **0 at 18 of 19 recordings on MEA1, 0 at 19 of 19 on
MEA2**, 0–3 of 768 on rat. *(A7c)* — **This answers the question the project
started with.**

**A2. Three anomalous recording days are session events, not culture events.**
Both parallel plates collapse across DIV 48/51/56 and recover at 59 (MEA1
143/69/45→133; MEA2 124/60/55→132). Two separate plates cannot do that
independently. **The expLogs for exactly those dates are unpublished.** *(A12, A9)*

**A2b. The collapse is not electrodes falling silent.** *(added 16 Aug 2026,
session 2, from per-electrode distributions; extends A2 rather than replacing
it.)* On DIV 51 and 56 the active-electrode count falls by roughly two thirds on
both plates while **not one electrode on either plate stops producing spikes** —
384 of 384 present, both days, both plates. **The loss is confined to the top of
the distribution.** Against the DIV 45 baseline, the lower quartile retains
**79–88%** of its rate while the ninetieth percentile retains **9–14%**. The
distribution does not shift downward; **it collapses onto a floor that does not
move** — **from DIV 42 onward** the bottom decile sits between **29 and 34 spikes
per 600 s on every recording of both plates**, baseline and anomaly alike, i.e.
**2.9–3.4 spikes/min against a pharmacologically silenced median of 3.30**
*(M3)*. That stable floor is what M4 predicts: a self-normalising threshold holds
false-positive output constant while consuming true positives.
*(`threshold_suppression.py`, checked by `verify_threshold_suppression.py`)*

> **Two corrections made on 16 Aug, both within the session, both by the second
> implementation.**
>
> **Scope.** The floor claim first read *"on every day of the experiment"*.
> **False.** The bottom decile falls from 56 and 62 spikes per 600 s at DIV 3 to
> the low thirties by DIV 42, and is stable only across the late phase. Confined
> to DIV 42–66, the window the comparison needs. The error came from
> generalising a seven-row printout to nineteen recordings.
>
> **Range.** It then read 30–33, taken from `hPSC_MEA1` alone. `hPSC_MEA2` runs
> **29–34** over the same window. Both plates, or neither.
>
> **Precision.** The §3.6.1 ratios are **convention-dependent in the second
> decimal**. Linear interpolation and nearest-lower-sample differ by up to 0.017.
> **Do not quote a ratio from that table to 2 dp as though it were exact.** The
> pattern — lower quartile 0.77–0.88, ninetieth percentile 0.09–0.16 — holds
> under both.

**What A2b does not establish.** Spike times alone **cannot separate** *"the
threshold rose and ate real spikes"* from *"the cultures were genuinely quieter
that day"*. Both produce this signature; separating them needs amplitudes, and
the `.h5` files are unreachable *(§2.2)*. **The claim is the structural one — no
electrode fell silent, and the residual floor matches the silenced floor — with
M4 as a sufficient explanation, not the demonstrated one.** State it that way or
not at all.

---

## 4. WITHDRAWN — these must never appear

Five claims died under test. **If any of these reappears in a draft, the draft is
wrong.**

| withdrawn | why it died | date |
|---|---|---|
| ~~No electrode ever fails~~ | rested on "≥1 detected spike = functioning interface". TTX ceiling refuted the premise | 8 Aug |
| ~~Interface attrition is ~zero~~ | inherited the above | 8 Aug |
| ~~meaRtools' criterion is 5 spikes/min~~ | **false.** Package default is 1/min (`elec_min_rate=0.0167`; vignette *"a lenient 1 spike in 60s"*) | 10 Aug |
| ~~Stated (`>`) and implemented (`>=`) rules differ by one spike~~ | artefact of assuming exactly 600.000 s. Derived duration 599.689–599.997 s makes both rules `>=100` | 10 Aug |
| ~~16–53% of counted-active electrodes fire within noise~~ | **artefact of the ceiling statistic.** Same data give 0% (p95), 0% (p99), 53% (max), 98% (max incl. one bad well) | 10 Aug |

**A7c is not a revival of C3/C4.** C3 claimed electrodes do not fail, inferred
from detected spikes. A7c reports what the *experimenters' own malfunction log*
contains. Different evidence, different claim. Keep them visibly separate.

---

## 5. LIMITATIONS — state these before a reviewer does

1. **"Noisy electrode" is defined only outside the published record** (A6b).
   **RESOLVED 12 Aug.** The flag is load-bearing for H1's 336/336, and the
   descriptor never says how membership was decided. Flagged electrodes are
   overwhelmingly near-silent (median 2.6/min), which is the opposite of what
   the name implies. **Kapucu (pers. comm., 12 Aug): marked by eye during
   recording on baseline noise, glitches and drift, plus a post-hoc outlier
   pass. Two-stage provenance; the second stage is outcome-dependent.** The
   stated rule and the measured bimodality agree and were reached
   independently. **State it as answered, cite it as personal communication,
   and keep it in this list**: it is not reader-verifiable, and the flag is a
   bench judgement of signal quality rather than a calibrated measure of
   electrode condition.
2. **The noise ceiling does not transfer as a maximum** (C6). Rat max 216.40/min
   vs human 17.70 — traced to two electrodes in one well. The *distribution*
   agrees to p99. **Report percentiles, never a maximum.**
3. **29% of the survey draw had no machine-accessible full text.** The population
   is open-access papers; a criterion in a paywalled Methods section is invisible.
   **This biases toward better reporting, so S1 is conservative.**
4. **In vitro only.** Chronically implanted arrays genuinely do fail. Say so
   early — a reviewer from that literature will otherwise assume the claim
   overreaches. **Amended 12 Aug: state the boundary as untested, not as
   principled.** The conflation follows from defining "active" by a rate
   threshold, not from anything specific to culture, so the honest form is "we
   did not examine chronic preparations", not "this does not apply there". That
   is a harder limitation, not a softer one: it concedes the confound may reach
   further than was tested. **The concession that chronic arrays really do fail
   stays exactly as it is** — it is what protects the paper from the in vivo
   reviewer. Carried in §4 (with a forward-looking clause) and §5 (without one).
5. **One dataset for the reanalysis**, though three plates and two species.
6. **A7b unresolved** — whether `InactiveChannels` was regenerated per recording.
   Bounded to 0–3 entries, so nearly moot, but not answered.

---

## 6. Figures

| # | content | script | status |
|---|---|---|---|
| 1 | **Four** criteria × three plates; decline vanishes at package default | `day3_threshold_landscape.py` | **done, amended 28 Aug 2026** |

> **Amendment, 28 August 2026 — figure 1, three criteria to four.** §2.5 documents four criteria and the figure carried three, so §3.2's table read *"four documented sources"* above three rows. Found by the Methods-against-Results loop audit (`notes/LOOPS-M2R-28AUG.md` L-3). **Evidence:** MEA-ToolBox's 6 spikes/min is 60 spikes over the ~600 s recording, by the same arithmetic already used for 1, 5 and 10 per minute. Recounted on `hPSC_MEA1`: **344 electrodes at DIV 3, 164 at DIV 66, a 52% decline.** The computation was validated by reproducing the three published rows from the same code path first — 384/382, 355/201 and 321/103, all exact. No new claim is made: the recount falls under the existing claim that the same spike times were recounted under each documented criterion. What changed is that *each* now means four rather than three.
| 2 | The 23 stated criteria, log axis, 0.042→60/min, rule-kind coloured | *to write* | from `classification_n100_FINAL.csv` |
| 3 | Silenced-electrode distribution vs the 10/min criterion, both TTX plates | `ttx_ceiling_two_plates.py` | data done, figure to write |
| 4 | MEA1 vs MEA2 replication, r = 0.986 | *to write* | — |

---

## 7. What the paper does NOT claim

- Not that Kapucu et al. made an error. **They documented their choice.** The
  problem is that four careful groups made four different choices and none
  noticed the others.
- Not that the active-electrode count is useless — it works where activity is
  far above any plausible criterion.
- Not that electrodes never degrade — only that *this* metric cannot detect it,
  and that these plates' own malfunction logs record none.
- Not anything about *in vivo* arrays.

**Tone rule for drafting:** every critical sentence must be one you would be
comfortable reading aloud to the authors of the dataset. They made the data
public, documented their threshold, and published the noisy-electrode lists that
made half this analysis possible. **The paper is only possible because they were
unusually open, and it should say so.**
