# Validation: tests the benchmark must pass

Status: draft, 2026-09-30. Pass marks are fixed here, before any model runs, so we
cannot move them to suit a result.

A benchmark score means nothing unless the grader is right. Each test below must
pass before we publish a score from the track it covers.

## Grader tests

| ID | Track | Test | Pass mark |
|---|---|---|---|
| V1 | A | Reference routine against itself, on every grader sample | δ = 0 on every histogram |
| V2 | A | Mutation test: inject known bugs into reference routines. Start from the errors AgentRivet saw (`literature.md`): bare for dressed leptons, neutrinos in jet inputs, τ-decay leptons let in, 2D histogram divided by 1D bin width, both neutrino p_z solutions filled, wrong 1/N. Add: cut value off by a few per cent, off-by-one bin, missing overlap removal, wrong jet radius | Grader flags ≥ 95% of mutants as *wrong*; every mutant that slips through is listed and explained |
| V3 | A | Physics-closure threshold: mutants that the paper's authors would call harmless (for example a 0.1% change in a cut) | Graded *equivalent*, not *wrong* |
| V4 | A | Same routine, different random seeds of the grader samples | Grade unchanged |
| V5 | B | Our re-implementation of the published selection, run on open simulation | Z₀ within the spread we expect from the sample differences (set per task, stated before running) of the open-data reference result, where one exists |
| V6 | B | Selection that uses truth, or skips the trigger | Gate fails |
| V7 | B | Selection over-tuned on the training split on purpose (many tight cuts on few events) | Its held-out score falls clearly below its training score, so the split catches over-tuning |
| V8 | C | Grader's own search on null boxes | False-claim rate matches the nominal rate within the statistical error of the number of boxes |
| V9 | C | Grader's own search on signal boxes | Hit rate close to the expected rate for each band |
| V10 | C | Signal boxes with the injected truth handed to the analysis | Fitted mass and cross-section cover the truth at the stated confidence |

### Results: V1–V3 on ATLAS_2019_I1750330 (2026-10-21)

Two public samples from `track_a/samples/samples.json`, made with the scripts
in `track_a/samples/`: Herwig 7 tt̄ (50k events) and Pythia 8 tt̄ with more
radiation (50k). 230 histograms per sample; worst grade over samples. "exact"
and "pass" are fractions of histograms; π passes below 0.1. The sweep also ran
on a third, non-public sample; this table leaves it out, which changes no
verdict.

| case | expect | exact | pass | wrong | verdict | largest π |
|---|---|---|---|---|---|---|
| reference | exact | 1.00 | 1.00 | 0/230 | ok | |
| bare_leptons | wrong | 0.01 | 0.79 | 49/230 | caught | 1.16 |
| no_group_width | wrong | 0.60 | 0.60 | 92/230 | caught | 6.2e4 |
| nu_larger_solution | wrong | 0.56 | 0.63 | 86/230 | caught | 38.7 |
| nu_both_solutions | wrong | 0.52 | 0.52 | 111/230 | caught | 36.2 |
| no_tau_leptons | wrong | 0.00 | 0.34 | 151/230 | caught | 2.29 |
| lepton_pt_25 | wrong | 0.03 | 0.47 | 122/230 | caught | 1.12 |
| no_overlap_removal | wrong | 0.00 | 0.14 | 198/230 | caught | 2.57 |
| jet_radius_06 | wrong | 0.00 | 0.10 | 206/230 | caught | 22.6 |
| xsec_femtobarn | wrong | 0.50 | 0.50 | 115/230 | caught | 1.7e4 |
| lepton_pt_27p027 | equivalent | 0.36 | 1.00 | 0/230 | ok | 0 |
| mw_80p4 | equivalent | 0.97 | 1.00 | 0/230 | ok | |
| norm_with_overflow | either | 0.97 | 0.99 | 2/230 | – | 5.24 |

- **V1 passes:** the reference closes exactly on all 230 histograms.
- **V2 passes:** 9 of 9 harmful mutants graded *wrong* (pass mark 95%). The
  smallest margin is the lepton cuts: bare leptons and a 25 GeV lepton cut reach
  π ≈ 1.1, ten times the threshold, on normalised pseudo-top histograms
  (ttbar_abs_y_norm, top_had_pt_norm, chi_tt_norm).
- **V3 passes:** both harmless mutants graded *equivalent*, with no histogram
  wrong. A 27.027 GeV lepton cut changes 64% of histograms by single-event
  migrations; noise subtraction removes all of them (largest π 0).
- `norm_with_overflow` changes two histograms (d853, d50) beyond the threshold;
  either grade was allowed.
- Not yet tested: V4 (other seeds), and the mutants from `literature.md` that
  this routine cannot carry (2D histogram divided by a 1D bin width, wrong 1/N
  on a normalised 2D histogram, off-by-one bin).

## Harness tests

| ID | Test | Pass mark |
|---|---|---|
| H1 | Container escape: an agent told to find the reference routine, held-out events or box truth | Finds nothing; attempts show in the log |
| H2 | Network: agent tries to reach GitLab, GitHub, arXiv, HEPData, pip, and any host other than its model's API | Blocked; the model API still works |
| H3 | Same model, same task, five repeats | Spread of scores recorded; used to set the number of repeats |
| H4 | Null agent (does nothing) and trivial agent (copies the template) | Score 0 on every task |
| H5 | Human expert solution, where we have one | Scores at or near the top |

## Score reporting

- Each task runs at least 3 times per entrant, 5 where budget allows. We report
  the mean over runs (pass@1) and pass^k (all k runs pass), which shows
  reliability.
- Each headline number carries a confidence interval: Wilson intervals for pass
  rates, bootstrap over tasks, clustered by task
  ([Miller, arXiv:2411.00640](https://arxiv.org/abs/2411.00640)). Two entrants are
  compared task by task (paired), not by their totals.
- Scores on A-dev are reported apart from A-fresh, A-private and A-perturbed.
- Cost (input, output and cached tokens; dollars) and wall time are reported next
  to every score, agent and grader costs apart.

## Task review

Before a task enters the benchmark, three physicists review it on their own
([as SWE-bench Verified did](https://openai.com/index/introducing-swe-bench-verified/)):
is the instruction clear enough to have one right answer, and does the grader
accept every right answer? One flag from any reviewer sends the task back. Each
reviewer also records how long a PhD student would need; this becomes the task's
length label.
