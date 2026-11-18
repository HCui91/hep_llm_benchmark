# Plan

Version 2, 2026-09-30. Changes from version 1: Tracks B and C go first;
compute and model routes set. Nothing here is decided until it appears in
`decisions.md`.

Output: an arXiv paper and a released benchmark data set.

## Claim

We will build a benchmark that measures how well an AI agent does the daily work
of an LHC analysis PhD student: write analysis code in ROOT, Rivet, C++ and
Python, run it on events, and reach a physics result. Every score is a physics
number computed by a program (histogram closure, expected significance, discovery
and false-claim rates), set against human work on the same inputs.

## Why

Public leaderboards test coding, maths, and knowledge questions. None of the 31
evaluations Artificial Analysis lists touches collider data. The closest physics
test, CritPt, poses research-style problems with a checkable answer, but the model
never runs an analysis: no events, no detector, no statistics, no software stack.

Agents doing HEP analysis is not new (AgentRivet, JFC, Agents of Discovery). One
public benchmark exists, Collider-Bench (May 2026): agents recast CMS SUSY searches
and are scored against published yields. Its reference comes from full simulation
the agent cannot rebuild, so even a perfect agent misses. None of the three scores
below exists yet. JFC's authors ask for Track B in so many words. (Details and
sources: `literature.md`.)

## Approach

Three tracks, each with its own grader (full spec: `tracks.md`):

- **A. Rivet closure.** Paper in, Rivet routine out. Score: agreement of its
  histograms with the human routine's on the same events, in two forms: exact
  logic agreement, and agreement within a tenth of the data uncertainty.
  AgentRivet is the starting point and a natural first entrant.
- **B. Sensitivity.** Simulation and a systematic model in, selection out. Score:
  expected significance on held-out events, over the published selection run on
  the same events.
- **C. Blind search.** Pseudo-data that may hold a hidden signal. Score: hit rate
  minus a penalty for false claims, over many boxes made by a program.

The tracks rise in how much judgement they need. A tests reading and coding
against a fixed spec. B tests analysis design. C tests the whole chain, including
knowing when not to claim a result.

## Harness

- Each task runs in a container built from a Docker image with a pinned stack:
  ROOT, Rivet, Pythia 8, Herwig 7, Delphes, and the Python HEP stack (uproot,
  awkward, hist, pyhf, iminuit, scikit-learn, XGBoost, PyTorch on CPU).
- Grader, reference solutions, held-out events and box truth stay outside the
  container.
- **Harness: Harbor** ([docs](https://docs.harborframework.com/); v0.24.0,
  `uv tool install harbor`). It runs agents in parallel,
  and Artificial Analysis already runs Terminal-Bench through it. Each task is
  `instruction.md`, `task.toml`, an environment, a reference solution and a test
  script; the verifier can run in its own container and writes a numeric reward.
  That matches our rule that the grader sits outside the agent's container.
- **Local backends**, from Harbor's own docs:
  - `podman`: full network control. Use it for scored runs.
  - `singularity` (works with Apptainer, made for Slurm nodes): no network
    control, because the container shares the host network. Development runs
    only.
- **Network rule, per phase** (Harbor sets it in `task.toml`):
  - agent setup: public, to install the agent;
  - agent run: allow-list holding only the model's API host (for example
    `api.anthropic.com`, or our own open-weight model server). The agent must
    reach its model, so "no network" in practice means "nothing but the model";
  - verifier: no network.
  The allow-list on Podman needs nftables support for Harbor's egress sidecar;
  check this with one smoke-test task before building more (open question 5).
- Two kinds of entrant: (1) models inside one fixed minimal scaffold (shell and
  file tools), to compare models fairly; (2) complete agents as shipped (Claude
  Code, Codex CLI, Gemini CLI, AgentRivet), to compare real tools.
- **Models, in order of cost.** (1) Claude Code on a subscription: the pilot
  entrant. Subscription limits cap the number of repeats. (2) Open-weight
  models served on an 8×A100 node, driven through the minimal scaffold: no API
  cost, and a second model family for the paper. (3) Other commercial models,
  once there is money. A paper that tests one model family is weak, so (2)
  matters.
- **Compute.** Event generation, Delphes, grading, and agent containers on a
  Slurm batch queue. GPUs for open-weight models and for trained selections in
  Track B.
- The harness logs transcript, tokens, cost and wall time. A monitor (a language
  model, checked against human reads on a sample) scans every transcript for
  cheating and made-up results, as Collider-Bench does. It can void a run; it
  never adds to a score.
