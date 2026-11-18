# Data and tools

Checked 2026-09-30. Raw notes with every source: `notes/data_tools.md`. Items the
notes mark UNCONFIRMED stay unconfirmed here.

## On this machine

| Item | Value |
|---|---|
| Newest LCG view with Rivet and Pythia 8 | `/cvmfs/sft.cern.ch/lcg/views/LCG_110a/x86_64-el9-gcc14-opt` |
| Rivet in that view | 4.1.2 (latest release is 4.1.4, 2026-09-10) |
| Pythia 8 in that view | 8.317 |
| Also in that view | Herwig, Sherpa, MadGraph5_aMC (need the view's `setup.sh`) |
| Apptainer | 1.5.4 |
| Podman | installed (`/usr/bin/podman`) |
| Harbor | v0.24.0 clone at `../harbor`; also `uv tool install harbor` |
| ROOT (system) | 6.40.04 |

So a first container can take the LCG view as is. For others to run the
benchmark, the `hepstore/rivet-*` Docker images (kept by the Rivet authors) are
the portable base: [Docker Hub](https://hub.docker.com/u/hepstore).

## Track A: Rivet

- **Release:** Rivet 4.1.4, 2026-09-10
  ([GitLab](https://gitlab.com/hepcedar/rivet/-/releases/rivet-4.1.4)). Release
  note: [arXiv:2404.15984](https://arxiv.org/abs/2404.15984).
- **Routines:** about 2075 in the repository today, counted by the GitLab API.
  Each routine is `.cc` + `.info` + `.plot` + `.yoda.gz`; the `.info` carries the
  INSPIRE ID that links to HEPData.
- **Dates for the time split:** every routine arrives through a GitLab merge
  request with public dates, and per-file commit history is in the public API. So
  we can list routines merged after any model's cut-off. This makes the A-fresh
  pool practical.
- **Comparing histograms:** `yodadiff` gives numeric diffs with a relative
  tolerance; YODA's built-in χ² is "naive" (no bin correlations). We will write our
  own δ and π metrics (`tracks.md`) on top of the YODA Python API.
- **Reuse of events:** running Rivet on a stored HepMC file is the normal pattern
  ([Pythia manual](https://pythia8.web.cern.ch/manuals/pythia8318/RIVETusage.html)),
  so we generate grader samples once per task.
- **Searches:** Rivet has built-in detector smearing (`SmearedJets`,
  `SmearedParticles`, `SmearedMET`, with ATLAS and CMS functions;
  [arXiv:1910.01637](https://arxiv.org/abs/1910.01637)). Enough for tier A4.

## Track B: simulation and open data

| Source | Content | Licence | Reference code | Fit for Track B |
|---|---|---|---|---|
| ATLAS Open Data, 2020 education release | 10 fb⁻¹ of 2016 data, skimmed ntuples, SM and some BSM simulation | CC0 | Twelve example analyses, including H→γγ and H→ZZ→4ℓ ([list](https://opendata.atlas.cern/docs/documentation/example_analyses/analysis_examples_education_2020)) | Good for a first pilot: small, simple, reference selections exist |
| ATLAS Open Data, research release (2024) | 36 fb⁻¹ of 2015–16 data, PHYSLITE, about 300 simulation samples, 65 TB | CC0 ([portal](https://opendata.cern.ch/docs/atlas-open-data-for-research-release-2024)) | ttbar PHYSLITE tutorial; no Higgs notebook in PHYSLITE found | Realistic but heavy; needs our own reference selections |
| CMS Open Data 2015–16 | MiniAOD and NanoAOD, 2.3 fb⁻¹ (2015); about half of 2016 | CC0; each dataset DOI must be cited | H→4ℓ NanoAOD example ([repo](https://github.com/cms-opendata-analyses/HiggsToFourLeptonsNanoAODOutreachAnalysis)) | Good; separate rules for CMS members (not checked, we are ATLAS) |
| IRIS-HEP Analysis Grand Challenge | ttbar cross-section on CMS 2015 open data, with a full pyhf model and systematics | CMS terms | coffea and RDataFrame reference pipelines ([repo](https://github.com/iris-hep/analysis-grand-challenge)) | Strong: a complete analysis with a known answer. No one has used it to test agents, as far as the search found |
| HiggsML 2014 | 818k simulated H→ττ and background events, AMS metric | CC0 ([record](http://opendata.cern.ch/record/328)) | Kaggle leaderboard gives human scores | Useful human baseline, but winning solutions are public: dev only |
| FAIR Universe HiggsML Uncertainty Challenge (2024–25) | 280M Pythia + Delphes H→ττ events; scored on interval width and coverage | Data on [Zenodo](https://zenodo.org/records/15131565); code licence unconfirmed | Scoring code public ([repo](https://github.com/FAIR-Universe/HEP-Challenge)) | Good model for a systematics-aware score |

For the first pilot, the ATLAS 2020 release is the cheapest start: the reference
H→γγ and H→ZZ→4ℓ selections exist in code, and files are small. Our own Delphes
samples remain the fallback where licence or contamination is a concern.

## Track C: search pseudo-data

- **LHC Olympics 2020** ([arXiv:2101.08320](https://arxiv.org/abs/2101.08320);
  data on [Zenodo](https://doi.org/10.5281/zenodo.3547721)). Black Box 1: Z′→XY
  at 3.8 TeV, 834 signal events in 1M. Black Box 2: no signal, background from
  Herwig++ with a changed Delphes card instead of Pythia. Black Box 3: a KK
  graviton with two decay modes. Box 2 is the pattern for our null boxes and for
  the mismatched background. All answers are public, so these are dev tasks only.
- **2026 extensions:** a larger background sample (22.5M Pythia + 10M Herwig
  dijets, [Zenodo](https://zenodo.org/records/22685072)) and four new signal
  models ([Zenodo](https://zenodo.org/records/18983506)). These could seed our own
  box generator.
- **Dark Machines** ([arXiv:2105.14027](https://arxiv.org/abs/2105.14027)): over
  a billion simulated events for model-free searches. A second source.
- No new formal blind challenge since 2021 was found.

## Statistics and recasting

| Tool | Public | Use here |
|---|---|---|
| [pyhf](https://github.com/scikit-hep/pyhf), [cabinetry](https://github.com/scikit-hep/cabinetry) | Yes | Grader fits for Tracks B and C |
| RooFit / RooStats | Yes, in ROOT | Agent may use; grader need not |
| [TRExFitter](https://gitlab.cern.ch/TRExStats/TRExFitter) | Code readable without CERN login | Agent may use |
| [Combine](https://github.com/cms-analysis/HiggsAnalysis-CombinedLimit) | Yes | Agent may use |
| HEPData pyhf likelihoods | Yes, for a growing set of searches | Reference for search tasks where the experiment published its model |
| MadAnalysis5 PAD, CheckMATE, SModelS | Yes | Reference recasts for A4 and C when no published likelihood exists |

## Cost of event generation

The one hard number found: ATLAS's average over all its generation is about 15
core-seconds per event ([arXiv:2605.12229](https://arxiv.org/abs/2605.12229)), but
that average is dominated by NLO matched samples. Plain LO Pythia 8 is far faster
(an estimate of tens of milliseconds per event, unconfirmed). We should time a
test job on this node before we size the grader samples.
