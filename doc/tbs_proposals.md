# Terminal-Bench-Science: task ideas using HEPData and Rivet

Draft, 2026-10-09. Ideas only; none proposed yet. Sources: the TB-Science
[CONTRIBUTING.md](https://github.com/harbor-framework/terminal-bench-science/blob/main/CONTRIBUTING.md)
and [proposal rubric](https://github.com/harbor-framework/terminal-bench-science/blob/main/rubrics/task-proposal.md).
(The proposal dashboard on terminal-bench-science.ai was not checked for
duplicates.)

## What TB-Science asks for

- Frontier models should pass only 10–20% of the time at release.
- Research-level work needing a PhD or years of domain practice; "anything an
  average undergraduate could solve in a few days is too easy".
- Verified by a program on the outcome, not the method; LLM judges only in rare
  cases.
- Well specified: two experts reading the instruction would write equivalent
  verifiers. Hard for real reasons, not because of ambiguity or volume.
- Open internet for the agent: the instruction forbids looking up the answer and
  a process grader checks transcripts. Better still if the answer is not online.
- Different from every other TB-Science task.
- Route: proposal form, then an LLM rubric review, then maintainer approval on
  Discord, then a PR with oracle, nop and frontier-model runs.

## HEP tasks already open (avoid overlap)

| PR | Task | Authors |
|---|---|---|
| [#2098](https://github.com/harbor-framework/terminal-bench-science/pull/2098) | H→ZZ*→4ℓ: measure m_H and μ with calibrated uncertainties; frozen pipeline graded blind on 10 withheld pseudo-datasets (varied truth, some μ = 0, varied detector response) | Novak, Zhao, Garcia (MIT; advisor Harris) |
| [#2267](https://github.com/harbor-framework/terminal-bench-science/pull/2267) | Model-agnostic dijet anomaly detection: report a look-elsewhere-corrected global significance on 40 hidden boxes (10 null), mismodelled simulation | Noll (Stanford), Li (Yale) |
| [#1258](https://github.com/harbor-framework/terminal-bench-science/pull/1258) | Generative data-driven background for a diphoton search | qibin2020 |
| [#1020](https://github.com/harbor-framework/terminal-bench-science/pull/1020) | Adaptive Level-1 anomaly trigger on real CMS 2016 open data | Zixind |
| [#896](https://github.com/harbor-framework/terminal-bench-science/pull/896) | Fast simulation of CMS jets from truth particles (classifier AUC ≤ 0.60), Parnassus CMS 2011 paired jets | Li, Noll |
| [#1489](https://github.com/harbor-framework/terminal-bench-science/pull/1489) | SLD central drift chamber performance | dntounis |

None uses Rivet or HEPData. That is the gap.

## Ideas, best first

The author must build and defend the expert reference, so the first task sits in
the author's own field: jet substructure and machine-learning unfolding
(decision 2026-10-09, `decisions.md`).

### 1. Unfold the Lund jet plane (`unfold-lund-plane`)

> Now a suite of tests (response, statistics, model, detector, plus the full
> analysis as capstone): `tbs_proposal_form.md`. Background, dataset decision
> and validation plan: `tbs_proposal_lund_unfolding.md`. Chosen setting: e⁺e⁻ → hadrons with ALEPH
> archived simulation (Electron-Positron Alliance, CC BY 4.0), subject to a
> licence check; fallback CMS open-data jets (Parnassus).

- **Task.** From detector-level pseudo-data, measure the primary Lund jet plane
  density, ρ(ln 1/Δ, ln k_t) per jet, at particle level, with its full
  covariance, written as a HEPData record. The particle-level target is fixed
  by a Rivet routine (as in ATLAS_2020_I1790256). Deliver a frozen pipeline
  that the verifier runs on withheld datasets.
- **Agent gets.** Paired Pythia 8 + Delphes simulation (particle- and
  detector-level jets with constituents); an alternative generator (Herwig 7);
  detector-variation samples (e.g. track efficiency and resolution up and
  down); one development pseudo-dataset with its truth for self-checks.
- **Withheld datasets (about 10).** Each mixes a different true physics model
  (Herwig shower variants, Pythia tune variants, a reweighted region of the
  plane)
  with a detector response drawn inside the variation envelope. The pipeline
  must handle prior dependence and detector systematics, not just closure on
  its own simulation.
- **Verifier.** Computes the true density of each dataset with the Rivet
  routine, then the Gaussian log score of that truth under the submitted values
  and covariance (χ² plus log det Σ, a proper scoring rule, so inflated errors
  cost too), relative to the expert reference on the same dataset; plus a
  coverage check of χ² over the datasets. Pass mark set from the reference and
  one independent expert method (e.g. OmniFold and 2D IBU both pass).
- **Why hard.** The Lund-plane density counts several emissions per jet, so
  efficiencies and fakes live at emission level, and detector and particle
  emissions must be matched.
  Then regularisation, prior dependence on a different true model, detector
  systematics, bootstrap covariances, per-jet normalisation. These are expert
  judgements; the likely agent failures (no prior uncertainty, no bootstrap,
  jet-level instead of emission-level efficiency, wrong normalisation) are
  exactly what the score punishes.
- **Answer not online.** Withheld truths are our own samples.
- **Reference.** The author's OmniFold / IBU code.
- **Compute.** Generation and Delphes on Slurm (a few million dijet events);
  each verifier run capped at minutes per dataset; 2D IBU runs in seconds, so a
  cap does not force a method.
- **Distinct from #2098** (parameter fit) and from Track A (routine writing).

### 2. Generator tuning to HEPData-format measurements (`pythia8-tune`)

Needs a tuning expert as co-author (outside the author's field).

- **Task.** Tune 5–8 Pythia 8 shower and hadronisation parameters to e⁺e⁻ →
  hadrons measurements at 91 GeV, given as Rivet routines with HEPData-format
  pseudo-data made at a hidden parameter point; deliver values and covariance.
- **Verifier.** χ² on withheld Rivet routines against an expert Professor tune,
  and parameter pulls against the hidden truth.
- **Why hard.** Sampling design, surrogates, correlated parameters, MC noise,
  over-fitting, honest errors. Cheap: CPU only.

### 3. Reinterpretation with a published likelihood (`recast-limit`)

- **Task.** For a made-up new-physics model (signal events provided at several
  masses), compute expected and observed 95% CL limits on σ × BR, and the
  excluded mass range, using a published ATLAS search: its HEPData record with
  the full pyhf likelihood, cut-flows and efficiency maps. Signal-region
  selections go in a Rivet routine with detector smearing.
- **Verifier.** Limits against our reference recast (validated on the paper's
  own benchmark cut-flows): per-mass ratio within a set band; excluded mass
  boundary within a set tolerance.
- **Why hard.** Reproducing signal regions with smearing, validating against
  published cut-flows, patching the workspace, CLs. Real work (recasting).
- **Answer not online:** the model is made up. Distinct from Collider-Bench,
  which reproduces published yields.

### 4. Global exclusion from measurements (`contur-exclusion`)

- Variant of 3 using unfolded measurements instead of searches: is a given model
  point excluded by existing LHC measurements (Rivet + HEPData, the Contur
  method)? Contur is developed at UCL (Butterworth, Gütschow;
  [arXiv:2505.09272](https://arxiv.org/abs/2505.09272)). Heavy event
  generation; pre-generated signal events would keep it inside the limits.

### 5. A Rivet routine for a measurement with no public routine

- Track A as a TB-Science task: closure against our private reference on
  hidden events (`track_a/grader`). Verifiable and search-proof until the
  official routine appears.
- **Risk: too easy.** A detailed summary written from the official routine
  spells out every choice, so a strong agent may close exactly. To clear the
  10–20% bar it needs the paper alone and an analysis with subtle particle-level definitions (Lund plane, b-hadron
  labelling, pseudo-tops). Ambiguity does not count as difficulty under the
  rubric.

## Suggested order

1 first: in the author's field, research-level, verifiable, search-proof, and
nobody has it; it also serves as the re-scoped Track B. 3 and 4 need a Rivet
and Contur expert as co-author. 2 only with a tuning expert on board.
