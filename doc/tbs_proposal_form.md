# TB-Science proposals: Lund-plane unfolding on ALEPH data, as a suite of tests

Version 4.2, 2026-10-10 (after two per-test rubric reviews). Replaces the single big analysis (now the capstone, T5,
in `tbs_proposal_form_full.md`) by tests that each isolate one step of an
unfolding measurement, with one deliverable and one pass rule. Background,
dataset decision and reviews: `tbs_proposal_lund_unfolding.md`,
`notes/tbs_rubric_self_review.md`.

## The suite

| Test | One step it isolates | Deliverable | Graded by | Expected difficulty | Where |
|---|---|---|---|---|---|
| T1 `lep-lund-response` | Build the detector response of the Lund-plane density | Response in a fixed schema (static files) | Folding hidden truths of 10 models, compared with their detector-level densities | Medium | Our benchmark |
| T2 `lep-lund-unfold-stat` | Unfold with a given response; statistics only; truths inside the training span | `run.sh` → density + covariance | Log score and coverage on 10 pseudo-datasets | Easy–medium | Our benchmark |
| **T3 `lep-lund-unfold-model`** | Unfold when the true model is outside every model given; model uncertainty | `run.sh` → density + covariance | Same, out-of-span truths, nominal detector | Hard | **TB-Science** |
| **T4 `lep-lund-unfold-detector`** | Unfold under shifted detector response; detector systematics | `run.sh` → density + covariance | Same, in-span truths, detector shifts | Medium–hard | **TB-Science** |
| T5 `lep-lund-unfolding` (capstone) | All at once, response built by the agent | `run.sh` → density + covariance | `tbs_proposal_form_full.md` | Hardest | TB-Science, later |

**Why tests instead of one analysis.** Each test has a short instruction, one
output and one rule, so it is easier to specify, to validate and to review, and
a failure says which step went wrong. T2–T4 hand the agent the expert response,
so an error in one step does not spoil the next (the "oracle carry-over" CritPt
uses for its checkpoints).

**What goes to TB-Science.** T3 first. T4 follows once its sensitivity check
passes (each detector source shifts ρ by more than the statistical error in
some scored bins, and plain unfolding without detector systematics fails);
otherwise T4 stays inside T5. T5 later, once the tests show where agents fail. T1 and T2 stay in our own benchmark as
diagnostic rungs: on their own they are standard work (a per-test review rated
them Uncertain and Reject on difficulty), and T3 and T4 ship the expert
response, so a public T1 would have its answer in the repository. No
TB-Science task yet uses Harbor's multi-step format (0 of 90 merged tasks);
we ask the maintainers whether they would rather take T3 and T4 as one
multi-step task.

## Shared setup (all tests)

- **Data.** ALEPH 1994 archived data and Pythia 6.1 full simulation released by
  the Electron-Positron Alliance, Zenodo record 22285585, CC BY 4.0 (cite PRL
  123 (2019) 212002 and the ALEPH collaboration; label "ALEPH Archived Data").
  The agent gets a training half of the simulation: particle-level and
  detector-level particles paired by event, plus particle-level events failing
  the detector selection. Hidden samples come from the withheld half (no shared
  events).
- **Observable** (the provided Python code is the definition, with a matching
  Rivet routine). Particles: the generator record as released (GEANT3 codes)
  minus neutrinos; detector level: ALEPH energy-flow objects. Charged particles
  enter if p_T > 0.2 GeV and |cos θ| < 0.94; neutral ones if E > 0.4 GeV and
  |cos θ| < 0.98. Events: at least 5 charged, charged energy ≥ 15 GeV,
  |cos θ_thrust| < 0.82. Hemispheres from the thrust axis; the charged
  particles of each are clustered with the e⁺e⁻ Cambridge algorithm and
  declustered along the higher-energy branch; each splitting gives
  (ln 1/Δθ, ln k_t/GeV) with k_t = E_softer sin Δθ. Density ρ = splittings per
  hemisphere per bin area, in 8 × 12 bins over ln(1/Δθ) ∈ [0, 4] and
  ln(k_t/GeV) ∈ [−3, 3]; the instruction lists the scored bins.
