"""Toy inject-reinfer test: does atmospheric memory bias the STIX electron inference?

This is a semi-analytic forward model, not a radiation-hydrodynamic simulation. The
coronal column and the temperature after the first pulse are inputs; a hydrodynamic
code (HYDRAD, or RADYN) has to supply them for a real case. The point of the toy is to
measure, cheaply, whether the bias it predicts is large compared with the statistical
error of a STIX fit, before the expensive chain is built.

Physics included
- Electron transport: beamed electrons (mu = 1) slowing down by Coulomb collisions,
  dE/dN = -K/E with K = 2 pi e^4 Lambda, in a two-zone target: a fully ionized corona of
  column N_cor followed by a neutral chromosphere, as in the nonuniform-ionization model
  of Kontar, Brown & McArthur (2002). K_ion / K_neut = 2.8 by default.
- Bremsstrahlung: electron-ion cross-section of Haug (1997, A&A 326, 417, Eq. 4) with the
  Elwert factor, for a mean atomic number z = 1.2, the same choice as the FP solver and
  the HESSI routine Brm_BremCross.
- Thermal emission: free-free from a Maxwellian with the same cross-section; no lines and
  no free-bound emission (absent in the fit model too, so they cannot create a bias here).
- Instrument: an illustrative STIX-like response (effective area, Gaussian energy
  resolution, STIX-like science energy channels). It is NOT the STIX response matrix.

Not included: warm-target effects, return current, pitch-angle scattering, albedo,
spectral lines, pile-up, attenuator, background, and any hydrodynamics.

The "standard model" used for the re-inference is an isothermal component plus a cold
thick target with a uniform, fully ionized target. The "two-zone model" adds N_cor as a
free parameter (a nonuniform-ionization fit).
"""
from __future__ import annotations

import math
from dataclasses import dataclass
from typing import Callable, Optional, Tuple

import numpy as np
from scipy.optimize import minimize
from scipy.special import erf

MC2_KEV = 510.99895
ALPHA = 7.2973525693e-3
R0_CM = 2.8179403262e-13
TWO_ALPHA_R02 = 2.0 * ALPHA * R0_CM ** 2            # cm^2
E_ESU = 4.80320471e-10
KEV_PER_ERG = 1.0 / 1.602176634e-9
TWO_PI_E4 = 2.0 * math.pi * E_ESU ** 4 * KEV_PER_ERG ** 2   # keV^2 cm^2
C_CM_S = 2.99792458e10
KB_KEV_PER_K = 8.617333262e-8
AU_CM = 1.495978707e13

# Approximately the STIX science energy channels between 4 and 150 keV (to be checked
# against the STIX documentation before any use with real data).
STIX_LIKE_EDGES_KEV = np.array([4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16, 18, 20, 22, 25, 28,
                                32, 36, 40, 45, 50, 56, 63, 70, 76, 84, 100, 120, 150], float)


# --------------------------------------------------------------------------- physics
def haug_cross(eel, eph, z: float = 1.2) -> np.ndarray:
    """Electron-ion bremsstrahlung cross-section dσ/dk [cm^2 keV^-1] (Haug 1997, Eq. 4 + Elwert).

    eel: electron kinetic energy [keV]; eph: photon energy [keV]; zero where eph >= eel.
    """
    eel, eph = np.broadcast_arrays(np.asarray(eel, float), np.asarray(eph, float))
    out = np.zeros(eel.shape)
    ok = eph < eel
    k = eph[ok] / MC2_KEV
    e1 = eel[ok] / MC2_KEV + 1.0
    e2 = e1 - k
    p1 = np.sqrt(e1 * e1 - 1.0)
    p2 = np.sqrt(e2 * e2 - 1.0)
    e1e2, p1p2 = e1 * e2, p1 * p2
    k2 = k * k
    pe = (p1 * p1 + p2 * p2) / e1e2 ** 3
    ch1 = (4.0 / 3.0 * e1e2 + k2) - (7.0 / 15.0 * k2 / e1e2) - (11.0 / 70.0 * k2 * pe / e1e2)
    ch2 = 1.0 + 1.0 / e1e2 + 7.0 / 20.0 * pe + (9.0 / 28.0 * k2 + 263.0 / 210.0 * p1p2 ** 2) / e1e2 ** 3
    cr = ch1 * (2.0 * np.log((e1e2 + p1p2 - 1.0) / k) - p1p2 / e1e2 * ch2)
    cr = z * z * cr / (k * p1 * p1)
    a1 = ALPHA * z * e1 / p1
    a2 = ALPHA * z * e2 / p2
    fe = (a2 / a1) * (1.0 - np.exp(-2.0 * np.pi * a1)) / (1.0 - np.exp(-2.0 * np.pi * a2))
    out[ok] = TWO_ALPHA_R02 * fe * cr / MC2_KEV
    return out


