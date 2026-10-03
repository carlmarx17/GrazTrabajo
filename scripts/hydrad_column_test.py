"""Column test (decision gate OE1) on HYDRAD runs, and the toy bias it implies.

Reads HYDRAD profiles (Results/profileN.phy, columns s, v, Cs, n_e, n_H, P_e, P_H, T_e, T_H,
Fc_e, Fc_H) of the E2 (two pulses) and E5 (pulse 1 only) runs, measures at the onset of
each pulse the hydrogen column of the plasma hotter than a threshold (taken as the
ionized corona and transition region), the emission-measure-weighted temperature and the
emission measure of the T > 1 MK plasma, compares the column with the stopping column of
the beam, and feeds those numbers to the toy inject-reinfer model (src/toy_bias.py).

    .venv/bin/python scripts/hydrad_column_test.py <E2 results dir> <E5 results dir>

HYDRAD's .phy files carry n_e = n_H (no hydrogen ionization is modelled with the shipped
configuration), so the ionized/neutral boundary is defined by temperature.
"""
from __future__ import annotations

import json
import os
import sys
from dataclasses import replace

import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, "..", "src"))
import toy_bias as tb  # noqa: E402
from experiments import BaseCase  # noqa: E402

AREA_CM2 = 1.0e17            # loop cross-section, as BaseCase.area_cm2
THRESHOLDS_K = (3.0e4, 1.0e5)
OUT = os.path.join(HERE, "..", "results", "hydrad_column")


def load(results_dir: str, i: int) -> dict:
    a = np.loadtxt(os.path.join(results_dir, "profile%d.phy" % i))
    s = a[:, 0]
    edges = np.concatenate([[s[0] - 0.5 * (s[1] - s[0])], 0.5 * (s[1:] + s[:-1]), [s[-1] + 0.5 * (s[-1] - s[-2])]])
    return dict(s=s, ds=np.diff(edges), v=a[:, 1], ne=a[:, 3], nh=a[:, 4], te=a[:, 7], th=a[:, 8])


def diagnostics(p: dict, loop_length: float) -> dict:
    apex = 0.5 * loop_length
    legs = (p["s"] <= apex, p["s"] > apex)
    out = {}
    for thr in THRESHOLDS_K:
        hot = p["te"] > thr
        out["N_cor_leg1_T>%g" % thr] = float(np.sum((p["nh"] * p["ds"])[hot & legs[0]]))
        out["N_cor_leg2_T>%g" % thr] = float(np.sum((p["nh"] * p["ds"])[hot & legs[1]]))
    cor = p["te"] > 1e6
    w = p["ne"] ** 2 * p["ds"]
    out["EM_T>1MK"] = float(np.sum(w[cor]) * AREA_CM2)
    out["T_EM_T>1MK"] = float(np.sum((w * p["te"])[cor]) / np.sum(w[cor])) if np.any(cor) else float("nan")
    k = int(np.argmin(np.abs(p["s"] - apex)))
    out["T_apex"], out["n_apex"] = float(p["te"][k]), float(p["ne"][k])
    out["v_max_up_kms"] = float(np.max(np.abs(p["v"])) / 1e5)
    return out


