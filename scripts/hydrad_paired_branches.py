"""Core pilot with HYDRAD: the four paired branches at several waiting times (docs/00, test T3).

Runs, from the same initial atmosphere (src/experiments.py, build_paired_branches):

  A0     no beam, up to the end of the longest window;
  B0     test pulse b on the relaxed atmosphere;
  A1     pulse 1 only, ONCE, up to the end of the longest window (every A1_tau is a
         time window of this run, because the tables differ only in their end time);
  B1     for every tau, a restart from the A1 profile written just before the test
         ramp starts (the same branching by restart that RADYN needs), with b added;
  A1r    the restart check: A1 restarted from the same profile as the first B1,
         without b.  A1r - A1 measures the error introduced by restarting itself.

Branches run in parallel, each in its own copy of the HYDRAD directory.  For coronal
proxies D (emission measure and EM-weighted temperature of the T > 1 MK plasma, apex
density and temperature, column above 3e4 K) it reports, per tau:

  - relaxation of pulse 1 at t_k: A1 versus A0 in state variables, with the
    tolerances STATE_RTOL declared here before any run;
  - the history contrast M_D(tau, t') = (B1 - A1) - (B0 - A0) and its peak;
  - the restart error max |D(A1r) - D(A1)| over the same window;
  - with --sigma, the decision |M| > k sigma_tot and tau* (memory_contrast.tau_star);

and, per run, the total hydrogen column and energy of the loop (closed boundaries:
the column must stay constant).  HYDRAD is the exploratory route: analytic collisional
beam heating and optically thin losses as shipped; its proxies are coronal and do not
support chromospheric-line claims.

    scripts/build_hydrad_scratch.sh <dir> [--linear-restriction] [--no-conservation]
    .venv/bin/python scripts/hydrad_paired_branches.py <dir> [--taus 10 30 60 120] \
        [--length-cm 2.6e9] [--jobs 4] [--label NAME] [--sigma sigma.json]

sigma.json, written before the run, per diagnostic in its own units:
    {"EM_T>1MK": {"numerical": ..., "beam": ..., "observational": ..., "k": 3}, ...}
"""
from __future__ import annotations

import argparse
import json
import math
import os
import shutil
import subprocess
import sys
import time
from concurrent.futures import ThreadPoolExecutor

import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, "..", "src"))
sys.path.insert(0, HERE)
import memory_contrast as mc  # noqa: E402
from experiments import PILOT, PILOT_TAUS, build_paired_branches  # noqa: E402
from hydrad_column_test import diagnostics, load  # noqa: E402
from hydrad_gate_variants import IC_TEMPLATE  # noqa: E402

OUT = os.path.join(HERE, "..", "results", "paired_branches_hydrad")
CADENCE = 1.0  # [s] HYDRAD output period: profile i is written at t ~ i * CADENCE
DIAGNOSTICS = ("EM_T>1MK", "T_EM_T>1MK", "n_apex", "T_apex", "N_cor_leg1_T>30000")
STATE_RTOL = {"N_cor_leg1_T>30000": 0.05, "n_apex": 0.05, "T_apex": 0.05}
MASS_TOL = 0.01  # contrasts are evaluated only while every branch keeps the loop mass within 1 %
OSC_MAX = 0.6    # ... and while T_e changes slope in fewer than 60 % of the cells (no grid-scale oscillation)
K_B, M_P = 1.380649e-16, 1.6726e-24
RUN_TIMEOUT_S = 6 * 3600
SHIPPED_CHROMOSPHERE_CM = 5e8


def ic_config(length_cm: float, chromosphere_cm: float = SHIPPED_CHROMOSPHERE_CM) -> str:
    """Initial-conditions configuration: loop length and depth of the isothermal chromosphere per footpoint.

    The shipped 5 Mm chromosphere drains through the fixed boundary cells after strong
    heating; 8 Mm keeps the loop mass to 0.04 % (docs/07_core_pilot_hydrad.md, Section 6).
    """
    text = IC_TEMPLATE.format(L=length_cm, apex=0.5 * length_cm)
    assert "\n5E8\n" in text
    return text.replace("\n5E8\n", "\n%.4E\n" % chromosphere_cm)