- **Hidden truths.** Every pseudo-dataset has its own true model, never the
  training model: built by reweighting withheld simulation at particle level,
  unweighting, and (T4 only) shifting the detector response. Each truth is the
  expected particle-level density under its model, computed over withheld
  events disjoint from the graded sample. No truth is the training model or a
  mixture of the provided samples. Returning the training density, with any
  covariance, must fail every test.
- **Development set.** Each test ships one development pseudo-dataset made the
  same way, with its truth and the reference's score on it, so the agent can
  compute its own score before submitting.
- **Isolation.** Agent network limited to the model provider's API (Harbor
  allow-list), because the public simulation would let an agent look up the
  truth of each event; no ALEPH files beyond those provided; run and event
  numbers removed, events and particles shuffled. Verifier without network.
  A process check of the transcript can fail a run, never pass one.
- **Score for T2–T4.** Per dataset, the Gaussian log score
  L = −½[(x−t)ᵀΣ⁻¹(x−t) + log det 2πΣ] of the submitted density x and
  covariance Σ at the truth t, minus the reference's, per scored bin: d_k.
  Pass: mean d_k ≥ −0.15 over the 10 datasets (the reference with its
  covariance doubled scores −0.10, tripled −0.22); at most one dataset with a
  χ² p-value below 10⁻³; covariance symmetric, positive definite, condition
  number below 10¹⁰. The rule is stated in the instruction: the log score is a
  proper scoring rule, so honesty maximises it. The reference is the author's
  2D iterative Bayesian unfolding; the independent second method is Tikhonov
  regularised unfolding (TUnfold, in ROOT), written separately; both must pass
  in 100 of 100 independent draws, within the CPU cap, before the PR. T2–T4
  ship the reference response and 100 bootstrap replicas of it (for the
  simulation-statistics uncertainty), so no test needs T1's work.
- **Resources.** 4 CPU cores, 16 GB memory, no GPU (the tests work in fixed
  bins). Agent session 3 hours (T1: 2 hours). Verifier: T1 a few seconds (it
  only multiplies matrices; no agent code runs); T2–T4 5 minutes per dataset,
  under an hour in all.

---

## T1 `lep-lund-response`: build the detector response

**Scientific Problem.** Every unfolding rests on a model of how the detector
turns particle-level quantities into measured ones. For the Lund-plane density
this is not a simple bin-to-bin map: each hemisphere has several splittings,
and the detector-level declustering differs from the particle-level one in the
same event (lost or extra tracks reorder the clustering). The task: from paired
simulation, build the binned response of the density, good enough to predict
the detector-level density of physics models it was not built on.

**Workflow Details.** Deliver, in the stated schema, the folding
Fold(t)_i = c · (Σ_j M_ij a_j t_j + b_i) + (1 − c) · g_i, where t_j is the
particle-level splittings per hemisphere in bin j (j = 97 collects splittings
outside the 96 bins), M (96 × 97) the expected detector-level splittings in bin
i per particle-level splitting in bin j, a_j the share of particle-level
splittings in bin j that lie in hemispheres of events passing both selections,
b_i the detector-level splittings per such hemisphere not traced to a
particle-level one, c the share of detector-level hemispheres whose event also
passes the particle-level selection, and g_i the splittings per hemisphere in
events passing only the detector selection. How to match splittings, or
whether to match at all, is the agent's choice.