def trapezoid_weights(x: np.ndarray) -> np.ndarray:
    w = np.zeros_like(x)
    d = np.diff(x)
    w[:-1] += 0.5 * d
    w[1:] += 0.5 * d
    return w


@dataclass(frozen=True)
class Grid:
    e: np.ndarray        # electron energies [keV]
    we: np.ndarray       # trapezoid weights in e
    k: np.ndarray        # photon energies [keV]
    wk: np.ndarray       # trapezoid weights in k
    sigma: np.ndarray    # (nk, ne) dσ/dk [cm^2 keV^-1]
    h: np.ndarray        # (nk, ne) ∫_0^E σ(k,E') E' dE'  [cm^2 keV]


def make_grid(ne: int = 1000, nk: int = 300, e_range=(1.0, 3000.0), k_range=(3.0, 200.0),
              z: float = 1.2, cross: Optional[Callable] = None) -> Grid:
    cross = cross or (lambda ee, kk: haug_cross(ee, kk, z))
    e = np.geomspace(e_range[0], e_range[1], ne)
    k = np.geomspace(k_range[0], k_range[1], nk)
    sigma = cross(e[None, :], k[:, None])
    g = sigma * e[None, :]
    h = np.zeros_like(g)
    h[:, 1:] = np.cumsum(0.5 * (g[:, 1:] + g[:, :-1]) * np.diff(e)[None, :], axis=1)
    return Grid(e, trapezoid_weights(e), k, trapezoid_weights(k), sigma, h)


@dataclass(frozen=True)
class Target:
    lambda_ion: float = 20.0           # Coulomb logarithm of the ionized target
    ion_to_neutral_loss: float = 2.8   # K_ion / K_neut (Kontar et al. 2002: yield up to 2.8x)

    @property
    def k_ion(self) -> float:
        return TWO_PI_E4 * self.lambda_ion

    @property
    def k_neut(self) -> float:
        return self.k_ion / self.ion_to_neutral_loss

    def stopping_column(self, e_kev) -> np.ndarray:
        """Column [cm^-2] that stops an electron of energy e in the ionized target (mu = 1)."""
        return np.asarray(e_kev, float) ** 2 / (2.0 * self.k_ion)


def _interp_columns(a: np.ndarray, e: np.ndarray, e_new: np.ndarray) -> np.ndarray:
    idx = np.clip(np.searchsorted(e, e_new, side="right") - 1, 0, e.size - 2)
    t = np.clip((e_new - e[idx]) / (e[idx + 1] - e[idx]), 0.0, 1.0)
    out = a[:, idx] * (1.0 - t) + a[:, idx + 1] * t
    out[:, e_new <= e[0]] = 0.0
    return out


def zone_operators(a: np.ndarray, e: np.ndarray, target: Target, n_cor: float) -> Tuple[np.ndarray, np.ndarray]:
    """Split an operator built on h (rows: photon energies or channels; columns: injected
    energies) into the corona (ionized, column n_cor) and chromosphere (neutral) parts.

    Photons per keV emitted by one electron of initial energy E0 in a zone traversed from
    E_in to E_out are ∫ σ(k,E) E / K dE between E_out and E_in, and E_out^2 = E0^2 - 2 K N.
    n_cor = inf gives the uniform ionized thick target; n_cor = 0 a fully neutral one.
    """
    e_out = np.sqrt(np.maximum(e * e - 2.0 * target.k_ion * n_cor, 0.0))
    a_out = _interp_columns(a, e, e_out)
    return (a - a_out) / target.k_ion, a_out / target.k_neut


