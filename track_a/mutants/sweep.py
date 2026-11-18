#!/usr/bin/env python3
"""Grader tests V1-V3: grade the reference against itself and every mutant,
then tabulate what the grader said against what it should say.

Usage (inside the LCG view, e.g. via track_a/grader/run_closure.sh's setup):
  sweep.py slurm   --mutants DIR --samples samples.json --work DIR [--nevents N] [--mem 8G]
  sweep.py run     --mutants DIR --samples samples.json --work DIR [--parallel 2] [--nevents N]
  sweep.py summary --mutants DIR --work DIR [--markdown FILE]
"""

import argparse
import json
import shlex
import subprocess
import sys
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path

HERE = Path(__file__).resolve().parent
GRADER = HERE.parent / "grader" / "run_closure.sh"
REF = HERE.parent / "references" / "ATLAS_2019_I1750330"


def cases(mutants_dir: Path):
    table = json.loads((mutants_dir / "mutants.json").read_text())
    yield {"name": "reference", "expect": "exact", "desc": "V1: reference against itself"}, REF
    for m in table:
        yield m, mutants_dir / m["name"]


def run(args):
    def one(item):
        m, cand = item
        out = args.work / "reports" / f"{m['name']}.json"
        if out.exists() and not args.force:
            return m["name"], "cached"
        cmd = [str(GRADER), "--reference", str(REF), "--candidate", str(cand),
               "--samples", str(args.samples), "--workdir", str(args.work / "runs" / m["name"]),
               "--out", str(out)]
        if args.nevents:
            cmd += ["--nevents", str(args.nevents)]
        p = subprocess.run(cmd, capture_output=True, text=True)
        (args.work / "logs").mkdir(parents=True, exist_ok=True)
        (args.work / "logs" / f"{m['name']}.log").write_text(p.stdout + p.stderr)
        return m["name"], "ok" if p.returncode == 0 else f"exit {p.returncode}"

    with ThreadPoolExecutor(max_workers=args.parallel) as pool:
        for name, status in pool.map(one, list(cases(args.mutants))):
            print(f"{name}: {status}", flush=True)


SBATCH = """#!/bin/bash
#SBATCH --job-name=closure_sweep
#SBATCH --partition={partition}
#SBATCH --array=0-{last}
#SBATCH --cpus-per-task={cpus}
#SBATCH --mem={mem}
#SBATCH --time={time}
#SBATCH --output={work}/logs/%a.log
set -eo pipefail
CASES=({cases})
CANDS=({cands})
NAME=${{CASES[$SLURM_ARRAY_TASK_ID]}}
{grader} --reference {ref} --candidate ${{CANDS[$SLURM_ARRAY_TASK_ID]}} \\
  --samples {samples} --workdir {work}/runs/$NAME --out {work}/reports/$NAME.json {extra}
rm -rf {work}/runs/$NAME/ref {work}/runs/$NAME/cand
"""


def slurm(args):
    """One Slurm array task per case; heavy runs belong on the batch queue."""
    items = list(cases(args.mutants))
    (args.work / "logs").mkdir(parents=True, exist_ok=True)
    (args.work / "reports").mkdir(parents=True, exist_ok=True)
    extra = f"--nevents {args.nevents}" if args.nevents else ""
    script = SBATCH.format(
        partition=args.partition, last=len(items) - 1, cpus=args.cpus, mem=args.mem, time=args.time,
        work=args.work, cases=" ".join(shlex.quote(m["name"]) for m, _ in items),
        cands=" ".join(shlex.quote(str(c)) for _, c in items), grader=GRADER, ref=REF,
        samples=args.samples, extra=extra)
    path = args.work / "sweep.sbatch"
    path.write_text(script)
    out = subprocess.run(["sbatch", str(path)], capture_output=True, text=True)
    print(out.stdout.strip() or out.stderr.strip())


def verdict(expect, rep):
    if rep.get("status") != "ok":
        return f"grader status {rep.get('status')}"
    n_wrong = sum(g == "wrong" for g in rep["grades"].values())
    n_exact = sum(g == "exact" for g in rep["grades"].values())
    if expect == "exact":
        return "ok" if n_exact == rep["n_histograms"] else "FAIL"
    if expect == "wrong":
        return "caught" if n_wrong else "MISSED"
    if expect == "equivalent":
        return "ok" if n_wrong == 0 else "FALSE ALARM"
    return "-"


def worst_hists(rep, k=3):
    rows = []
    for tail, per in rep.get("histograms", {}).items():
        pis = [r.get("pi") for r in per.values() if isinstance(r.get("pi"), (int, float))]
        infs = any(r.get("pi") == "inf" for r in per.values())
        rows.append((float("inf") if infs else max(pis, default=-1.0), tail))
    rows.sort(reverse=True)
    return ", ".join(f"{t} ({'inf' if p == float('inf') else f'{p:.2f}'})" for p, t in rows[:k] if p > 0)


def summary(args):
    lines = ["| case | expect | exact | pass | wrong | verdict | largest pi |",
             "|---|---|---|---|---|---|---|"]
    for m, _ in cases(args.mutants):
        f = args.work / "reports" / f"{m['name']}.json"
        if not f.exists():
            lines.append(f"| {m['name']} | {m['expect']} | | | | not run | |")
            continue
        rep = json.loads(f.read_text())
        n = rep.get("n_histograms") or 0
        n_wrong = sum(g == "wrong" for g in rep.get("grades", {}).values())
        lines.append(f"| {m['name']} | {m['expect']} | {rep.get('exact_fraction', 0):.2f} | "
                     f"{rep.get('pass_fraction', 0):.2f} | {n_wrong}/{n} | {verdict(m['expect'], rep)} | "
                     f"{worst_hists(rep)} |")
    text = "\n".join(lines)
    print(text)
    if args.markdown:
        args.markdown.write_text(text + "\n")


def main():
    ap = argparse.ArgumentParser()
    sub = ap.add_subparsers(dest="cmd", required=True)
    r = sub.add_parser("run")
    r.add_argument("--mutants", type=Path, required=True)
    r.add_argument("--samples", type=Path, required=True)
    r.add_argument("--work", type=Path, required=True)
    r.add_argument("--parallel", type=int, default=2)
    r.add_argument("--nevents", type=int, default=None)
    r.add_argument("--force", action="store_true")
    b = sub.add_parser("slurm")
    b.add_argument("--mutants", type=Path, required=True)
    b.add_argument("--samples", type=Path, required=True)
    b.add_argument("--work", type=Path, required=True)
    b.add_argument("--nevents", type=int, default=None)
    b.add_argument("--partition", default="short")
    b.add_argument("--cpus", type=int, default=4)
    b.add_argument("--mem", default="8G")
    b.add_argument("--time", default="06:00:00")
    s = sub.add_parser("summary")
    s.add_argument("--mutants", type=Path, required=True)
    s.add_argument("--work", type=Path, required=True)
    s.add_argument("--markdown", type=Path, default=None)
    args = ap.parse_args()
    {"run": run, "slurm": slurm, "summary": summary}[args.cmd](args)


if __name__ == "__main__":
    sys.exit(main())
