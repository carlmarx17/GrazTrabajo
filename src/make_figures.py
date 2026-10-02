"""Figures for docs/02_informe_experimentos_pulsos.html (synthetic base case)."""
from __future__ import annotations

import math
import os

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
from matplotlib.patches import FancyArrowPatch, Rectangle

from beam_tables import KEV_TO_ERG, build_table, naive_table
from experiments import BaseCase, build_experiments

HERE = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.join(HERE, "..", "docs", "figures")

C = {"pulse": "#c0392b", "tube": "#1f4e79", "fil1": "#d35400", "fil2": "#16a085",
     "cont": "#7f8c8d", "grey": "#555555", "good": "#1b7a3d"}
plt.rcParams.update({"font.size": 10, "axes.spines.top": False, "axes.spines.right": False,
                     "axes.grid": True, "grid.alpha": 0.25, "figure.dpi": 130,
                     "savefig.bbox": "tight"})


def save(fig, name):
    os.makedirs(OUT, exist_ok=True)
    fig.savefig(os.path.join(OUT, name))
    plt.close(fig)


def fig_stopping_column():
    """N_c(Ec) with the exact expression used in Heating_Model/source/heat.cpp (mu0 = 1)."""
    ec = np.logspace(np.log10(5), np.log10(100), 200)
    delta = 5.0
    e_avg = ec * KEV_TO_ERG * (delta - 1) / (delta - 2)       # erg, as in heat.cpp
    k = 1.0006128424679109e-36                                # (2 + b/2) 2 pi e^4, b = 2

    def nc(x, ne):
        lam1 = 66.0 + 1.5 * np.log(e_avg) - 0.5 * math.log(ne)
        lam2 = 25.1 + np.log(e_avg)
        g = x * lam1 + (1 - x) * lam2
        return (ec * KEV_TO_ERG) ** 2 / (g * k)

    fig, ax = plt.subplots(figsize=(6.4, 4.0))
    ax.loglog(ec, nc(0.0, 1e11), color=C["fil1"], lw=2, label="gas neutro (x = 0)")
    ax.loglog(ec, nc(1.0, 1e11), color=C["tube"], lw=2, label="gas ionizado, n_e = 10¹¹ cm⁻³")
    ax.loglog(ec, nc(1.0, 1e13), color=C["tube"], lw=2, ls="--", label="gas ionizado, n_e = 10¹³ cm⁻³")
    i20 = np.argmin(abs(ec - 20))
    r = nc(0.0, 1e11)[i20] / nc(1.0, 1e11)[i20]
    ax.annotate("20 keV: la columna de frenado\ncambia ×%.1f solo por la\nionización del blanco" % r,
                xy=(20, nc(0.0, 1e11)[i20]), xytext=(6.5, 4e20), fontsize=9,
                arrowprops=dict(arrowstyle="->", color=C["grey"]))
    ax.set_xlabel("Ec [keV]")
    ax.set_ylabel("columna de frenado N_c [cm⁻²]")
    ax.set_title("Dónde se frena el haz: N_c depende de Ec y del estado del plasma", fontsize=10)
    ax.legend(frameon=False, fontsize=9, loc="lower right")
    ax.text(0.02, 0.97, "δ = 5, incidencia normal (μ₀ = 1)\nexpresión de heat.cpp", transform=ax.transAxes,
            va="top", fontsize=8, color=C["grey"])
    save(fig, "fig1_stopping_column.png")


def fig_schematic():
    fig, ax = plt.subplots(figsize=(8.6, 3.6))
    ax.set_xlim(0, 16)
    ax.set_ylim(0, 8)
    ax.axis("off")

    def tube(x, w, label, color, ytop=4.3):
        ax.add_patch(Rectangle((x, 1.3), w, ytop - 1.3, fc=color, alpha=0.18, ec=color, lw=1.5))
        ax.text(x + w / 2, 1.0, label, ha="center", va="top", fontsize=8.5, color=color)

    def beam(x, label, color):
        ax.add_patch(FancyArrowPatch((x, 6.4), (x, 4.4), arrowstyle="-|>", mutation_scale=14,
                                     color=color, lw=2))
        ax.text(x, 6.55, label, ha="center", fontsize=8.5, color=color)

    ax.text(0.2, 8.0, "Mismo tubo (recalentamiento)", fontsize=10, weight="bold", va="top")
    tube(0.8, 3.0, "atmósfera con memoria\nde la historia previa", C["tube"])
    beam(1.5, "pulso 1", C["pulse"])
    beam(3.3, "pulso 2", C["pulse"])
    ax.text(4.3, 3.0, "→ la atmósfera\nse modifica y no\nse reinicia", fontsize=8, va="center", color=C["grey"])

    ax.text(8.6, 8.0, "Filamentos independientes", fontsize=10, weight="bold", va="top")
    tube(9.2, 2.2, "filamento A\n(relajado)", C["fil1"])
    tube(12.0, 2.2, "filamento B\n(relajado)", C["fil2"])
    beam(10.3, "pulso 1", C["pulse"])
    beam(13.1, "pulso 2", C["pulse"])
    ax.text(14.6, 3.0, "→ cada pulso\nve una atmósfera\nrelajada", fontsize=8, va="center", color=C["grey"])
    ax.text(8.0, -0.2, "STIX mide los fotones del conjunto: ambos escenarios pueden dar la misma curva "
            "de potencia P(t).", ha="center", fontsize=8.5, style="italic")
    save(fig, "fig0_scenarios.png")


