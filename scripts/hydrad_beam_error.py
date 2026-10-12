"""Beam part of the uncertainty: how much the relaxed response Delta D_0 changes with the test beam.

Reruns B0 (test pulse on the relaxed atmosphere) with the beam varied one parameter at a time
within typical STIX fit uncertainties.  The defaults follow the relative errors of the first-burst
fit of Collier et al. (2024): electron rate +-12 %, cutoff +-4 %, spectral index +-0.1.  It then
compares Delta D_0 = B0 - A0 with the pilot's, using the pilot's A0 and mass-conserving window
of the given tau.  sigma_beam(D) = max over variants and t' of |Delta D_0(variant) - Delta D_0|.

    .venv/bin/python scripts/hydrad_beam_error.py <pilot HYDRAD dir> --pilot <pilot output dir> [--tau 10]
"""
from __future__ import annotations

import argparse
import json
import os
import sys
from concurrent.futures import ThreadPoolExecutor
from dataclasses import replace

import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, "..", "src"))
sys.path.insert(0, HERE)
import hydrad_paired_branches as hp  # noqa: E402
import memory_contrast as mc  # noqa: E402
from beam_tables import build_table  # noqa: E402
from experiments import PILOT  # noqa: E402

VARIANTS = {"ndot+12%": dict(ndot=1.12), "ndot-12%": dict(ndot=0.88),
            "ec+4%": dict(ec_kev=1.04), "ec-4%": dict(ec_kev=0.96),
            "delta+0.1": dict(delta=0.1), "delta-0.1": dict(delta=-0.1)}


def varied_pulse(change: dict):
    p = PILOT.pulses()[0]
    kw = {}
    for k, v in change.items():
        kw[k] = getattr(p, k) + v if k == "delta" else getattr(p, k) * v
    return replace(p, **kw)


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    ap.add_argument("hydrad_dir", help="the pilot HYDRAD directory (its runs/A0 is reused)")
    ap.add_argument("--pilot", required=True)
    ap.add_argument("--tau", type=float, default=10.0)
    ap.add_argument("--jobs", type=int, default=4)
    ap.add_argument("--only", help="comma-separated subset of " + ",".join(VARIANTS))
    args = ap.parse_args()
    hdir = os.path.abspath(args.hydrad_dir)
    with open(os.path.join(args.pilot, "summary.json")) as fh:
        pilot = json.load(fh)
    with open(os.path.join(args.pilot, "series.json")) as fh:
        ser = json.load(fh)
    names = args.only.split(",") if args.only else list(VARIANTS)
    entry = pilot["contrasts"]["%g" % args.tau]
    t_rel_max = entry["valid_window_s"][1]
    t0 = PILOT.t0
    t_end = t0 + t_rel_max + 2 * hp.CADENCE

    def job(name):
        wd = os.path.join(hdir, "runs", "B0_" + name)
        hp.clone(hdir, wd)
        table = build_table([varied_pulse(VARIANTS[name])], PILOT.ramp)
        return name, hp.run_hydrad(wd, table.to_cfg(), "Initial_Conditions/profiles/initial.amr", t_end, name)

    with ThreadPoolExecutor(max_workers=args.jobs) as ex:
        runs = dict(ex.map(job, names))
    out = {"tau_s": args.tau, "window_s": [0.0, t_rel_max], "variants": {n: VARIANTS[n] for n in names},
           "sigma_beam": {}}
    for key, r in entry["diagnostics"].items():
        if "delta_D0" not in r:
            continue
        t_rel = np.array(r["t_rel_s"])
        a0 = mc.on_common_grid(ser["A0"]["t_s"], ser["A0"][key], t0, t_rel)
        per = {}
        for name, info in runs.items():
            t, d, _ = hp.series(info["dir"], pilot["length_cm"])
            dd0 = mc.on_common_grid(t, d[key], t0, t_rel) - a0
            per[name] = mc.peak_abs(dd0 - np.array(r["delta_D0"]))
        out["sigma_beam"][key] = {"max_abs_change_delta_D0": max(per.values()), "per_variant": per,
                                  "pilot_peak_abs_M": r["peak_abs_M"]}
        print("%-20s sigma_beam = %.3e   (pilot max|M| = %.3e)" % (key, max(per.values()), r["peak_abs_M"]))
    path = os.path.join(args.pilot, "beam_error_tau%g.json" % args.tau)
    with open(path, "w") as fh:
        json.dump(out, fh, indent=1, default=float)
    print("written", os.path.normpath(path))


if __name__ == "__main__":
    main()