**Evaluation Strategy.** The verifier takes 10 hidden models (8 outside the
span of the provided samples), computes for each the particle-level truth t_m
and the detector-level density d_m from disjoint sets of hidden events (so
their statistical errors are independent and add in quadrature), folds t_m
with the submitted response, and computes χ²_m between Fold(t_m) and d_m. Pass: the mean of χ²_m/n over the models is at
most 1.25 times the reference's (or 1.2, whichever is larger), and no single
model has χ²_m/n above 1.5 times the reference's for that model (or 3,
whichever is larger). A linear binned response never folds other models
perfectly, so the bar is the reference's own non-closure; if the reference's
χ²_m/n is large on the hidden models, the models are made milder before the
proposal. Cheap and deterministic: no agent code runs. Evidence required: an
independently built response passes, and a diagonal bin-by-bin response,
per-hemisphere ratios, and M = 0 with b set to the training detector-level
density each fail, with their χ²/n reported beside the reference's. If the
bin-by-bin response comes within 10% of the bar, T1 is dropped as a test and
kept only inside T5.

**Complexity.** One to three days for an expert (standard work; hence our
benchmark only). The difficulty is getting a
response that transfers between models: a response built from bin-by-bin
ratios, or one that ignores the selection and hemisphere-count migrations,
folds the training model well and other models badly, which is exactly what
the hidden models test. Expected agent failures: per-hemisphere ratios instead
of splitting-level migrations, fakes or inefficiencies left out, wrong
normalisation between the two hemisphere counts.

## T2 `lep-lund-unfold-stat`: unfold with statistical uncertainties

**Scientific Problem.** With the response known, unfold detector-level data to
the particle-level density and give its covariance, including the uncertainty
from the finite simulation used to build the response.

**Workflow Details.** Inputs: the shared setup, the reference response from T1
(as files), and the bootstrap replicas. Deliver `run.sh <dataset> <out>` writing density and
covariance (HEPData format, with the provided writer). Pseudo-datasets: about
25,000 events each, nominal detector, each with its own true model inside the
span of the provided Pythia 8 and Herwig 7 samples (a small version of T3;
hence our benchmark only).

**Evaluation Strategy.** The shared score for T2–T4.

**Complexity.** Hours for an expert. Expected failures: covariance from data
statistics only (missing simulation statistics), bin correlations dropped,
wrong normalisation, over-regularised results with small errors.

## T3 `lep-lund-unfold-model`: unfold when the true model is unknown

**Scientific Problem.** Unfolding depends on the model used to build it (the
prior). A measurement must stay unbiased, or quote enough uncertainty, when
nature differs from the simulation. The task: unfold pseudo-datasets whose
true models lie outside every model the agent is given, and quote a model
uncertainty that covers the error.

**Workflow Details.** Inputs: the shared setup; the reference response and 100 bootstrap replicas of it
(files); particle-level samples of Pythia 8 (Monash) and Herwig 7 (default);
the development pseudo-dataset with its truth and reference score; the
observable code and the HEPData writer. Deliver
`/app/submission/run.sh <dataset_dir> <output_dir>`, writing `density.yaml`
and `covariance.yaml` (HEPData format, bins row-major: ln(1/Δθ) outer,
ln k_t inner). Pseudo-datasets: 10, about 25,000 events each, nominal detector; true models are
Herwig 7 and Pythia 8 with other shower and hadronisation settings and smooth
reweightings of the plane (10–30% in ρ); at least 8 of 10 lie outside the span
of the provided samples (outside their per-bin range in at least 20% of the
scored bins by more than twice the statistical error). The instruction says
the truths differ from the training model, not how.

**Evaluation Strategy.** The shared score for T2–T4. Evidence required: plain
iterative Bayesian unfolding without model uncertainty fails; the training
density returned fails; the measured largest per-bin shift of the truths is
stated in the instruction. A forward-folded fit of a smooth reweighting is run
and its score reported; it is a legitimate method and wins or loses on the
score.

**Complexity.** A week for an expert. Expected failures: no model uncertainty,
or one taken as the spread between the two provided generators, which does not
cover truths outside their span; prior not updated from data.

## T4 `lep-lund-unfold-detector`: unfold under detector systematics

**Scientific Problem.** The detector is never known exactly. The task: unfold
pseudo-datasets whose detector response is shifted inside a stated envelope,
and propagate the detector systematic uncertainties into the covariance.

