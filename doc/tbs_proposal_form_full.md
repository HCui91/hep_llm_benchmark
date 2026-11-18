# TB-Science task proposal: full analysis (capstone of the test suite)

Superseded as the first submission by the test suite in `tbs_proposal_form.md`;
kept as the capstone (test T5). Fields as in the TB-Science proposal form (e.g.
discussion #427). Background, checks and the validation plan:
`tbs_proposal_lund_unfolding.md`; rubric review of version 1 and the fixes
applied here: `notes/tbs_rubric_self_review.md`. Version 3.1, 2026-10-09 (final; three rubric reviews, last verdict Accept).

---

**Task title.** Unfold the primary Lund jet plane in e⁺e⁻ → hadrons from
archived ALEPH data (`lep-lund-unfolding`)

**Scientific Domain.** Physical Sciences > Physics > Experimental particle physics

**Scientific Problem.**
Measurements in particle physics are corrected for detector effects
("unfolded") so that theorists and event-generator authors can use them. The
primary Lund jet plane maps the emissions inside a jet by angle and relative
transverse momentum, separating perturbative from non-perturbative QCD. ATLAS
and CMS have measured it in proton collisions; no LEP collaboration has
published it. The task: from ALEPH detector-level events at √s = 91.2 GeV,
measure the particle-level primary Lund-plane density of e⁺e⁻ → hadrons with a
full covariance matrix that honestly covers statistical, simulation-statistics,
model and detector uncertainties. The agent's frozen pipeline is scored on
withheld pseudo-datasets whose true physics and detector response differ from
the training simulation, so it passes only if it unfolds correctly and knows
how wrong it can be.

**Workflow Details.**

*Inputs.* (1) A training half of the ALEPH 1994 Pythia 6.1 full simulation:
per event, the particle-level and detector-level particles, paired by event,
plus particle-level events that fail the detector selection. (2) Particle-level
samples of Pythia 8 (Monash) and Herwig 7 (default) only (particles with
cτ > 1 cm stable, K⁰_S and Λ decayed, neutrinos dropped, to match the ALEPH
record as closely as a generator setting can). (3) The detector systematic envelope, applied per
detector-level object: each charged track is dropped with probability
ε ∈ [0, 0.02]; its momentum is scaled by (1+s), s ∈ [−0.003, 0.003]; its 1/p_T
is smeared by a Gaussian of width f·σ_nom, f ∈ [0, 0.2], with the nominal ALEPH
resolution σ_nom(1/p_T) = 0.6×10⁻³ ⊕ 0.005/p_T (GeV)⁻¹ (ALEPH, Nucl. Instrum.
Meth. A 360 (1995) 481); neutral energy-flow objects get an energy scale
(1+s_n), s_n ∈ [−0.01, 0.01]. (4) One development pseudo-dataset with its
truth and the reference's log score on it, so the agent can compute its own
d on it. (5) A reference implementation of the particle-level observable
(Python, plus a Rivet routine) and a writer for the output format. The
instruction says the true models of the withheld datasets differ from the
training model in shower, hadronisation and Lund-plane shape, without naming
them, and states the largest per-bin shift of ρ among them (measured when the
truths are built; the design aims at 10–30%).

*Particle-level target* (the Python implementation is the definition):
- Particles: the particles of the generator record as released (GEANT3 codes),
  excluding neutrinos. Charged (charge ±1) particles enter if p_T > 0.2 GeV and
  |cos θ| < 0.94; neutral ones if E > 0.4 GeV and |cos θ| < 0.98.
- Events: at least 5 such charged particles, total charged energy ≥ 15 GeV,
  and thrust axis with |cos θ_T| < 0.82 (thrust from all entering particles),
  mirroring ALEPH's standard hadronic selection.
- Hemispheres: split by the plane normal to the thrust axis; every hemisphere
  of a selected event counts in N_hemispheres, even with no splitting.
- Declustering: the charged particles of each hemisphere are clustered into one
  jet with the e⁺e⁻ Cambridge algorithm (fastjet `ee_genkt`, p = 0, R large
  enough to merge all). Undo the last clustering step; the branch with the
  higher energy is "harder". Record Δθ, the opening angle between the two
  branches, and k_t = E_softer · sin Δθ. Repeat on the harder branch until it
  is a single particle.
- Density: ρ = (1/N_hemispheres) · N_splittings per bin / (bin area), in
  ln(1/Δθ) from 0 to 4 (8 bins of 0.5) × ln(k_t/GeV) from −3 to 3 (12 bins of
  0.5); 96 bins, of which the instruction lists the scored ones (the bins with
  at least 50 expected splittings per pseudo-dataset in every truth).

*Deliverable.* `/app/submission/run.sh <dataset_dir> <output_dir>` writes
`density.yaml` and `covariance.yaml` (HEPData format, bins in row-major order:
ln(1/Δθ) outer, ln k_t inner) with the provided writer. The method is the
agent's choice (binned iterative Bayesian, unbinned OmniFold-style, forward
folding, or other), using the pre-installed software (fastjet, fjcontrib,
numpy, PyTorch and the rest).