def clone(hdir: str, dest: str) -> None:
    shutil.rmtree(dest, ignore_errors=True)
    subprocess.run(["rsync", "-a", "--exclude", "Results*", "--exclude", "runs", "--exclude", "*.log",
                    "--exclude", "Diag_*", hdir + "/", dest + "/"], check=True)


def run_hydrad(workdir: str, table_cfg: str, start_amr: str, t_end: float, label: str) -> dict:
    """Run HYDRAD in workdir from start_amr to t_end with the given beam table."""
    with open(os.path.join(workdir, "Heating_Model", "config", "beam_heating_model.cfg"), "w") as fh:
        fh.write(table_cfg)
    with open(os.path.join(workdir, "HYDRAD", "config", "hydrad.cfg"), "w") as fh:
        fh.write("%s\nInitial_Conditions/profiles/initial.amr.gravity\n%d\n%g\n\nPaired branch %s\n"
                 % (start_amr, int(math.ceil(t_end - 1e-9)), CADENCE, label))
    res = os.path.join(workdir, "Results")
    shutil.rmtree(res, ignore_errors=True)
    os.makedirs(res)
    tic = time.time()
    try:
        with open(os.path.join(workdir, "run.log"), "w") as fh:
            code = subprocess.run(["./HYDRAD.exe"], cwd=workdir, stdout=fh, stderr=subprocess.STDOUT,
                                  timeout=RUN_TIMEOUT_S).returncode
    except subprocess.TimeoutExpired:
        code = "timeout"
    return dict(exit_code=code, wall_s=time.time() - tic, dir=res, t_end=t_end)


def profile_times(res: str) -> dict:
    """{profile index: time} for every profile written in res (time from the .amr header)."""
    out = {}
    for f in os.listdir(res):
        if f.startswith("profile") and f.endswith(".amr"):
            with open(os.path.join(res, f)) as fh:
                out[int(f[7:-4])] = float(fh.readline())
    return out


def totals(p: dict) -> dict:
    """Total hydrogen column and energy (thermal + kinetic) per unit area of the loop."""
    eth = 1.5 * (p["ne"] * p["te"] + p["nh"] * p["th"]) * K_B
    ek = 0.5 * p["nh"] * M_P * p["v"] ** 2
    return {"N_total": float(np.sum(p["nh"] * p["ds"])), "E_total": float(np.sum((eth + ek) * p["ds"]))}


def series(res: str, length: float) -> tuple:
    """Diagnostics of every profile in time order, stopping at the first profile with NaN."""
    times = profile_times(res)
    t, rows, nan_at = [], [], None
    for i in sorted(times):
        try:
            p = load(res, i)
        except (ValueError, IndexError, OSError):  # a profile cut short when a run was stopped
            break
        if any(np.isnan(v).any() for v in p.values()):
            nan_at = times[i]
            break
        d = diagnostics(p, length)
        d.update(totals(p))
        d["osc_fraction"] = oscillating_fraction(p["te"])
        t.append(times[i])
        rows.append(d)
    keys = rows[0].keys() if rows else ()
    return np.array(t), {k: np.array([r[k] for r in rows]) for k in keys}, nan_at


def oscillating_fraction(te: np.ndarray) -> float:
    """Fraction of cells where dT_e/ds changes sign.  Smooth runs stay near 0.2-0.4; the
    conduction instability of docs/07, Section 2, drives it to ~1 with runaway refinement."""
    te = np.asarray(te, float)
    if te.size < 3:
        return 0.0
    return float(np.sum(np.diff(np.sign(np.diff(te))) != 0) / te.size)


def stable_until(t: np.ndarray, osc: np.ndarray, osc_max: float = OSC_MAX) -> float:
    """Last output time before the first profile with grid-scale oscillation."""
    bad = np.asarray(osc) > osc_max
    if not bad.any():
        return float(t[-1])
    i = int(np.argmax(bad))
    return float(t[i - 1]) if i > 0 else float("-inf")


def mass_valid_until(t: np.ndarray, n_total: np.ndarray, n_ref: float, tol: float = MASS_TOL) -> float:
    """Last output time before the total loop column first departs from n_ref by more than tol.

    The fixed boundary cells of HYDRAD act as a reservoir: when the adaptive grid reaches
    them, the shallow isothermal chromosphere can drain, which is not physical
    (docs/07_core_pilot_hydrad.md).  Contrasts after that time are not used.
    """
    bad = np.abs(np.asarray(n_total) / n_ref - 1.0) > tol
    if not bad.any():
        return float(t[-1])
    i = int(np.argmax(bad))
    return float(t[i - 1]) if i > 0 else float("-inf")


