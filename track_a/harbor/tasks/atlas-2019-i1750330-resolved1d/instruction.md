# Implement a Rivet routine from an analysis summary

Write a Rivet 4 routine named `BENCH_0001` that implements the particle-level analysis described below.

Save these files:

- `/app/BENCH_0001.cc` (required): the routine source.
- `/app/BENCH_0001.info`: the analysis metadata.
- `/app/BENCH_0001.plot`: the plot configuration.

`/app/BENCH_0001.yoda.gz` holds the reference data, so `book(h, "d04-x01-y01")` books a histogram with the binning of that reference histogram. Use the HEPData IDs below as histogram names. Rivet 4.1.2 is installed.

You can test the routine on `/app/test_events.hepmc.gz` (a small sample of HepMC events):

```
cd /app
rivet-build RivetBENCH_0001.so BENCH_0001.cc
rivet --pwd -a BENCH_0001 /app/test_events.hepmc.gz
```

Your routine is graded on other events with the same generator setup. The grader compares every histogram bin by bin with a reference routine.

## Analysis summary

### Beam energy

13 TeV proton-proton collisions

### Process

pp -> ttbar, lepton + jets channel (one top decays to b l nu, the other to b q q'; l = e or mu, including e and mu from tau decays)

### Object construction

All objects at particle level, built from stable final-state particles with |eta| < 5. ELECTRONS AND MUONS: prompt (not from hadron decays); leptons from tau decays count as prompt. Each is dressed by adding the four-momenta of all prompt photons (photons not from hadron decays; photons from tau decays are NOT used for dressing) within Delta R < 0.1 of the bare lepton. Keep dressed leptons with pT > 27 GeV and |eta| < 2.5. JETS: anti-kT, R = 0.4, clustered from all final-state particles with |eta| < 5 except (a) prompt electrons and muons together with ALL photons (prompt or not) within Delta R < 0.1 of them, and (b) prompt neutrinos (including neutrinos from tau decays). Muons and neutrinos from hadron decays stay in the jet inputs. Keep jets with pT > 25 GeV and |eta| < 2.5. B-TAGGING: a jet is b-tagged if a B hadron with pT > 5 GeV is ghost-associated to it. MISSING TRANSVERSE MOMENTUM: the negative vector sum of the momenta of all visible final-state particles (no eta cut). OVERLAP REMOVAL: remove any electron or muon within Delta R < 0.4 of a selected jet (the jet is kept).

### Cuts

1. After overlap removal: exactly one electron and no muon, or exactly one muon and no electron
2. Split jets in pT order: the first two b-tagged jets are the b-jets; any further b-tagged jets count as light jets. Require exactly two b-jets (so at least two b-tagged jets)
3. Require at least two light jets
4. No cut on missing transverse momentum or transverse mass

### Fiducial definition and observables

Events passing the cuts. PSEUDO-TOP RECONSTRUCTION: the b-jet closer in Delta R to the lepton is the leptonic b-jet (if equal, the leading b-jet); the other is the hadronic b-jet. The hadronic W is the pair of light jets whose invariant mass is closest to 80.399 GeV (all pairs tried). The neutrino is massless, with px, py from the missing transverse momentum and pz from the W-mass constraint m(l nu) = 80.399 GeV: solve the quadratic in pz; if the discriminant is negative take pz = -b/(2a); otherwise take the solution with the smaller |pz|. Leptonic pseudo-top = dressed lepton + neutrino + leptonic b-jet; hadronic pseudo-top = hadronic b-jet + both W jets; ttbar = sum of the two. ABSOLUTE histograms are differential cross-sections: scale by (generator cross-section in pb) / (sum of event weights) and divide by bin width. NORMALISED histograms are scaled to unit area over the histogram range, overflow excluded.

### Histograms (26)

Book each histogram under its HEPData ID. The binning comes from the reference file.

| # | Name | HEPData ID | Definition |
|---|------|-----------|------------|
| 1 | `top_had_pt` | `d04-x01-y01` | pT of the hadronic pseudo-top (see fiducial_definition), in GeV. Absolute differential cross-section in pb/GeV |
| 2 | `top_had_pt_norm` | `d02-x01-y01` | As top_had_pt, normalised to unit area over the histogram range (overflow not included) |
| 3 | `top_had_abs_y` | `d08-x01-y01` | \|rapidity\| of the hadronic pseudo-top. Absolute differential cross-section |
| 4 | `top_had_abs_y_norm` | `d06-x01-y01` | As top_had_abs_y, normalised to unit area over the histogram range |
| 5 | `leading_top_pt` | `d12-x01-y01` | The larger pT of the two pseudo-tops (hadronic and leptonic), in GeV. Absolute differential cross-section |
| 6 | `leading_top_pt_norm` | `d10-x01-y01` | As leading_top_pt, normalised to unit area over the histogram range |
| 7 | `subleading_top_pt` | `d16-x01-y01` | The smaller pT of the two pseudo-tops, in GeV. Absolute differential cross-section |
| 8 | `subleading_top_pt_norm` | `d14-x01-y01` | As subleading_top_pt, normalised to unit area over the histogram range |
| 9 | `ttbar_m` | `d20-x01-y01` | Invariant mass of the ttbar system (sum of the two pseudo-top four-momenta), in GeV. Absolute differential cross-section |
| 10 | `ttbar_m_norm` | `d18-x01-y01` | As ttbar_m, normalised to unit area over the histogram range |
| 11 | `ttbar_pt` | `d24-x01-y01` | pT of the ttbar system, in GeV. Absolute differential cross-section |
| 12 | `ttbar_pt_norm` | `d22-x01-y01` | As ttbar_pt, normalised to unit area over the histogram range |
| 13 | `abs_pout` | `d28-x01-y01` | \|p_out\| in GeV: the absolute value of the projection of the hadronic pseudo-top three-momentum onto the unit vector (p_lep x z)/\|p_lep x z\|, where p_lep is the leptonic pseudo-top three-momentum and z the beam axis. Absolute differential cross-section |
| 14 | `abs_pout_norm` | `d26-x01-y01` | As abs_pout, normalised to unit area over the histogram range |
| 15 | `delta_phi_tt` | `d32-x01-y01` | Azimuthal angle difference between the two pseudo-tops, in [0, pi]. Absolute differential cross-section |
| 16 | `delta_phi_tt_norm` | `d30-x01-y01` | As delta_phi_tt, normalised to unit area over the histogram range |
| 17 | `ht_tt` | `d36-x01-y01` | Scalar sum of the pT of the two pseudo-tops, in GeV. Absolute differential cross-section |
| 18 | `ht_tt_norm` | `d34-x01-y01` | As ht_tt, normalised to unit area over the histogram range |
| 19 | `extra_jets` | `d40-x01-y01` | Number of extra jets = (number of selected jets, b-tagged or not) - 4. The reference histogram has text bin labels; fill the label "0.0", "1.0", "2.0", "3.0", "4.0" or "5.0" for 0 to 5 extra jets and "$\geq$6.0" for 6 or more. Absolute cross-section in pb per bin (no division by a width) |
| 20 | `extra_jets_norm` | `d38-x01-y01` | As extra_jets, normalised so that the bins sum to one |
| 21 | `ttbar_abs_y` | `d44-x01-y01` | \|rapidity\| of the ttbar system. Absolute differential cross-section |
| 22 | `ttbar_abs_y_norm` | `d42-x01-y01` | As ttbar_abs_y, normalised to unit area over the histogram range |
| 23 | `abs_y_boost` | `d48-x01-y01` | \|y_boost\| = \|y_had + y_lep\| / 2, with y the rapidities of the hadronic and leptonic pseudo-tops. Absolute differential cross-section |
| 24 | `abs_y_boost_norm` | `d46-x01-y01` | As abs_y_boost, normalised to unit area over the histogram range |
| 25 | `chi_tt` | `d52-x01-y01` | chi_tt = exp(\|y_had - y_lep\|), i.e. exp(2\|y*\|) with y* = (y_had - y_lep)/2. Absolute differential cross-section |
| 26 | `chi_tt_norm` | `d50-x01-y01` | As chi_tt, normalised to unit area over the histogram range |
