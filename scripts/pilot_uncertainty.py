"""Time-resolved comparison of the history contrast with its numerical and beam uncertainties.

For one pilot and one tau, combines
  M_D(t')            from summary.json,
  sigma_num(t')      = |M_D(time-step variant) - M_D(pilot)|   (numerical_error_<label>.json),
  sigma_beam(t')     = max over beam variants |Delta D_0(variant) - Delta D_0|   (runs/B0_<variant>),
and reports where |M_D| > k * sqrt(sigma_num^2 + sigma_beam^2).  sigma_obs is not included,
and these sigmas were measured after the pilot contrasts, so this is an exploratory map of
where a signature could lie, not the pre-registered decision of docs/00, Section 3.5.

    .venv/bin/python scripts/pilot_uncertainty.py <pilot HYDRAD dir> --pilot <pilot output dir> \
        [--tau 10] [--numerical cond01] [--k 3] [--figure docs/figures/fig10_pilot_uncertainty.png]
"""
from __future__ import annotations

import argparse
import json
import os
import sys

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402
import numpy as np  # noqa: E402

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, "..", "src"))
sys.path.insert(0, HERE)
import hydrad_paired_branches as hp  # noqa: E402
import memory_contrast as mc  # noqa: E402
from experiments import PILOT  # noqa: E402
from plot_paired_branches import LABELS  # noqa: E402


def intervals(t: np.ndarray, mask: np.ndarray) -> list:
    """Contiguous [start, end] ranges of t where mask is true."""
    out, start = [], None
    for x, m in zip(t, mask):
        if m and start is None:
            start = x
        if not m and start is not None:
            out.append([float(start), float(prev)])
            start = None
        prev = x
    if start is not None:
        out.append([float(start), float(t[-1])])
    return out


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    ap.add_argument("hydrad_dir")
    ap.add_argument("--pilot", required=True)
    ap.add_argument("--tau", type=float, default=10.0)
    ap.add_argument("--numerical", default="cond01")
    ap.add_argument("--k", type=float, default=3.0)
    ap.add_argument("--figure", default=None)
    args = ap.parse_args()
    with open(os.path.join(args.pilot, "summary.json")) as fh:
        summ = json.load(fh)
    with open(os.path.join(args.pilot, "series.json")) as fh:
        ser = json.load(fh)
    num_path = os.path.join(args.pilot, "numerical_error_%s.json" % args.numerical)
    num = json.load(open(num_path)) if os.path.exists(num_path) else None
    entry = summ["contrasts"]["%g" % args.tau]
    runs_dir = os.path.join(os.path.abspath(args.hydrad_dir), "runs")
    beam_runs = sorted(d for d in os.listdir(runs_dir) if d.startswith("B0_"))
    beam_series = {d: hp.series(os.path.join(runs_dir, d, "Results"), summ["length_cm"])[:2] for d in beam_runs}
    t0 = PILOT.t0

    keys = [k for k in hp.DIAGNOSTICS if "M" in entry["diagnostics"].get(k, {})]
    out = {"tau_s": args.tau, "k": args.k, "beam_variants": beam_runs, "numerical_variant": args.numerical,
           "note": "exploratory: sigmas measured after the pilot; sigma_obs not included", "diagnostics": {}}
    fig, axes = plt.subplots(len(keys), 1, figsize=(6.5, 1.9 * len(keys)), sharex=True)
    for ax, key in zip(np.atleast_1d(axes), keys):
        r = entry["diagnostics"][key]
        t = np.array(r["t_rel_s"])
        m = np.array(r["M"])
        a0 = mc.on_common_grid(ser["A0"]["t_s"], ser["A0"][key], t0, t)
        s_beam = np.zeros_like(t)
        for d, (tb, db) in beam_series.items():
            ok = t <= tb[-1] - t0 + 1e-9
            dd0 = np.full_like(t, np.nan)
            dd0[ok] = mc.on_common_grid(tb, db[key], t0, t[ok]) - a0[ok]
            s_beam = np.fmax(s_beam, np.abs(dd0 - np.array(r["delta_D0"])))
        s_num = np.abs(np.array(num["sigma_num"][key]["M"]) - m) if num and key in num["sigma_num"] else np.zeros_like(t)
        s_tot = np.sqrt(s_num ** 2 + s_beam ** 2)
        above = np.abs(m) > args.k * s_tot
        out["diagnostics"][key] = {"t_rel_s": t.tolist(), "M": m.tolist(), "sigma_num": s_num.tolist(),
                                   "sigma_beam": s_beam.tolist(), "intervals_above_k_sigma_s": intervals(t, above)}
        name, unit, scale = LABELS[key]
        ax.plot(t, m * scale, color="#1f4e79", lw=1.4, label="$M_D$")
        ax.fill_between(t, -args.k * s_tot * scale, args.k * s_tot * scale, color="#c0392b", alpha=0.18,
                        label="$\\pm%g\\,(\\sigma_{num} \\oplus \\sigma_{beam})$" % args.k)
        ax.axhline(0.0, color="0.5", lw=0.8)
        ax.set_ylabel("%s\n[%s]" % (name, unit), fontsize=8)
        print("%-20s |M| > %g sigma for t' in %s" % (key, args.k, out["diagnostics"][key]["intervals_above_k_sigma_s"]))
    np.atleast_1d(axes)[0].legend(fontsize=7)
    np.atleast_1d(axes)[-1].set_xlabel("t' since onset of the test pulse [s]")
    np.atleast_1d(axes)[0].set_title("History contrast and uncertainty, tau = %g s (exploratory, no $\\sigma_{obs}$)"
                                     % args.tau, fontsize=9)
    path = os.path.join(args.pilot, "uncertainty_tau%g.json" % args.tau)
    with open(path, "w") as fh:
        json.dump(out, fh, indent=1, default=float)
    figure = args.figure or os.path.join(args.pilot, "figures", "fig10_pilot_uncertainty_tau%g.png" % args.tau)
    os.makedirs(os.path.dirname(figure), exist_ok=True)
    fig.savefig(figure, bbox_inches="tight", dpi=130)
    print("written", os.path.normpath(path), "and", os.path.normpath(figure))


if __name__ == "__main__":
    main()