def injection_weights(e: np.ndarray, ndot: float, delta: float, ec: float) -> np.ndarray:
    """Coefficients c with ∫_Ec^∞ F0(E) g(E) dE ≈ Σ c_j g(E_j) for g linear between nodes.

    F0(E) = ndot (δ-1)/Ec (E/Ec)^-δ [electrons s^-1 keV^-1]; the weights are continuous in Ec.
    """
    c = np.zeros(e.size)
    j = int(np.searchsorted(e, ec))
    if j >= e.size:
        return c
    fe = ndot * (delta - 1.0) / ec * (e / ec) ** (-delta)
    if j < e.size - 1:
        seg = e[j + 1:] - e[j:-1]
        c[j:-1] += 0.5 * seg * fe[j:-1]
        c[j + 1:] += 0.5 * seg * fe[j + 1:]
    if j > 0 and e[j] > ec:
        d = e[j] - ec
        t = (ec - e[j - 1]) / (e[j] - e[j - 1])
        fec = ndot * (delta - 1.0) / ec
        c[j - 1] += 0.5 * d * fec * (1.0 - t)
        c[j] += 0.5 * d * (fec * t + fe[j])
    return c


def maxwellian_vf(e: np.ndarray, t_k: float) -> np.ndarray:
    """v(E) f(E) for a Maxwellian normalized to one particle [cm s^-1 keV^-1]."""
    kt = KB_KEV_PER_K * t_k
    f = (2.0 / np.sqrt(np.pi)) * np.sqrt(e) * kt ** -1.5 * np.exp(-e / kt)
    gam = 1.0 + e / MC2_KEV
    return C_CM_S * np.sqrt(1.0 - 1.0 / gam ** 2) * f


# --------------------------------------------------------------------------- instrument
@dataclass(frozen=True)
class Instrument:
    edges: np.ndarray
    response: np.ndarray     # (nch, nk): counts per unit photon flux density on the k grid
    fit_mask: np.ndarray     # channels used in the fit


def make_instrument(grid: Grid, edges=STIX_LIKE_EDGES_KEV, exposure_s: float = 10.0,
                    area_cm2: float = 6.0, fit_range=(6.0, 100.0)) -> Instrument:
    """Illustrative STIX-like response: smooth low-energy window cut-off near 3-4 keV, CdTe
    efficiency falling above ~100 keV, FWHM resolution sqrt(1 + (0.02 k)^2) keV."""
    k = grid.k
    aeff = area_cm2 * np.exp(-(3.2 / k) ** 3) * (1.0 - np.exp(-(130.0 / k) ** 2.5))
    sig = np.sqrt(1.0 + (0.02 * k) ** 2) / 2.3548
    edges = np.asarray(edges, float)
    lo, hi = edges[:-1, None], edges[1:, None]
    p = 0.5 * (erf((hi - k[None, :]) / (np.sqrt(2.0) * sig[None, :]))
               - erf((lo - k[None, :]) / (np.sqrt(2.0) * sig[None, :])))
    resp = exposure_s * p * (aeff * grid.wk)[None, :]
    mask = (edges[:-1] >= fit_range[0] - 1e-9) & (edges[1:] <= fit_range[1] + 1e-9)
    return Instrument(edges, resp, mask)


# --------------------------------------------------------------------------- scenario
@dataclass(frozen=True)
class Geometry:
    area_cm2: float = 1.0e17        # loop cross-section (order of Collier et al. 2024)
    half_length_cm: float = 1.3e9   # loop half-length (as the FP example loop)
    distance_au: float = 0.5        # Solar Orbiter distance

    def em_from_column(self, n_cor: float) -> float:
        """Emission measure of a uniform corona of column n_cor in both legs [cm^-3]."""
        return 2.0 * n_cor ** 2 * self.area_cm2 / self.half_length_cm


@dataclass(frozen=True)
class Pulse:
    ndot: float = 3.4e34      # electrons s^-1 above Ec   (Collier et al. 2024, first burst)
    delta: float = 4.97
    ec_kev: float = 13.4
    n_cor: float = 1.0e19     # ionized coronal column [cm^-2]
    t_k: float = 3.0e6        # coronal temperature [K]
    em: Optional[float] = None  # emission measure; None ties it to n_cor via Geometry


