# Step-1 rubric review of `tbs_proposal_form.md` (version 1, 2026-10-09)

This review follows the TB-Science proposal rubric (`task-proposal.md`) and
judges the form text alone, as the bot would. The background note
(`tbs_proposal_lund_unfolding.md`) was read only to avoid inventing facts in
the fixes. Negatives carry IDs (V1, W2, ...) that the "Concrete fixes" section
uses.

---

## Scientific Domain
**Domain:** Physical Sciences
**Field:** Physics
**Subfield:** Experimental particle physics (jet substructure, detector unfolding)

## Problem Statement
The agent gets half of the ALEPH 1994 Pythia 6.1 full simulation at √s = 91.2
GeV, with particle-level and detector-level particles paired event by event
(plus particle-level events that fail the detector selection). It also gets
particle-level samples from Pythia 8, Herwig 7 and Sherpa, the sizes of three
detector variations (track efficiency, momentum scale, momentum resolution),
and one development pseudo-dataset with its truth. It must build a frozen
pipeline, `run.sh <dataset_dir> <output_dir>`, that takes a detector-level
dataset and returns the particle-level primary Lund-plane density
ρ = (1/N_hemispheres) dN_splittings / d ln(1/Δθ) d ln k_t (thrust hemispheres,
charged particles, e⁺e⁻ Cambridge declustering along the harder branch) in a
fixed binning, with a full covariance, as a HEPData record. The method is free.
The verifier runs the pipeline offline on about 10 withheld pseudo-datasets
built from the other half of the simulation, each reweighted at particle level
to a different true model and given a shifted detector response. For each
dataset it computes a Gaussian log score of the exact truth under the
submitted density and covariance, minus the reference's score. Pass: mean
score difference above a cut, and no dataset with χ² p-value below 10⁻³.

## Verifiable

**Positives**
- The truth is exact: every pseudo-dataset comes from simulation, so its
  particle-level density is known, with no human or LLM judgement.
- The score is a proper scoring rule. It punishes both bias and wrong
  uncertainty, which is the right target for an unfolded result with a
  covariance.
- Scoring against the expected density (not the realised one) is correct for
  an unfolded measurement, and the truth's own statistical error enters the
  score.
- The plan tests the verifier against the oracle, `nop` and six named gaming
  attempts, including scaled covariances (0.5, 3) and the training prior.
- Hard failures (format, non-positive-definite Σ, time-outs) are mechanical.

**Negatives**
- **V1.** The form gives no pass cut: "above a cut set from the reference and
  an independent expert method" is neither a number nor a rule. The bot
  rejected #993 for this same gap (undefined pass tolerance).
- **V2.** The verifier re-runs the agent's pipeline, so ML seeds and GPU
  non-determinism change the output from one verifier run to the next. The form
  does not show that the oracle passes on repeated runs. With the cut set near
  the reference, a correct but less precise method (e.g. binned IBU against
  OmniFold) may fail. The rubric asks for "all-but-guaranteed" passes for
  correct solutions.
- **V3.** The rule "no dataset with p < 10⁻³" over 10 datasets fails a
  perfectly calibrated method about 1% of the time (1 − 0.999¹⁰), and more in
  sparse corners of the plane, where Poisson counts break the Gaussian χ². The
  form sets no minimum bin population.
- **V4.** The positive-definite check is ambiguous. A bootstrap covariance
  with fewer replicas than bins is singular; adding the truth's statistical
  covariance would make it positive definite. The form does not say which Σ is
  checked, or cap the condition number, so log det Σ and Σ⁻¹ can make the score
  unstable.
- **V5.** No numbers show that the score separates correct from subtly wrong
  pipelines. With ~10 datasets of unstated size, dataset-to-dataset spread in
  the relative log score could swamp the gap between, say, the reference and a
  pipeline with no prior uncertainty.
- **V6.** (Minor.) The truth uses the whole withheld half, which holds the
  dataset's own events, so the truth error and the data fluctuation are
  slightly correlated; the form adds them as if independent.
- See also D1: a template-fit shortcut could out-score honest unfolding on
  generator-truth datasets, which would make the score rank the wrong thing.

**Judgement:** Accept

## Well-Specified

**Positives**
- The observable is outlined with the right ingredients (thrust hemispheres,
  charged particles, e⁺e⁻ Cambridge, harder-branch declustering, per-hemisphere
  normalisation), and the agent gets a reference implementation in Python and
  Rivet.
- The interface (`run.sh <dataset_dir> <output_dir>`) and hard limits are
  stated, and the form is short.
- The agent may pick any method, which keeps the instruction free of steps.

**Negatives**
- **W1.** The form says the agent is "not [told] the formula or the cut".
  The rubric requires that the description "completely describes what the
  verification algorithm will look for. Nothing is left up to guessing." Two
  people writing verifiers from this instruction would set different cuts and
  pass different submissions. Hiding a proper scoring rule also buys nothing:
  under it, honest reporting already maximises the expected score.
- **W2.** "A fixed hadronic event selection" is not stated, at either level.
  Also missing: which particles count as stable and charged; any momentum or
  polar-angle acceptance at particle level; whether the thrust axis uses all
  particles or charged only; the formulas for Δθ and k_t (energy or momentum;
  min(E_a, E_b) sin Δθ or another form); what "harder" means; how
  N_hemispheres is counted; and which of the two reference implementations
  defines the target if they differ. Undefined selections were the other half
  of the #993 rejection.
- **W3.** "In a given binning": no binning. The number of bins sets the
  dimension of Σ and the scale of the log score.
- **W4.** "A HEPData-format record" has no schema: file names, bin order in
  2D, and how the covariance is stored.
- **W5.** The range of truth shifts is unstated ("Pythia 8 variants",
  "reweighted regions of the plane" of unknown size). The score punishes both
  under- and over-coverage, so the agent must guess how far truths stray from
  training; one development dataset is a single draw. For the detector, "drawn
  inside the stated systematic envelope" gives no distribution (uniform?
  Gaussian with the stated width?), and the form does not say how each
  variation acts on tracks.
- **W6.** Verify-time conditions are vague: is the training simulation
  present in the verifier image (an OmniFold pipeline needs it per dataset)?
  "About 10 minutes" and "about 10 datasets" are not exact. Events per dataset
  are not given. Network access during the agent session is not stated.
- **W7.** (Minor.) "Simulation uncertainties" could mean simulation
  statistics or model (prior) dependence; the score depends on both.

**Judgement:** Reject (as written; every gap is fixable with a few sentences,
and a lenient reading would give Uncertain)

## Solvable

**Positives**
- The task replicates a known kind of measurement: Lund-plane unfolding exists
  in ATLAS (arXiv:2004.03540), and archived-ALEPH unfolding exists for thrust
  (arXiv:2510.22038).
- The pseudo-data keep each event's real detector response and change the
  truth only by reweighting, so the inverse problem is well posed by
  construction.
- The author has working OmniFold and IBU unfolding code and plans closure,
  stress, coverage and real-data checks.
- Data are public (CC BY 4.0) and the software stack is standard and open.

