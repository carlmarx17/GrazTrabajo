"""Toy inject-reinfer campaign: is the memory-induced bias larger than the STIX fit error?

Writes results/toy_bias/summary.json and prints the tables quoted in
docs/06_toy_bias_test.md. Run from the repository root:

    .venv/bin/python scripts/toy_bias_sweep.py
"""
from __future__ import annotations

import json
import math
import os
import sys
import time
from concurrent.futures import ProcessPoolExecutor
from dataclasses import asdict, replace

import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, "..", "src"))
import toy_bias as tb  # noqa: E402

OUT = os.path.join(HERE, "..", "results", "toy_bias")
PULSE1 = tb.Pulse()                         # relaxed: N_cor = 1e19 cm^-2, T = 3 MK
NCOR2 = (1e19, 3e19, 1e20, 3e20)
T2 = (1e7, 2e7, 3e7)
BRIGHTNESS = (0.1, 1.0, 10.0)               # multiplies the exposure (flare size / distance / time)
MAIN = dict(n_cor=1e20, t_k=2e7)            # representative pulse 2 for the detailed tests
N_REP = 200
IDX = dict(delta=3, ec=4, lndot=2)

_MODELS = {}


def model_for(brightness: float, ratio: float = 2.8, fit_range=(6.0, 100.0)) -> tb.ForwardModel:
    key = (brightness, ratio, fit_range)
    if key not in _MODELS:
        grid = _MODELS.setdefault("grid", tb.make_grid())
        ins = tb.make_instrument(grid, exposure_s=10.0 * brightness, fit_range=fit_range)
        _MODELS[key] = tb.ForwardModel(grid=grid, instrument=ins, target=tb.Target(ion_to_neutral_loss=ratio))
    return _MODELS[key]


def summarize(model, pulse, x, sig, two_zone=False):
    xt = tb.truth_vector(model, pulse, two_zone)
    mu = model.pulse_counts(pulse)
    return dict(pulse=asdict(pulse), em=model.pulse_em(pulse), fit=x.tolist(), sigma=sig.tolist(),
                bias=(x - xt).tolist(), counts_fit_range=float(mu[model.instrument.fit_mask].sum()),
                coronal_photon_fraction_25_50keV=model.coronal_photon_fraction(pulse),
                coronal_energy_fraction=model.coronal_energy_fraction(pulse))


def delta_b(r1, r2):
    """Memory-induced bias ΔB = fit(pulse 2) - fit(pulse 1) for the same injected beam, and
    its significance against the error of a measured difference sqrt(σ1² + σ2²)."""
    out = {}
    for name, i in IDX.items():
        d = r2["fit"][i] - r1["fit"][i]
        s = math.hypot(r1["sigma"][i], r2["sigma"][i])
        out[name] = dict(delta_b=d, sigma_diff=s, z=d / s if s > 0 else float("inf"))
    return out


def _mc_worker(args):
    brightness, pulse, n_rep, seed, two_zone = args
    return tb.monte_carlo(model_for(brightness), pulse, n_rep, seed, two_zone)


