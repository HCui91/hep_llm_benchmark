# Tracks: tasks, outputs and scores

Status: draft, 2026-09-30. Nothing here is decided until it appears in `decisions.md`.

Each track answers one question about an agent:

| Track | Question | Score comes from |
|---|---|---|
| A. Rivet closure | Can it turn a paper into a correct analysis routine? | Its histograms against the human routine's, on the same events |
| B. Sensitivity | Can it design a selection as good as the experiment's? | Expected significance on held-out simulation, against the published selection on the same samples |
| C. Blind search | Can it find new physics and, harder, not claim what is not there? | Hits and false claims over many pseudo-data sets with hidden truth |

Three rules hold for all tracks:

1. **A number, not an opinion.** A grader program computes every headline score.
   No language model sets a score. A transcript monitor may void a run for
   cheating or made-up results (`plan.md`), never raise one.
2. **The reference sees the same inputs.** We never compare the agent with a
   published number made from inputs the agent lacks (full simulation, internal
   data). We re-run the human method on the agent's inputs.
3. **The grader holds data the agent never sees.** Held-out events (B), hidden
   truth (C), and the reference routine and extra event samples (A) live outside
   the agent's container.

## Keeping answers private

The worry: ATLAS requires a Rivet routine for every
measurement, and routines are open source. So the answer to any real Track A task
is public, and a model may have learned it in training.

There are two leaks, and they need different fixes.

**Leak 1: look-up during the run.** Fix: in scored runs the agent can reach
only its model's API host, nothing else (Harbor allow-list; `plan.md`,
"Harness"). The container holds the paper, its HEPData record, the Rivet manual,
and the ROOT and Python docs. This fixes leak 1 only.

**Leak 2: the answer is in the training data.** No sandbox fixes this. Only a
task whose answer has never been public is clean. By track:

- **Track B:** clean. The score comes from held-out simulation and our
  systematic model. The published selection is public, but copying it scores
  only 1.0, the baseline; anything above 1 has to be earned.
- **Track C:** clean. Boxes are drawn fresh with private seeds.
- **Track A:** only some pools are clean.

| Pool | Clean against training data? | Use |
|---|---|---|
| A-dev: old public routines | No | Harness tests; contamination measure (below) |
| A-fresh: routines merged after a model's stated cut-off | Only for older models, and cut-off dates are vague; each new model shrinks the pool | Extra, not headline |
| Rolling window: real papers with no routine yet; we write the reference | Yes, until the official routine appears; then no, for every later model | Extra, short-lived |
| A-perturbed: real paper plus a note that changes cuts or binning | Partly: a model can recall the routine and patch it | Tests whether it reads the spec |
| **Made-up measurements**: a short paper-style spec for a measurement no one has made, with our reference routine | **Yes**, as long as we never publish it | **Headline** |

So headline Track A scores come only from made-up measurements. Two costs:
- Specs must read like real papers and leave no room for two readings.
- No measured data exist, so physics closure π has no σᵢ. We borrow the
  relative uncertainties of the nearest real measurement, and say so.

**What is fine to learn from public routines.** A model that learned Rivet idioms
from the 2000 public routines (dressed leptons, FastJet calls, booking) has
learned what a PhD student learns by reading them. That is skill, not
contamination. Contamination means the answer to *this* task was seen.

