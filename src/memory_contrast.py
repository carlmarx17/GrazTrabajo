"""History contrast of the paired-branch experiment and its decision rule (docs/00, Section 3).

Four runs start from the same initial atmosphere (experiments.build_paired_branches):

    A0  no beam                         B0  test pulse b on the relaxed atmosphere
    A1  pulse 1, no test pulse          B1  pulse 1, waiting time tau, then the same b

For a diagnostic D of each run, at t' = time since the onset of b (t_k in A1 and
B1, the onset of b in B0, the same solver time in A0):

    Delta D_0(t') = D[B0] - D[A0]
    Delta D_1(t') = D[B1] - D[A1]
    M_D(tau, t')  = Delta D_1 - Delta D_0

M_D is the error, for D, of the independent-pulse approximation: adding the
response of a relaxed atmosphere onto the state left by pulse 1.  It stays in
the units of D; nothing is divided by Delta D_0, which can be close to zero.
The decision rule

    |M_D| > k * sigma_tot,   sigma_tot**2 = sigma_num**2 + sigma_beam**2 + sigma_obs**2

uses values fixed and recorded before any contrast is computed.  Whether pulse 1
has relaxed is judged from state variables of A1 and A0 at t_k
(relaxation_check), never from M_D -> 0.
"""
from __future__ import annotations

import math
from typing import Dict, Mapping, Sequence

import numpy as np


def on_common_grid(t: Sequence[float], d: Sequence[float], onset: float,
                   t_rel: Sequence[float]) -> np.ndarray:
    """D(t) of one run sampled at t = onset + t_rel (linear interpolation, no extrapolation)."""
    t = np.asarray(t, float)
    d = np.asarray(d, float)
    want = onset + np.asarray(t_rel, float)
    if t.ndim != 1 or d.shape != t.shape:
        raise ValueError("t and d must be 1-D arrays of equal length")
    if np.any(np.diff(t) <= 0):
        raise ValueError("output times must increase")
    eps = 1e-9 * max(1.0, abs(t[-1]))
    if want.min() < t[0] - eps or want.max() > t[-1] + eps:
        raise ValueError("t' = [%g, %g] s after onset %g s is outside the run [%g, %g] s"
                         % (want.min() - onset, want.max() - onset, onset, t[0], t[-1]))
    return np.interp(want, t, d)


def history_contrast(d_b1, d_a1, d_b0, d_a0) -> np.ndarray:
    """M_D = (B1 - A1) - (B0 - A0), all four sampled on the same t' grid."""
    b1, a1, b0, a0 = (np.asarray(x, float) for x in (d_b1, d_a1, d_b0, d_a0))
    if not b1.shape == a1.shape == b0.shape == a0.shape:
        raise ValueError("the four branches must be sampled on the same t' grid")
    return (b1 - a1) - (b0 - a0)


def peak_abs(m) -> float:
    """max |M| over the analysis window.  NaN means a failed run, not a small effect."""
    m = np.asarray(m, float)
    if m.size == 0 or np.isnan(m).any():
        raise ValueError("contrast is empty or contains NaN: check the runs before deciding")
    return float(np.max(np.abs(m)))


def combined_sigma(numerical, beam, observational):
    """sigma_tot = sqrt(sigma_num^2 + sigma_beam^2 + sigma_obs^2), in the units of D."""
    parts = [np.asarray(x, float) for x in (numerical, beam, observational)]
    if any(np.any(p < 0) for p in parts):
        raise ValueError("uncertainties must be >= 0")
    return np.sqrt(sum(p ** 2 for p in parts))


def exceeds(m, sigma_tot, k: float = 3.0) -> np.ndarray:
    """Where the independent-pulse approximation fails for D: |M| > k * sigma_tot."""
    if not k > 0:
        raise ValueError("k must be > 0")
    return np.abs(np.asarray(m, float)) > k * np.asarray(sigma_tot, float)


def tau_star(taus: Sequence[float], peak_abs_m: Sequence[float], sigma_tot,
             k: float = 3.0) -> Dict[str, object]:
    """Shortest sampled waiting time from which the approximation is adequate at every longer tau.

    peak_abs_m[i] is max |M_D(tau_i, t')| over the analysis window.  tau_star is
    None when the approximation still fails at the longest sampled tau.  It is a
    property of the sampled grid: the approximation may fail between grid points.
    """
    taus = np.asarray(taus, float)
    peaks = np.abs(np.asarray(peak_abs_m, float))
    if taus.ndim != 1 or peaks.shape != taus.shape or taus.size == 0:
        raise ValueError("taus and peak_abs_m must be 1-D arrays of equal, non-zero length")
    if len(set(taus.tolist())) != taus.size:
        raise ValueError("waiting times must be distinct")
    order = np.argsort(taus)
    taus, peaks = taus[order], peaks[order]
    sigma = np.broadcast_to(np.asarray(sigma_tot, float), taus.shape)[order]
    ok = ~exceeds(peaks, sigma, k)
    first = None
    for i in range(taus.size - 1, -1, -1):
        if not ok[i]:
            break
        first = i
    return {"tau_star_s": None if first is None else float(taus[first]),
            "fails_at_s": [float(x) for x in taus[~ok]],
            "adequate_everywhere": bool(ok.all())}


def relaxation_check(state_a1: Mapping[str, float], state_a0: Mapping[str, float],
                     rtol: Mapping[str, float]) -> Dict[str, object]:
    """Has pulse 1 relaxed by t_k?  State variables of A1 and A0 at the same solver time.

    rtol gives the relative tolerance of every variable that is checked, for
    example the coronal column, apex density and temperature, or the column mass
    above the transition region.  Tolerances are declared before the runs.
    """
    if not rtol:
        raise ValueError("declare at least one state variable and its tolerance")
    report = {}
    for name, tol in rtol.items():
        if name not in state_a1 or name not in state_a0:
            raise ValueError("state variable %r missing from A1 or A0" % name)
        a1, a0 = float(state_a1[name]), float(state_a0[name])
        if a0 != 0:
            rel = abs(a1 - a0) / abs(a0)
        else:
            rel = 0.0 if a1 == 0 else math.inf
        report[name] = {"A1": a1, "A0": a0, "relative_difference": rel, "within": rel <= tol}
    return {"relaxed": all(v["within"] for v in report.values()), "variables": report}
