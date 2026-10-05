"""Core pilot with HYDRAD: the four paired branches at several waiting times (docs/00, test T3).

Runs A0, B0 and, for every tau, A1 and B1 (src/experiments.py, build_paired_branches) in
one loop and reports, for coronal proxies D (emission measure and EM-weighted temperature
of the T > 1 MK plasma, apex density and temperature, column of the plasma above 3e4 K):

  - pre-test identity: largest relative difference between A1 and B1 profiles before
    the test ramp (0 for a deterministic solver);
  - relaxation of pulse 1 at t_k: A1 versus A0 in state variables, with the tolerances
    STATE_RTOL declared here before any run;
  - the history contrast M_D(tau, t') = (B1 - A1) - (B0 - A0) and its peak;
  - with --sigma, the decision |M| > k sigma_tot and tau* (memory_contrast.tau_star).

HYDRAD is the exploratory route: analytic collisional beam heating and optically thin
losses as shipped.  Its proxies are coronal and do not support chromospheric-line claims.

    scripts/build_hydrad_scratch.sh <scratch HYDRAD dir>
    .venv/bin/python scripts/hydrad_paired_branches.py <scratch HYDRAD dir> \
        [--taus 10 30 60 120] [--length-cm 2.6e9] [--sigma sigma.json]

sigma.json, written before the run, per diagnostic in its own units:
    {"EM_T>1MK": {"numerical": ..., "beam": ..., "observational": ..., "k": 3}, ...}
"""
from __future__ import annotations

import argparse
import json
import math
import os
import shutil
import sys
import time

import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, "..", "src"))
sys.path.insert(0, HERE)
import memory_contrast as mc  # noqa: E402
from experiments import PILOT, PILOT_TAUS, build_paired_branches  # noqa: E402
from hydrad_column_test import diagnostics, load  # noqa: E402
from hydrad_gate_variants import IC_TEMPLATE, run  # noqa: E402

OUT = os.path.join(HERE, "..", "results", "paired_branches_hydrad")
CADENCE = 1.0  # [s] HYDRAD output period: profile i is written at t = i * CADENCE
DIAGNOSTICS = ("EM_T>1MK", "T_EM_T>1MK", "n_apex", "T_apex", "N_cor_leg1_T>30000")
STATE_RTOL = {"N_cor_leg1_T>30000": 0.05, "n_apex": 0.05, "T_apex": 0.05}


def run_branch(hdir: str, exp) -> tuple:
    comp = exp.components[0]
    with open(os.path.join(hdir, "Heating_Model", "config", "beam_heating_model.cfg"), "w") as fh:
        fh.write(comp.table.to_cfg())
    duration = int(math.ceil(comp.t_end_sim - 1e-9))
    with open(os.path.join(hdir, "HYDRAD", "config", "hydrad.cfg"), "w") as fh:
        fh.write("Initial_Conditions/profiles/initial.amr\nInitial_Conditions/profiles/initial.amr.gravity\n"
                 "%d\n%g\n\nPaired branch %s\n" % (duration, CADENCE, exp.name))
    res = os.path.join(hdir, "Results")
    shutil.rmtree(res, ignore_errors=True)
    os.makedirs(res)
    tic = time.time()
    code = run(["./HYDRAD.exe"], hdir, "run_%s.log" % exp.name)
    wall = time.time() - tic
    dest = os.path.join(hdir, "Results_" + exp.name)
    shutil.rmtree(dest, ignore_errors=True)
    os.rename(res, dest)
    idx = sorted(int(f[7:-4]) for f in os.listdir(dest) if f.startswith("profile") and f.endswith(".phy"))
    return dest, idx, dict(exit_code=code, wall_s=wall, last_profile=idx[-1] if idx else -1,
                           expected_last=int(round(duration / CADENCE)), dir=dest)


def series(dest: str, idx: list, length: float) -> tuple:
    """Diagnostics of every profile, stopping at the first profile with NaN."""
    t, rows, nan_at = [], [], None
    for i in idx:
        p = load(dest, i)
        if any(np.isnan(v).any() for v in p.values()):
            nan_at = i * CADENCE
            break
        t.append(i * CADENCE)
        rows.append(diagnostics(p, length))
    keys = set(DIAGNOSTICS) | set(STATE_RTOL)
    return np.array(t), {k: np.array([r[k] for r in rows]) for k in keys}, nan_at


