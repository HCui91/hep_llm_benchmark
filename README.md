# hep_llm_benchmark

A benchmark that gives AI agents real LHC analysis tasks in the field's own
tools (ROOT, Rivet, C++, Python) and scores each task by a physics number that a
program computes. Draft, design stage.

## Tracks

- **A. Rivet closure.** Paper in, Rivet routine out. Score: how well its
  histograms agree with a human-written routine's on the same events.
- **B. Sensitivity.** Simulation and a systematic model in, event selection
  out. Score: expected significance on held-out events, over the published
  selection run on the same events.
- **C. Blind search.** Many pseudo-datasets, some with a hidden signal and some
  with none. Score: hit rate less a penalty for each false discovery claim.

## Making the score hard to game

- Pass marks are fixed before any model runs (`doc/validation.md`).
- The grader must flag at least 95% of deliberately broken analysis routines
  and pass harmless changes. Done for one routine: 9 of 9 harmful bugs caught,
  2 of 2 harmless ones passed.
- Planned harness tests check that an agent that does nothing scores zero and
  that an agent told to find the answers cannot reach them.
- The grader, reference solutions and held-out data stay outside the agent's
  container; in scored runs the agent can reach only its model's API.
- Track C measures how often an agent claims a discovery that is not there.
- A transcript monitor can void a run for cheating; it never raises a score.

## Layout

- `doc/`: the design. Start with `doc/README.md`, then `doc/plan.md` and
  `doc/tracks.md`.
- `track_a/grader/`: the closure grader.
- `track_a/mutants/`: planted bugs and the sweep that tests the grader.
- `track_a/samples/`: scripts that generate the public grader samples.
- `track_a/harbor/`: one Track A task in [Harbor](https://docs.harborframework.com/) format.
- `track_a/references/`: the reference routine, copied from Rivet.

## Running the Track A grader

Needs the LCG_110a view on CVMFS (Rivet 4.1.2). Event samples are not in git;
set `HEPBENCH_DATA` to the directory that holds them (`track_a/samples/`).

    export HEPBENCH_DATA=/path/to/data
    track_a/grader/run_closure.sh --reference track_a/references/ATLAS_2019_I1750330 \
      --candidate DIR --samples track_a/samples/samples.json \
      --workdir /tmp/grade --out report.json

## Licence

No licence chosen yet. `track_a/references/ATLAS_2019_I1750330/` comes from
[Rivet](https://gitlab.com/hepcedar/rivet) (GPL-3.0) and its reference data
from [HEPData](https://www.hepdata.net/).
