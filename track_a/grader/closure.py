#!/usr/bin/env python3
"""Closure grader for Track A: a candidate Rivet routine against a reference.

Both routines are renamed, built and run in one Rivet pass over the same
events, so any difference between their histograms comes from their logic.
Metrics (doc/tracks.md, Track A):

  logic closure    delta = sum_i |g_i - r_i| / sum_i |r_i|        pass: < 1e-4
  physics closure  pi = max_i (excess_i / |r_i|) / (sigma_i / |d_i|)
                   with d_i, sigma_i the measured value and total uncertainty
                   from the HEPData reference file                  pass: < 0.1
                   excess_i = max(0, |g_i - r_i| - k sqrt(|g_i - r_i| w_i)):
                   the difference less k times its own statistical noise, with
                   w_i = |r_i| / n_i the value per raw entry. If n events move
                   between bins, |g - r| ~ n w and its noise ~ sqrt(n) w, so a
                   bin counts only once about k^2 + 1 events differ (k = 2).

Grades per histogram: exact (delta pass), equivalent (pi pass only), wrong.
A histogram's final grade is its worst grade over all samples.

Run inside the LCG view (needs rivet, rivet-build and the yoda module); see
run_closure.sh.
"""

from __future__ import annotations

import argparse
import gzip
import json
import math
import os
import re
import shutil
import subprocess
import sys
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path

DELTA_PASS = 1e-4
PI_PASS = 0.1
MIN_ENTRIES = 10
NOISE_K = 2.0
GRADE_ORDER = {"exact": 0, "equivalent": 1, "wrong": 2}
PLUGIN_RE = re.compile(r"(?:RIVET_DECLARE_PLUGIN|DECLARE_RIVET_PLUGIN)\s*\(\s*(\w+)\s*\)")


# ---------------------------------------------------------------- metrics

def logic_closure(g: list[float], r: list[float]) -> float:
    """delta: summed absolute difference over summed absolute reference."""
    num = sum(abs(a - b) for a, b in zip(g, r))
    den = sum(abs(b) for b in r)
    if den == 0.0:
        return 0.0 if num == 0.0 else math.inf
    return num / den


def physics_closure(g, r, d, sigma, entries=None, min_entries=MIN_ENTRIES, k=NOISE_K):
    """pi: worst relative difference in units of the relative data uncertainty.

    Bins are skipped when the measured value or its uncertainty is zero or
    missing, or when the reference has fewer than min_entries raw entries.
    With raw entries known, the difference is first reduced by k times its
    statistical noise (module docstring), so that a few events migrating
    across a cut do not fail a harmless change.
    Returns (pi, number of bins used); pi is None when no bin is usable.
    """
    worst, used = None, 0
    for i, (gi, ri) in enumerate(zip(g, r)):
        di, si = d[i], sigma[i]
        if di is None or si is None or di == 0.0 or si <= 0.0:
            continue
        n = entries[i] if entries is not None else None
        if n is not None and n < min_entries:
            continue
        diff = abs(gi - ri)
        if ri == 0.0:
            if gi == 0.0:
                continue
            p = math.inf
        else:
            if n:
                diff = max(0.0, diff - k * math.sqrt(diff * abs(ri) / n))
            p = (diff / abs(ri)) / (si / abs(di))
        used += 1
        worst = p if worst is None else max(worst, p)
    return worst, used


def shape_closure(g, r) -> float:
    """delta after scaling both to unit summed |value|: splits norm from shape bugs."""
    sg, sr = sum(abs(x) for x in g), sum(abs(x) for x in r)
    if sg == 0.0 or sr == 0.0:
        return 0.0 if sg == sr else math.inf
    return logic_closure([x / sg for x in g], [x / sr for x in r])


def grade(delta: float, pi: float | None) -> str:
    if delta < DELTA_PASS:
        return "exact"
    if pi is not None and pi < PI_PASS:
        return "equivalent"
    return "wrong"


def worst(grades: list[str]) -> str:
    return max(grades, key=GRADE_ORDER.__getitem__)


# ---------------------------------------------------------------- yoda access

