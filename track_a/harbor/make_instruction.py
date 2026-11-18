#!/usr/bin/env python3
"""Render the analysis summary JSON as the Harbor task instruction.md."""
import json, re
from pathlib import Path
here = Path(__file__).resolve().parent
d = json.loads((here.parent / "summaries" / "ATLAS_2019_I1750330_resolved1d.json").read_text())
out = ["""# Implement a Rivet routine from an analysis summary

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
"""]
def sec(t, b): out.append(f"### {t}\n\n{b}\n")
sec("Beam energy", d["beam_energy"])
sec("Process", d["process"])
sec("Object construction", d["object_construction"])
sec("Cuts", "\n".join(f"{i}. {c}" for i, c in enumerate(d["cuts"], 1)))
sec("Fiducial definition and observables", d["fiducial_definition"])
rows = ["| # | Name | HEPData ID | Definition |", "|---|------|-----------|------------|"]
for i, h in enumerate(d["histograms"], 1):
    assert h["binning_source"] == "HEPDATA" and not h["bin_edges"]
    rows.append(f"| {i} | `{h['name']}` | `{h['hepdata_id']}` | {h['observable_definition'].replace('|', chr(92)+'|')} |")
sec(f"Histograms ({len(d['histograms'])})", "Book each histogram under its HEPData ID. The binning comes from the reference file.\n\n" + "\n".join(rows))
txt = "\n".join(out)
assert not re.search(r"1750330|https?://|hepdata\.net|inspire|arxiv|gitlab", txt, re.I) or print("WARN forbidden text")
(here / "tasks/atlas-2019-i1750330-resolved1d/instruction.md").write_text(txt)
