"""Figures of the HYDRAD core pilot (docs/07_core_pilot_hydrad.md).

Reads results/paired_branches_hydrad/<label>/{summary,series}.json written by
scripts/hydrad_paired_branches.py and draws:

  fig8_pilot_history.png   coronal proxies of A0, A1 and B0 versus time, with the test
                           onsets t_k, and A1/A0 versus time (how far pulse 1 has relaxed);
  fig9_pilot_contrast.png  Delta D_0 (relaxed response) and M_D(tau, t') for every tau.

    .venv/bin/python scripts/plot_paired_branches.py [label] [--out docs/figures]
"""
from __future__ import annotations

import argparse
import json
import os

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402
import numpy as np  # noqa: E402

HERE = os.path.dirname(os.path.abspath(__file__))
RES = os.path.join(HERE, "..", "results", "paired_branches_hydrad")
LABELS = {"EM_T>1MK": ("EM (T > 1 MK)", "cm$^{-3}$", 1.0),
          "T_EM_T>1MK": ("EM-weighted T (T > 1 MK)", "MK", 1e-6),
          "n_apex": ("apex density", "cm$^{-3}$", 1.0),
          "T_apex": ("apex temperature", "MK", 1e-6),
          "N_cor_leg1_T>30000": ("column above 3$\\times$10$^4$ K", "cm$^{-2}$", 1.0)}
plt.rcParams.update({"font.size": 9, "axes.spines.top": False, "axes.spines.right": False,
                     "axes.grid": True, "grid.alpha": 0.25, "figure.dpi": 130, "savefig.bbox": "tight"})


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("label", nargs="?", default="pilot_cond02")
    ap.add_argument("--out", default=os.path.join(HERE, "..", "docs", "figures"))
    args = ap.parse_args()
    d = os.path.join(RES, args.label)
    with open(os.path.join(d, "summary.json")) as fh:
        summ = json.load(fh)
    with open(os.path.join(d, "series.json")) as fh:
        ser = json.load(fh)
    os.makedirs(args.out, exist_ok=True)
    taus = summ["taus_s"]
    tks = {tau: summ["contrasts"]["%g" % tau].get("t_k_s") for tau in taus}
    keys = [k for k in LABELS if k in ser["A0"]]
    colors = plt.cm.viridis(np.linspace(0.0, 0.85, len(taus)))

    fig, axes = plt.subplots(len(keys), 2, figsize=(9.5, 2.0 * len(keys)), sharex="col")
    for row, key in enumerate(keys):
        name, unit, scale = LABELS[key]
        ax, axr = axes[row]
        for run, style in (("A0", dict(color="0.5", lw=1.2, label="A0 no beam")),
                           ("A1", dict(color="#1f4e79", lw=1.4, label="A1 pulse 1 only")),
                           ("B0", dict(color="#c0392b", lw=1.0, ls="--", label="B0 test pulse only"))):
            ax.plot(ser[run]["t_s"], np.array(ser[run][key]) * scale, **style)
        for tau, c in zip(taus, colors):
            if tks[tau] is not None:
                ax.axvline(tks[tau], color=c, lw=0.8, ls=":")
        ax.set_ylabel("%s\n[%s]" % (name, unit))
        if key in ("EM_T>1MK", "n_apex", "N_cor_leg1_T>30000"):
            ax.set_yscale("log")
        t_a1, y_a1 = np.array(ser["A1"]["t_s"]), np.array(ser["A1"][key])
        y_a0 = np.interp(t_a1, ser["A0"]["t_s"], ser["A0"][key])
        with np.errstate(divide="ignore", invalid="ignore"):
            axr.plot(t_a1, y_a1 / y_a0, color="#1f4e79", lw=1.2)
        axr.axhline(1.0, color="0.5", lw=0.8)
        for tau, c in zip(taus, colors):
            if tks[tau] is not None:
                axr.axvline(tks[tau], color=c, lw=0.8, ls=":", label="t$_k$, $\\tau$ = %g s" % tau)
        axr.set_ylabel("A1 / A0")
        if key in ("EM_T>1MK", "n_apex", "N_cor_leg1_T>30000"):
            axr.set_yscale("log")
    axes[0, 0].legend(fontsize=7, loc="best")
    axes[0, 1].legend(fontsize=7, loc="best")
    axes[-1, 0].set_xlabel("t [s]")
    axes[-1, 1].set_xlabel("t [s]")
    fig.suptitle("Pilot (HYDRAD, %.0f Mm loop): state left by pulse 1 and its relaxation"
                 % (summ["length_cm"] / 1e8), fontsize=10)
    fig.savefig(os.path.join(args.out, "fig8_pilot_history.png"))
    plt.close(fig)

    fig, axes = plt.subplots(len(keys), 2, figsize=(9.5, 2.0 * len(keys)), sharex=True)
    for row, key in enumerate(keys):
        name, unit, scale = LABELS[key]
        ax, axm = axes[row]
        drawn = False
        for tau, c in zip(taus, colors):
            r = summ["contrasts"]["%g" % tau].get("diagnostics", {}).get(key, {})
            if "M" not in r:
                continue
            t = np.array(r["t_rel_s"])
            if not drawn:
                ax.plot(t, np.array(r["delta_D0"]) * scale, color="#c0392b", lw=1.4,
                        label="$\\Delta D_0$ (relaxed)")
                drawn = True
            ax.plot(t, np.array(r["delta_D1"]) * scale, color=c, lw=1.0, label="$\\Delta D_1$, $\\tau$ = %g s" % tau)
            axm.plot(t, np.array(r["M"]) * scale, color=c, lw=1.2, label="$\\tau$ = %g s" % tau)
        axm.axhline(0.0, color="0.5", lw=0.8)
        ax.set_ylabel("%s\n[%s]" % (name, unit))
        axm.set_ylabel("$M_D$ [%s]" % unit)
    axes[0, 0].legend(fontsize=7)
    axes[0, 1].legend(fontsize=7)
    axes[-1, 0].set_xlabel("t' since onset of the test pulse [s]")
    axes[-1, 1].set_xlabel("t' since onset of the test pulse [s]")
    axes[0, 0].set_title("incremental response to the test pulse", fontsize=9)
    axes[0, 1].set_title("history contrast $M_D = \\Delta D_1 - \\Delta D_0$", fontsize=9)
    fig.savefig(os.path.join(args.out, "fig9_pilot_contrast.png"))
    plt.close(fig)
    print("written", os.path.normpath(os.path.join(args.out, "fig8_pilot_history.png")), "and fig9")


if __name__ == "__main__":
    main()