# parameter vectors: standard = (log10 T, log10 EM, log10 ndot, delta, Ec); two-zone adds log10 N_cor
STANDARD_LOWER = np.array([6.3, 40.0, 30.0, 2.2, 3.0])
STANDARD_UPPER = np.array([7.8, 51.0, 38.0, 12.0, 60.0])
NCOR_LOWER, NCOR_UPPER = 17.0, 22.0
PARAM_NAMES = ("log10_T", "log10_EM", "log10_ndot", "delta", "Ec_keV", "log10_Ncor")


class ForwardModel:
    def __init__(self, grid: Optional[Grid] = None, instrument: Optional[Instrument] = None,
                 target: Target = Target(), geometry: Geometry = Geometry()):
        self.grid = grid or make_grid()
        self.instrument = instrument or make_instrument(self.grid)
        self.target = target
        self.geometry = geometry
        self.dilution = 1.0 / (4.0 * math.pi * (geometry.distance_au * AU_CM) ** 2)
        self.rh = self.instrument.response @ self.grid.h          # (nch, ne)
        self.rs = self.instrument.response @ self.grid.sigma      # (nch, ne)
        self.rh_uniform = self.rh / target.k_ion

    # -- counts
    def thermal_counts(self, t_k: float, em: float) -> np.ndarray:
        return em * self.dilution * (self.rs @ (maxwellian_vf(self.grid.e, t_k) * self.grid.we))

    def nonthermal_counts(self, ndot: float, delta: float, ec: float, n_cor: float = np.inf) -> np.ndarray:
        c = injection_weights(self.grid.e, ndot, delta, ec)
        if np.isinf(n_cor):
            op = self.rh_uniform
        else:
            cor, ch = zone_operators(self.rh, self.grid.e, self.target, n_cor)
            op = cor + ch
        return self.dilution * (op @ c)

    def pulse_em(self, pulse: Pulse) -> float:
        return pulse.em if pulse.em is not None else self.geometry.em_from_column(pulse.n_cor)

    def pulse_counts(self, pulse: Pulse) -> np.ndarray:
        return (self.thermal_counts(pulse.t_k, self.pulse_em(pulse))
                + self.nonthermal_counts(pulse.ndot, pulse.delta, pulse.ec_kev, pulse.n_cor))

    def model_counts(self, x: np.ndarray) -> np.ndarray:
        n_cor = 10.0 ** x[5] if x.size > 5 else np.inf
        return (self.thermal_counts(10.0 ** x[0], 10.0 ** x[1])
                + self.nonthermal_counts(10.0 ** x[2], x[3], x[4], n_cor))

    # -- diagnostics
    def coronal_photon_fraction(self, pulse: Pulse, band=(25.0, 50.0)) -> float:
        """Fraction of the non-thermal photons in a band emitted in the corona (an upper
        bound on a loop-top source, since the coronal emission is spread along the legs)."""
        c = injection_weights(self.grid.e, pulse.ndot, pulse.delta, pulse.ec_kev)
        cor, ch = zone_operators(self.grid.h, self.grid.e, self.target, pulse.n_cor)
        sel = (self.grid.k >= band[0]) & (self.grid.k <= band[1])
        w = self.grid.wk[sel]
        i_cor, i_ch = (cor @ c)[sel], (ch @ c)[sel]
        return float(np.sum(w * i_cor) / np.sum(w * (i_cor + i_ch)))

    def coronal_energy_fraction(self, pulse: Pulse) -> float:
        """Fraction of the injected beam energy deposited in the ionized corona."""
        e = self.grid.e
        c = injection_weights(e, pulse.ndot, pulse.delta, pulse.ec_kev)
        e_out = np.sqrt(np.maximum(e * e - 2.0 * self.target.k_ion * pulse.n_cor, 0.0))
        return float(np.sum(c * (e - e_out)) / np.sum(c * e))


def truth_vector(model: ForwardModel, pulse: Pulse, two_zone: bool = False) -> np.ndarray:
    x = [math.log10(pulse.t_k), math.log10(model.pulse_em(pulse)), math.log10(pulse.ndot),
         pulse.delta, pulse.ec_kev]
    if two_zone:
        x.append(math.log10(pulse.n_cor))
    return np.array(x)