def main(e2_dir: str, e5_dir: str) -> None:
    base = BaseCase()
    loop_length = 6.0e9                       # Initial_Conditions/config: L = 6e9 cm
    pulses = base.pulses()
    t1, t2 = pulses[0].t_start, pulses[1].t_start
    n_stop = float(tb.Target().stopping_column(base.ec_kev))

    print("Stopping column of a %.0f keV electron (ionized, mu = 1): %.2e cm^-2" % (base.ec_kev, n_stop))
    print("\n t[s]  N_cor leg1 (T>3e4 K)  N_cor leg2  N_cor (T>1e5 K)  T_apex[MK]  n_apex[cm^-3]  EM(T>1MK)  T_EM[MK]  |v|max[km/s]")
    series = {}
    for i in sorted({0, 1, 5, 11, 16, 21, 26, 30, 31, 36, 41, 51, 71, 101}):
        d = diagnostics(load(e2_dir, i), loop_length)
        series[i] = d
        print("%5d  %18.2e  %10.2e  %15.2e  %10.2f  %13.2e  %9.2e  %8.2f  %10.0f" % (
            i, d["N_cor_leg1_T>30000"], d["N_cor_leg2_T>30000"], d["N_cor_leg1_T>100000"], d["T_apex"] / 1e6,
            d["n_apex"], d["EM_T>1MK"], d["T_EM_T>1MK"] / 1e6, d["v_max_up_kms"]))

    # last saved profile before each ramp starts (ramp centred on the nominal onset, 1 s cadence)
    i1, i2 = (int(np.floor(t - 0.5 * base.ramp - 1e-9)) for t in (t1, t2))
    d1, d2 = diagnostics(load(e2_dir, i1), loop_length), diagnostics(load(e2_dir, i2), loop_length)
    d2_e5 = diagnostics(load(e5_dir, i2), loop_length)
    same = abs(d2["N_cor_leg1_T>30000"] / d2_e5["N_cor_leg1_T>30000"] - 1)
    print("\nE2 and E5 share the history up to pulse 2: relative difference of N_cor at t = %d s: %.1e" % (i2, same))
    print("Profiles used: pulse-1 onset t = %d s, pulse-2 onset t = %d s (ramps start at %.1f and %.1f s)" % (
        i1, i2, t1 - 0.5 * base.ramp, t2 - 0.5 * base.ramp))

    ratio1 = d1["N_cor_leg1_T>30000"] / n_stop
    ratio2 = d2["N_cor_leg1_T>30000"] / n_stop
    print("Gate (OE1): N_cor/N_stop(Ec) = %.3f at pulse-1 onset, %.3f at pulse-2 onset (x%.1f)" % (
        ratio1, ratio2, ratio2 / ratio1))

    # toy prediction for the same synthetic beam
    model_kw = dict(ndot=base.ndot, delta=base.delta, ec_kev=base.ec_kev)
    p1 = tb.Pulse(n_cor=d1["N_cor_leg1_T>30000"], t_k=max(d1["T_EM_T>1MK"], 1e6), em=max(d1["EM_T>1MK"], 1e40), **model_kw)
    p2 = tb.Pulse(n_cor=d2["N_cor_leg1_T>30000"], t_k=d2["T_EM_T>1MK"], em=d2["EM_T>1MK"], **model_kw)
    print("\nToy inject-reinfer with the HYDRAD atmosphere (beam: Ndot %.1e, Ec %.0f keV, delta %.0f)" % (
        base.ndot, base.ec_kev, base.delta))
    print("pulse 1: N_cor %.2e, T %.1f MK, EM %.1e | pulse 2: N_cor %.2e, T %.1f MK, EM %.1e" % (
        p1.n_cor, p1.t_k / 1e6, p1.em, p2.n_cor, p2.t_k / 1e6, p2.em))
    toy = {}
    grid = tb.make_grid()
    for b in (0.1, 1.0, 10.0):
        m = tb.ForwardModel(grid=grid, instrument=tb.make_instrument(grid, exposure_s=10.0 * b))
        x1, s1, _ = tb.asimov_fit(m, p1)
        x2, s2, _ = tb.asimov_fit(m, p2)
        counts = float(m.pulse_counts(p1)[m.instrument.fit_mask].sum())
        row = {}
        for name, i in (("delta", 3), ("Ec", 4), ("log10_ndot", 2)):
            d = x2[i] - x1[i]
            sd = float(np.hypot(s1[i], s2[i]))
            row[name] = dict(delta_b=float(d), sigma_diff=sd, z=float(d / sd))
        row["counts_pulse1"] = counts
        toy[b] = row
        print("brightness %4.1f (%.1e counts): d_delta %+.3f (z %+.1f)  d_Ec %+.2f keV (z %+.1f)  Ndot2/Ndot1 %.2f (z %+.1f)" % (
            b, counts, row["delta"]["delta_b"], row["delta"]["z"], row["Ec"]["delta_b"], row["Ec"]["z"],
            10 ** row["log10_ndot"]["delta_b"], row["log10_ndot"]["z"]))
    m1 = tb.ForwardModel(grid=grid)
    print("coronal energy fraction: pulse 1 %.2f, pulse 2 %.2f; 25-50 keV coronal photon fraction: %.2f -> %.2f" % (
        m1.coronal_energy_fraction(p1), m1.coronal_energy_fraction(p2),
        m1.coronal_photon_fraction(p1), m1.coronal_photon_fraction(p2)))

    os.makedirs(OUT, exist_ok=True)
    with open(os.path.join(OUT, "summary.json"), "w") as fh:
        json.dump(dict(n_stop=n_stop, series=series, pulse1=d1, pulse2=d2, e2_e5_difference=same,
                       gate_ratio=[ratio1, ratio2], toy=toy), fh, indent=1)
    print("\nwritten", os.path.normpath(os.path.join(OUT, "summary.json")))


if __name__ == "__main__":
    main(sys.argv[1], sys.argv[2])