def bin_labels(obj):
    """Bin edges for a continuous axis, labels for a discrete one."""
    if obj.axisConfig() == "d":
        return [round(x, 9) for x in obj.xEdges()]
    return [str(b.xEdge()) for b in obj.bins()]


def values(obj):
    return [b.val() for b in obj.bins()]


def ref_values(obj):
    vals, errs = [], []
    for b in obj.bins():
        vals.append(b.val())
        try:
            errs.append(b.totalErrAvg())
        except Exception:
            errs.append(None)
    return vals, errs


def raw_entries(objs, path):
    raw = objs.get("/RAW" + path)
    if raw is None or not hasattr(raw.bins()[0], "numEntries"):
        return None
    return [b.numEntries() for b in raw.bins()]


def finalised(objs, name):
    prefix = f"/{name}/"
    return {p[len(prefix):]: o for p, o in objs.items()
            if p.startswith(prefix) and not p[len(prefix):].startswith("_")}


# ---------------------------------------------------------------- build and run

def find_name(cc: Path) -> str:
    m = PLUGIN_RE.search(cc.read_text())
    if not m:
        raise ValueError(f"no RIVET_DECLARE_PLUGIN in {cc}")
    return m.group(1)


def stage(src_dir: Path, ref_dir: Path, name: str, ref_name: str, new: str, dest: Path) -> list[str]:
    """Copy a routine declared as `name` into dest under the name `new`.

    The reference files in ref_dir carry the reference's name `ref_name`, which
    differs from `name` when the candidate uses its own routine name (e.g. a
    neutral benchmark name). Returns notes.
    """
    notes = []
    dest.mkdir(parents=True, exist_ok=True)
    word = re.compile(rf"\b{re.escape(name)}\b")
    ref_word = re.compile(rf"\b{re.escape(ref_name)}\b")
    cc = sorted(src_dir.glob("*.cc"))[0]
    (dest / f"{new}.cc").write_text(word.sub(new, cc.read_text()))
    for ext in ("info", "plot"):
        src = src_dir / f"{name}.{ext}"
        if src.exists():
            (dest / f"{new}.{ext}").write_text(word.sub(new, src.read_text()))
            continue
        src = ref_dir / f"{ref_name}.{ext}"
        if src.exists():
            notes.append(f"{ext} missing; used the reference {ext}")
            (dest / f"{new}.{ext}").write_text(ref_word.sub(new, src.read_text()))
    # Reference data is part of the task input, so both routines get the same file.
    ref_yoda = ref_dir / f"{ref_name}.yoda.gz"
    if ref_yoda.exists():
        text = gzip.open(ref_yoda, "rt").read()
        with gzip.open(dest / f"{new}.yoda.gz", "wt") as f:
            f.write(text.replace(f"/REF/{ref_name}/", f"/REF/{new}/"))
    return notes


def build(dest: Path, new: str, env) -> tuple[bool, str]:
    p = subprocess.run(["rivet-build", f"Rivet{new}.so", f"{new}.cc"], cwd=dest,
                       env=env, capture_output=True, text=True)
    (dest / "build.log").write_text(p.stdout + p.stderr)
    return p.returncode == 0, (p.stdout + p.stderr)[-2000:]


def run_rivet(analyses, files, out: Path, env, nevents=None, xsec=None, timeout=None):
    cmd = ["rivet", "--skip-weights", "-o", str(out)]
    for a in analyses:
        cmd += ["-a", a]
    if nevents:
        cmd += ["-n", str(nevents)]
    if xsec:
        cmd += ["-x", str(xsec)]
    cmd += [str(f) for f in files]
    log = out.with_suffix(".log")
    with open(log, "w") as fh:
        p = subprocess.run(cmd, env=env, stdout=fh, stderr=subprocess.STDOUT, timeout=timeout)
    return p.returncode == 0 and out.exists()


# ---------------------------------------------------------------- comparison

