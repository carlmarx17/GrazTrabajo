"""Which flares keep enough memory? HYDRAD variants of the decision gate.

For each variant, runs HYDRAD with pulse 1 only, up to the onset of pulse 2, measures the
column of the plasma hotter than 3e4 K (ionized corona + transition region) and the
coronal temperature and emission measure, and feeds them to the toy inject-reinfer model.

Needs a HYDRAD build with BEAM_HEATING (Initial_Conditions.exe and HYDRAD.exe in the
given directory, run with the repository's beam tables). The directory is modified
(configuration files, Results_* folders), so use a scratch copy of vendor/HYDRAD:

    .venv/bin/python scripts/hydrad_gate_variants.py <scratch HYDRAD dir>
"""
from __future__ import annotations

import json
import math
import os
import shutil
import subprocess
import sys
import time

import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, "..", "src"))
sys.path.insert(0, HERE)
import toy_bias as tb  # noqa: E402
from beam_tables import Pulse as BeamPulse, build_table, ndot_from_flux  # noqa: E402
from hydrad_column_test import diagnostics, load  # noqa: E402

AREA = 1.0e17
EC, DELTA = 20.0, 5.0
OUT = os.path.join(HERE, "..", "results", "hydrad_gate_variants")

# name: (full loop length [cm], flux [erg cm^-2 s^-1], pulse-1 duration [s], gap [s], ramp [s])
VARIANTS = {
    "V0_L60_F1.3e10_10s": (6.0e9, 1.28e10, 10.0, 20.0, 0.2),
    "V1_L26_F1.3e10_10s": (2.6e9, 1.28e10, 10.0, 20.0, 0.2),
    "V2_L60_F1.3e10_30s": (6.0e9, 1.28e10, 30.0, 20.0, 0.2),
    "V3_L60_F5e10_10s": (6.0e9, 5.0e10, 10.0, 20.0, 1.0),
    "V4_L26_F5e10_10s": (2.6e9, 5.0e10, 10.0, 20.0, 1.0),
    "V5_L26_F1.3e10_30s": (2.6e9, 1.28e10, 30.0, 20.0, 0.2),
}

IC_TEMPLATE = """Initial_Conditions/profiles/initial.amr

{L:.4E}
0
5E8

2E4

1E11

{apex:.4E}
1E308
-8.0
2.0
0.001
10000.0

Initial conditions for the gate variants
"""


def run(cmd, cwd, log):
    with open(os.path.join(cwd, log), "w") as fh:
        return subprocess.run(cmd, cwd=cwd, stdout=fh, stderr=subprocess.STDOUT, timeout=3600).returncode