def fig_encoding(base):
    ps = base.pulses()
    good, bad = build_table(ps, base.ramp), naive_table(ps)
    t = np.linspace(0, base.t_end_global - base.tail + 4, 6000)
    f0 = ps[0].flux
    nominal = np.array([sum(p.flux for p in ps if p.t_start <= x < p.t_end) for x in t])
    gf = np.array([good.flux_at(x) for x in t])
    bf = np.array([bad.flux_at(x) for x in t])
    fig, (a, b) = plt.subplots(2, 1, figsize=(7.2, 5.4), sharex=True, gridspec_kw={"height_ratios": [1.2, 1]})
    a.plot(t, nominal / 1e10, color=C["grey"], lw=4, alpha=0.3, label="pulsos nominales (cajas)")
    a.plot(t, gf / 1e10, color=C["good"], lw=1.8, label="tabla con filas F = 0 y rampa de %.1f s (la generada)" % base.ramp)
    a.plot(t, bf / 1e10, color=C["pulse"], lw=1.8, ls="--", label="tabla ingenua de 2 filas por pulso")
    a.set_ylabel("F [10¹⁰ erg cm⁻² s⁻¹]")
    a.set_ylim(0, 2.1)
    a.legend(frameon=False, fontsize=8, loc="upper center", ncol=1)
    a.set_title("Cómo ve HYDRAD los pulsos: interpola linealmente entre filas", fontsize=10)
    for arr, col, ls in ((nominal, C["grey"], "-"), (gf, C["good"], "-"), (bf, C["pulse"], "--")):
        b.plot(t, np.cumsum(arr) * (t[1] - t[0]) / 1e10 * 1.0, color=col, ls=ls, lw=1.8 if col != C["grey"] else 4,
               alpha=1 if col != C["grey"] else 0.3)
    b.set_ylabel("∫F dt [10¹⁰ erg cm⁻²]")
    b.set_xlabel("tiempo [s]")
    b.text(0.03, 0.93, "energía inyectada: tabla correcta = %.1f×10¹⁰, ingenua = %.1f×10¹⁰ (×%.1f)" % (
        good.energy_per_area() / 1e10, bad.energy_per_area() / 1e10, bad.energy_per_area() / good.energy_per_area()),
        transform=b.transAxes, va="top", fontsize=8.5)
    save(fig, "fig2_table_encoding.png")


def fig_experiments(exps, base):
    fig, axes = plt.subplots(len(exps), 1, figsize=(7.6, 8.6), sharex=True)
    t = np.linspace(0, base.t_end_global, 8000)
    cols = [C["fil1"], C["fil2"], C["tube"]]
    for ax, e in zip(axes, exps):
        for k, c in enumerate(e.components):
            y = np.array([c.table.flux_at(x - c.offset) for x in t]) / 1e10
            col = (cols[k] if len(e.components) > 1 else (C["cont"] if "E4" in e.name else C["tube"]))
            ax.fill_between(t, y, color=col, alpha=0.25)
            ax.plot(t, y, color=col, lw=1.5)
        ax.set_ylim(0, 3.1)
        ax.set_ylabel("F [10¹⁰]", fontsize=8)
        ax.text(0.99, 0.82, "%s   (A_total = %.0e cm²)" % (e.name, e.total_area_cm2()),
                transform=ax.transAxes, ha="right", fontsize=8.5)
    axes[-1].set_xlabel("tiempo global [s]  (filamentos: curvas desplazadas por su desfase)")
    axes[0].set_title("Flujo de energía del haz en cada experimento (por tubo, F en erg cm⁻² s⁻¹)", fontsize=10)
    save(fig, "fig3_experiments_flux.png")


