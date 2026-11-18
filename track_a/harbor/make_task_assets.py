#!/usr/bin/env python3
"""Build the generated assets of the Harbor task from the official reference.

Usage: make_task_assets.py  (run from anywhere; paths derive from this file)
 - environment/BENCH_0001.yoda.gz : reference data, /REF/ATLAS_2019_I1750330/ -> /REF/BENCH_0001/
 - environment/test_events.hepmc.gz, tests/herwig7_ttbar_80ev.hepmc.gz : smoke file,
   the first 80 events of $HEPBENCH_DATA/samples/herwig7_ttbar/herwig7_ttbar_01.hepmc.gz
 - tests/closure.py, tests/reference/ : grader and official reference
 - solution/BENCH_0001.{cc,info,plot} : official routine renamed
"""
import gzip, os, shutil
from pathlib import Path

OLD, NEW = "ATLAS_2019_I1750330", "BENCH_0001"
here = Path(__file__).resolve().parent
ta = here.parent
ref = ta / "references" / OLD
task = here / "tasks" / "atlas-2019-i1750330-resolved1d"
smoke = Path(os.environ["HEPBENCH_DATA"]) / "samples" / "smoke" / "herwig7_ttbar_80ev.hepmc.gz"

data = gzip.decompress((ref / f"{OLD}.yoda.gz").read_bytes()).decode()
assert f"/REF/{OLD}/" in data
data = data.replace(f"/REF/{OLD}/", f"/REF/{NEW}/")
with gzip.open(task / "environment" / f"{NEW}.yoda.gz", "wb") as f:
    f.write(data.encode())

for ext in ("cc", "info", "plot"):
    txt = (ref / f"{OLD}.{ext}").read_text().replace(OLD, NEW)
    (task / "solution" / f"{NEW}.{ext}").write_text(txt)

shutil.copy(smoke, task / "environment" / "test_events.hepmc.gz")
shutil.copy(smoke, task / "tests" / "herwig7_ttbar_80ev.hepmc.gz")
shutil.copy(ta / "grader" / "closure.py", task / "tests" / "closure.py")
shutil.copytree(ref, task / "tests" / "reference", dirs_exist_ok=True)