def main(hdir: str) -> None:
    hdir = os.path.abspath(hdir)
    os.makedirs(OUT, exist_ok=True)
    grid = tb.make_grid()
    models = {b: tb.ForwardModel(grid=grid, instrument=tb.make_instrument(grid, exposure_s=10.0 * b)) for b in (1.0, 10.0)}
    n_stop = float(tb.Target().stopping_column(EC))
    summary = dict(n_stop_20keV=n_stop, variants={})
    current_l = None
    print("%-22s %6s %9s %8s | %9s %9s %6s | %6s %8s | %8s %6s %8s %6s" % (
        "variant", "wall_s", "t2_prof", "NaN", "N_cor(0)", "N_cor(t2)", "ratio", "T2_MK", "EM2", "dDelta", "z(1e5)", "Ndot2/1", "z(1e6)"))
    for name, (length, flux, dur, gap, ramp) in VARIANTS.items():
        if length != current_l:
            with open(os.path.join(hdir, "Initial_Conditions", "config", "initial_conditions.cfg"), "w") as fh:
                fh.write(IC_TEMPLATE.format(L=length, apex=0.5 * length))
            if run(["./Initial_Conditions.exe"], hdir, "ic.log") != 0:
                raise RuntimeError("initial conditions failed for %s" % name)
            current_l = length
        t0 = max(1.0, ramp)          # the beam table needs the ramp to start at t >= 0
        t2 = t0 + dur + gap
        last = int(math.floor(t2 - 0.5 * ramp - 1e-9))
        table = build_table([BeamPulse.from_flux(t0, dur, flux, EC, DELTA, AREA)], ramp)
        with open(os.path.join(hdir, "Heating_Model", "config", "beam_heating_model.cfg"), "w") as fh:
            fh.write(table.to_cfg())
        with open(os.path.join(hdir, "HYDRAD", "config", "hydrad.cfg"), "w") as fh:
            fh.write("Initial_Conditions/profiles/initial.amr\nInitial_Conditions/profiles/initial.amr.gravity\n"
                     "%d\n1.0\n\nGate variant %s\n" % (last, name))
        res = os.path.join(hdir, "Results")
        shutil.rmtree(res, ignore_errors=True)
        os.makedirs(res)
        tic = time.time()
        code = run(["./HYDRAD.exe"], hdir, "run_%s.log" % name)
        wall = time.time() - tic
        dest = os.path.join(hdir, "Results_" + name)
        shutil.rmtree(dest, ignore_errors=True)
        os.rename(res, dest)
        profiles = sorted(int(f[7:-4]) for f in os.listdir(dest) if f.endswith(".phy"))
        last_ok = max(profiles) if profiles else -1
        nan = any(np.isnan(np.loadtxt(os.path.join(dest, "profile%d.phy" % i))).any() for i in profiles[-3:])
        row = dict(length_cm=length, flux=flux, duration_s=dur, gap_s=gap, ramp_s=ramp, exit_code=code,
                   wall_s=wall, last_profile=last_ok, expected_last=last, nan_in_last_profiles=bool(nan))
        if last_ok < last or nan:
            summary["variants"][name] = row
            print("%-22s %6.0f %9s %8s | run did not reach pulse 2 cleanly" % (name, wall, "%d/%d" % (last_ok, last), nan))
            continue
        d0 = diagnostics(load(dest, 0), length)
        d2 = diagnostics(load(dest, last), length)
        n0, n2 = d0["N_cor_leg1_T>30000"], d2["N_cor_leg1_T>30000"]
        ndot = ndot_from_flux(flux, EC, DELTA, AREA)
        p1 = tb.Pulse(ndot=ndot, delta=DELTA, ec_kev=EC, n_cor=n0, t_k=max(d0["T_EM_T>1MK"], 1e6),
                      em=max(d0["EM_T>1MK"], 1e40))
        p2 = tb.Pulse(ndot=ndot, delta=DELTA, ec_kev=EC, n_cor=n2, t_k=max(d2["T_EM_T>1MK"], 1e6),
                      em=max(d2["EM_T>1MK"], 1e40))
        toy = {}
        for b, m in models.items():
            x1, s1, _ = tb.asimov_fit(m, p1)
            x2, s2, _ = tb.asimov_fit(m, p2)
            toy[b] = dict(counts=float(m.pulse_counts(p1)[m.instrument.fit_mask].sum()),
                          d_delta=float(x2[3] - x1[3]), z_delta=float((x2[3] - x1[3]) / np.hypot(s1[3], s2[3])),
                          ndot_ratio=float(10 ** (x2[2] - x1[2])),
                          z_ndot=float((x2[2] - x1[2]) / np.hypot(s1[2], s2[2])))
        row.update(diag_t0=d0, diag_t2=d2, gate_ratio=n2 / n_stop, ndot=ndot, toy=toy,
                   coronal_energy_fraction_pulse2=models[1.0].coronal_energy_fraction(p2))
        summary["variants"][name] = row
        print("%-22s %6.0f %9s %8s | %9.2e %9.2e %6.2f | %6.2f %8.1e | %+8.3f %6.1f %8.2f %6.1f" % (
            name, wall, "%d/%d" % (last_ok, last), nan, n0, n2, n2 / n_stop, d2["T_EM_T>1MK"] / 1e6, d2["EM_T>1MK"],
            toy[1.0]["d_delta"], toy[1.0]["z_delta"], toy[1.0]["ndot_ratio"], toy[10.0]["z_delta"]))
    with open(os.path.join(OUT, "summary.json"), "w") as fh:
        json.dump(summary, fh, indent=1, default=float)
    print("written", os.path.normpath(os.path.join(OUT, "summary.json")))


if __name__ == "__main__":
    main(sys.argv[1])