**We must not leak the private tasks ourselves.**
- Consumer Claude plans (Free, Pro, Max, including Claude Code on them) train on
  sessions when the account's "help improve Claude" setting is on
  ([Anthropic](https://www.anthropic.com/news/updates-to-our-consumer-terms)).
  That setting must be off on any account that runs private tasks. Check the same
  for every other provider; API terms usually exclude training, but check each.
- The private test split is never pushed to a public repository, never posted,
  and never pasted into a chat tool with training on. We release the dev split
  and the code; we run the private split ourselves, as CritPt does with its
  server.
- A private task that leaks, or whose official routine appears, moves to the dev
  pool.

**Contamination as a result.** Score gap per model between A-dev (public) and
made-up tasks of the same tier, plus the memorisation probe, measures how much a
model recalls rather than works out. LiveCodeBench showed such a drop after model
cut-offs. This number is worth reporting in the paper.

---

## Track A: Rivet closure

### Task
The agent receives a paper and must write the Rivet routine for its measurement.

Inputs in the container:
- The paper as PDF and LaTeX source, and its HEPData record (YODA reference file).
  The reference file fixes the histogram paths and bin edges. Where no HEPData
  record exists, we supply a table of paths and bin edges, so the task tests
  physics and not guessing binning from figures.
- Rivet and its manual, the `rivet-mkanalysis` template, and the other routines in
  the release, **minus** the target routine and any older version of it.
- A small event sample (HepMC) of the right process, to test with.
- No network except the model's API host (see "Keeping answers private").

Output: `ANALYSIS.cc`, `ANALYSIS.info`, `ANALYSIS.plot`, built with `rivet-build`.

### Grader
1. Build the routine. It must compile and run on every grader sample without a
   crash. Failure scores 0 for the task.
2. Run the agent routine and the reference routine on the **same** hidden event
   samples: at least two generators (for example Pythia 8 and Herwig 7), and one
   stress sample that fills the corners of phase space (events near cut values,
   photons near leptons, jets near overlap-removal limits).
3. Compare each reference histogram *r* with the agent histogram *g* of the same
   path. Wrong or missing path, or different bin edges: that histogram scores 0.

### Metrics
Both routines see identical events, so any difference comes from different logic,
not from statistics. Two measures per histogram:

- **Logic closure**, δ = Σᵢ |gᵢ − rᵢ| / Σᵢ |rᵢ|. δ = 0 means the same logic up to
  rounding. Pass: δ < 10⁻⁴.
- **Physics closure**, π = maxᵢ (|gᵢ − rᵢ| / rᵢ) / (σᵢ / dᵢ), where dᵢ and
  σᵢ are the measured value and its total uncertainty in bin *i* from HEPData.
  It is the relative difference between the routines, in units of the relative
  data uncertainty. Relative, because an LO generator's normalisation can sit far
  from the data. π tells whether the difference would change any comparison of a
  generator with the data. Pass: π < 0.1. For made-up measurements, σᵢ / dᵢ
  comes from the nearest real measurement.
- **Noise in π.** With finite events, a harmless change moves a few events
  between bins, and one event in a 50-entry bin is already a 2% change. So the
  grader first subtracts twice the statistical noise of the difference itself:
  if n events move, |gᵢ − rᵢ| ≈ n·wᵢ with noise ≈ √n·wᵢ, where wᵢ = rᵢ / nᵢ is
  the value per raw entry. A bin then counts only once about five events
  differ. Bins with fewer than 10 raw entries are left out of π (δ still sees
  them). As built: `track_a/grader/closure.py`.

Histogram grade: *exact* (logic pass), *equivalent* (physics pass only), or
*wrong*. A histogram passes only if it passes on every grader sample, since one
generator can hide a bug that another shows.

Task score: fraction of histograms graded exact or equivalent (report both
fractions). Diagnostics, not scored: δ after normalising both to unit area (splits
normalisation bugs from shape bugs), and the build and run logs.

### The reference can be wrong
Rivet routines have bugs. When the agent and the reference disagree, an expert
reads both against the paper. If the reference is wrong, we fix it, log the fix in
an errata file, and re-grade. A reference bug found by an agent is a result worth
reporting.

### The paper can be unclear
AgentRivet found that most physics errors trace back to unclear papers: 1/N over
which events, dressed or bare leptons, a vague jet definition. If a right-minded
expert could read the paper two ways, the task must settle it in a short note, or
the grader must accept both readings. Otherwise we score the paper, not the
agent. The three task reviewers (`validation.md`) look for such points.

### Difficulty tiers

| Tier | Features | Example type |
|---|---|---|
| A1 | One or two observables, simple cuts | Inclusive jet or photon cross-section |
| A2 | Dressed leptons, isolation, several regions | Z+jets, W+jets, diboson |
| A3 | Hard object definitions | ttbar pseudo-top, jet substructure, Lund plane, event shapes, b-jets by ghost matching |
| A4 | Searches with detector smearing | SUSY or exotics signal regions, graded on cut-flow tables the experiment published |

For A4, experiments publish cut-flows for benchmark signal points. These give a
reference made by the experiment itself, not by a Rivet author.

### Contamination
Task pools and which of them are clean against training data: see "Keeping
answers private" above. Headline scores come from made-up measurements only.
During the run, the sandbox also keeps the agent away from the answer: no Rivet
source for the target, no git history, no network beyond the model's API.

Two checks run on every task:
- **Memorisation probe:** give the model only the analysis name and ask for the
  routine. If that alone closes, flag the task for that model.
- **Similarity check:** compare the agent's code with the public routine, as
  MLE-bench does with Kaggle notebooks. Near-copies on a pool that should be clean
  point to a leak.

---

## Track B: sensitivity of a selection

> **Status, 2026-10-09: largely covered elsewhere.** TB-Science PR
> [#2098](https://github.com/harbor-framework/terminal-bench-science/pull/2098)
> (Novak, Zhao, Garcia, MIT; advisor Harris) is a stronger version of this
> track: the agent's frozen H→4ℓ pipeline runs blind on 10 withheld
> pseudo-datasets with different injected m_H and μ (some μ = 0) and different
> detector response, and is scored by a log score of m_H and μ, with their
> uncertainties, against the truth, relative to an expert reference, plus fit
> quality, calibrations and compute. Frontier agents reached 40–60% of the
> reference score; none passed. The authors declare they are building a broader
> HEP agent benchmark. Our Z₀-ratio design below tests only the selection step.
> Proposal: re-scope Track B to unfolded measurements (`tbs_proposals.md`,
> idea 2), and borrow from #2098 the ideas listed under "Design lessons" below.
> Not decided.

### Task
The agent receives simulated signal and background events at reconstructed level
for a known process, the luminosity, the trigger, and a systematic model. It must
design the event and object selection (cuts, categories, or a trained
classifier) that gives the best expected result.

Candidate first tasks: H→γγ and H→ZZ*→4ℓ on ATLAS or CMS open data simulation;
later ttH, VBF H→ττ, and HH→bbγγ on fresh Delphes samples. See
`data_and_tools.md` for sources.

Inputs in the container:
- A **training** split of the simulation (for example, events with even event
  number). Only reconstructed-level branches; truth branches removed.
- The paper of the reference analysis, and a written statement of the systematic
  model the grader will use.
- For "blind" variants: real open data outside the signal region only (sidebands,
  control regions). The grader keeps the signal-region data sealed.

Output: selection code with a fixed interface, for example a Python function
`category(events) -> int array` (−1 = rejected) over awkward arrays, or a C++
function for RDataFrame, plus any trained model file it loads.

### Checkpoint B0: rebuild the baseline
Before it designs anything, the agent implements the published selection and
submits the list of selected events on the training split. The grader compares it
with our list, event by event, as Saito et al. did for H→4ℓ
([arXiv:2604.14696](https://arxiv.org/abs/2604.14696)). This scores reading and
coding apart from design, so a low final score can be traced to its cause. B0 is
reported on its own and does not enter the main score.

### Grader
1. Check the rules: only allowed branches used, trigger applied, runs within the
   time limit.
2. Apply the selection to the **held-out** split, never seen by the agent.
3. Build the statistical model (pyhf) from the selected events: per category, the
   fit observable (for example m_γγ) or a single count, with the stated
   systematics.
4. Compute the expected discovery significance Z₀ on the Asimov data set (μ = 1),
   following Cowan, Cranmer, Gross and Vitells,
   [arXiv:1007.1727](https://arxiv.org/abs/1007.1727). For measurement tasks, also
   compute the expected uncertainty on the signal strength, Δμ.
5. Run the published selection, as implemented by us, through steps 2–4 on the
   same events. This gives Z_ref.

### Metrics
- **Score** = Z₀(agent) / Z₀(ref). Above 1 means the agent beat the published
  selection on these samples. Also report Δμ(ref) / Δμ(agent).
- **Gates** (score 0 if failed): each category keeps at least a set number of
  effective background simulation events (for example 10), so that a cut tuned to
  a hole in the simulation cannot win; no truth information; trigger applied.

### What "a better cut" means here
The idea that a sharper selection might beat the published one is fair to
test, with care:
- Published analyses carry limits the simulation does not: trigger, data-driven
  background estimates, control regions, systematics we cannot rebuild. A higher
  Z₀ on simple simulation does not show a better analysis in the real world.
- A selection tuned on the same events it is scored on will look better than it
  is. The held-out split removes this.
- With statistics alone, very tight cuts win for free. The systematic model must
  punish them the way real analyses are punished: background normalisation and
  shape uncertainties, and for H→γγ the spurious-signal term.

So we report "beats the reference on equal inputs", never "beats ATLAS".

### Blinding variant
Real PhD work runs blind. In this variant the agent may look at control regions
and sidebands of real open data but not at the signal region. The grader unblinds
once, after the agent freezes its selection, and reports the observed
significance next to the expected one. Only the expected result counts in the
score; any attempt to read sealed data fails the task.

---

## Track C: blind search

> **Status, 2026-10-09: largely covered elsewhere.** TB-Science PR
> [#2267](https://github.com/harbor-framework/terminal-bench-science/pull/2267)
> (Noll, Stanford; Li, Yale) is close to this track for dijet resonances: the
> agent's program reports a look-elsewhere-corrected global significance on 40
> hidden boxes (10 without signal, 3 × 10 with different unseen signals), the
> simulation describes the pseudo-data imperfectly, and the verifier checks
> reproducibility, no false discoveries and sensitivity against a reference.
> [#1258](https://github.com/harbor-framework/terminal-bench-science/pull/1258)
> covers data-driven background modelling in a diphoton search. Proposal:
> replace discovery with reinterpretation, the null-result side of BSM work
> (`tbs_proposals.md`, ideas 3 and 4: published likelihoods from HEPData, Rivet,
> Contur). Not decided.

### Task
The agent receives one "box": a pseudo-data set (reconstructed-level events,
unit weights, Poisson-fluctuated) and a background simulation. The box may hold an
injected signal or none. The agent must say whether it found something, and back
the claim with numbers.

Output: a JSON report with
- claim: `discovery` (≥ 5σ global), `evidence` (≥ 3σ global), or `none`;
- local and global significance;
- if a claim: the final state, the mass (or other feature) and its uncertainty,
  and the fitted signal cross-section;
- if no claim: 95% CL upper limits on σ × BR against mass for a stated model;
- the analysis code, so the grader can re-run it.

### Making boxes
Boxes are made by a program, not by hand: for each box, draw from set priors
whether there is a signal, which model (for example dijet or dilepton resonance,
a new particle with a cascade decay, a long-lived particle), its mass and its
cross-section. Events come from Pythia 8 + Delphes. A large background pool,
generated once, is resampled per box. Seeds stay private. This gives as many boxes
as we need, and a fresh set for each release, so no model can have seen them.

Signal strength is set by the expected significance of a good analysis, in three
bands: easy (about 8σ), medium (about 5σ), hard (about 3σ).

### Realism: imperfect background simulation
If the background simulation matched the pseudo-data exactly, any excess over
simulation would be signal, and the task would be trivial. So the pseudo-data
background comes from a different generator or tune, or with a set shape
distortion, from the simulation the agent gets. The agent must choose a
data-driven method (fit a smooth function to a mass spectrum, sidebands, ABCD)
as a real analyser would. The size of the mismatch is a difficulty knob.

### Metrics
Over a set of boxes, half of them with no signal:
- **Hit rate**: signal boxes where the agent claims evidence or more, with the
  right final state and the mass within twice the resolution.
- **False-claim rate**: null boxes with a claim of evidence or more.
- **Score** = hit rate − k × false-claim rate, with k fixed in advance (for
  example k = 3; a false discovery costs more than a miss).
- **Calibration**: on null boxes, reported global p-values should be uniform.
  Test with a Kolmogorov–Smirnov test; report the look-elsewhere handling.
- **Limits** (null boxes): the agent's expected limit over the limit of the
  grader's own analysis; injection tests check the limits cover.

### Prior work to reuse
The LHC Olympics 2020 black boxes and the Dark Machines challenge set the pattern.
Their answers are public, so they serve as dev tasks only. See `literature.md`.

---

## Design lessons from TB-Science PRs #2098 and #2267

Worth adopting in every track that grades a measurement or a search:
- **Grade a frozen pipeline, not one answer.** The agent hands over a program;
  the verifier runs it offline on many withheld datasets. One agent session then
  yields a score over many datasets, and false-claim rates become measurable.
- **Vary the truth and the detector between datasets**, including null cases,
  so a pipeline must calibrate rather than recall numbers.
- **Score against an expert reference on the same datasets**, with a log score
  of value and uncertainty (#2098), so honest errors matter as much as the
  central value.
- **Re-fit the declared model in the verifier** instead of trusting reported
  numbers; check consistency between report and model; check an event list
  against the data.
- **Tell the agent what is scored, not the formula** (`GRADING.md` in #2098).
- **Publish the gaming attempts that fail**, with their scores.
- **Isolation:** run the submission as `nobody`, answer key root-only, withheld
  data encrypted on Hugging Face with the key only in the verifier image.

## Shared output rules

Every task writes the same files so one harness can score all tracks:
- `result.json`: the track-specific output above;
- `code/`: everything needed to re-run the result;
- the transcript, tool calls, tokens used, cost and wall time, logged by the
  harness, not the agent.