**Dependencies & System Requirements.**
Container with Python (uproot, awkward, numpy, scipy, fastjet, scikit-learn,
PyTorch), ROOT and Rivet. Agent container: 4 CPU cores, 16 GB memory, 1 GPU,
4-hour session; network limited to the model provider's API (Harbor
`allowlist`). The simulation behind the withheld datasets is public on Zenodo,
so an agent with open internet could fetch it and look up each pseudo-event's
truth; the allow-list closes that, and the instruction forbids any ALEPH files
beyond those provided. Verifier container: same hardware including the GPU,
no network; it holds the training files, so a pipeline may retrain per
dataset. Cap: 8 minutes per dataset, 10 datasets, so the verifier stays under
1.5 hours and agent plus verifier under the 6-hour runner limit. The GPU is
optional: the reference uses CPUs only.

**Dataset.**
ALEPH 1994 archived data and Pythia 6.1 full simulation released by the
Electron-Positron Alliance, Zenodo record 22285585, under CC BY 4.0, which
permits copying and redistribution with attribution (cite PRL 123 (2019)
212002 and the ALEPH collaboration; label "ALEPH Archived Data"). A slimmed
copy (needed branches only, about 2 GB) goes into the agent image and is
mirrored in the TB-Science dataset. The 10 withheld pseudo-datasets (about
20,000–25,000 events each after capping the reweighting weights, about 1 GB in
all) go encrypted into the verifier image.
They come from the withheld half of the simulation (no events shared with the
training half; the 10 datasets are disjoint). Each is reweighted at particle
level to a true model, unweighted, and given a detector shift drawn uniformly
inside the stated envelope. Run and event numbers are removed and the order of
events and of particles is shuffled. True models: Herwig 7 and Pythia 8 with
shower and hadronisation settings different from the provided samples
(changes that are not low-order smooth in the plane), and smooth reweightings
of the Lund plane (tilts and bumps of 10–30% in ρ). No truth equals a provided
sample; at least 6 of the 10 lie outside the span of the provided samples,
meaning outside the per-bin range of those samples and their mixtures in at
least 20% of the scored bins by more than twice the dataset's statistical
error. The truths are the author's and appear nowhere online.

**Evaluation Strategy.**
The score tests the pipeline the way a real analysis is tested on
pseudo-data before it touches data. The frozen submission runs offline as an
unprivileged user on each withheld dataset. For dataset k the truth t_k is the
expected particle-level density under its true model, computed with the same
weights over the withheld events not drawn into that dataset (its small
statistical error is added to Σ in scoring, after the checks below). The
reference is the author's 2D iterative Bayesian unfolding; it sets L_ref. Over the scored bins (n of them) the verifier computes the Gaussian log
score L = −½[(x−t)ᵀΣ⁻¹(x−t) + log det 2πΣ] for the submission and for the
expert reference on the same dataset, and d_k = (L_agent − L_ref)/n.

