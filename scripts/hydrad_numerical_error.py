"""Numerical error of the history contrast for one waiting time (docs/00, test T4).

Repeats the four branches of one tau with a different HYDRAD build (time-step safety
factor or refinement thresholds, see scripts/build_hydrad_scratch.sh --set) and compares
M_D with the pilot.  A0 and B0 run from the initial atmosphere; A1 and B1 restart from
the pilot's A1 profile just before t_k, so the comparison isolates the numerical error
of the response to the test pulse.  sigma_num(D) = max_t' |M_D(variant) - M_D(pilot)|.

    .venv/bin/python scripts/hydrad_numerical_error.py <variant HYDRAD dir> \
        --pilot results/paired_branches_hydrad/pilot_cond02 --pilot-dir results/hydrad_pilot \
        [--tau 30] [--label NAME]
"""
from __future__ import annotations

import argparse
import json
import os
import sys
from concurrent.futures import ThreadPoolExecutor

import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, "..", "src"))
sys.path.insert(0, HERE)
import hydrad_paired_branches as hp  # noqa: E402
import memory_contrast as mc  # noqa: E402
from experiments import PILOT, build_paired_branches  # noqa: E402


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    ap.add_argument("hydrad_dir")
    ap.add_argument("--pilot", required=True, help="pilot output directory (summary.json, series.json)")
    ap.add_argument("--pilot-dir", required=True, help="pilot HYDRAD directory (holds runs/A1)")
    ap.add_argument("--tau", type=float, default=30.0)
    ap.add_argument("--label", default=None)
    ap.add_argument("--analyze-only", action="store_true", help="reuse the runs already in <dir>/runs")
    args = ap.parse_args()
    hdir = os.path.abspath(args.hydrad_dir)
    label = args.label or os.path.basename(hdir.rstrip("/"))
    with open(os.path.join(args.pilot, "summary.json")) as fh:
        pilot = json.load(fh)
    length = pilot["length_cm"]
    taus = pilot["taus_s"]
    exps = {e.name: e for e in build_paired_branches(PILOT, taus)}
    b1, a1_long = "B1_tau%gs" % args.tau, "A1_tau%gs" % max(taus)
    tk = exps[b1].marks["test_onset"]
    t_end = tk + PILOT.duration + PILOT.tail
    a1_dir = os.path.join(args.pilot_dir, "runs", "A1", "Results")
    i = hp.restart_index(hp.profile_times(a1_dir), tk - 0.5 * PILOT.ramp)
    start = os.path.join(a1_dir, "profile%d.amr" % i)

    specs = [("A0", "A0_no_beam", "initial", exps["B0_test_relaxed"].components[0].t_end_sim),
             ("B0", "B0_test_relaxed", "initial", exps["B0_test_relaxed"].components[0].t_end_sim),
             ("A1r", a1_long, start, t_end), ("B1", b1, start, t_end)]
    runs_dir = os.path.join(hdir, "runs")
    if args.analyze_only:
        runs = {n: dict(dir=os.path.join(runs_dir, n, "Results"), t_end=end) for n, _, _, end in specs}
        report(args, hdir, label, pilot, exps, b1, tk, runs)
        return
    with open(os.path.join(hdir, "Initial_Conditions", "config", "initial_conditions.cfg"), "w") as fh:
        fh.write(hp.ic_config(length, pilot.get("chromosphere_cm", hp.SHIPPED_CHROMOSPHERE_CM)))
    with open(os.path.join(hdir, "ic.log"), "w") as fh:
        hp.subprocess.run(["./Initial_Conditions.exe"], cwd=hdir, stdout=fh, stderr=hp.subprocess.STDOUT, check=True)
    os.makedirs(runs_dir, exist_ok=True)

    def job(spec):
        name, exp_name, start_amr, end = spec
        wd = os.path.join(runs_dir, name)
        hp.clone(hdir, wd)
        if start_amr != "initial":
            hp.shutil.copy(start_amr, os.path.join(wd, "start.amr"))
        amr = "Initial_Conditions/profiles/initial.amr" if start_amr == "initial" else "start.amr"
        return name, hp.run_hydrad(wd, exps[exp_name].components[0].table.to_cfg(), amr, end, name)

    runs = {}
    with ThreadPoolExecutor(max_workers=4) as ex:
        for name, info in ex.map(job, specs):
            runs[name] = info
            print("%-4s exit %s wall %6.0f s" % (name, info["exit_code"], info["wall_s"]), flush=True)
    report(args, hdir, label, pilot, exps, b1, tk, runs)


def report(args, hdir: str, label: str, pilot: dict, exps: dict, b1: str, tk: float, runs: dict) -> None:
    data = {n: hp.series(info["dir"], pilot["length_cm"])[:2] for n, info in runs.items()}

    t0 = exps["B0_test_relaxed"].marks["test_onset"]
    out = {"variant": label, "tau_s": args.tau, "hydrad_numerics": hp.numerics(hdir),
           "runs": {k: {kk: vv for kk, vv in v.items() if kk != "dir"} for k, v in runs.items()}, "sigma_num": {}}
    ref = pilot["contrasts"]["%g" % args.tau]["diagnostics"]
    for key in hp.DIAGNOSTICS:
        if "M" not in ref.get(key, {}):
            continue
        t_rel = np.array(ref[key]["t_rel_s"])  # the pilot's mass-conserving window
        w = lambda n, onset: mc.on_common_grid(data[n][0], data[n][1][key], onset, t_rel)  # noqa: E731
        m = mc.history_contrast(w("B1", tk), w("A1r", tk), w("B0", t0), w("A0", t0))
        diff = m - np.array(ref[key]["M"])
        out["sigma_num"][key] = {"max_abs_diff_M": mc.peak_abs(diff), "pilot_peak_abs_M": ref[key]["peak_abs_M"],
                                 "variant_peak_abs_M": mc.peak_abs(m), "M": m.tolist()}
        print("%-20s max|M_var - M_pilot| = %.3e   pilot max|M| = %.3e"
              % (key, out["sigma_num"][key]["max_abs_diff_M"], ref[key]["peak_abs_M"]))
    path = os.path.join(args.pilot, "numerical_error_%s.json" % label)
    with open(path, "w") as fh:
        json.dump(out, fh, indent=1, default=float)
    print("written", os.path.normpath(path))


if __name__ == "__main__":
    main()