def restart_index(times: dict, t_limit: float, max_gap: float = 2 * CADENCE) -> int:
    """Last profile written strictly before t_limit (the onset of the test ramp).

    It must lie within max_gap of t_limit: a run that stopped or slowed down earlier
    would otherwise silently give a restart state from the wrong time.
    """
    before = {i: t for i, t in times.items() if t < t_limit - 1e-6}
    if not before:
        raise ValueError("no profile before t = %g s" % t_limit)
    i = max(before, key=before.get)
    if t_limit - before[i] > max_gap:
        raise ValueError("last profile before t = %g s is at %g s" % (t_limit, before[i]))
    return i


def numerics(hdir: str) -> list:
    with open(os.path.join(hdir, "HYDRAD", "source", "config.h")) as fh:
        return [ln.strip() for ln in fh if ln.startswith("#define") and not ln.startswith("#define WRITE")]


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    ap.add_argument("hydrad_dir")
    ap.add_argument("--taus", type=float, nargs="+", default=list(PILOT_TAUS))
    ap.add_argument("--length-cm", type=float, default=2.6e9)
    ap.add_argument("--chromosphere-cm", type=float, default=SHIPPED_CHROMOSPHERE_CM,
                    help="depth of the isothermal chromosphere at each footpoint (shipped: 5e8)")
    ap.add_argument("--jobs", type=int, default=4)
    ap.add_argument("--label", default="pilot")
    ap.add_argument("--sigma", help="JSON with sigma components per diagnostic, fixed before the run")
    ap.add_argument("--analyze-only", action="store_true", help="reuse the runs already in <dir>/runs")
    args = ap.parse_args()
    hdir = os.path.abspath(args.hydrad_dir)
    sigma = None
    if args.sigma:  # read before any run, so the decision rule cannot be tuned afterwards
        with open(args.sigma) as fh:
            sigma = json.load(fh)
    out = os.path.join(OUT, args.label)
    os.makedirs(out, exist_ok=True)
    exps = {e.name: e for e in build_paired_branches(PILOT, args.taus)}
    taus = sorted(args.taus)
    a1_long = "A1_tau%gs" % taus[-1]
    half_ramp = 0.5 * PILOT.ramp

    runs_dir = os.path.join(hdir, "runs")
    if args.analyze_only:
        runs = {"A0": exps["A0_no_beam"].components[0].t_end_sim,
                "B0": exps["B0_test_relaxed"].components[0].t_end_sim,
                "A1": exps[a1_long].components[0].t_end_sim}
        for tau in taus:
            end = exps["B1_tau%gs" % tau].marks["test_onset"] + PILOT.duration + PILOT.tail
            runs["B1_tau%gs" % tau] = end
            if tau == taus[0]:
                runs["A1r_tau%gs" % tau] = end
        runs = {n: dict(dir=os.path.join(runs_dir, n, "Results"), t_end=end) for n, end in runs.items()
                if os.path.isdir(os.path.join(runs_dir, n, "Results"))}
        analyze(args, hdir, out, exps, taus, runs, sigma)
        return
    with open(os.path.join(hdir, "Initial_Conditions", "config", "initial_conditions.cfg"), "w") as fh:
        fh.write(ic_config(args.length_cm, args.chromosphere_cm))
    with open(os.path.join(hdir, "ic.log"), "w") as fh:
        if subprocess.run(["./Initial_Conditions.exe"], cwd=hdir, stdout=fh, stderr=subprocess.STDOUT).returncode:
            raise SystemExit("initial conditions failed; see %s" % os.path.join(hdir, "ic.log"))
    os.makedirs(runs_dir, exist_ok=True)
    initial = "Initial_Conditions/profiles/initial.amr"

    def full(name: str, exp_name: str) -> tuple:
        wd = os.path.join(runs_dir, name)
        clone(hdir, wd)
        c = exps[exp_name].components[0]
        return name, run_hydrad(wd, c.table.to_cfg(), initial, c.t_end_sim, name)

    def restart(name: str, exp_name: str, start: str, t_end: float) -> tuple:
        wd = os.path.join(runs_dir, name)
        clone(hdir, wd)
        shutil.copy(start, os.path.join(wd, "start.amr"))
        return name, run_hydrad(wd, exps[exp_name].components[0].table.to_cfg(), "start.amr", t_end, name)

    runs = {}
    with ThreadPoolExecutor(max_workers=args.jobs) as ex:
        for name, info in ex.map(lambda a: full(*a), [("A0", "A0_no_beam"), ("B0", "B0_test_relaxed"),
                                                     ("A1", a1_long)]):
            runs[name] = info
            print("%-10s exit %s  wall %6.0f s" % (name, info["exit_code"], info["wall_s"]), flush=True)
    a1_t, _, a1_nan = series(runs["A1"]["dir"], args.length_cm)
    if a1_nan is not None or not len(a1_t) or a1_t[-1] < runs["A1"]["t_end"] - CADENCE:
        raise SystemExit("A1 did not finish cleanly (NaN at %s s, last clean t = %s s); no restarts"
                         % (a1_nan, a1_t[-1] if len(a1_t) else None))
    a1_times = profile_times(runs["A1"]["dir"])
    jobs = []
    for tau in taus:
        tk = exps["B1_tau%gs" % tau].marks["test_onset"]
        i = restart_index(a1_times, tk - half_ramp)
        start = os.path.join(runs["A1"]["dir"], "profile%d.amr" % i)
        jobs.append(("B1_tau%gs" % tau, "B1_tau%gs" % tau, start, tk + PILOT.duration + PILOT.tail))
        if tau == taus[0]:
            jobs.append(("A1r_tau%gs" % tau, a1_long, start, tk + PILOT.duration + PILOT.tail))
    with ThreadPoolExecutor(max_workers=args.jobs) as ex:
        for name, info in ex.map(lambda a: restart(*a), jobs):
            runs[name] = info
            print("%-10s exit %s  wall %6.0f s" % (name, info["exit_code"], info["wall_s"]), flush=True)
    analyze(args, hdir, out, exps, taus, runs, sigma)