- A canary string sits in every public task file, as a weak extra guard.
- Private tasks run only from accounts with model training off (on consumer
  Claude plans this is the "help improve Claude" setting); the same check for
  every provider. The private split never goes to a public repository.

## Phases

Each phase ends with a go or stop test. A failed test means we fix the design
before we spend more.

### Phase 0: design (to November 2026)
Settle the rest of `open_questions.md`.

Track A tooling comes first (`decisions.md`): the closure grader (`tracks.md`,
Track A) as a plain script, then wrapped as Harbor tasks, then tested against
planted bugs (`validation.md`, V1–V3).

### Phase 1: Track B pilot (from November 2026)
Moved first: its answers live in held-out samples we control, so no one can look
them up (see `tracks.md`, "Keeping answers private").
- Two tasks: H→γγ and H→ZZ*→4ℓ on the ATLAS 2020 open-data release. Its files
  are small and the reference selections exist in code. Fall-back: our own Delphes
  samples. Check first that the simulation has enough events to split into
  training and held-out halves.
- Build the container, harness, systematic model and pyhf grader. Pass V5–V7 and
  H1–H4.
- Run Claude Code and one open-weight model, three repeats each.
- **Go if:** our re-run of the published selection gives a sensible Z₀, an
  over-tuned selection scores worse on held-out events, and scores spread out.

### Phase 2: Track C pilot
- One topology first (dijet resonance, as in the LHC Olympics), 20 boxes, half
  null.
- Pass V8–V10.
- **Go if:** the grader's own search shows the nominal false-claim rate and the
  expected hit rates, and the boxes are neither all easy nor all hopeless for a
  first entrant.

### Phase 3: Track A pilot
- Ten tasks over tiers A1–A3. Headline: four made-up measurements, each a short
  paper-style spec with our reference routine. For the contamination measure:
  three A-dev tasks, each with a perturbed twin (`tracks.md`, "Keeping answers
  private").
- Include AgentRivet's two analyses: ATLAS Wγ
  ([arXiv:2603.22478](https://arxiv.org/abs/2603.22478)), which now has an
  official routine, and CMS event shapes
  ([arXiv:2602.17509](https://arxiv.org/abs/2602.17509)), which needs a reference
  written by us. This gives a direct comparison with their paper.
- Pre-generate grader samples (Pythia 8, Herwig 7, one stress sample) per task.
- Pass V1–V4 in `validation.md`.
- Run three entrants, three repeats each.
- **Go if:** the grader passes its tests, and scores spread out (not all 0, not all
  1), so the track can tell entrants apart.

### Phase 4: scale and publish
- Grow to about 100 tasks over all tracks. With 100 tasks, a success rate near 50%
  has a 95% interval of about ±10 points; ten tasks give about ±30.
- Human baselines on a subset (open question 4).
- Release: public dev split with code, private test split held by us.
- Side output: a few general HEP analysis tasks offered to Terminal-Bench-Science,
  in its own format.
- arXiv paper.

## Risks

| Risk | Effect | What we do |
|---|---|---|
| Reference routines have bugs | Agent marked wrong when right | Expert review of every disagreement; errata log (`tracks.md`) |
| Models have memorised public routines | Track A measures recall, not skill | Headline Track A scores only from made-up measurements; public tasks used to measure the recall gap; memorisation probe; similarity check |
| We leak private tasks through our own runs | Future models train on them | Training off on every account used; private split never published; leaked tasks move to dev |
| Another team publishes first (AgentRivet or Collider-Bench authors) | Less new | Talk to them early; Tracks B and C have no near rival |
| Agents cheat (read grader, fetch answers) | False scores | Grader outside container; network list; transcript audit; H1–H2 |
| Goodhart in Track B: agent tunes to our systematic model | "Better than published" means little | Held-out split; statistics gates; realistic systematics; report as "equal inputs" only |
| Track C boxes too easy (simulation matches data) | Trivial excess-over-simulation wins | Mismatched background generator; data-driven methods needed |
| Cost of long agent runs; subscription limits | Few repeats, wide errors; one model family only | Token and time caps per task; open-weight models on our own GPUs; seek funding; report cost next to score |
| Open-data rules | Cannot publish some tasks | Cite every data set (CC0, `data_and_tools.md`); fall back to our own Delphes samples |
| Software drift (Rivet, ROOT versions) | Old tasks break | Pin versions in the container; version the benchmark |

## Out of scope

- Internal ATLAS or CMS data or software. Everything must be public or made by us.
- Scoring by a language-model judge for any headline number.
- Training or fine-tuning models.