**Workflow Details.** Inputs: the shared setup; the reference response and 100 bootstrap replicas of it
(files); particle-level samples of Pythia 8 (Monash) and Herwig 7 (default);
the development pseudo-dataset with its truth and reference score; the
observable code and the HEPData writer. Deliver
`/app/submission/run.sh <dataset_dir> <output_dir>`, writing `density.yaml`
and `covariance.yaml` (HEPData format, bins row-major: ln(1/Δθ) outer,
ln k_t inner). Pseudo-datasets: 10, about 25,000 events each; plus the detector
envelope, applied per detector-level object: each charged track dropped with probability ε ∈ [0, 0.02]; momentum
scaled by (1+s), s ∈ [−0.003, 0.003]; 1/p_T smeared by a Gaussian of width
f·σ_nom, f ∈ [0, 0.2], σ_nom(1/p_T) = 0.6×10⁻³ ⊕ 0.005/p_T (GeV)⁻¹ (ALEPH,
Nucl. Instrum. Meth. A 360 (1995) 481); neutral energies scaled by (1+s_n),
s_n ∈ [−0.01, 0.01]. These are within ALEPH's documented tracking
performance. Each pseudo-dataset has its own true model inside the span of the
provided Pythia 8 and Herwig 7 samples but not a mixture of them, differing
from the training density by more than three times the statistical error in
at least 80% of the scored bins, and a detector shift drawn uniformly inside
the envelope.

**Evaluation Strategy.** The shared score for T2–T4. Evidence required, before
proposing T4: each source's effect on ρ, in units of the statistical error,
measured and stated in the instruction; plain iterative Bayesian unfolding
without detector systematics fails; the training density returned fails; a
template fit over the provided samples with detector nuisances is run and its
score reported.

**Complexity.** Two to four days for an expert, plus the in-span model change.
Expected failures: only some sources propagated; bin-to-bin correlations of
each systematic dropped (treated as independent noise per bin); the envelope's
range used as a Gaussian width without thought; the model change ignored
because the truths lie inside the span.

---

## Common form fields (paste into each proposal)

**Scientific Domain.** Physical Sciences > Physics > Experimental particle physics

**Dependencies & System Requirements.** Python (uproot, awkward, numpy, scipy,
fastjet, scikit-learn, PyTorch), ROOT, Rivet. 4 CPU cores, 16 GB, no GPU.
Agent network: model API only (allow-list). Verifier: no network.

**Dataset.** As "Shared setup: Data" above; slimmed copy (about 2 GB) in the
agent image and mirrored in the TB-Science dataset; hidden samples encrypted
in the verifier image; truths are the author's and appear nowhere online.

**References & Resources.** Lund jet plane: arXiv:1807.04758; ATLAS
measurement: arXiv:2004.03540. OmniFold: arXiv:1911.09107. Iterative Bayesian
unfolding: D'Agostini, Nucl. Instrum. Meth. A 362 (1995) 487. ALEPH archived
data: PRL 123 (2019) 212002; unbinned thrust: arXiv:2510.22038. Prior
agent-made analysis of the same observable on real ALEPH data (disclosed; it
cannot give the hidden truths): JFC, arXiv:2603.20179, Zenodo record 20693601.

**Additional Information.** Part of a suite on one dataset (T3 and T4 proposed
now, the full analysis later); each test is graded on its own. Distinct from
existing TB-Science HEP tasks (#2098, #2267, #896, #1489, #1258, #1020); the
nearest, #896, is the forward simulation of CMS jets. Conflict of interest: the author is building a
broader HEP agent benchmark built on Rivet and HEPData; these tests are part of
it. Questions to maintainers: do the review runners enforce the Harbor network
allow-list; would you rather take T3 and T4 as one multi-step task?

**Author Information.** Hanfei Cui, University College London (ATLAS);
unfolding of the Lund jet plane with OmniFold and iterative Bayesian methods.