def compare(objs, ref_data, ref_new, cand_new, name, min_entries, select=None):
    """Per-histogram metrics for one sample."""
    refs = finalised(objs, ref_new)
    if select:
        refs = {t: o for t, o in refs.items() if re.search(select, t)}
    cands = finalised(objs, cand_new)
    rows = {}
    for tail, robj in sorted(refs.items()):
        row: dict[str, object] = {"type": type(robj).__name__}
        cobj = cands.get(tail)
        if cobj is None:
            row.update(grade="wrong", reason="missing")
            rows[tail] = row
            continue
        if type(cobj).__name__ != type(robj).__name__ or bin_labels(cobj) != bin_labels(robj):
            row.update(grade="wrong", reason="binning or type differs")
            rows[tail] = row
            continue
        r, g = values(robj), values(cobj)
        row["delta"] = logic_closure(g, r)
        row["delta_shape"] = shape_closure(g, r)
        data = ref_data.get(f"/REF/{name}/{tail}")
        pi, used = None, 0
        if data is not None and bin_labels(data) == bin_labels(robj):
            d, sigma = ref_values(data)
            ent = raw_entries(objs, f"/{ref_new}/{tail}")
            pi, used = physics_closure(g, r, d, sigma, ent, min_entries)
        row["pi"], row["pi_bins"] = pi, used
        row["grade"] = grade(row["delta"], pi)
        rows[tail] = row
    extra = sorted(set(cands) - set(refs))
    return rows, extra