Pass rule, stated in full in the instruction (the log score is a proper
scoring rule, so an honest density and covariance maximise the expected score
and stating it opens no shortcut):
1. mean of d_k over the 10 datasets ≥ −0.15. For a calibrated reference, the
   same result with its covariance doubled scores −0.10 (passes) and tripled
   −0.22 (fails); halved scores −0.15 and fails rule 2 as well; a method whose
   honestly stated variance is 1.35 times the reference's sits at the cut. The
   cut is confirmed before the PR so that the second expert method (OmniFold)
   passes, and may only be loosened, never tightened;
2. at most one of the 10 datasets with a χ² p-value below 10⁻³ (n degrees of
   freedom);
3. every output valid: covariance symmetric, all eigenvalues positive,
   condition number below 10¹⁰, files in the stated format, run within the cap.

A process check of the transcript can fail a run (for example for fetching
outside files) but never pass one.

Evidence with the PR: the reference and the second method each pass in 100 of
100 independent draws of the withheld set (fresh reweightings, detector shifts
and pipeline seeds), with mean d at least 3σ above the cut; `nop` fails; these
attempts fail by the score alone, with their scores reported: training prior
returned, a template fit over the provided generator samples, bin-by-bin
correction factors, the detector-level density, covariance scaled by 0.5 or
3, the development truth copied, and plain bin-by-bin factors or a 2D
iterative Bayesian unfolding without model uncertainty (if either passes, the
detector and truth shifts are enlarged before the PR). A forward-folded fit of
a low-order smooth reweighting of the training model is run and its score
reported; it is a legitimate method and must win or lose on the score. The PR
also states the spread of the reference's mean d, its CPU minutes per dataset
and its worst p-value.

**Complexity.**
An expert who knows the method needs one to two weeks; the reference reuses
the author's thesis unfolding code. The difficulty is substantive: the density
counts several splittings per hemisphere and the detector-level declustering
differs from the particle-level one in the same event, so binned methods need
splitting-level efficiencies, fakes and migrations; the result must survive
true models outside the training span (prior dependence) and shifted detector
response; and the covariance must include simulation statistics (bootstrap)
and model uncertainty. Likely agent failures: binned unfolding that treats
splittings as independent entries, no model uncertainty, no simulation
bootstrap, wrong normalisation, overconfident covariances. Target frontier
pass rate: 20% or lower, checked with Claude Code and one other frontier agent
before the PR.

**References & Resources.**
- Lund jet plane: Dreyer, Salam, Soyez, arXiv:1807.04758. ATLAS measurement:
  arXiv:2004.03540.
- OmniFold: Andreassen et al., arXiv:1911.09107. Iterative Bayesian unfolding:
  D'Agostini, Nucl. Instrum. Meth. A 362 (1995) 487.
- ALEPH archived data: PRL 123 (2019) 212002; unbinned thrust measurement,
  arXiv:2510.22038.
- Prior agent-made analysis of the same observable on real ALEPH data
  (disclosed; it cannot give the withheld truths): JFC, arXiv:2603.20179,
  Zenodo record 20693601.

**Additional Information.**
Distinct from existing TB-Science HEP tasks: #2098 (H→4ℓ parameter
measurement), #2267 (anomaly detection), #896 (forward fast simulation of CMS
jets; this task is the inverse problem with uncertainty quantification, on
e⁺e⁻), #1489, #1258, #1020. Conflict of interest: the author is building a
broader HEP agent benchmark built on Rivet and HEPData; this task is one part
of it. Question to maintainers: do the review runners enforce Harbor's
network `allowlist` for the agent container? The task relies on it (see
Dependencies).

**Author Information.**
Hanfei Cui, University College London (ATLAS); unfolding of the Lund jet plane
with OmniFold and iterative Bayesian methods.