def fig_ledger(exps, base):
    t = np.linspace(0, base.t_end_global, 4000)
    fig, (a, b) = plt.subplots(1, 2, figsize=(9.2, 3.8), gridspec_kw={"width_ratios": [1.6, 1]})
    style = {"E1_single_relaxed": ("#8e44ad", ":", 2.2), "E2_same_strand": (C["tube"], "-", 3.5),
             "E3a_independent_same_flux": (C["fil1"], "--", 2.0), "E3b_independent_equal_area": (C["fil2"], "-.", 2.0),
             "E4_continuous": (C["cont"], "-", 1.6), "E5_relaxation": ("#c0392b", ":", 1.6)}
    for e in exps:
        p = np.array([e.power(x) for x in t])
        cum = np.cumsum(p) * (t[1] - t[0])
        col, ls, lw = style[e.name]
        a.plot(t, cum / 1e28, color=col, ls=ls, lw=lw, label=e.name)
    a.set_xlabel("tiempo global [s]")
    a.set_ylabel("energía inyectada acumulada [10²⁸ erg]")
    a.set_title("Misma energía total en E2, E3a, E3b y E4", fontsize=10)
    a.legend(frameon=False, fontsize=7.5, loc="upper left")
    names = [e.name.split("_")[0] for e in exps]
    areas = [e.total_area_cm2() / base.area_cm2 for e in exps]
    pk = [max(max(r[1] for r in c.table.rows) for c in e.components) / 1e10 for e in exps]
    x = np.arange(len(exps))
    b.bar(x - 0.2, areas, 0.4, color=C["tube"], label="A_total / A_ref")
    b.bar(x + 0.2, pk, 0.4, color=C["pulse"], label="F_pico [10¹⁰]")
    b.set_xticks(x)
    b.set_xticklabels(names, fontsize=8)
    b.set_title("Lo que NO se conserva", fontsize=10)
    b.legend(frameon=False, fontsize=8)
    save(fig, "fig4_energy_ledger.png")


def fig_degeneracy(exps, base):
    t = np.linspace(0, base.t_end_global - base.tail + 5, 6000)
    byname = {e.name: e for e in exps}
    fig, (a, b) = plt.subplots(1, 2, figsize=(9.4, 3.8), gridspec_kw={"width_ratios": [1.4, 1]})
    for name, col, ls, lw in (("E2_same_strand", C["tube"], "-", 4), ("E3a_independent_same_flux", C["fil1"], "--", 2.2),
                              ("E3b_independent_equal_area", C["fil2"], ":", 2.6), ("E4_continuous", C["cont"], "-", 1.4)):
        a.plot(t, [byname[name].power(x) / 1e27 for x in t], color=col, ls=ls, lw=lw, label=name, alpha=0.9)
    a.set_xlabel("tiempo global [s]")
    a.set_ylabel("P_total(t) = Σ A_i F_i [10²⁷ erg s⁻¹]")
    a.set_title("La potencia total no distingue la geometría", fontsize=10)
    a.set_ylim(0, 1.95)
    a.legend(frameon=False, fontsize=7.5, loc="upper center", ncol=2)
    p = base.pulses()[0]
    f = np.logspace(-1.2, 0.3, 100)
    b.loglog(f, p.power_erg_s / (f * base.area_cm2), color=C["tube"], lw=2)
    for fr, lab, col in ((1.0, "E3a", C["fil1"]), (0.5, "E3b", C["fil2"])):
        b.plot([fr], [p.power_erg_s / (fr * base.area_cm2)], "o", color=col, ms=8)
        b.annotate(lab, (fr, p.power_erg_s / (fr * base.area_cm2)), textcoords="offset points", xytext=(6, 5), fontsize=9)
    b.set_xlabel("área del filamento / A_ref")
    b.set_ylabel("F por pulso [erg cm⁻² s⁻¹]")
    b.set_title("P fija ⇒ F = P / A", fontsize=10)
    save(fig, "fig5_degeneracy.png")


def main():
    base = BaseCase()
    exps = build_experiments(base)
    fig_schematic()
    fig_stopping_column()
    fig_encoding(base)
    fig_experiments(exps, base)
    fig_ledger(exps, base)
    fig_degeneracy(exps, base)
    print("figures written to", os.path.normpath(OUT))


if __name__ == "__main__":
    main()