**Negatives**
- **S1.** The form shows no result on ALEPH pseudo-data: no closure, stress or
  coverage numbers for the reference. It says only that the reference "reuses
  the author's thesis unfolding code".
- **S2.** The cut is built from the reference and "an independent expert
  method", but the form does not say who writes the second method or whether
  it exists. If the same author writes both, "independent" is weak, and there
  is no evidence yet that a second route clears a cut set near the first.
- **S3.** Budget: about 10 minutes per dataset on 4 CPUs and one GPU must
  cover unfolding and covariance. OmniFold with bootstrap ensembles seldom fits
  that; the form claims the GPU makes it fit but gives no timing. It also
  does not address whether TB-Science runners provide a GPU; if not, ML
  pipelines fail. (#427 drew "Uncertain" on Solvable for budget alone.)
- **S4.** The reference's own wall time on the stated hardware is not given,
  so no one can tell whether building, training and validating the pipeline
  fits the 4-hour session.
- **S5.** Agent 4 h plus verifier up to 2 h is 6 h. The author's notes cite a
  6-hour runner limit from #2267; the form does not show it stays under it.
- **S6.** The form hints that "ALEPH archive terms" may concern maintainers
  but does not state them, which invites a "publicly available?" question. It
  should state that the CC BY 4.0 release allows redistribution.

**Judgement:** Uncertain

## Difficult

**Positives**
- Unfolding a multi-emission 2D density with a covariance that survives a
  change of true model and of detector response is PhD-level work; the stated
  traps (fakes and efficiencies at splitting level, prior dependence,
  simulation-statistics bootstrap, normalisation) are real.
- An expert estimate of one to two weeks is credible.
- Scoring calibration on shifted truths targets a known weak point (honest
  uncertainties), not a trick.

**Negatives**
- **D1.** Template shortcut. The agent gets particle-level Pythia 8, Herwig 7
  and Sherpa samples, and the truths are reweightings of Pythia 6.1 to those
  same models. An agent can reweight its own training half to each provided
  generator (as the author does), fold each through the response, pick the one
  that best fits the detector-level data, and return that model's density with
  a small covariance. On generator-truth datasets this needs no unfolding and
  could beat the reference. Only the "reweighted regions" datasets defend
  against it, and the form does not say how many there are. The gaming list
  does not include this attempt.
- **D2.** Much is scaffolded: exact observable code, systematic sizes,
  alternative generators, a development truth. What remains (2D IBU with
  bootstrap and prior variation) follows a public recipe (ATLAS) and a public
  agent-made pipeline on the same data and observable (JFC, Zenodo 20693601).
  The form does not say whether the agent has network access, or whether reuse
  of the JFC code is banned and checked.
- **D3.** Target pass rate "one third or lower" is above the benchmark's
  stated 10–20% at release, and no frontier runs exist yet.
- **D4.** One listed failure is doubtful: "unfolding per hemisphere instead of
  per splitting". Event-level OmniFold reweights whole events, and the
  splitting density computed with those weights is correct; per-event
  unfolding is a valid method. A domain reviewer will doubt the difficulty
  argument if it lists a correct method as a failure. The real trap is binned
  unfolding that treats splittings as independent entries.
- **D5.** Part of the difficulty comes from withheld information (formula,
  cut, size of truth shifts; W1, W5), not from the science. That is hard for
  the wrong reason.

**Judgement:** Accept

## Scientifically Grounded & Interesting

**Positives**
- Unfolding with honest uncertainties is the core of every differential
  measurement; theorists and generator authors use the result.
- The Lund plane separates perturbative from non-perturbative QCD and has no
  collaboration measurement at LEP; e⁺e⁻ gives a clean, colour-singlet
  baseline next to the ATLAS and CMS pp results.
- Real archived full simulation, real generators, and a real research code
  base. Choosing what to propagate (prior, detector, simulation statistics)
  needs domain judgement that a generalist lacks.

**Negatives**
- **G1.** The scored output is a closure test on pseudo-data, not the new
  physics result; the form motivates the task with "no collaboration has
  measured it at LEP" but grades no measurement on real data. Mild: closure
  and stress tests are how real analyses validate before unblinding.
- **G2.** An agent-made Lund-plane analysis of the same data exists (JFC,
  arXiv:2603.20179). The "not measured" claim holds only for collaborations
  and should say so.

**Judgement:** Strong Accept

## Scope

**Positives**
- Experimental particle physics is physics, a covered science, and the work
  (detector unfolding of a QCD observable on collider data) belongs to it
  outright. Nothing is shoehorned.

**Negatives**
- None of weight.

**Judgement:** Strong Accept

## Outcome-Verified

**Positives**
- Only the density and covariance on withheld data are scored; the method is
  free (binned, unbinned, other).
- Constraints (offline, unprivileged user, time cap, frozen pipeline) are
  mechanical and guard against cheating.

**Negatives**
- **O1.** HEPData YAML with a 2D covariance is fiddly; format errors could
  fail correct physics. No template or writer is mentioned.
- **O2.** The form does not say how the ban on online answers (or on the JFC
  code, if banned) is enforced, or that such a process check can only fail a
  run.
- **O3.** The gaming list names methods ("bin-by-bin factors"). The form
  should say these fail through the score alone, not through method checks.
- **O4.** The 10-minute cap limits methods (e.g. per-dataset OmniFold with
  bootstrap). Mechanical and acceptable, but the instruction should state it
  exactly.

**Judgement:** Accept

## Final Analysis
The science, the scope and the verifier idea are strong: exact truths from
simulation, a proper scoring rule, model and detector shifts that test what
real unfolding gets wrong, and a gaming test list. The proposal falls short on
specification in the same places the bot faulted #993: the event selection,
the binning and the pass cut are not stated, and the form says outright that
the agent will not be told the formula or the cut. Two further risks need
human judgement. First, the truths are reweightings to the very generators the
agent receives, which opens a template-fit shortcut that could out-score honest
unfolding. Second, the form shows no reference result, no timing on the stated
hardware, and no evidence that an independent correct method clears a cut set
near the reference. All of these have a direct fix, so the task has a clear
path to Accept; as written it is not there yet.

**Decision-Reason:** Strong, well-grounded unfolding task with exact truths, but the form hides the scoring rule and cut, omits the selection, binning and output schema, and leaves a template-fit shortcut and the verifier budget unproven.
**Decision:** Uncertain

---

## Concrete fixes (outside the bot format)

Each fix names the form field and the sentence to add or change. ⟨…⟩ marks a
fact the form lacks; the note after the arrow says what it is. Where the
background note already holds the fact, the fix says so.

### Verifiable

- **V1** (Evaluation Strategy, replace the "Pass:" sentence):
  "Pass if (i) the mean over the ⟨10⟩ datasets of S_agent − S_ref is at least
  −⟨c⟩, where ⟨c⟩ = ⟨rule, e.g. the independent method's mean difference minus
  two standard errors⟩, and (ii) on every dataset
  χ² = (x−t)ᵀ(Σ+Σ_t)⁻¹(x−t) has p ≥ 10⁻³ for ⟨N_bins⟩ degrees of freedom."
  → Needs: the numeric value of c and N_bins.
- **V2** (Evaluation Strategy, add):
  "The reference and the independent method each pass in ⟨20⟩ of ⟨20⟩ verifier
  runs with different random seeds; their worst run clears the cut by ⟨m⟩."
  → Needs: these runs done and the margin m.
- **V3** (Evaluation Strategy, add):
  "Only bins with at least ⟨N⟩ expected splittings per dataset enter the
  score; the binning is chosen so that every bin meets this."
  → Needs: N and a binning that meets it.
- **V4** (Evaluation Strategy, replace "Invalid or non-positive-definite
  covariances ... fail"):
  "The verifier checks the submitted Σ before adding the truth's error: it
  must be symmetric, with all eigenvalues > 0 and condition number below
  10^⟨k⟩, or the dataset fails."
  → Needs: k.
- **V5** (Evaluation Strategy, add after the gaming list):
  "Margins on the 10 datasets: reference ⟨…⟩, independent method ⟨…⟩; each
  gaming attempt scores at least ⟨…⟩ below the cut."
  → Needs: the measured scores.
- **V6** (Evaluation Strategy, change "computed over the whole withheld half"):
  "computed from the withheld-half events not drawn into that dataset, so its
  statistical error is independent of the data".

### Well-specified

- **W1** (Evaluation Strategy, replace "The agent is told what is scored and
  every hard limit, not the formula or the cut."):
  "The instruction states the scoring formula, the pass cut and every hard
  limit. Because the log score is a proper scoring rule, an honest density and
  covariance maximise the expected score, so stating it opens no shortcut."
- **W2** (Workflow Details, replace "a fixed hadronic event selection" and
  extend the target definition):
  "Event selection, at both levels: ⟨cuts⟩. Particle level: stable charged
  particles with ⟨lifetime and acceptance cuts⟩. Thrust axis from ⟨all /
  charged⟩ particles. For a splitting into branches a and b, Δθ is their
  opening angle, k_t = ⟨min(E_a, E_b) sin Δθ, or the form used⟩, and the
  harder branch is the one with larger ⟨E⟩. N_hemispheres = 2 × the number of
  selected particle-level events. The Python implementation defines the
  target; the Rivet routine matches it to ⟨tolerance⟩."
  → Needs: copy each item from the author's reference implementation; the form
  and background note hold none of these values.
- **W3** (Workflow Details, replace "in a given binning"):
  "in ⟨n⟩ bins of ln(1/Δθ) from ⟨a⟩ to ⟨b⟩ and ⟨m⟩ bins of ln(k_t/GeV) from
  ⟨c⟩ to ⟨d⟩ (⟨n·m⟩ bins in all)".
  → Needs: the binning.
- **W4** (Workflow Details, replace "as a HEPData-format record"):
  "as `density.yaml` and `covariance.yaml` in HEPData YAML, bins in row-major
  order of (ln 1/Δθ, ln k_t); the container ships an example record and a
  writer function."
- **W5** (Workflow Details or Dataset, add):
  "True models shift ρ by at most ⟨X⟩% in any bin (about ⟨k⟩ times the spread
  of the provided generators). Each dataset draws its track-efficiency,
  momentum-scale and resolution shifts from independent Gaussians with the
  stated widths, applied as ⟨rule, e.g. drop each track with probability ε⟩."
  → Needs: the author's chosen truth range and the detector-shift rule.
- **W6** (Dependencies, add):
  "The verifier image holds the training files at the same paths as the agent
  image. Each run of `run.sh` gets at most ⟨10⟩ minutes on 4 CPUs and 16 GB
  ⟨with / without⟩ a GPU. There are exactly ⟨10⟩ withheld datasets of ⟨N⟩
  detector-level events each. The agent session ⟨has / has no⟩ network
  access."
  → Needs: N (the background note implies roughly one tenth of a ~383k-event
  withheld half, i.e. ~38k; confirm), the exact cap and count, the GPU and
  network decisions.
- **W7** (Scientific Problem, replace "statistical, simulation and detector
  uncertainties"):
  "data statistics, simulation statistics, dependence on the true physics
  model, and the stated detector variations".

### Solvable

- **S1** (Complexity, replace "the reference reuses the author's thesis
  unfolding code"):
  "The reference (OmniFold, from the author's thesis code) closes on
  independent simulation halves within ⟨…⟩ and passes all ⟨10⟩ withheld
  datasets; its χ² summed over them is ⟨…⟩ for ⟨…⟩ degrees of freedom."
  → Needs: these results; run them before submitting.
- **S2** (Evaluation Strategy, add):
  "A second method (binned 2D IBU with bootstrap and prior variation), written
  without the reference's unfolding code, passes the same cut."
  → Needs: whether it exists and who wrote it; if another person writes it,
  name them.
- **S3** (Dependencies, add):
  "Measured on the stated hardware: the reference trains in ⟨h⟩ h and runs in
  ⟨m⟩ min per dataset with a GPU; the binned method passes within the cap on
  CPU alone, so a GPU helps but is not needed."
  → Needs: timings, and confirmation that the CPU-only route fits.
- **S4**: covered by S3 (state training time against the 4-hour session).
- **S5** (Dependencies, change "under 2 hours total"):
  "under ⟨1.5⟩ hours in all, so agent plus verifier stays under ⟨the runner
  limit⟩."
  → Needs: the actual TB-Science runner limit.
- **S6** (Dataset, add):
  "The Zenodo release is CC BY 4.0, which allows redistribution with
  attribution; the task README and data card carry the citation and the label
  'ALEPH Archived Data'."
  (Add "and we have told the Electron-Positron Alliance" only once done.)

### Difficult

- **D1** (Dataset, add; and add the attempt to the gaming list):
  "No truth equals a provided generator sample: the agent gets ⟨Pythia 8
  default, Herwig 7 default, Sherpa default⟩, while truths use ⟨other tunes or
  shower settings⟩, and ⟨k⟩ of the ⟨10⟩ truths are smooth reweightings outside
  the span of the provided samples. A template fit (fold each provided model,
  return the best one with its statistical covariance) fails."
  → Needs: which settings the agent gets, which the truths use, and k.
- **D2** (Workflow Details, add one of):
  "The agent session has no network access." or
  "Reuse of the JFC analysis code is not allowed; a transcript check enforces
  this."
- **D3** (Complexity, replace the last sentence):
  "Target frontier pass rate: at most 20%, in line with the benchmark's aim,
  checked with ⟨k⟩ runs each of Claude Code and ⟨other agent⟩ before the PR."
- **D4** (Complexity, replace "unfolding per hemisphere instead of per
  splitting"):
  "binned unfolding that treats each splitting as an independent entry, which
  mis-models migrations and bin-to-bin correlations; naive matching of
  splittings between levels".
- **D5**: fixed by W1 and W5.

### Scientifically grounded

- **G1** (Scientific Problem, add):
  "The score tests the pipeline the way a real analysis is tested before it
  touches data: accuracy and coverage on pseudo-data with known truth."
- **G2** (Scientific Problem, change "no collaboration has measured it at
  LEP"):
  "no experimental collaboration has published it at LEP; one agent-made
  analysis exists (JFC, disclosed below)".

### Outcome-verified

- **O1**: fixed by W4 (example record and writer function).
- **O2** (Evaluation Strategy, add):
  "The only process check is a transcript review for forbidden online code;
  it can fail a run but never pass one."
- **O3** (Evaluation Strategy, add after the gaming list):
  "All of these fail through the score alone; the verifier has no
  method-specific checks."
- **O4**: fixed by W6 (exact per-dataset cap in the instruction).

---

# Re-review of version 2

Same rubric, same strict reading, form text only (`tbs_proposal_form.md`
version 2, 2026-10-09). New negatives are numbered N1, N2, ...; fixes R1, R2,
... at the end, most important first.

## Status of the version-1 negatives

| Item | Status in version 2 |
|---|---|
| V1 pass cut | Fixed: mean d ≥ −0.15, stated in the instruction |
| V2 repeat runs | Partly: 20 of 20 seeded replicas promised (see N2) |
| V3 p-value rule | Fixed: at most one of 10 datasets below 10⁻³; scored bins need ≥ 50 expected splittings |
| V4 positive-definite check | Fixed: checked before the truth's error is added; condition number < 10¹⁰ |
| V5 margins | Promised with the PR; no numbers yet |
| V6 truth uses the dataset's own events | Not taken (minor; N5) |
| W1 hidden formula and cut | Fixed |
| W2 particle-level definition | Mostly fixed; stable-particle rule open (N7) |
| W3 binning, W4 output schema | Fixed |
| W5 truth-shift range, detector shifts | Mostly fixed; smearing rule and "span" open (N6, N10) |
| W6 verify-time conditions | Fixed; GPU at verify time unclear (N10) |
| W7 uncertainty wording | Fixed |
| S1 reference results | Open: promised with the PR (N11) |
| S2 second method | Fixed in plan |
| S3 budget, S5 runner limit, S6 licence | Fixed |
| S4 training time in 4 h | Open (N12) |
| D1 template shortcut | Fixed: truths outside the span; template fit in the gaming list |
| D2 network and JFC reuse | Partly: JFC reuse banned, but public network opens a worse route (N1) |
| D3 pass-rate target, D4 failure list, D5 hidden information | Fixed |
| G1 closure test vs real result | Open (minor) |
| G2 "no collaboration" wording | Fixed |
| O1 format, O3 score-only gaming, O4 cap | Fixed |
| O2 process check | Partly (N8) |

## Scientific Domain
**Domain:** Physical Sciences
**Field:** Physics
**Subfield:** Experimental particle physics (jet substructure, detector unfolding)

## Problem Statement
Unchanged in substance from version 1. Changes: the target is now defined in
full (particle acceptance, ALEPH-style hadronic selection, thrust hemispheres,
e⁺e⁻ Cambridge declustering with k_t = E_softer sin Δθ, 8 × 12 bins in
ln(1/Δθ) ∈ [0, 4] and ln(k_t/GeV) ∈ [−3, 3], scored bins listed). The agent gets
Pythia 8 Monash and Herwig 7 default at particle level, the detector envelope
in numbers, and a format writer. The pipeline gets 8 minutes per dataset on 10
withheld datasets of about 25,000 events. The truths are other Herwig 7 and
Pythia 8 settings and smooth 10–30% tilts and bumps of ρ, at least 6 of 10
outside the span of the provided samples. Pass: mean per-bin relative log
score d ≥ −0.15, at most one dataset with χ² p < 10⁻³, all outputs valid.

## Verifiable

**Positives**
- The pass rule is numeric and complete, and the validity checks are exact.
- The calibration numbers check out. For the reference's result with its
  covariance scaled by α, the expected per-bin score difference is
  −½(1/α + ln α − 1): −0.097 at α = 2, −0.216 at α = 3, −0.153 at α = 0.5. For
  an honest method with β times the reference's variance it is −½ ln β, which
  is −0.150 at β = 1.35. The form's figures match.
- Allowing one outlier in rule 2 cuts the false-fail chance of a calibrated
  method from about 1% to about 5 × 10⁻⁵, and the 50-splitting floor keeps the
  Gaussian χ² sound.
- Every gaming attempt, now including the template fit, must fail by score
  alone.

**Negatives**
- **N1 (serious).** Lookup route. The agent session has public network, and
  the pseudo-datasets come from the withheld half of a public simulation:
  Zenodo 22285585 holds all of it, with run and event numbers. An agent can
  download the release and build a table keyed on detector-level content (the
  neutral objects are untouched by the shifts, as are run and event numbers if
  kept). A few MB is enough, so a size cap would not stop it. At verify time
  the pipeline looks up each pseudo-event's particle-level splittings. The
  dataset's own particle-level density differs from t only by data
  statistics, so the pipeline returns near-exact values with a small, honest
  covariance. It beats the reference by a wide margin and does no unfolding.
  The instruction bans reusing analysis code, not fetching the simulation, and
  the verifier cannot tell the two apart. The rubric prefers outright
  prevention to a process check.
- **N2.** 20 passes in 20 replicas only bound a correct method's failure rate
  below about 14% (95% CL). The rubric asks that hundreds of reruns show no
  failure. "Seeded replicas of the withheld set" is also unclear: fresh
  pseudo-datasets, fresh pipeline seeds, or both?
- **N3.** The cut asks for near-reference precision. An honest method with
  errors 16% larger than the reference's (β = 1.35) passes about half the
  time. If the second method sits near that line, correct solutions pass or
  fail at random. "The cut is confirmed before the PR" leaves room to change it
  without saying in which direction.
- **N4.** The reference itself is not pinned down. Dependencies says "the
  binned reference", Complexity says it reuses the thesis code, and the
  evidence names "2D iterative Bayesian and OmniFold" without saying which one
  sets L_ref.
- **N5.** (Minor.) The truth still uses the whole withheld half, including
  the dataset's own events. Datasets drawn from the same half may also share
  events. Both slightly correlate the 10 values of d.

**Judgement:** Uncertain (Accept once N1 is closed)

## Well-Specified

**Positives**
- Two reasonable people could now write equivalent verifiers. The
  definition, binning, scored-bin rule, output schema, formula, cut, envelope
  numbers, shift distribution (uniform), truth classes and verify-time
  conditions are all stated.
- The Python implementation is named as the definition, which settles any
  conflict with the Rivet routine.

**Negatives**
- **N6.** "Extra momentum resolution 0–20% of nominal" needs the nominal
  σ(p) the verifier smears with. Without it the agent cannot reproduce the
  shift. The form does not say whether the efficiency loss is per track and
  independent of momentum.
- **N7.** "The stable particles of the generator record as released" gives
  no lifetime rule, and does not say whether neutrinos enter the neutral list.
  They would shift the thrust axis and the event selection. The form also does
  not say that the provided Pythia 8 and Herwig 7 samples follow the same rule.
- **N8.** The ban on "published analysis code for this observable" is vague.
  fjcontrib's LundPlane package is published code for this observable, and the
  agent cannot tell whether it may use it.
- **N9.** The agent knows the rule but cannot apply it. d needs L_ref, which
  the agent never sees, so even on the development dataset it cannot tell
  where it stands against −0.15.
- **N10.** (Minor.) "Outside the span of the provided samples" is undefined
  (per-bin envelope? convex hull?). The truth classes and the 10–30% range sit
  in the Dataset field, and the form does not say the instruction gives them to
  the agent. "Same hardware" implies a verifier GPU, while "the GPU is
  optional" leaves open whether a pipeline may rely on one.

**Judgement:** Accept

## Solvable

**Positives**
- The budget is explicit and consistent: 8 minutes × 10 datasets, under
  1.5 h, and 5.5 h with the agent session against a 6-hour limit. A CPU-only
  binned route exists, and the training files sit in the verifier.
- A reference and a separately written second method are planned, each with
  replica evidence. The licence is stated.

**Negatives**
- **N11.** All evidence is promised "with the PR". The form shows no
  measured number: no closure, no spread of d, no CPU minutes per dataset.
  "The binned reference passes on CPUs alone" reads as fact but has no number
  behind it.
- **N12.** The reference's training time on the stated hardware is still not
  given, so the 4-hour session is not shown to fit (v1 S4).

**Judgement:** Accept

## Difficult

**Positives**
- Version 1's strengths remain. Truths outside the span close the template
  shortcut.
- The one-sided envelope (track losses and extra smearing only) creates a
  bias the agent must correct, not just a variance.
- The failure list is now right, and the ≤ 20% target matches the benchmark.

**Negatives**
- **N1** again. As written, a lookup solves the task without unfolding. The
  rubric rules out tasks solvable by looking up the answer.
- **N13.** Stating the truth classes (smooth tilts and bumps of 10–30%)
  invites a forward-fold fit of a low-order smooth reweighting of the training
  model. On the 6 or more smooth-reweighting datasets, such a fit can earn a
  small covariance from knowing how the test is built, not from the physics.
  The gaming list does not test it.
- **N14.** The pass rate is unproven until the frontier runs.

**Judgement:** Accept

## Scientifically Grounded & Interesting

**Positives**
- Unchanged: a real unfolding workflow on archived full simulation, an
  observable no LEP collaboration has published, and uncertainty choices that
  need domain judgement. The claim about prior work is now accurate.

**Negatives**
- G1 remains (minor): the score grades a closure test on pseudo-data, not a
  physics result.

**Judgement:** Strong Accept

## Scope

**Positives**
- Experimental particle physics, a covered field. The task fits it outright.

**Negatives**
- None.

**Judgement:** Strong Accept

## Outcome-Verified

**Positives**
- Only the outputs are scored. Gaming attempts fail by score alone. A writer
  removes format risk. All constraints are mechanical.

**Negatives**
- A process check is the only guard against code reuse (N8) and lookups
  (N1), where the rubric prefers prevention. The form does not say the check
  can only fail a run, never pass one.

**Judgement:** Accept

## Final Analysis
Version 2 fixes almost every version-1 gap. The task is now fully specified,
the pass rule is numeric and its calibration figures are correct, the template
shortcut is closed, and the budget fits the runner limit. One serious hole
remains. With public network, an agent can fetch the public ALEPH simulation,
which holds every withheld event, and look up each pseudo-event's truth. That
yields near-perfect scores with no unfolding, and the verifier cannot detect
it. One sentence closes it. The rest are small: the smearing rule, the
stable-particle rule, a reliability bound stronger than 20 of 20, L_ref on the
development dataset, which method is the reference, and a forward-fold item in
the gaming list.

**Decision-Reason:** Version 2 is specified and verifiable in full, but with public network an agent can fetch the public ALEPH simulation and look up each pseudo-event's truth, which must be closed before submission.
**Decision:** Accept

---

## Remaining fixes for version 2 (most important first)

- **R1 (N1, must fix).** Dependencies: replace "public network" with "no
  network; all software is in the image". Dataset: add "Pseudo-datasets carry
  no run or event numbers." Workflow, replacing the JFC sentence: "The agent
  has no network; the instruction forbids using any ALEPH files beyond those
  provided."
- **R2 (N2).** Evaluation Strategy: replace "each pass in 20 of 20 seeded
  replicas of the withheld set" with "each pass in ⟨100⟩ of ⟨100⟩ replicas,
  each with freshly drawn pseudo-datasets and fresh pipeline seeds, with mean
  d at least ⟨3⟩ standard deviations above −0.15."
  → Needs: the replica count the author can afford (~80 CPU-minutes each) and the
  measured spread.
- **R3 (N6).** Workflow (3): "Per dataset, ε, s and f are drawn uniformly
  from the envelope; each track is dropped with probability ε, its momentum
  multiplied by (1 + s), then smeared by a Gaussian of width
  f · σ_nom(p), with σ_nom(p) = ⟨formula⟩."
  → Needs: the nominal resolution formula, and whether smearing acts on p or
  1/p_T.
- **R4 (N7).** Particle-level target, first bullet: "Stable: ⟨lifetime rule
  of the release⟩; neutrinos excluded. The provided Pythia 8 and Herwig 7
  samples follow the same rule."
  → Needs: the release's convention (check `tgen` for K⁰_S, Λ and neutrinos).
- **R5 (N9).** Workflow (4): "One development pseudo-dataset with its truth
  and the reference's log score on it, so the agent can compute d." (Give
  L_ref only, not the reference's covariance, which would leak its uncertainty
  model.)
- **R6 (N3, N4).** Evaluation Strategy: "The reference (L_ref) is the
  author's ⟨2D iterative Bayesian / OmniFold⟩ unfolding; the second method is
  ⟨the other⟩. If the second method misses −0.15, the cut is loosened, never
  tightened."
- **R7 (N13).** Gaming list, add: "a forward-folded fit of a low-order smooth
  reweighting of the training model, with its fit covariance". Report its
  score. If it passes honestly, say such fits are allowed.
- **R8 (N10).** Dataset: "Outside the span means outside the per-bin envelope
  of Pythia 6.1, Pythia 8 Monash and Herwig 7 default in at least ⟨k⟩ scored
  bins. The instruction gives the agent these truth classes and the 10–30%
  range." Dependencies: "The verifier ⟨has / may lack⟩ a GPU."
- **R9 (N11, N12).** Complexity or Dependencies: add any numbers in hand, e.g.
  "Reference: closure within ⟨…⟩; ⟨m⟩ CPU-minutes per dataset; trains in ⟨h⟩
  h." If none are in hand yet, run them first; the author's plan says to build
  most of the task before proposing.
- **R10 (N8, only if network stays).** "Forbidden: the JFC ALEPH Lund-plane
  code (Zenodo 20693601 and its repository). Allowed: general libraries,
  including fastjet, fjcontrib, RooUnfold and public OmniFold code. The
  process check can fail a run but never pass one."
- **R11 (minor; N5, G1).** "The truth for a dataset uses the withheld-half
  events not drawn into it; datasets share no events" (if 10 disjoint draws
  of 25,000 do not fit the ~383k-event half after unweighting, state the
  overlap instead). And in the Scientific
  Problem: "The score tests the pipeline as a real analysis is tested before
  it touches data."

---

# Re-review of version 3

Same rubric and strict reading, form text only (`tbs_proposal_form.md`
version 3). Version 3 applies R1–R11. This section lists only what would still
move a verdict.

## Problem Statement
Unchanged from version 2. New in version 3:
- Agent network is limited to the model API (Harbor allow-list), and the form
  states the lookup risk.
- No ALEPH files beyond those provided. Run and event numbers are removed, and
  events and particles are shuffled.
- Detector-shift formulas, including ALEPH σ(1/p_T) and a neutral energy scale.
- A stable-particle rule (GEANT3 record minus neutrinos).
- L_ref on the development set.
- Reference = 2D IBU on CPU, second method = OmniFold; the cut may only be
  loosened.
- Truths come from events not in their dataset; the datasets are disjoint.
- "Outside the span" is defined. Evidence: 100 of 100 draws with a 3σ margin.
- The forward-fold fit is reported. The process check can fail a run but never
  pass one.

## Verifiable
**Positives.** The lookup route is closed by prevention (allow-list) and
defence in depth (no IDs, shuffling). The pass rule, validity checks and
reference are fixed, and the cut can only be loosened. The reliability plan
(100 draws, 3σ margin) meets the rubric's bar. The truth no longer shares
events with its dataset.
**Negatives.** No result yet. The 100 "independent" draws come from one
~383k-event pool, so they are re-draws, not independent. This does not change
the verdict.
**Judgement:** Accept

## Well-Specified
**Positives.** Every quantity the verifier uses is stated: the definition,
binning, scored bins, schema, formula, cut, the shift formulas and their
ranges, the truth classes and their size, the span rule, and verify-time
conditions. The agent can compute its own d on the development set.
**Negatives.** The instruction says the truths differ "by up to about 30% in
ρ". For the Herwig 7 and Pythia 8 variants this is a claim about the build,
not a design choice. Generators often differ by more than 30% at low k_t. If
any truth exceeds the stated size, the instruction misleads (see C3).
**Judgement:** Accept

## Solvable
**Positives.** The budget is consistent: 8 minutes × 10 datasets on CPU, 5.5 h
in all. The reference method is cheap (2D IBU, 96 bins), its code exists, and
a second method is named.
**Negatives.** No part of the build has run. The cut, the 50-splitting floor,
the "6 of 10 outside the span" design and the claim that the CPU reference
passes rule 2 on those truths are all unchecked. The crux is whether an honest
IBU covers truths that lie, by design, outside every model the agent can use
for a prior envelope. That is plausible, but not shown.
**Judgement:** Accept (argument, not evidence; see C1)

## Difficult
**Positives.** Unchanged, and the stated forward-fold fit must win or lose on
the score like any other method.
**Negatives.** The difficulty rests on one untested premise: that detector
migrations matter. The observable uses charged particles only, and ALEPH
tracking is precise (σ(1/p_T) ≈ 0.6×10⁻³ GeV⁻¹ at high p_T) and close to fully
efficient. The response may therefore be close to diagonal. If so, bin-by-bin
factors with a simple model envelope could pass, and the task would be
easier than claimed (see C2). Frontier pass rate still unproven.
**Judgement:** Accept

## Scientifically Grounded & Interesting
**Judgement:** Strong Accept (no change)

## Scope
**Judgement:** Strong Accept (no change)

## Outcome-Verified
**Positives.** Only outputs are scored. Cheating is blocked mechanically, and
the process check can only fail a run. The method is free, and a writer
handles the format.
**Negatives.** None that would change the verdict.
**Judgement:** Accept

## Final Analysis
Version 3 leaves no Step-1 gap open. It is specified, verifiable,
cheat-resistant, in scope and well grounded. What remains are claims the build
must confirm: the reference passes, bin-by-bin fails, the truth sizes match
the instruction, and the runners enforce the allow-list. If any of these fails
after approval, the task needs redesign rather than a sentence.

**Decision-Reason:** Version 3 closes every specification and cheating gap; what remains is evidence the build must supply, not a flaw in the design.
**Decision:** Accept

## Conditions that would change a verdict

- **C1 (Solvable → Uncertain).** The reference IBU fails rule 1 or rule 2 on
  the outside-span truths, or OmniFold misses the cut by more than a small
  loosening can fix. Check first: run the reference on a few re-draws before
  posting. Put three numbers in the form: the spread of mean d, CPU minutes
  per dataset, and the worst p-value.
- **C2 (Difficult → Uncertain or Reject).** Bin-by-bin factors, or a plain 2D
  IBU with no model uncertainty, pass the cut. Check first: score both early.
  If either passes, the detector shifts or the truth shifts are too mild for
  the task to be hard.
- **C3 (Well-specified → Uncertain).** Any truth shifts some scored bin by
  much more than "about 30%". Fix: after building the truths, compute the
  largest per-bin shift and state that number in the instruction.
- **C4 (Verifiable → Uncertain).** The TB-Science runners cannot enforce the
  Harbor allow-list, which brings the lookup route back. Check first: confirm
  the allow-list works on the runners before posting.

## For the human reviewer (no Step-1 verdict change)

- The particle definition leans on the GEANT3 record (a few undecayed K⁰_S
  and Λ), which Pythia 8 and Herwig 7 cannot copy literally. Give the
  generator-level rule (e.g. a cτ threshold) that reproduces the record, so
  "the same stable-particle rule" is concrete and the result is usable
  outside ALEPH.
- Ten disjoint draws of 25,000 events from a ~383k-event half leave room for
  a maximum weight of only about 1.5 per truth. Weights may need capping. The
  truth uses the same weights, so capping stays consistent, but dataset sizes
  may fall below 25,000.

---

# Review of version 4 (test suite)

Same rubric and strict reading. Each test is judged as its own proposal: the
shared setup, plus its own section, plus the common form fields of
`tbs_proposal_form.md` version 4. T5 (the capstone, version 3.1) is not
re-reviewed here.

## T1 `lep-lund-response`

The agent builds a binned response (M, b, acceptance factors) from paired
simulation. The verifier folds the particle-level truths of 10 hidden models
with it and compares each result with the model's detector-level density
by χ², relative to the reference response.

- **Verifiable: Uncertain.** The grader is deterministic, cheap and runs no
  agent code. But the rule is relative to the reference, so the reference
  passes by construction (ratio 1 ≤ 1.25) and that proves nothing. The form
  gives no evidence that an independently built correct response clears 1.25×
  the reference, or that naive responses fail. The error model is also
  contradictory: T1 compares Fold(t_m) with d_m "of the same hidden events"
  and adds "the statistical errors of both". The shared setup computes truths
  "over withheld events outside the graded sample". If t and d come from the
  same events, their errors are strongly correlated. Adding them in quadrature
  then inflates the errors and pushes everyone under the 1.2 floor, so sloppy
  responses pass.
- **Well-specified: Uncertain.** "The instruction defines how these combine
  into the folding d = Fold(t)" — but the form does not give Fold, the size of
  the "acceptance factors" (a scalar? per bin?), or how particle-level
  splittings outside the 96-bin range enter. These are the core of the grader.
  "8 outside the span of the provided samples" means little, since T1 provides
  no other generator. The number of events per hidden model is not stated.
- **Solvable: Accept.** The reference response exists in principle and the
  budget is trivial. "If the reference's χ²_m/n is large, the models are made
  milder before the proposal" shows the check has not run yet.
- **Difficult: Uncertain (leaning Reject).** One to three expert days.
  Building a matched-splitting response with fakes and efficiencies is
  standard; the rubric calls a few days of undergraduate work too easy. The
  bar is the reference's own non-closure, so an agent that does the standard
  thing the reference does should pass. The test is hard only if naive
  responses fail by a wide margin. With charged-only splittings and precise
  ALEPH tracking, the response may be nearly diagonal, and then a bin-by-bin
  response could pass. ≤ 20% frontier pass is doubtful.
- **Scientifically grounded: Accept.** Published responses are used for
  forward folding by theorists, and transfer to unseen models is the right
  test. On its own, though, it is one routine step of a measurement.
- **Scope: Strong Accept.**
- **Outcome-verified: Accept.** Static files; the method is free; a fixed
  schema is a fair output format.
- **Decision: Uncertain.**

## T2 `lep-lund-unfold-stat`

The agent unfolds pseudo-data drawn from the training model, with the
reference response given, and quotes statistical and simulation-statistics
uncertainties.

- **Verifiable: Reject.** Every T2 truth is the expected density of the
  training model, which the agent holds with ~15 times the statistics of a
  pseudo-dataset. Returning the training particle-level density with its
  simulation-statistics covariance ignores the data and beats any unfolding
  by a wide margin: d ≈ −½ ln(var_agent/var_ref) ≈ +1, far above −0.15. The
  same holds, more weakly, for any heavily regularised unfolding. So the
  listed failure "over-regularised results with small errors" is rewarded,
  not caught. The verifier cannot separate correct work from ignoring the
  data.
- **Well-specified: Accept.** The shared score and output are clear. One
  gap: the agent gets the reference response "as files" and "the training
  simulation for bootstrapping". To propagate simulation statistics it must
  rebuild the response on bootstrap replicas, which is T1's work, so the step
  is not isolated.
- **Solvable: Accept.**
- **Difficult: Reject.** "Hours for an expert". IBU with a given response
  plus a bootstrap is a textbook exercise (RooUnfold tutorial level). The
  author rates it Medium.
- **Scientifically grounded: Uncertain.** A standard method with no research
  judgement left once the response is given.
- **Scope: Strong Accept.**
- **Outcome-verified: Accept.**
- **Decision: Reject.** Fixing the shortcut would still leave Difficult; this
  matches the author's plan to keep T2 in-house unless frontier runs show
  ≤ 20%.

## T3 `lep-lund-unfold-model`

The agent unfolds pseudo-data whose true models lie outside every model it is
given, with the reference response, and quotes a model uncertainty.

- **Verifiable: Accept.** The truths differ from the training model by
  10–30%, so returning the prior fails. The score and pass rule are exact.
  Evidence (100 of 100 draws for both methods) is promised, not shown.
- **Well-specified: Accept.** The verifier is fully defined. "The
  instruction says the truths differ from the training model, not how" is
  defensible: the detector-level data show how far each truth sits from the
  prior. A strict bot may still read it as guesswork about how wide to make
  the covariance (see F8).
- **Solvable: Accept.** One risk: the second method, OmniFold, must run with
  a covariance within 5 CPU-minutes per dataset with no GPU. That is tight
  unless its simulation-statistics replicas are trained in advance.
- **Difficult: Accept.** Covering truths outside the prior's span with an
  honest model uncertainty, ideally from a data-driven prior update, is
  research-level, and the listed failure (generator spread as the
  uncertainty) is real. The test is hard only if prior dependence is
  material. If the response is nearly diagonal, plain IBU with data and
  simulation statistics may pass with no model uncertainty. Unproven, not
  disproved.
- **Scientifically grounded: Strong Accept.** Model dependence is the central
  problem of unfolding.
- **Scope: Strong Accept.**
- **Outcome-verified: Accept.**
- **Decision: Accept.**

## T4 `lep-lund-unfold-detector`

The agent unfolds pseudo-data with shifted detector response inside a stated
envelope, with the reference response, and propagates detector systematics.

- **Verifiable: Reject.** The truth is "training-model truth" for every
  dataset, so the T2 shortcut applies unchanged. Returning the training
  particle-level density with its simulation-statistics covariance ignores
  both the data and the detector shifts, and passes with a large margin.
- **Well-specified: Accept.** The envelope formulas, ranges and distribution
  are exact. The same response-replica gap as T2.
- **Solvable: Accept.**
- **Difficult: Uncertain.** Propagating track loss, scale, smearing and
  neutral scale by varying the simulation and re-unfolding is a standard
  recipe that agents know. The one-sided envelope adds a real bias
  correction. Two to four expert days; ≤ 20% unproven. One listed failure is
  doubtful: "variations applied to the data instead of the simulation".
  Shifting pseudo-data and unfolding with the nominal response is a standard
  first-order way to size a systematic. A domain reviewer will doubt the
  difficulty argument if it lists a valid method as a failure.
- **Scientifically grounded: Accept.**
- **Scope: Strong Accept.**
- **Outcome-verified: Accept.**
- **Decision: Reject** (fixable; with the fix, Uncertain on Difficult).

## Fixes that would change a verdict (most important first)

- **F1 (T4 Verifiable Reject → Accept; same for T2 if kept).** The truths
  must vary from dataset to dataset by more than the data's statistical
  error, or the training density wins. For T4, replace "training-model truth"
  with: "Each pseudo-dataset has its own hidden truth: a mixture or smooth
  reweighting inside the span of the provided Pythia 8 and Herwig 7 samples
  (given to the agent), differing from the training density by more than
  ⟨3⟩ times the dataset's statistical error in at least ⟨80⟩% of the scored
  bins." Add to the T2–T4 gaming list: "the training particle-level density
  returned with its simulation-statistics covariance; it must fail." For T2
  the same fix brings in prior dependence and turns it into a small T3, so
  the cleaner choice is to keep T2 out of TB-Science, as planned.
- **F2 (T1 Well-specified Uncertain → Accept).** State the folding and the
  error model in the proposal. Suggested, for the author to confirm:
  "Fold(t)_i = (1/A_i)·[c·Σ_j M_ij A_j t_j + b_i], with A the bin areas, t the
  particle-level density over all particle-level hemispheres, plus one
  overflow entry for splittings outside the 96 bins (supplied by the verifier
  from each truth), c the scalar ratio of particle- to detector-level
  hemisphere counts, M (96 × 97) the expected detector-level splittings in
  bin i per particle-level splitting in bin j, and b the detector-level
  splittings per detector-level hemisphere not traced to a particle-level
  one. t_m comes from withheld events outside the graded sample and d_m from
  the ⟨N⟩ graded events, so their errors add in quadrature; χ² runs over the
  n scored detector bins." Delete "of the same hidden events" or make it
  agree.
- **F3 (T1 Verifiable Uncertain → Accept).** Add the evidence plan to the
  T1 Evaluation Strategy: "Before the proposal: a second response built
  independently (⟨method, e.g. per-hemisphere least-squares regression of
  detector counts on particle counts⟩) passes; a diagonal bin-by-bin
  response, per-hemisphere ratios, and M = 0 with b = the training
  detector-level density each fail. Their mean χ²/n is reported beside the
  reference's (⟨…⟩)."
- **F4 (T1 Difficult Uncertain → Accept, or drop T1).** Report the diagonal
  bin-by-bin response's score against the 1.25× bar. If it passes, or comes
  within ⟨10⟩%, the detector is too kind for T1 to be hard alone. In that
  case, fold T1 into T3/T5 rather than proposing it. If it fails clearly, add
  one sentence: "A bin-by-bin response scores mean χ²/n = ⟨…⟩, ⟨k⟩ times the
  reference's, and fails."
- **F5 (T3 Difficult stays Accept; protects it).** Run plain IBU with data
  and simulation statistics but no model uncertainty on the T3 draws, and
  state that it fails rule 1 or 2. If it passes, prior dependence is too weak
  and the truths must move further out.
- **F6 (T4 Difficult Uncertain → Accept).** Replace the doubtful failure:
  "Expected failures: no correction for the non-zero mean of the one-sided
  shifts (track loss, extra smearing); uniform ranges treated as Gaussian
  ±1σ; correlations between sources ignored; shifts treated as statistical
  noise." Then show plain IBU without detector systematics fails the T4 draws.
- **F7 (T3/T4 Solvable, Verifiable evidence).** "The second method is
  OmniFold with its simulation-statistics replicas trained in advance; it
  runs in ⟨m⟩ CPU-minutes per dataset." If it cannot fit 5 CPU-minutes, name
  a second method that does (e.g. an independent IBU or TUnfold
  implementation).
- **F8 (T3 Well-specified, guards against a strict bot).** Add: "The truths
  shift ρ by up to ⟨measured maximum⟩% in any scored bin." Use the measured
  value from the built truths, not the design range.
- **F9 (T2–T4 Well-specified).** "The container provides ⟨100⟩ bootstrap
  replicas of the reference response (M, b, c), so simulation statistics can
  be propagated without rebuilding it." Without this, T2–T4 silently include
  T1's work.
- **F10 (cross-task; human reviewer).** T3 and T4 ship T1's reference
  response, so once merged, T1's answer sits in the public repository. The
  allow-list keeps it out of reach at run time. Say so in T1's form, or ship
  T3 and T4 with a response built by a different method.

---

# Review of version 4.1 (T3, T4)

Same rubric and strict reading. Each test is judged as it would be pasted
alone: the shared setup, plus its own section, plus the common fields. Only
issues that would still change a verdict are listed.

## T3 `lep-lund-unfold-model`

- **Verifiable: Accept.** Every dataset has its own truth, the training
  density must fail, and the pass rule is exact. The reference (2D IBU) and an
  independent second method (TUnfold, CPU) must pass 100 of 100 draws.
- **Well-specified: Uncertain.** As pasted alone, T3's inputs read "As T2,
  plus ...", but T2 is not part of the submission. The bot would not see the
  deliverable path (`run.sh <dataset> <out>`), the writer, the HEPData output,
  the event count (~25,000) or the response files. Fixed by one paragraph
  (G1). The rest is clear, including the measured largest shift stated in the
  instruction.
- **Solvable: Accept.** The CPU budget fits both IBU and TUnfold. The
  reference's pass on out-of-span truths is promised, not shown.
- **Difficult: Accept.** Model uncertainty for truths outside every given
  model is research-level. The required evidence (plain IBU without model
  uncertainty fails) is the right check. If that evidence fails, this drops
  to Uncertain.
- **Scientifically grounded: Strong Accept.**
- **Scope: Strong Accept.**
- **Outcome-verified: Accept.**
- **Decision: Accept.**

## T4 `lep-lund-unfold-detector`

- **Verifiable: Accept.** Each dataset has its own in-span truth, more than 3σ
  from the training density in ≥ 80% of scored bins, so returning the prior
  fails.
- **Well-specified: Uncertain.** Two gaps. (1) The same "As T2" problem as
  T3. (2) The truths lie "inside the span of the provided Pythia 8 and Herwig
  7 samples", but under "As T2, plus the envelope" T4 does not provide those
  samples. Only T3 adds them. The agent cannot use a span it is not given, and
  the failure "model change ignored because the truths lie inside the span"
  assumes it has them.
- **Solvable: Accept.**
- **Difficult: Uncertain.** Two risks, both verdict-level.
  (a) Much of the envelope may be too small to matter. A 0.3% momentum scale
  moves ln k_t by ~0.003, against a bin width of 0.5. Extra smearing of 20%
  of ALEPH's σ(p_T)/p_T (~0.5% at a few GeV) adds ~0.1%. The neutral scale
  touches only the thrust axis and the selection. Only the 0–2% track loss is
  likely to move ρ, and plausibly by about the statistical error in populated
  bins. If plain IBU without detector systematics passes, which the form's own
  evidence rule tests, T4 does not test its step. The in-span model change
  then carries the score, making T4 a small T3.
  (b) If the in-span truths are mixtures of the provided samples, a
  three-template forward fit with detector nuisances is the exact model class.
  It would beat unfolding without doing it. (My earlier F1 wording, "a mixture
  or smooth reweighting", invited this.)
- **Scientifically grounded: Accept.**
- **Scope: Strong Accept.**
- **Outcome-verified: Accept.**
- **Decision: Uncertain.**

## Fixes that would still change a verdict (most important first)

- **G1 (T3 and T4 Well-specified → Accept).** Replace "As T2, plus ..." in
  each with a full inputs line. For T4: "Inputs: the training half of the
  simulation; the reference response and 100 bootstrap replicas of it;
  particle-level samples of Pythia 8 (Monash) and Herwig 7 (default); the
  detector envelope below. Deliver `/app/submission/run.sh <dataset> <out>`
  writing `density.yaml` and `covariance.yaml` with the provided writer.
  Pseudo-datasets: about 25,000 events each." For T3, the same line without
  the envelope.
- **G2 (T4 Difficult → Accept, or merge T4 into T5).** Before proposing,
  measure each envelope source's largest effect on ρ in units of the
  dataset's statistical error, and state it. Add: "Track loss shifts ρ by up
  to ⟨k⟩σ; the momentum scale, extra smearing and neutral scale shift it by
  less than ⟨…⟩σ." If plain IBU without detector systematics passes, T4 does
  not test its step. Keep it inside T5 rather than widening the envelope
  beyond what ALEPH's documented uncertainties support.
- **G3 (T4 Difficult, risk (b)).** Add to the T4 truth definition: "No truth
  is a mixture of the provided samples; a template fit over them, with
  detector nuisances, is run and its score reported."

Not verdict-changing, but quick: version 3 gave a development pseudo-dataset
with its truth and L_ref; version 4.1 dropped it, so the agent cannot compute
its own d. The suite table in `tbs_proposal_form.md` also has two header rows
(lines 11–14), which breaks its rendering.