# --------------------------------------------------------------------------- fitting
def _bounds(two_zone: bool) -> Tuple[np.ndarray, np.ndarray]:
    if two_zone:
        return np.append(STANDARD_LOWER, NCOR_LOWER), np.append(STANDARD_UPPER, NCOR_UPPER)
    return STANDARD_LOWER, STANDARD_UPPER


def cash(model: ForwardModel, x: np.ndarray, counts: np.ndarray, mask: np.ndarray) -> float:
    mu = model.model_counts(x)[mask]
    if not np.all(np.isfinite(mu)) or np.any(mu <= 0):
        return 1e30
    n = counts[mask]
    return float(2.0 * np.sum(mu - n * np.log(mu)))


def fit(model: ForwardModel, counts: np.ndarray, x0: np.ndarray, restarts: int = 2) -> Tuple[np.ndarray, float]:
    """Poisson maximum-likelihood (Cash) fit with Nelder-Mead and restarts.

    The parameter vector decides the model: 5 entries = standard, 6 = two-zone.
    """
    lo, hi = _bounds(x0.size > 5)
    mask = model.instrument.fit_mask

    def objective(x):
        if np.any(x < lo) or np.any(x > hi):
            return 1e30
        return cash(model, x, counts, mask)

    x = np.clip(np.asarray(x0, float), lo + 1e-6, hi - 1e-6)
    best = None
    for _ in range(restarts + 1):
        res = minimize(objective, x, method="Nelder-Mead",
                       options=dict(maxiter=10000, maxfev=10000, xatol=1e-6, fatol=1e-6, adaptive=True))
        if best is None or res.fun < best.fun:
            best = res
        x = best.x
    return best.x, float(best.fun)


def fisher_sigma(model: ForwardModel, x: np.ndarray, rel_step: float = 1e-4) -> np.ndarray:
    """1-sigma errors from the Poisson Fisher matrix Σ (1/μ) ∂μ/∂x_i ∂μ/∂x_j at x."""
    mask = model.instrument.fit_mask
    mu = model.model_counts(x)[mask]
    grads = []
    for i in range(x.size):
        h = rel_step * max(1.0, abs(x[i]))
        xp, xm = x.copy(), x.copy()
        xp[i] += h
        xm[i] -= h
        grads.append((model.model_counts(xp)[mask] - model.model_counts(xm)[mask]) / (2 * h))
    g = np.array(grads)
    fmat = (g / mu) @ g.T
    cov = np.linalg.pinv(fmat)
    return np.sqrt(np.clip(np.diag(cov), 0.0, None))


def asimov_fit(model: ForwardModel, pulse: Pulse, x0: Optional[np.ndarray] = None,
               two_zone: bool = False) -> Tuple[np.ndarray, np.ndarray, float]:
    """Fit the noise-free expected counts: the large-sample bias, plus Fisher errors."""
    mu = model.pulse_counts(pulse)
    if x0 is None:
        x0 = initial_guess(model, pulse, two_zone)
    x, f = fit(model, mu, x0)
    return x, fisher_sigma(model, x), f


def initial_guess(model: ForwardModel, pulse: Pulse, two_zone: bool = False) -> np.ndarray:
    """An analyst's starting point: the true beam, and a thermal guess at least 8 MK and
    1e45 cm^-3 (a relaxed corona is invisible to STIX)."""
    x = truth_vector(model, pulse, two_zone)
    x[0] = max(x[0], math.log10(8e6))
    x[1] = max(x[1], 45.0)
    return x


def monte_carlo(model: ForwardModel, pulse: Pulse, n_rep: int, seed: int,
                two_zone: bool = False) -> np.ndarray:
    """Fit n_rep Poisson realizations of the pulse; returns (n_rep, nparam)."""
    rng = np.random.default_rng(seed)
    mu = model.pulse_counts(pulse)
    x0 = initial_guess(model, pulse, two_zone)
    out = []
    for _ in range(n_rep):
        x, _ = fit(model, rng.poisson(mu).astype(float), x0, restarts=1)
        out.append(x)
    return np.array(out)
