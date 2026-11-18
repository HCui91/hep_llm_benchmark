# Decisions

Settled decisions, newest first. A recommendation moves here once settled.

## 2026-10-09 (TB-Science)

- **Tasks must sit in the author's field.** The author has to validate the
  reference and the answers, and works on jet substructure and
  machine-learning unfolding, not generator tuning. So the first TB-Science
  task is unfolding (the Lund jet plane), and tuning needs a tuning expert as
  co-author or is dropped (`tbs_proposals.md`).

## 2026-10-09

- **Track A grader first.** Build the closure grader as a plain script, then
  wrap it as Harbor tasks.
- **Harness.** Harbor (`plan.md`, "Harness").

## 2026-09-30

- **Output.** An arXiv paper and a released benchmark data set.
- **Data.** Public data only, cited as each data set asks.
- **Terminal-Bench-Science.** Post some general HEP analysis tasks there,
  while we build the deeper HEP benchmark here.
- **Aim.** A benchmark for AI agents doing LHC analysis work as a PhD researcher
  would, with ROOT, Rivet, C++ and Python; not textbook problems.
- **Directions.** Three: compare AI-written Rivet routines with human ones by
  histogram closure, starting from AgentRivet; score an AI event and object
  selection by the significance it reaches in an existing measurement; search
  for new physics. The detailed designs in `tracks.md` are proposals, not yet
  settled.
