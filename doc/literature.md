# Literature and novelty check

Checked 2026-09-30. Raw notes with every source and all UNCONFIRMED items:
`notes/prior_work.md` (HEP work) and `notes/benchmark_practice.md` (benchmark
practice). This file keeps what bears on the plan.

## The gap

Artificial Analysis's Intelligence Index (v4.3.2) has ten evaluations: agents,
coding, general knowledge, and science reasoning (HLE and CritPt). None of its 31
listed evaluations touches collider data, ROOT or Rivet. The nearest are CritPt,
whose HEP items are theory problems, and Terminal-Bench-Science 0.1, with 17
physical-science tasks and none on particle physics
([AA evaluations](https://artificialanalysis.ai/evaluations)).

CritPt ([arXiv:2509.26574](https://arxiv.org/abs/2509.26574)): 71 research-style
problems, graded by code (numeric tolerance, SymPy, unit tests), with answers held
on a private server. It tests reasoning to a checkable answer. No events, no
detector, no analysis software.

## Closest work

| Work | What it does | How it differs from us |
|---|---|---|
| **AgentRivet** ([arXiv:2606.13535](https://arxiv.org/abs/2606.13535), June 2026; Costa, Doglioni, Pilkington, Sinha at Manchester; Gütschow at UCL) | Fixed four-role LLM pipeline (analyst, coder, code reviewer, physics reviewer) writes Rivet routines from papers. Two analyses (ATLAS Wγ, CMS event shapes), three LLMs, three runs each. | A tool, not a benchmark. It never compiles inside its loop; humans fixed compile errors. Quality judged by eye; only v4 overlays one official routine (Wγ photon pT "within 5%", one 2D distribution 4× low from a bin-width bug). No numeric closure score. Lists "validate against official routines" as future work. |
| **Collider-Bench** ([arXiv:2605.13950](https://arxiv.org/abs/2605.13950), May 2026; Faroughy, Palacios Schweitzer, Pang, Mishra-Sharma, Shih) | Public agent benchmark: recast 10 CMS SUSY search tasks with MG5 + Pythia 8 + Delphes, submit signal-region yields. Scored by relative L2 distance to the published yields. Hidden references, 3 runs, cost per task, and an LLM judge that flags made-up results. No agent reliably beats a physicist-in-the-loop solution. | The reference is the experiment's full-simulation yield, which public tools only approximate, so even a perfect agent has an error floor. Our Track A compares with a human routine on the *same* events, so the floor is zero and every miss is the agent's. Our Track B scores design (the score can exceed 1), not reproduction. Track C has null boxes. |
| **JFC** ([arXiv:2603.20179](https://arxiv.org/abs/2603.20179), MIT, 2026) | Claude Code runs whole analyses on ALEPH, DELPHI and CMS open data from one-line prompts; 8 of 9 results within 2σ of published values. | A demonstration, not a benchmark; single runs. Its authors say a benchmark is still needed that tests "the full analysis chain, from event selection design through statistical inference, on real datasets with known ground truth". That is our Track B. |
| **Agents of Discovery** ([arXiv:2509.08535](https://arxiv.org/abs/2509.08535), 2025) | GPT agents hunt a hidden resonance in the LHC Olympics R&D data; scored on significance improvement, mass and p-value. GPT-5 near human results; strong prompt dependence. | Every data set held a signal. No null runs, so no false-claim rate. Our Track C centres on that. |
| **Gendreau-Distler et al.** ([arXiv:2512.07785](https://arxiv.org/abs/2512.07785), 2025) | Agent inside a fixed Snakemake flow does ATLAS open-data H→γγ, including category choice for expected significance. | Scores exact match with a reference output per step, not significance. |
| **Saito et al.** ([arXiv:2604.14696](https://arxiv.org/abs/2604.14696), 2026) | ATLAS open-data H→ZZ*→4ℓ: extract cuts from the paper, write selection code; event-level match to a hand-written baseline. | Exact event match in at most 3 of 10 runs. One analysis, open-weight models. A good model for a "reproduce the baseline" checkpoint (Track B, step B0). |
| **tZ FCNC case study** ([arXiv:2507.04272](https://arxiv.org/abs/2507.04272), 2025) | o3 picks cuts for t→uZ at FCC-hh: S/√(S+B) of 14.6 against 12.9 for human cuts and 26.7 for a BDT. | The only sigma-scored LLM cut design found. One process, one model, no held-out split. |

Other HEP work (tool-syntax tests, ROOT coding tests, CERN documentation
assistants, generator agents such as MadAgents and ColliderAgent) is narrower. It
is listed in `notes/prior_work.md`, section B.

## Terminal-Bench-Science HEP tasks (checked 2026-10-09)

Six open task PRs in [Terminal-Bench-Science](https://github.com/harbor-framework/terminal-bench-science),
the science suite Artificial Analysis runs, change the verdict below for
Tracks B and C. Details: `tbs_proposals.md`.

| PR | What it grades | Overlap |
|---|---|---|
| [#2098](https://github.com/harbor-framework/terminal-bench-science/pull/2098) H→4ℓ (MIT: Novak, Zhao, Garcia; advisor Harris) | Frozen pipeline on 10 withheld pseudo-datasets (varied m_H, μ incl. 0, detector response); log score of m_H and μ with uncertainties vs truth, relative to an expert reference; GoF, calibrations, compute. No frontier agent passes (best ~57% of reference). | Track B, and more |
| [#2267](https://github.com/harbor-framework/terminal-bench-science/pull/2267) LHC anomaly detection (Noll, Stanford; Li, Yale) | Program reports a look-elsewhere-corrected global significance on 40 hidden dijet boxes, 10 null, mismodelled simulation; reproducibility, no false discovery, sensitivity | Track C |
| [#1258](https://github.com/harbor-framework/terminal-bench-science/pull/1258) generative diphoton search | Data-driven background via generative ML | Part of C |
| [#1020](https://github.com/harbor-framework/terminal-bench-science/pull/1020) adaptive L1 trigger | Trigger design on real CMS 2016 open data | None |
| [#896](https://github.com/harbor-framework/terminal-bench-science/pull/896) detector simulation tuning (Li, Noll) | Fast simulation of CMS jets from truth; classifier AUC ≤ 0.60 vs full simulation (Parnassus CMS 2011 paired jets) | Nearest to an unfolding task (forward, not inverse) |
| [#1489](https://github.com/harbor-framework/terminal-bench-science/pull/1489) SLD drift chamber | Detector performance from transport physics | None |

The #2098 authors state in `task.toml`: "The authors are building a broader,
HEP-dedicated agent benchmark; this task is one part of that planned effort".
This is the group behind JFC. None of the four uses Rivet or HEPData.

## Verdict

**Updated 2026-10-09:** Tracks B and C are no longer new: #2098 and #2267 (above)
cover them, with stronger designs than ours. Track A (Rivet closure) and tasks
built on Rivet and HEPData (tuning, unfolding, reinterpretation) remain open.
The original verdict follows.

No public benchmark scores agents on (A) Rivet closure against a human routine on
the same events, (B) expected significance of a designed selection against the
published one on held-out simulation, or (C) blind search with null samples and a
penalty for false claims. "Agents doing HEP analysis" is not new; the scoring
design and the task set are.

Two teams could close the gap soon: the AgentRivet authors (they list validation
against official routines as next work, and sit in the Rivet GitLab group), and
the Collider-Bench authors. Both are reasons to move fast and to talk to them.
AgentRivet is moving: on 2026-10-09 its repository had a branch
`je-compile-in-reviewloop`, which adds compilation to the review loop, one of
their stated next steps.

## Lessons for task design

From AgentRivet's failure list (all from the paper, v4, sections 5–6):
- Normalisation: 1/N over events in the plot range, or over all fiducial events?
  The paper often does not say.
- Bare against dressed leptons; neutrinos kept in jet inputs; leptons from τ
  decays allowed or not.
- Double-differential histograms booked as 1D slices: Rivet divides by the 1D bin
  width, not the 2D bin area (a factor 4 in their case).
- Neutrino p_z: both solutions filled (a factor 2). W-mass constraint on the wrong
  system.
- Binning guessed from figures when there is no HEPData record.
- Rivet 3 syntax leaking into Rivet 4 code.

These are the mutation classes for grader test V2 and the corners the stress
sample must fill (`validation.md`, `tracks.md`). Where the paper is truly
ambiguous (the normalisation case), the task statement must settle it, or the
grader must accept both readings; otherwise we punish the paper, not the agent.

From benchmark practice (`notes/benchmark_practice.md`):
- Grader in its own container, run after the agent stops (Terminal-Bench, PaperBench).
- No network by default; strip git history from anything shipped (the SWE-bench
  "future commits" leak).
- Fresh answers per run where we can (new seeds, new injected signals), after
  Functional MATH.
- Private test split graded only by us, as CritPt does.
- Agents cheat when they can: o3 patched a scoring function and read answers from
  the call stack (METR); GPT-5 fetched a flag from an online write-up (NIST CAISI).
  Asking them not to has almost no effect.
- At least 3 runs per task; Wilson intervals; paired comparisons
  ([arXiv:2411.00640](https://arxiv.org/abs/2411.00640)).
- Three expert reviewers per task, drop on any flag (SWE-bench Verified dropped 68%
  of the original tasks this way).
- Human baselines timed per task (METR, RE-Bench, PaperBench).

## Read first

1. AgentRivet, [arXiv:2606.13535](https://arxiv.org/abs/2606.13535)
2. Collider-Bench, [arXiv:2605.13950](https://arxiv.org/abs/2605.13950)
3. Agents of Discovery, [arXiv:2509.08535](https://arxiv.org/abs/2509.08535)
4. JFC, [arXiv:2603.20179](https://arxiv.org/abs/2603.20179)
5. LHC Olympics 2020, [arXiv:2101.08320](https://arxiv.org/abs/2101.08320)