def monte_carlo_parallel(brightness, pulse, n_rep, seed, workers=8):
    chunks = [(brightness, pulse, n_rep // workers, seed + i, False) for i in range(workers)]
    with ProcessPoolExecutor(max_workers=workers) as ex:
        return np.vstack(list(ex.map(_mc_worker, chunks)))


def main():
    t0 = time.time()
    os.makedirs(OUT, exist_ok=True)
    res = dict(assumptions=dict(pulse1=asdict(PULSE1), geometry=asdict(tb.Geometry()), target=asdict(tb.Target()),
                                fit_range_keV=[6, 100], exposure_s_at_brightness_1=10.0, area_cm2=6.0,
                                note="toy model; see src/toy_bias.py docstring for what is not included"),
               sweep=[], decomposition={}, two_zone_fit={}, sensitivity={}, monte_carlo={})

    # 1. main sweep with Asimov fits and Fisher errors
    print("\n=== Sweep: memory-induced bias (pulse 2 - pulse 1), same injected beam ===")
    print("%5s %8s %5s | %9s %6s %5s | %8s %6s %5s | %8s %5s | %9s %6s %6s" % (
        "bright", "Ncor2", "T2MK", "dB_delta", "s_diff", "z", "dB_Ec", "s_diff", "z", "Ndot2/1", "z",
        "counts1", "cor_ph", "cor_E"))
    for b in BRIGHTNESS:
        m = model_for(b)
        x1, s1, _ = tb.asimov_fit(m, PULSE1)
        r1 = summarize(m, PULSE1, x1, s1)
        res["sweep"].append(dict(brightness=b, which="pulse1", **r1))
        for n2 in NCOR2:
            for t2 in T2:
                p2 = replace(PULSE1, n_cor=n2, t_k=t2)
                x2, s2, _ = tb.asimov_fit(m, p2)
                r2 = summarize(m, p2, x2, s2)
                db = delta_b(r1, r2)
                res["sweep"].append(dict(brightness=b, which="pulse2", delta_b=db, **r2))
                print("%5.1f %8.0e %5.0f | %+9.3f %6.3f %5.1f | %+8.2f %6.2f %5.1f | %8.2f %5.1f | %9.2e %6.2f %6.2f" % (
                    b, n2, t2 / 1e6, db["delta"]["delta_b"], db["delta"]["sigma_diff"], db["delta"]["z"],
                    db["ec"]["delta_b"], db["ec"]["sigma_diff"], db["ec"]["z"],
                    10 ** db["lndot"]["delta_b"], db["lndot"]["z"], r1["counts_fit_range"],
                    r2["coronal_photon_fraction_25_50keV"], r2["coronal_energy_fraction"]))
        print("   pulse-1 bias (method baseline B1) at brightness %.1f: delta %+.3f, Ec %+.2f keV, Ndot x%.2f; "
              "sigma_delta %.3f" % (b, r1["bias"][3], r1["bias"][4], 10 ** r1["bias"][2], r1["sigma"][3]))

    # 2. mechanism decomposition at the representative pulse 2
    m = model_for(1.0)
    em1 = m.pulse_em(PULSE1)
    em2 = m.geometry.em_from_column(MAIN["n_cor"])
    cases = dict(column_only=replace(PULSE1, n_cor=MAIN["n_cor"], em=em1),
                 thermal_only=replace(PULSE1, t_k=MAIN["t_k"], em=em2),
                 both=replace(PULSE1, n_cor=MAIN["n_cor"], t_k=MAIN["t_k"]))
    x1, s1, _ = tb.asimov_fit(m, PULSE1)
    r1 = summarize(m, PULSE1, x1, s1)
    print("\n=== Decomposition at N_cor2 = 1e20, T2 = 20 MK, brightness 1 ===")
    for name, p in cases.items():
        x, s, _ = tb.asimov_fit(m, p)
        r = summarize(m, p, x, s)
        db = delta_b(r1, r)
        res["decomposition"][name] = dict(delta_b=db, **r)
        print("%-13s dB_delta %+.3f (z %5.1f)  dB_Ec %+.2f (z %5.1f)  Ndot2/1 %.2f (z %5.1f)" % (
            name, db["delta"]["delta_b"], db["delta"]["z"], db["ec"]["delta_b"], db["ec"]["z"],
            10 ** db["lndot"]["delta_b"], db["lndot"]["z"]))

    # 3. does the existing nonuniform-ionization (two-zone) fit remove the bias?
    print("\n=== Two-zone (nonuniform ionization) fit ===")
    for b in (1.0, 10.0):
        m = model_for(b)
        for n2 in (1e20, 3e20):
            out = {}
            for label, p in (("pulse1", PULSE1), ("pulse2", replace(PULSE1, n_cor=n2, t_k=MAIN["t_k"]))):
                x, s, _ = tb.asimov_fit(m, p, two_zone=True)
                out[label] = summarize(m, p, x, s, two_zone=True)
            db = delta_b(out["pulse1"], out["pulse2"])
            res["two_zone_fit"]["b%g_n%g" % (b, n2)] = dict(delta_b=db, **out)
            p2 = out["pulse2"]
            print("brightness %4.1f N_cor2 %.0e: dB_delta %+.3f (z %4.1f) dB_Ec %+.2f  Ndot2/1 %.2f | "
                  "fitted log10 Ncor2 %.2f +- %.2f (true %.2f); pulse1 log10 Ncor %.2f +- %.2f (true 19.00)" % (
                      b, n2, db["delta"]["delta_b"], db["delta"]["z"], db["ec"]["delta_b"],
                      10 ** db["lndot"]["delta_b"], p2["fit"][5], p2["sigma"][5], math.log10(n2),
                      out["pulse1"]["fit"][5], out["pulse1"]["sigma"][5]))

    # 4. sensitivity: K_ion/K_neut and fit range
    print("\n=== Sensitivity at N_cor2 = 1e20, T2 = 20 MK, brightness 1 ===")
    p2 = replace(PULSE1, **MAIN)
    for label, m in (("ratio_3.4", model_for(1.0, ratio=3.4)), ("fit_10_100keV", model_for(1.0, fit_range=(10.0, 100.0)))):
        x1, s1, _ = tb.asimov_fit(m, PULSE1)
        x2, s2, _ = tb.asimov_fit(m, p2)
        db = delta_b(summarize(m, PULSE1, x1, s1), summarize(m, p2, x2, s2))
        res["sensitivity"][label] = db
        print("%-14s dB_delta %+.3f (z %5.1f)  dB_Ec %+.2f (z %5.1f)  Ndot2/1 %.2f" % (
            label, db["delta"]["delta_b"], db["delta"]["z"], db["ec"]["delta_b"], db["ec"]["z"],
            10 ** db["lndot"]["delta_b"]))

    # 5. Monte Carlo check of the Asimov/Fisher shortcut
    print("\n=== Monte Carlo check (%d Poisson realizations per pulse, brightness 1) ===" % N_REP)
    m = model_for(1.0)
    mc1 = monte_carlo_parallel(1.0, PULSE1, N_REP, seed=11)
    mc2 = monte_carlo_parallel(1.0, p2, N_REP, seed=101)
    xa1, sa1, _ = tb.asimov_fit(m, PULSE1)
    xa2, sa2, _ = tb.asimov_fit(m, p2)
    for name, i in IDX.items():
        mean_d = mc2[:, i].mean() - mc1[:, i].mean()
        sd = math.hypot(mc1[:, i].std(ddof=1), mc2[:, i].std(ddof=1))
        res["monte_carlo"][name] = dict(mc_delta_b=mean_d, mc_sigma_diff=sd, asimov_delta_b=xa2[i] - xa1[i],
                                        fisher_sigma_diff=math.hypot(sa1[i], sa2[i]),
                                        mc_median_delta_b=float(np.median(mc2[:, i]) - np.median(mc1[:, i])))
        print("%-6s MC: dB %+.3f, sigma_diff %.3f | Asimov/Fisher: dB %+.3f, sigma_diff %.3f" % (
            name, mean_d, sd, xa2[i] - xa1[i], math.hypot(sa1[i], sa2[i])))
    np.save(os.path.join(OUT, "mc_pulse1.npy"), mc1)
    np.save(os.path.join(OUT, "mc_pulse2.npy"), mc2)

    with open(os.path.join(OUT, "summary.json"), "w") as fh:
        json.dump(res, fh, indent=1, default=float)
    print("\nwritten %s (%.0f s)" % (os.path.normpath(os.path.join(OUT, "summary.json")), time.time() - t0))


if __name__ == "__main__":
    main()
