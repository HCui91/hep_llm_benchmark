# Open questions

Each answer moves to `decisions.md`.

1. **Network in scored runs.** Proposal (`tracks.md`, "Keeping answers
   private"): no network in any scored run but the model's API host; the
   container holds the paper, HEPData record and docs.
2. **Made-up measurements for Track A.** Proposal: headline Track A tasks are
   measurements we invent and write up as short paper-style specs, plus perturbed
   real tasks.
3. **Who writes reference solutions.** Reference routines (Track A) and
   reference selections (Track B) take an expert a day or more each. Who else
   can write and check them?
4. **Human baselines.** Can PhD students and postdocs do a few tasks under a
   time limit, to set a human score and time per task?
5. **Podman on the batch nodes.** Harbor's Podman backend gives the network
   control scored runs need; its Singularity backend runs on Apptainer but has no
   network control. If the batch nodes lack a working rootless Podman, scored
   runs stay on a host that has one, and the batch queue does event generation
   and grading.
6. **Open-weight model.** Which one to serve first? It must fit one 8×A100 node
   and run a long agent session within a few days.
7. **Re-scope Tracks B and C?** TB-Science PRs #2098 (MIT) and #2267
   (Stanford/Yale) cover them. Proposal: B becomes unfolded measurements, C
   becomes reinterpretation (published likelihoods, Rivet, Contur), so the whole
   benchmark centres on Rivet and HEPData (`tracks.md`, `tbs_proposals.md`).
8. **Sending the TB-Science proposals** (`tbs_proposal_form.md`, the test
   suite): T1 (response), T3 (model) and T4 (detector) go as three proposals;
   T2 only if frontier runs show it is hard; T5 (full analysis) later.