def pretest_difference(dir_a1: str, dir_b1: str, t_limit: float) -> float:
    """Largest relative difference between A1 and B1 profiles at t < t_limit."""
    worst, i = 0.0, 0
    while i * CADENCE < t_limit:
        a = np.loadtxt(os.path.join(dir_a1, "profile%d.phy" % i))
        b = np.loadtxt(os.path.join(dir_b1, "profile%d.phy" % i))
        if a.shape != b.shape:
            return math.inf
        worst = max(worst, float(np.max(np.abs(a - b) / np.maximum(np.abs(a) + np.abs(b), 1e-300))))
        i += 1
    return worst


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    ap.add_argument("hydrad_dir")
    ap.add_argument("--taus", type=float, nargs="+", default=list(PILOT_TAUS))
    ap.add_argument("--length-cm", type=float, default=2.6e9)
    ap.add_argument("--sigma", help="JSON with sigma components per diagnostic, fixed before the run")
    args = ap.parse_args()
    hdir = os.path.abspath(args.hydrad_dir)
    sigma = None
    if args.sigma:  # read before any run, so the decision rule cannot be tuned afterwards
        with open(args.sigma) as fh:
            sigma = json.load(fh)
    os.makedirs(OUT, exist_ok=True)
    exps = {e.name: e for e in build_paired_branches(PILOT, args.taus)}

    with open(os.path.join(hdir, "Initial_Conditions", "config", "initial_conditions.cfg"), "w") as fh:
        fh.write(IC_TEMPLATE.format(L=args.length_cm, apex=0.5 * args.length_cm))
    if run(["./Initial_Conditions.exe"], hdir, "ic.log") != 0:
        raise SystemExit("initial conditions failed; see %s" % os.path.join(hdir, "ic.log"))

    runs, data = {}, {}
    for name, e in exps.items():
        dest, idx, info = run_branch(hdir, e)
        t, d, nan_at = series(dest, idx, args.length_cm)
        info.update(nan_at_s=nan_at, complete=nan_at is None and info["last_profile"] >= info["expected_last"])
        runs[name], data[name] = info, (t, d)
        print("%-18s exit %d  wall %6.0f s  profiles %d/%d  NaN at %s"
              % (name, info["exit_code"], info["wall_s"], info["last_profile"], info["expected_last"], nan_at))

    def at(name: str, key: str, t: float) -> float:
        return float(mc.on_common_grid(data[name][0], data[name][1][key], 0.0, [t])[0])

    t_rel = np.arange(0.0, PILOT.duration + PILOT.tail + 1e-9, CADENCE)
    summary = dict(pilot=dict(PILOT.__dict__), length_cm=args.length_cm, taus_s=args.taus,
                   cadence_s=CADENCE, state_rtol=STATE_RTOL, sigma=sigma, runs=runs, contrasts={})
    for tau in args.taus:
        a1, b1 = "A1_tau%gs" % tau, "B1_tau%gs" % tau
        names = ("A0_no_beam", "B0_test_relaxed", a1, b1)
        bad = [n for n in names if not runs[n]["complete"]]
        if bad:
            summary["contrasts"]["%g" % tau] = {"status": "incomplete runs: " + ", ".join(bad)}
            print("tau = %4g s: incomplete runs (%s); no contrast" % (tau, ", ".join(bad)))
            continue
        tk = exps[b1].marks["test_onset"]
        entry = {"t_k_s": tk,
                 "pretest_max_relative_difference": pretest_difference(
                     runs[a1]["dir"], runs[b1]["dir"], tk - 0.5 * PILOT.ramp),
                 "relaxation_at_t_k": mc.relaxation_check({k: at(a1, k, tk) for k in STATE_RTOL},
                                                          {k: at("A0_no_beam", k, tk) for k in STATE_RTOL},
                                                          STATE_RTOL),
                 "diagnostics": {}}
        for key in DIAGNOSTICS:
            if any(np.isnan(data[n][1][key]).any() for n in names):
                entry["diagnostics"][key] = {"status": "undefined at some times (e.g. no plasma above 1 MK)"}
                continue
            s = {n: mc.on_common_grid(data[n][0], data[n][1][key], exps[n].marks["test_onset"], t_rel)
                 for n in names}
            m = mc.history_contrast(s[b1], s[a1], s["B0_test_relaxed"], s["A0_no_beam"])
            dd0 = s["B0_test_relaxed"] - s["A0_no_beam"]
            entry["diagnostics"][key] = {"t_rel_s": t_rel.tolist(), "M": m.tolist(), "delta_D0": dd0.tolist(),
                                         "peak_abs_M": mc.peak_abs(m), "peak_abs_delta_D0": mc.peak_abs(dd0)}
        summary["contrasts"]["%g" % tau] = entry
        print("tau = %4g s: pre-test diff %.1e, relaxed %s" % (
            tau, entry["pretest_max_relative_difference"], entry["relaxation_at_t_k"]["relaxed"]))
        for key, r in entry["diagnostics"].items():
            if "peak_abs_M" in r:
                print("   %-20s max|M| = %.3e   max|Delta D_0| = %.3e" % (key, r["peak_abs_M"], r["peak_abs_delta_D0"]))
            else:
                print("   %-20s %s" % (key, r["status"]))

    if sigma:
        summary["decision"] = {}
        for key, sg in sigma.items():
            taus_ok = [tau for tau in args.taus
                       if "peak_abs_M" in summary["contrasts"]["%g" % tau].get("diagnostics", {}).get(key, {})]
            if not taus_ok:
                continue
            peaks = [summary["contrasts"]["%g" % tau]["diagnostics"][key]["peak_abs_M"] for tau in taus_ok]
            s_tot = float(mc.combined_sigma(sg["numerical"], sg["beam"], sg["observational"]))
            k = float(sg.get("k", 3.0))
            summary["decision"][key] = dict(sigma_tot=s_tot, k=k, taus_s=taus_ok,
                                            **mc.tau_star(taus_ok, peaks, s_tot, k))
            print("decision %-20s %s" % (key, summary["decision"][key]))

    path = os.path.join(OUT, "summary.json")
    with open(path, "w") as fh:
        json.dump(summary, fh, indent=1, default=float)
    print("written", os.path.normpath(path))


if __name__ == "__main__":
    main()