def jsonable(x):
    if isinstance(x, float) and not math.isfinite(x):
        return "inf" if x > 0 else "-inf"
    if isinstance(x, dict):
        return {k: jsonable(v) for k, v in x.items()}
    if isinstance(x, list):
        return [jsonable(v) for v in x]
    return x


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--reference", required=True, type=Path, help="dir with NAME.cc/.info/.plot/.yoda.gz")
    ap.add_argument("--candidate", required=True, type=Path, help="dir with the candidate .cc (+ .info/.plot)")
    ap.add_argument("--samples", required=True, type=Path,
                    help="samples.json manifest; file paths may use $VARS such as $HEPBENCH_DATA")
    ap.add_argument("--only", nargs="*", default=None, help="sample names to use (default: all)")
    ap.add_argument("--nevents", type=int, default=None, help="max events per sample")
    ap.add_argument("--max-files", type=int, default=None, help="max files per sample")
    ap.add_argument("--min-entries", type=int, default=MIN_ENTRIES)
    ap.add_argument("--select", default=None,
                    help="regex on histogram names (e.g. d04-x01-y01): grade only those the task asks for")
    ap.add_argument("--workdir", required=True, type=Path)
    ap.add_argument("--out", required=True, type=Path, help="report JSON")
    ap.add_argument("--reward", type=Path, default=None, help="optional Harbor-style reward.json")
    ap.add_argument("--timeout", type=int, default=None, help="seconds per Rivet run")
    args = ap.parse_args(argv)

    import yoda  # type: ignore[import-not-found]  # from the LCG view

    name = find_name(next(args.reference.glob("*.cc")))
    cand_cc = sorted(args.candidate.glob("*.cc"))
    if len(cand_cc) != 1:
        report = {"analysis": name, "status": "no_candidate" if not cand_cc else "several_candidates",
                  "build": False, "pass_fraction": 0.0, "exact_fraction": 0.0,
                  "notes": [f"{len(cand_cc)} .cc files in {args.candidate}; need exactly one"]}
        return finish(report, args)
    try:
        cand_name = find_name(cand_cc[0])
    except ValueError as e:
        report = {"analysis": name, "status": "no_plugin_declaration", "build": False,
                  "pass_fraction": 0.0, "exact_fraction": 0.0, "notes": [str(e)]}
        return finish(report, args)
    ref_new, cand_new = f"{name}_GRADEREF", f"{name}_GRADECAND"
    work = args.workdir.resolve()
    if work.exists():
        shutil.rmtree(work)
    rdir, cdir = work / "ref", work / "cand"

    report = {"analysis": name, "candidate_plugin_name": cand_name, "select": args.select, "notes": []}
    stage(args.reference, args.reference, name, name, ref_new, rdir)
    report["notes"] += stage(args.candidate, args.reference, cand_name, name, cand_new, cdir)
    if cand_name != name:
        report["notes"].append(f"candidate declares {cand_name}, reference {name}")

    env = dict(os.environ)
    path = f"{rdir}:{cdir}"
    env["RIVET_ANALYSIS_PATH"] = path + (":" + env["RIVET_ANALYSIS_PATH"] if env.get("RIVET_ANALYSIS_PATH") else "")
    env["RIVET_DATA_PATH"] = path + (":" + env["RIVET_DATA_PATH"] if env.get("RIVET_DATA_PATH") else "")

    ok, log = build(rdir, ref_new, env)
    if not ok:
        sys.exit(f"reference failed to build:\n{log}")
    ok, log = build(cdir, cand_new, env)
    report["build"] = ok
    if not ok:
        report.update(status="build_failed", build_log_tail=log, pass_fraction=0.0, exact_fraction=0.0)
        return finish(report, args)

    samples = json.loads(args.samples.read_text())
    if args.only:
        samples = [s for s in samples if s["name"] in args.only]
    ref_data = yoda.read(str(args.reference / f"{name}.yoda.gz")) \
        if (args.reference / f"{name}.yoda.gz").exists() else {}

    def one(s):
        files = s["files"][: args.max_files] if args.max_files else s["files"]
        files = [os.path.expandvars(f) for f in files]  # e.g. $HEPBENCH_DATA/...
        out = work / f"{s['name']}.yoda.gz"
        ok = run_rivet([ref_new, cand_new], files, out, env, args.nevents,
                       None if s.get("cross_section_pb") else s.get("xsec_override_pb"), args.timeout)
        if not ok:
            # Tell a candidate crash apart from a broken sample.
            ref_ok = run_rivet([ref_new], files, work / f"{s['name']}.refonly.yoda.gz", env,
                               min(args.nevents or 1000, 1000), None, args.timeout)
            return s["name"], {"status": "candidate_run_failed" if ref_ok else "sample_failed"}, None
        rows, extra = compare(yoda.read(str(out)), ref_data, ref_new, cand_new, name,
                              args.min_entries, args.select)
        return s["name"], {"status": "ok", "extra_candidate_objects": extra}, rows

    with ThreadPoolExecutor(max_workers=len(samples) or 1) as pool:
        results = list(pool.map(one, samples))

    report["samples"] = {n: info for n, info, _ in results}
    per_hist: dict[str, dict] = {}
    for sname, info, rows in results:
        if info["status"] == "sample_failed":
            sys.exit(f"reference failed on sample {sname}; see {work}/{sname}.refonly.yoda.log")
        if rows is None:
            continue
        for tail, row in rows.items():
            per_hist.setdefault(tail, {})[sname] = row

    if any(info["status"] == "candidate_run_failed" for _, info, _ in results):
        report.update(status="candidate_run_failed", pass_fraction=0.0, exact_fraction=0.0)
        return finish(report, args)

    final = {t: worst([r["grade"] for r in rows.values()]) for t, rows in per_hist.items()}
    n = len(final) or 1
    report.update(
        status="ok",
        n_histograms=len(final),
        exact_fraction=sum(g == "exact" for g in final.values()) / n,
        pass_fraction=sum(g != "wrong" for g in final.values()) / n,
        grades=final,
        histograms=per_hist,
    )
    return finish(report, args)


def finish(report, args):
    args.out.parent.mkdir(parents=True, exist_ok=True)
    args.out.write_text(json.dumps(jsonable(report), indent=1))
    if args.reward:
        args.reward.parent.mkdir(parents=True, exist_ok=True)
        args.reward.write_text(json.dumps({
            "pass_fraction": report.get("pass_fraction", 0.0),
            "exact_fraction": report.get("exact_fraction", 0.0),
            "build": 1.0 if report.get("build") else 0.0,
        }))
    print(json.dumps({k: report.get(k) for k in
                      ("analysis", "status", "n_histograms", "exact_fraction", "pass_fraction", "notes")}))
    return 0


if __name__ == "__main__":
    sys.exit(main())