def analyze(args, hdir: str, out: str, exps: dict, taus: list, runs: dict, sigma) -> None:
    data = {}
    for name, info in runs.items():
        t, d, nan_at = series(info["dir"], args.length_cm)
        complete = nan_at is None and len(t) > 0 and t[-1] >= info["t_end"] - CADENCE
        info.update(nan_at_s=nan_at, complete=bool(complete), last_time_s=float(t[-1]) if len(t) else None)
        data[name] = (t, d)
    n_ref = float(data["A0"][1]["N_total"][0])
    for name, info in runs.items():
        t, d = data[name]
        if len(t):
            info["N_total_drift"] = float(d["N_total"][-1] / n_ref - 1.0)
            info["mass_valid_until_s"] = mass_valid_until(t, d["N_total"], n_ref)
            info["stable_until_s"] = stable_until(t, d["osc_fraction"])
            info["valid_until_s"] = min(info["mass_valid_until_s"], info["stable_until_s"])

    def at(name: str, key: str, t: float) -> float:
        return float(mc.on_common_grid(data[name][0], data[name][1][key], 0.0, [t])[0])

    def window(name: str, key: str, onset: float, t_rel: np.ndarray) -> np.ndarray:
        return mc.on_common_grid(data[name][0], data[name][1][key], onset, t_rel)

    t_rel_full = np.arange(0.0, PILOT.duration + PILOT.tail - CADENCE + 1e-9, CADENCE)
    summary = dict(pilot=dict(PILOT.__dict__), length_cm=args.length_cm, chromosphere_cm=args.chromosphere_cm,
                   taus_s=taus, cadence_s=CADENCE,
                   hydrad_numerics=numerics(hdir), state_rtol=STATE_RTOL, mass_tol=MASS_TOL, sigma=sigma,
                   runs={k: {kk: vv for kk, vv in v.items() if kk != "dir"} for k, v in runs.items()},
                   contrasts={})
    t0 = exps["B0_test_relaxed"].marks["test_onset"]
    for tau in taus:
        b1 = "B1_tau%gs" % tau
        tk = exps[b1].marks["test_onset"]
        # A run that stops (NaN) is used up to its last clean profile, like a mass-conservation failure.
        bad = [n for n in ("A0", "B0", "A1", b1) if n not in runs or not len(data[n][0])]
        if bad:
            summary["contrasts"]["%g" % tau] = {"status": "missing runs: " + ", ".join(bad)}
            print("tau = %4g s: missing runs (%s); no contrast" % (tau, ", ".join(bad)))
            continue
        valid = min(runs["A0"]["valid_until_s"] - t0, runs["B0"]["valid_until_s"] - t0,
                    runs["A1"]["valid_until_s"] - tk, runs[b1]["valid_until_s"] - tk)
        t_rel = t_rel_full[t_rel_full <= valid + 1e-9]
        if len(t_rel) < 3:
            summary["contrasts"]["%g" % tau] = {"t_k_s": tk, "status": "no valid window: mass not conserved or "
                                                "grid-scale oscillation (valid to t' = %g s)" % valid}
            print("tau = %4g s: no valid window (mass or stability)" % tau)
            continue
        entry = {"t_k_s": tk, "valid_window_s": [0.0, float(t_rel[-1])],
                 "relaxation_at_t_k": mc.relaxation_check({k: at("A1", k, tk) for k in STATE_RTOL},
                                                          {k: at("A0", k, tk) for k in STATE_RTOL}, STATE_RTOL),
                 "diagnostics": {}}
        check = "A1r_tau%gs" % taus[0]
        for key in DIAGNOSTICS:
            if any(np.isnan(data[n][1][key]).any() for n in ("A0", "B0", "A1", b1)):
                entry["diagnostics"][key] = {"status": "undefined at some times (e.g. no plasma above 1 MK)"}
                continue
            s_b1, s_a1 = window(b1, key, tk, t_rel), window("A1", key, tk, t_rel)
            s_b0, s_a0 = window("B0", key, t0, t_rel), window("A0", key, t0, t_rel)
            m = mc.history_contrast(s_b1, s_a1, s_b0, s_a0)
            r = {"t_rel_s": t_rel.tolist(), "M": m.tolist(), "delta_D0": (s_b0 - s_a0).tolist(),
                 "delta_D1": (s_b1 - s_a1).tolist(), "peak_abs_M": mc.peak_abs(m),
                 "peak_abs_delta_D0": mc.peak_abs(s_b0 - s_a0)}
            if tau == taus[0] and check in runs and len(data[check][0]):
                ok = t_rel <= runs[check]["valid_until_s"] - tk + 1e-9
                if ok.sum() >= 3:
                    r["restart_error_peak"] = mc.peak_abs(window(check, key, tk, t_rel[ok]) - s_a1[ok])
            entry["diagnostics"][key] = r
        summary["contrasts"]["%g" % tau] = entry
        print("tau = %4g s: valid t' <= %g s, relaxed at t_k %s"
              % (tau, t_rel[-1], entry["relaxation_at_t_k"]["relaxed"]))
        for key, r in entry["diagnostics"].items():
            if "peak_abs_M" in r:
                extra = ("   restart error %.2e" % r["restart_error_peak"]) if "restart_error_peak" in r else ""
                print("   %-20s max|M| = %.3e   max|Delta D_0| = %.3e%s"
                      % (key, r["peak_abs_M"], r["peak_abs_delta_D0"], extra))
            else:
                print("   %-20s %s" % (key, r["status"]))

    if sigma:
        summary["decision"] = {}
        for key, sg in sigma.items():
            ok = [tau for tau in taus
                  if "peak_abs_M" in summary["contrasts"]["%g" % tau].get("diagnostics", {}).get(key, {})]
            if not ok:
                continue
            peaks = [summary["contrasts"]["%g" % tau]["diagnostics"][key]["peak_abs_M"] for tau in ok]
            s_tot = float(mc.combined_sigma(sg["numerical"], sg["beam"], sg["observational"]))
            k = float(sg.get("k", 3.0))
            summary["decision"][key] = dict(sigma_tot=s_tot, k=k, taus_s=ok, **mc.tau_star(ok, peaks, s_tot, k))
            print("decision %-20s %s" % (key, summary["decision"][key]))

    series_out = {name: {"t_s": t.tolist(), **{k: v.tolist() for k, v in d.items()}} for name, (t, d) in data.items()}
    with open(os.path.join(out, "series.json"), "w") as fh:
        json.dump(series_out, fh, default=float)
    with open(os.path.join(out, "summary.json"), "w") as fh:
        json.dump(summary, fh, indent=1, default=float)
    print("written", os.path.normpath(out))


if __name__ == "__main__":
    main()
