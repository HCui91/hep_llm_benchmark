#!/usr/bin/env python3
"""Make planted-bug copies (mutants) of a reference Rivet routine, for grader
test V2/V3 (doc/validation.md).

Each mutant is a list of exact text edits on the reference .cc; every edit
must match the stated number of times, so a mutant cannot silently be a no-op.
`expect` is what a correct grader should say:
  wrong       a real physics error; some histogram must grade wrong
  equivalent  a change too small to matter against the data; no histogram may
              grade wrong (exact is fine)
  either      a choice the paper leaves open; reported, not scored

Usage: make_mutants.py OUTDIR   (writes OUTDIR/<mutant>/NAME.{cc,info,plot}
                                 and OUTDIR/mutants.json)
"""

import json
import shutil
import sys
from pathlib import Path

NAME = "ATLAS_2019_I1750330"
REF = Path(__file__).resolve().parents[1] / "references" / NAME

BOTH_SOLUTIONS_HELPER = """    std::vector<double> computeneutrinozBoth(const FourMomentum& lepton, const FourMomentum& met) const {
      double m_W = 80.399;
      double k = (( sqr( m_W ) - sqr( lepton.mass() ) ) / 2 ) + (lepton.px() * met.px() + lepton.py() * met.py());
      double a = sqr ( lepton.E() )- sqr ( lepton.pz() );
      double b = -2*k*lepton.pz();
      double c = sqr( lepton.E() ) * sqr( met.pT() ) - sqr( k );
      double disc = sqr(b) - 4 * a * c;
      if (disc < 0) return { -b / (2 * a), -b / (2 * a) };
      return { (- b - sqrt(disc)) / (2 * a), (- b + sqrt(disc)) / (2 * a) };
    }


    double computeneutrinoz("""

MUTANTS = [
    dict(name="bare_leptons", expect="wrong",
         desc="Leptons not dressed (cone 0.1 -> 0); AgentRivet failure class",
         edits=[("LeptonFinder dressedelectrons(electrons, photons, 0.1, lep_cuts);",
                 "LeptonFinder dressedelectrons(electrons, photons, 0.0, lep_cuts);", 1),
                ("LeptonFinder dressedmuons(muons, photons, 0.1, lep_cuts);",
                 "LeptonFinder dressedmuons(muons, photons, 0.0, lep_cuts);", 1)]),
    dict(name="no_group_width", expect="wrong",
         desc="2D (grouped) histograms not divided by the outer bin width; AgentRivet failure class",
         edits=[("      divByGroupWidth(_h_multi);\n", "", 1)]),
    dict(name="nu_larger_solution", expect="wrong",
         desc="Neutrino p_z: larger |p_z| solution instead of the smaller",
         edits=[("if (absquad[0] < absquad[1])  pzneutrino = quad[0];",
                 "if (absquad[0] > absquad[1])  pzneutrino = quad[0];", 1)]),
    dict(name="nu_both_solutions", expect="wrong",
         desc="Resolved: histograms filled once per neutrino p_z solution; AgentRivet failure class",
         edits=[("      double pz = computeneutrinoz(lepton->momentum(), met);\n"
                 "      FourMomentum ppseudoneutrino(",
                 "      for (double pz : computeneutrinozBoth(lepton->momentum(), met)) {\n"
                 "      FourMomentum ppseudoneutrino(", 1),
                ('      _d["extrajet_n_norm"]->fill(new_extrajet_multi);\n    }',
                 '      _d["extrajet_n_norm"]->fill(new_extrajet_multi);\n      }\n    }', 1),
                ("    double computeneutrinoz(", BOTH_SOLUTIONS_HELPER, 1)]),
    dict(name="no_tau_leptons", expect="wrong",
         desc="Leptons from tau decays rejected (paper keeps them); AgentRivet failure class",
         edits=[("PromptFinalState electrons(Cuts::abspid == PID::ELECTRON, TauDecaysAs::PROMPT);",
                 "PromptFinalState electrons(Cuts::abspid == PID::ELECTRON, TauDecaysAs::NONPROMPT);", 1),
                ("PromptFinalState muons(Cuts::abspid == PID::MUON, TauDecaysAs::PROMPT);",
                 "PromptFinalState muons(Cuts::abspid == PID::MUON, TauDecaysAs::NONPROMPT);", 1)]),
    dict(name="lepton_pt_25", expect="wrong",
         desc="Lepton pT cut 25 GeV instead of 27 GeV",
         edits=[("(Cuts::pT > 27*GeV);", "(Cuts::pT > 25*GeV);", 1)]),
    dict(name="no_overlap_removal", expect="wrong",
         desc="Lepton-jet overlap removal dropped",
         edits=[("      idiscardIfAnyDeltaRLess(", "      // idiscardIfAnyDeltaRLess(", 4)]),
    dict(name="jet_radius_06", expect="wrong",
         desc="Small-R jets with R = 0.6 instead of 0.4",
         edits=[("FastJets jets_res(vfs_res, JetAlg::ANTIKT, 0.4,",
                 "FastJets jets_res(vfs_res, JetAlg::ANTIKT, 0.6,", 1)]),
    dict(name="xsec_femtobarn", expect="wrong",
         desc="Cross-section in fb instead of pb (pure normalisation bug)",
         edits=[("crossSection()/picobarn / sumOfWeights();",
                 "crossSection()/femtobarn / sumOfWeights();", 1)]),
    dict(name="lepton_pt_27p027", expect="equivalent",
         desc="Lepton pT cut moved by 0.1% (27 -> 27.027 GeV)",
         edits=[("(Cuts::pT > 27*GeV);", "(Cuts::pT > 27.027*GeV);", 1)]),
    dict(name="mw_80p4", expect="equivalent",
         desc="W mass in the neutrino solver 80.399 -> 80.4 GeV",
         edits=[("double m_W = 80.399; // in GeV, given in the paper",
                 "double m_W = 80.4; // in GeV, given in the paper", 1)]),
    dict(name="norm_with_overflow", expect="either",
         desc="1D normalised histograms: 1/N includes overflow events; AgentRivet ambiguity class",
         edits=[('        if (hit.first.find("_norm") != string::npos)  normalize(hit.second, 1.0, false);\n'
                 "        else",
                 '        if (hit.first.find("_norm") != string::npos)  normalize(hit.second, 1.0, true);\n'
                 "        else", 1)]),
]


def main(outdir: Path):
    src = (REF / f"{NAME}.cc").read_text()
    outdir.mkdir(parents=True, exist_ok=True)
    table = []
    for m in MUTANTS:
        text = src
        for old, new, count in m["edits"]:
            found = text.count(old)
            if found != count:
                sys.exit(f"{m['name']}: expected {count} match(es), found {found}: {old[:60]!r}")
            text = text.replace(old, new)
        d = outdir / str(m["name"])
        d.mkdir(exist_ok=True)
        (d / f"{NAME}.cc").write_text(text)
        for ext in ("info", "plot"):
            shutil.copy(REF / f"{NAME}.{ext}", d)
        table.append({k: m[k] for k in ("name", "expect", "desc")})
    (outdir / "mutants.json").write_text(json.dumps(table, indent=1))
    print(f"wrote {len(table)} mutants to {outdir}")


if __name__ == "__main__":
    main(Path(sys.argv[1]))
