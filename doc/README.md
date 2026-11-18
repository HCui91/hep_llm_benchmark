# hep_llm_benchmark: documentation

**Goal:** a benchmark that scores AI agents on the real work of an LHC analysis
PhD student: write ROOT, Rivet, C++ and Python code, run it on events, and reach a
physics result. Every score is a physics number from a program, set against human
work on the same inputs. Exact claim: `plan.md`.

**Status (2026-11-18):** Phase 0, design. Track A tooling built in `track_a/`
(closure grader, planted bugs, one Harbor task). Grader tests V1–V3 pass on
two public tt̄ samples: reference exact, 9 of 9 harmful planted bugs caught,
both harmless ones graded equivalent (`validation.md`). Harbor runs on the
development host are blocked by two admin-level limits
(`track_a/harbor/README.md`). TB-Science PRs #2098 and #2267 now cover Tracks
B and C; in their place, a suite of Lund-plane unfolding tests on ALEPH
archived data (`tbs_proposal_form.md`), T3 ready to submit.

**Read first:** `plan.md`, then `tracks.md`, then `open_questions.md`.

## Files

| File | Holds |
|---|---|
| `plan.md` | The current plan: claim, harness, phases with go or stop tests, risks. |
| `tracks.md` | Each track in full: inputs, outputs, grader, metrics, contamination. |
| `validation.md` | Tests the grader and harness must pass, with pass marks fixed in advance. |
| `literature.md` | Closest work, the novelty verdict, and lessons for task design. |
| `tbs_proposals.md` | Terminal-Bench-Science task ideas built on HEPData and Rivet; existing HEP task PRs. |
| `tbs_proposal_lund_unfolding.md` | Full TB-Science proposal draft: Lund-plane unfolding on ALEPH archived data; dataset decision, form fields, validation plan, rubric self-review. |
| `tbs_proposal_form.md` | **Current proposal**: the analysis split into tests T1–T4 (response, statistics, model, detector), paste-ready form text, shared setup. |
| `tbs_proposal_form_full.md` | The single full-analysis proposal (v3.1), kept as the capstone test T5. |
| `data_and_tools.md` | Data, generators and software, checked against primary sources. |
| `decisions.md` | Settled decisions, newest first. |
| `open_questions.md` | Questions still open. |
| `notes/` | Raw research notes with source links. Edited summaries go in the files above. |

## Rules for this folder

- All text for the project lives here as markdown.
- Every fact about a paper, dataset or tool carries a link to its primary source.
- A recommendation stays in `plan.md` or `tracks.md`; it moves to `decisions.md`
  once settled.

## Related code

- AgentRivet ([GitLab](https://gitlab.com/hepcedar/AgentRivet)): writes Rivet
  routines from papers; the closest prior work (`literature.md`).
- Harbor ([docs](https://docs.harborframework.com/)): the harness that runs
  agents on tasks in parallel; `uv tool install harbor`.
