# TB-Science proposal: unfold the primary Lund jet plane in e⁺e⁻ → hadrons

Version 2, 2026-10-09: dataset settled, ready to submit. Paste-ready form text:
`tbs_proposal_form.md`. Author: Hanfei Cui (jet substructure,
machine-learning unfolding). Checked against the TB-Science
[CONTRIBUTING.md](https://github.com/harbor-framework/terminal-bench-science/blob/main/CONTRIBUTING.md),
the [proposal rubric](https://github.com/harbor-framework/terminal-bench-science/blob/main/rubrics/task-proposal.md)
and every open HEP task in the repository (section 1).

## In short

- **Task.** From ALEPH detector-level events, measure the primary Lund jet
  plane density of e⁺e⁻ → hadrons at 91.2 GeV at particle level, with a full
  covariance. Deliver a frozen pipeline; the verifier runs it on about 10
  withheld pseudo-datasets whose true physics and detector response differ.
- **Dataset (decided).** ALEPH 1994 full simulation (Pythia 6.1, generator and
  reconstructed particles paired event by event) and real data, from the
  Electron-Positron Alliance release,
  [Zenodo 22285585](https://zenodo.org/records/22285585), public under CC BY
  4.0, the licence TB-Science already accepted for the data of #896. Not CERN
  Open Data: no CERN-portal dataset gives e⁺e⁻ simulation with linked truth in
  a usable format (section 3).
- **Now split into tests** (2026-10-10): `tbs_proposal_form.md` holds T1–T4
  (response, statistics, model, detector), each with one deliverable and one
  pass rule; the full analysis below became the capstone T5
  (`tbs_proposal_form_full.md`).
- **Capstone text:** `tbs_proposal_form_full.md` (version 3, after two rubric reviews,
  `notes/tbs_rubric_self_review.md`). It supersedes the form fields in section
  4 below where they differ: full particle-level definition, stated pass rule
  (mean relative log score per bin ≥ −0.15, coverage, validity), truths outside
  the span of the provided samples, 8 minutes × 10 datasets.
- **Validation.** Each withheld dataset is built from simulation, so its
  particle-level truth is known exactly. Score: a log score of the truth under
  the submitted values and covariance, relative to an expert reference on the
  same dataset, plus coverage over the datasets. The reference itself is
  checked by closure, by an independent second method, and on real ALEPH data
  against the published ALEPH thrust (section 5).

---

## 1. HEP tasks already in TB-Science

Checked 2026-10-09 by keyword search over all PRs and issues (unfolding,
OmniFold, Lund plane, jet substructure, ALEPH, LEP, Rivet, HEPData, collider,
open data).

| PR | Task | Authors | Status |
|---|---|---|---|
| [#2098](https://github.com/harbor-framework/terminal-bench-science/pull/2098) | H→4ℓ: m_H and μ with calibrated uncertainties on 10 withheld CMS-open-data pseudo-datasets | Novak, Zhao, Garcia (MIT; Harris) | open; domain and technical review passed |
| [#2267](https://github.com/harbor-framework/terminal-bench-science/pull/2267) | Dijet anomaly detection, global significance on 40 hidden boxes | Noll (Stanford), Li (Yale) | open |
| [#896](https://github.com/harbor-framework/terminal-bench-science/pull/896) | Fast simulation of CMS jets from truth particles; classifier AUC ≤ 0.60 against full simulation; data: Parnassus CMS 2011 paired jets | Li (Stanford/Yale), Noll (Stanford) | open; domain and technical review passed |
| [#1489](https://github.com/harbor-framework/terminal-bench-science/pull/1489) | SLD central drift chamber performance from transport and readout physics | dntounis | open |
| [#1258](https://github.com/harbor-framework/terminal-bench-science/pull/1258) | Generative data-driven background for a diphoton search | qibin2020 | open |
| [#1020](https://github.com/harbor-framework/terminal-bench-science/pull/1020) | Adaptive Level-1 anomaly trigger on CMS 2016 data | Zixind | open |

No unfolding task, no Lund-plane task, no LEP data, no Rivet or HEPData. #896
is the nearest: it is the forward problem (truth → detector) on CMS jets; this
task is the inverse problem with uncertainty quantification, on e⁺e⁻.

**Lessons from the proposal reviews.**
- [#427](https://github.com/harbor-framework/terminal-bench-science/discussions/427)
  (became #896): the automated review accepted it (difficulty "Strong Accept";
  solvability within budget "Uncertain"). Maintainers asked for it to be made
  harder rather than easier.
- [#993](https://github.com/harbor-framework/terminal-bench-science/discussions/993)
  (became #2098): the automated review said **Reject**, because selections,
  likelihood and the pass tolerance were undefined. The physics reviewer (Allen
  Graham Hart) approved anyway, but wants frontier models at 33% or below.
- After approval the PR was due three days later. So build most of the task
  before proposing.

## 2. Why this task

**Prior work on the same observable and data.** The JFC agents (MIT) produced
an ALEPH primary Lund-plane analysis on real data, with code and note public
([Zenodo 20693601](https://zenodo.org/records/20693601),
[GitHub](https://github.com/jfc-mit/analysis_aleph_lund_plane)). The rubric
allows tasks solved "once, or just a few times, before on the internet"; the
instruction forbids using it and the process grader checks. It cannot give the
answers here, which are the truths of private pseudo-datasets, and a pipeline
built for one real-data measurement is not thereby calibrated for shifted true
models and detector responses, which is what the score tests. Disclose it in
the proposal.


- **Real research work.** Unfolding jet substructure to particle level is what
  measurements of the Lund plane (ATLAS, [arXiv:2004.03540](https://arxiv.org/abs/2004.03540))
  and of LEP event shapes with archived data (ALEPH thrust with unbinned ML
  unfolding, [arXiv:2510.22038](https://arxiv.org/abs/2510.22038)) do. No
  collaboration has published a Lund-plane measurement on LEP data; the one
  existing analysis is agent-made (JFC, above).
- **Hard for real reasons.** The density counts several emissions per
  hemisphere, so efficiencies and fakes live at emission level, and the
  detector-level declustering differs from the particle-level one in the same
  event. Then: prior dependence when the truth differs from the training model,
  detector systematics, bootstrap covariances with limited simulation,
  normalisation per hemisphere, sparse corners of a 2D plane.
- **In the author's field**, so the reference and the pass mark can be built
  and defended by the author.

## 3. Dataset decision

| Option | Licence | Paired truth and reco | Real data | Stats | Effort | Overlap |
|---|---|---|---|---|---|---|
| **ALEPH 1994, Electron-Positron Alliance ([Zenodo 22285585](https://zenodo.org/records/22285585))** | CC BY 4.0 mirror; ALEPH policy: archived data for former members and their collaborators, publications labelled "ALEPH Archived Data" ([policy](https://dphep.web.cern.ch/aleph-preservation-policy/)) | **Yes**: trees `t` (reco) and `tgen` (truth) aligned by run and event; `tgenBefore` before selection; per-particle px, py, pz, charge, pid, energy-flow class (checked) | Yes, 1.36M events | ~766k MC events after selection (40 files × 19,158), 34 GB raw | Low: ROOT, uproot | None |
| CMS open-data jets, Parnassus ([Zenodo 11389651](https://zenodo.org/records/11389651)) | CC BY 4.0; accepted by TB-S in #896 | Yes, per jet (truth particles, PF candidates > 1 GeV) | No (separate CMS 2011 jet data exist) | 2.4M jets per pT slice | Low | Same data as #896 |
| DELPHI on the CERN Open Data portal | CC0, official | Not linked; matching left to the analyst | Yes | ~1.6M events (1994–95) | High: old DST formats and software | None |
| Own Pythia/Herwig + Delphes ALEPH card | Ours (CC0) | Yes | No | Unlimited | Medium | None; but a parametric detector |

**Decision: ALEPH via the Electron-Positron Alliance.** It is the only public
e⁺e⁻ full simulation with event-by-event truth in a modern format (checked in
the files: `t` and `tgen` aligned by run and event; `tgenBefore` before
selection), it comes with real data (433,947 events in the first of three data
files, about 1.36M in all), and no TB-Science task uses it. CERN Open Data
loses here: DELPHI is CC0 but in old DST formats without truth links, and the CMS samples are pp with
pileup and need CMSSW processing.

**Licence handling (requirements, not gates).**
- The release is CC BY 4.0, which allows copying and redistribution with
  attribution; TB-Science accepted the same licence for #896's data.
- Attribution: cite PRL 123 (2019) 212002 and the ALEPH collaboration, as the
  Zenodo record asks; carry the label "ALEPH Archived Data" (ALEPH policy) in
  the task README and data card.
- The slimmed copy is mirrored into the TB-Science Hugging Face dataset with
  the same licence and attribution (as #2098 and #2267 do).
- Courtesy: tell the Electron-Positron Alliance (Yen-Jie Lee, Anthony Badea)
  before the PR, and offer co-authorship.

**Risk register** (not an alternative path): should TB-Science maintainers
raise the 2003 ALEPH archive policy despite the CC BY 4.0 release, the same
task can be rebuilt on the author's own Pythia 8 and Herwig 7 samples through
the Delphes ALEPH card (CC0) without changing its design.

**Facts that shape the task.** The generator record holds stable particles only
(no b-hadron history, `bFlag` = −999 in simulation), so flavour-tagged
variants are not possible with this release; the task is inclusive.

## 4. Proposal text (TB-Science form fields)

**Scientific Domain.** Physical Sciences > Physics > Experimental particle
physics.

**Scientific Problem.** Detector unfolding of a jet-substructure observable:
measure the primary Lund jet plane density in e⁺e⁻ → hadrons at √s = 91.2 GeV,
corrected to particle level, with a full covariance, from archived ALEPH
detector-level events. Unfolding turns detector-level measurements into results
that theorists and generator authors can use; it is a core step of every
differential cross-section measurement, and its hard parts (prior dependence,
uncertainty propagation, multi-emission observables) are where real analyses
spend their time.

**Workflow Details.**
- Inputs in the container: a training half of the ALEPH 1994 simulation
  (particle-level and detector-level particles per event, paired by event, plus
  generator events failing the detector selection); generator-level samples of
  other models (Pythia 8, Herwig 7, Sherpa) at particle level only; a stated
  set of detector systematic variations (track efficiency, momentum scale and
  resolution, with their sizes); one development pseudo-dataset with its truth.
- Target, defined exactly in the instruction (with a reference implementation
  of the particle-level definition, and a Rivet routine for reuse): hadronic
  event selection at particle level; hemispheres from the thrust axis; charged
  particles in each hemisphere declustered with the e⁺e⁻ Cambridge algorithm,
  following the harder branch; each primary splitting gives (ln 1/Δθ, ln k_t);
  density ρ = (1/N_hemispheres) dN_emissions / d ln(1/Δθ) d ln k_t in a fixed
  binning.
- Deliverable: `/app/submission/run.sh <dataset> <out>` that writes the density
  and its covariance as a HEPData-format record.
- The agent chooses the method (iterative Bayesian, OmniFold-style unbinned,
  or anything else) and how to estimate uncertainties.

**Evaluation Strategy.**
- The frozen submission runs offline, as an unprivileged user, on about 10
  withheld pseudo-datasets (time cap per dataset). Each is built from the
  withheld half of the simulation (no events shared with the training half):
  events are reweighted at particle level to a different true model (Herwig 7,
  Pythia 8 tunes, Sherpa, reweighted regions of the plane), unweighted, and given
  a detector response drawn inside the stated systematic envelope.
- The truth t of a dataset is the expected particle-level density under its
  true model: the weighted particle-level density over the whole withheld half
  (about ten times a dataset's size), not the truth of the few events in that
  dataset. Its small statistical uncertainty is added to Σ when scoring.
- Per dataset, the verifier compares the submitted density x and covariance Σ
  with the truth t through the Gaussian log score
  −½[(x−t)ᵀΣ⁻¹(x−t) + log det 2πΣ], relative to the expert reference's log
  score on the same dataset. This is a proper scoring rule: overconfident and
  inflated uncertainties both lose.
- Pass: mean relative log score over datasets above a cut set from the
  reference and an independent expert method, and no dataset with a χ²
  p-value below 10⁻³. The agent is told what is scored, not the formula.
- Hard failures: invalid or non-positive-definite covariance, wrong format,
  time-outs, outputs equal to the training prior.
- Time budget: about 10 minutes per dataset on 4 CPUs and one GPU, so the whole
  verifier stays under about 2 hours (#2267 notes a 6-hour limit on the review
  runners for agent plus verifier).

**Dependencies & System Requirements.** Python with uproot, awkward, numpy,
scipy, fastjet (e⁺e⁻ Cambridge), scikit-learn, PyTorch; ROOT and Rivet for the
reference definition. Agent and verifier containers each: 4 CPU cores, 16 GB
memory, one GPU (unbinned ML unfolding, the current standard, needs it inside
the per-dataset time cap; binned methods run on CPU alone). Agent session 4
hours; verifier about 10 minutes per dataset, under 2 hours in all. Data: slimmed ALEPH simulation, about 2 GB in the agent image;
withheld pseudo-datasets about 1 GB, encrypted, verifier image only.

**Dataset.** ALEPH 1994 archived data and Pythia 6.1 full simulation from the
Electron-Positron Alliance (Zenodo 22285585, CC BY 4.0), labelled "ALEPH
Archived Data", slimmed and mirrored to the TB-Science dataset; generator-level
Pythia 8, Herwig 7 and Sherpa samples made by the author. Truths of the
withheld datasets are the author's own and appear nowhere online.

**Complexity.** An expert who knows the method needs one to two weeks; a
second-year PhD student would need longer. Expected failures of frontier
agents: unfolding at jet or hemisphere level instead of emission level, no
prior uncertainty (under-coverage when the truth model changes), no bootstrap
over simulation statistics, wrong normalisation, overconfident covariances.

**References & Resources.** Prior agent-made analysis of the same observable on
real ALEPH data (disclosed; not usable for the withheld truths): JFC,
[arXiv:2603.20179](https://arxiv.org/abs/2603.20179),
[Zenodo 20693601](https://zenodo.org/records/20693601). Lund jet plane: Dreyer, Salam, Soyez,
[arXiv:1807.04758](https://arxiv.org/abs/1807.04758); ATLAS measurement,
[arXiv:2004.03540](https://arxiv.org/abs/2004.03540). OmniFold: Andreassen et
al., [arXiv:1911.09107](https://arxiv.org/abs/1911.09107). Iterative Bayesian
unfolding: D'Agostini, Nucl. Instrum. Meth. A 362 (1995) 487. ALEPH archived
data: PRL 123 (2019) 212002; unbinned thrust,
[arXiv:2510.22038](https://arxiv.org/abs/2510.22038).

**Additional Information.** Conflict of interest to declare: the author is
building a broader HEP agent benchmark (Rivet and HEPData based); this task is
one part of it.

**Author Information.** Hanfei Cui, UCL (ATLAS; thesis work on unfolding the
Lund jet plane). *(Wording to be checked by the author; add co-authors, e.g.
the Electron-Positron Alliance if they join.)*

## 5. How the results are validated

**The answer.** Withheld pseudo-data come from simulation, so the
particle-level truth is exact. Reweighting at particle level keeps the
detector response of each event, so the unfolding problem is well posed: the
response is the one the agent can learn from its half of the simulation, up to
the stated systematic shifts. The reweighter need not be perfect: whatever
weights it gives define the true model of that dataset, and the truth is
computed with the same weights.

**The reference** (author's OmniFold and 2D IBU code):
- closure on independent simulation halves;
- stress tests: each withheld truth recovered within the quoted uncertainty;
- coverage: χ² over the 10 datasets consistent with its degrees of freedom;
- an independent method (2D IBU against OmniFold) passes the same cut;
- real data: the same pipeline unfolds thrust from real ALEPH data and is
  compared with the published ALEPH thrust (HEPData, Rivet routine
  ALEPH_2004_I636645, "Jet rates and event shapes at LEP I and II") and with arXiv:2510.22038. This checks the selection and
  detector handling on real data. The real-data Lund plane is reported, not
  scored.

**The verifier**, before submission:
- oracle (reference) passes on every dataset; `nop` scores zero;
- gaming attempts must fail: returning the training prior; bin-by-bin
  correction factors; detector-level density; covariance scaled by 0.5 or 3;
  development truth copied; a pipeline that memorises training statistics.

**Difficulty**, before proposing: runs of Claude Code and one other frontier
agent; target pass rate at or below a third.

## 6. Self-review against the rubric

| Criterion | Assessment |
|---|---|
| Verifiable | Strong: exact truths, proper scoring rule, no judge. Risk: numerical stability of Σ⁻¹ (require positive definite, cap condition number). |
| Well-specified | Must give the full particle-level definition, binning, output schema and pass rule in words. #993 was rejected by the bot for missing exactly this. |
| Solvable | Reference exists in the author's code; an independent method must also pass. |
| Difficult | Emission-level unfolding with prior and detector uncertainties is PhD-level. Unproven for agents until the frontier runs. |
| Scientifically grounded | Real workflow, unmeasured observable at LEP, archived real detector simulation. |
| Scope | Particle physics. |
| Outcome-verified | Only the delivered density and covariance are scored. |

## 7. Steps

1. Courtesy note to the Electron-Positron Alliance; offer co-authorship
   (section 3).
2. Slim the ALEPH simulation (branches needed only) and split into training and
   withheld halves; Slurm jobs only.
3. Generate particle-level Pythia 8, Herwig 7 and Sherpa samples; train the
   particle-level reweighters; build the withheld pseudo-datasets and truths.
4. Write the particle-level definition (Python and a Rivet routine; check they
   agree with the Track A closure grader).
5. Reference pipelines (OmniFold, 2D IBU) and the verifier; oracle, nop and
   gaming runs.
6. Frontier runs; set the pass cut.
7. Submit the proposal; open the PR within the deadline that follows approval.
