"""Figure for docs/06_toy_bias_test.md from results/toy_bias/summary.json."""
from __future__ import annotations

import json
import os

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402

HERE = os.path.dirname(os.path.abspath(__file__))
SRC = os.path.join(HERE, "..", "results", "toy_bias", "summary.json")
OUT = os.path.join(HERE, "..", "docs", "figures", "fig6_toy_bias.png")

# reference palette (dataviz skill): categorical slots 1-3 validated all-pairs, light mode;
# ordinal blue steps 250/450/650 validated with --ordinal; ink tokens for text and neutral marks
CAT = {1e7: "#2a78d6", 2e7: "#eb6834", 3e7: "#1baf7a"}
ORD = {0.1: "#86b6ef", 1.0: "#2a78d6", 10.0: "#104281"}
INK, INK2, GRID, SURF = "#0b0b0b", "#52514e", "#e4e3df", "#fcfcfb"

plt.rcParams.update({"font.size": 9.5, "axes.edgecolor": GRID, "axes.labelcolor": INK, "xtick.color": INK2,
                     "ytick.color": INK2, "axes.spines.top": False, "axes.spines.right": False,
                     "axes.grid": True, "grid.color": GRID, "grid.linewidth": 0.6, "grid.linestyle": "-",
                     "figure.facecolor": SURF, "axes.facecolor": SURF, "savefig.facecolor": SURF,
                     "figure.dpi": 140, "savefig.bbox": "tight", "legend.frameon": False})


def sci(v: float) -> str:
    m, e = ("%.0e" % v).split("e")
    sup = str.maketrans("-0123456789", "⁻⁰¹²³⁴⁵⁶⁷⁸⁹")
    return "%s×10%s" % (m, str(int(e)).translate(sup))


def main():
    res = json.load(open(SRC))
    sweep = [r for r in res["sweep"] if r["which"] == "pulse2"]
    ncor = sorted({r["pulse"]["n_cor"] for r in sweep})

    fig, (a, b, c) = plt.subplots(1, 3, figsize=(11.6, 3.7), gridspec_kw={"wspace": 0.32})

    # A: shift of the fitted delta (independent of the event brightness in the Asimov fit)
    for t, col in CAT.items():
        rows = sorted((r for r in sweep if r["brightness"] == 1.0 and r["pulse"]["t_k"] == t),
                      key=lambda r: r["pulse"]["n_cor"])
        x = [r["pulse"]["n_cor"] for r in rows]
        y = [r["delta_b"]["delta"]["delta_b"] for r in rows]
        a.plot(x, y, "-o", color=col, lw=2, ms=6, mec=SURF, mew=1.5, label="T₂ = %d MK" % (t / 1e6))
        dy = {1e7: 7, 2e7: -7, 3e7: 0}[t]
        a.annotate("%d MK" % (t / 1e6), (x[-1], y[-1]), xytext=(6, dy), textcoords="offset points",
                   va="center", fontsize=8.5, color=INK2)
    a.axhline(0, color=INK2, lw=0.8)
    a.set_xscale("log")
    a.set_xlim(7e18, 5e20)
    a.set_xlabel("coronal column at pulse-2 onset, N_cor [cm⁻²]")
    a.set_ylabel("Δδ_fit = δ_fit(pulse 2) − δ_fit(pulse 1)")
    a.set_title("A. Same beam, harder δ in pulse 2", fontsize=10, loc="left", color=INK)
    a.legend(fontsize=8, loc="lower left")

    # B: significance against the error of a measured difference, T2 = 20 MK
    for bright, col in ORD.items():
        rows = sorted((r for r in sweep if r["brightness"] == bright and r["pulse"]["t_k"] == 2e7),
                      key=lambda r: r["pulse"]["n_cor"])
        x = [r["pulse"]["n_cor"] for r in rows]
        z = [abs(r["delta_b"]["delta"]["z"]) for r in rows]
        counts = rows[0]["counts_fit_range"]
        b.plot(x, z, "-o", color=col, lw=2, ms=6, mec=SURF, mew=1.5,
               label="%s counts per pulse" % sci(counts))
        b.annotate(sci(counts), (x[-1], z[-1]), xytext=(6, 8 if bright == 1.0 else 0), textcoords="offset points",
                   va="center", fontsize=8.5, color=INK2)
    b.axhline(3, color=INK2, lw=1)
    b.text(7.5e18, 3.25, "3σ detection", fontsize=8, color=INK2)
    b.set_xscale("log")
    b.set_xlim(7e18, 5e20)
    b.set_ylim(0, 12.5)
    b.set_yticks([0, 2, 4, 6, 8, 10])
    b.set_xlabel("coronal column at pulse-2 onset, N_cor [cm⁻²]")
    b.set_ylabel("|Δδ_fit| / σ(δ₂ − δ₁)")
    b.set_title("B. Significance, T₂ = 20 MK", fontsize=10, loc="left", color=INK)
    b.legend(fontsize=8, loc="upper left")

    # C: mechanism, from the forward model (no fit)
    rows = sorted((r for r in sweep if r["brightness"] == 1.0 and r["pulse"]["t_k"] == 2e7),
                  key=lambda r: r["pulse"]["n_cor"])
    x = [r["pulse"]["n_cor"] for r in rows]
    e_frac = [r["coronal_energy_fraction"] for r in rows]
    p_frac = [r["coronal_photon_fraction_25_50keV"] for r in rows]
    c.plot(x, e_frac, "-o", color=INK, lw=2, ms=6, mec=SURF, mew=1.5, label="energy deposited in corona")
    c.plot(x, p_frac, "-s", color=INK2, lw=2, ms=6, mec=SURF, mew=1.5, label="25–50 keV photons from corona")
    c.annotate("energy", (x[-1], e_frac[-1]), xytext=(6, 0), textcoords="offset points", va="center",
               fontsize=8.5, color=INK2)
    c.annotate("photons", (x[-1], p_frac[-1]), xytext=(6, 0), textcoords="offset points", va="center",
               fontsize=8.5, color=INK2)
    c.set_xscale("log")
    c.set_xlim(7e18, 5e20)
    c.set_ylim(0, 1.25)
    c.set_yticks([0, 0.2, 0.4, 0.6, 0.8, 1.0])
    c.set_xlabel("coronal column at pulse-2 onset, N_cor [cm⁻²]")
    c.set_ylabel("fraction")
    c.set_title("C. Mechanism: corona stops the beam", fontsize=10, loc="left", color=INK)
    c.legend(fontsize=7.5, loc="upper left")

    fig.text(0.0, -0.06, "Toy forward model (src/toy_bias.py): two-zone target, Haug cross-section, illustrative "
             "STIX-like response; beam of Collier et al. (2024): Ṅ = 3.4×10³⁴ s⁻¹, δ = 4.97, Ec = 13.4 keV; "
             "pulse 1 (relaxed) at N_cor = 10¹⁹ cm⁻², 3 MK; counts in 6–100 keV; σ is the error of a measured difference δ₂ − δ₁.", fontsize=7.5, color=INK2)
    os.makedirs(os.path.dirname(OUT), exist_ok=True)
    fig.savefig(OUT)
    print("figure written to", os.path.normpath(OUT))


if __name__ == "__main__":
    main()
