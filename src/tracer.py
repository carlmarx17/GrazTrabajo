"""Evaporated plasma as a tracer of electron paths (project v4).

Plasma evaporated by earlier hard X-ray pulses fills the loops they heated and is seen
in thermal X-rays. It is dense enough to stop flare electrons in the corona (coronal
thick target). If a later pulse sends its electrons through those loops, the loop top
must therefore shine in non-thermal hard X-rays, by an amount set by the measured
thermal emission. This module computes

* a lower bound on the column crossed in the loop-top region, from the thermal
  emission measure and the largest volume compatible with the image,
* the knee energy E* = sqrt(2 K N) below which electrons are stopped in that column,
* the predicted loop-top / footpoint photon ratio R_pred if all electrons re-use the
  filled loops, and
* a conservative upper bound on the fraction phi of electrons that re-use them, given
  an upper limit on the observed ratio.

The bound. Let a fraction phi of the electrons cross the loop-top region along paths of
column N_h >= N_min, and the rest along empty paths. Photons in the band are I_LT(N_h)
from the loop-top crossing, I_rest(N_h) further down (legs and chromosphere), and I_0
from an electron that meets no coronal column (fully neutral thick target). Then

    R_obs (1 + a) = phi I_LT / (phi I_rest + (1 - phi) I_0),

with a the photospheric albedo. Because an ionized target radiates less per unit energy
lost than a neutral one, I_rest <= I_0, so phi <= R_obs (1 + a) I_0 / I_LT(N_h); and
because I_LT grows with the column, phi <= R_obs (1 + a) I_0 / I_LT(N_min). Every
choice that lowers I_LT or raises the observed ratio (filling factor below one, pitch
angles, extra coronal sources such as trapping, thermal emission left in the loop-top
flux, pre-flare coronal column on the empty paths, a larger albedo) only loosens the
bound, so the bound stays valid. Warm-target corrections are below 1 % for electrons
above 25 keV at T <= 30 MK and are neglected; the return current is not covered by
this argument and must be bounded separately (docs/00, Section 3.3).

Transport and bremsstrahlung reuse the two-zone machinery of toy_bias.py (beamed
electrons, Coulomb losses with K_ion / K_neut = 2.8, Haug cross-section).
"""
from __future__ import annotations

import itertools
import math
from dataclasses import dataclass
from typing import Optional, Sequence, Tuple

import numpy as np

from toy_bias import Grid, Target, injection_weights, make_grid, zone_operators


def density_lower_bound(em_cm3: float, volume_max_cm3: float) -> float:
    """rms density [cm^-3] of plasma with emission measure em in a volume <= volume_max.

    A filling factor f < 1 gives n = sqrt(em / (f V)) >= this value.
    """
    if em_cm3 < 0 or volume_max_cm3 <= 0:
        raise ValueError("emission measure must be >= 0 and volume > 0")
    return math.sqrt(em_cm3 / volume_max_cm3)


def column_lower_bound(em_cm3: float, volume_max_cm3: float, path_min_cm: float) -> float:
    """Lower bound on the column [cm^-2] crossed along a path of length >= path_min."""
    if path_min_cm < 0:
        raise ValueError("path length must be >= 0")
    return density_lower_bound(em_cm3, volume_max_cm3) * path_min_cm


def knee_energy_kev(column_cm2: float, target: Target = Target()) -> float:
    """Electron energy [keV] that is just stopped by an ionized column (beamed, cold target)."""
    return math.sqrt(2.0 * target.k_ion * column_cm2)


@dataclass(frozen=True)
class BandPhotons:
    """Photons in the band per injected electron spectrum (arbitrary common units)."""
    loop_top: float      # emitted while crossing the loop-top column
    rest: float          # emitted further down: legs (ionized) and chromosphere (neutral)
    all_neutral: float   # same electrons in a fully neutral thick target (empty loop)


class TracerModel:
    def __init__(self, grid: Optional[Grid] = None, target: Target = Target(),
                 band: Tuple[float, float] = (25.0, 50.0)):
        if not band[0] < band[1]:
            raise ValueError("band must be (low, high) with low < high")
        self.grid = grid or make_grid()
        self.target = target
        self.band = band
        k = self.grid.k
        self.w = np.where((k >= band[0]) & (k <= band[1]), self.grid.wk, 0.0)
        _, ch0 = zone_operators(self.grid.h, self.grid.e, target, 0.0)
        self._w_ch0 = self.w @ ch0

    def band_photons(self, delta: float, ec_kev: float, n_lt: float, n_leg: float = 0.0) -> BandPhotons:
        """Photons in the band for a loop-top column n_lt followed by a leg column n_leg."""
        if n_lt < 0 or n_leg < 0:
            raise ValueError("columns must be >= 0")
        e, h = self.grid.e, self.grid.h
        c = injection_weights(e, 1.0, delta, ec_kev)      # the electron rate cancels in ratios
        cor_lt, _ = zone_operators(h, e, self.target, n_lt)
        cor_all, ch_all = zone_operators(h, e, self.target, n_lt + n_leg)
        i_lt = float(self.w @ (cor_lt @ c))
        i_rest = float(self.w @ ((cor_all - cor_lt + ch_all) @ c))
        return BandPhotons(i_lt, i_rest, float(self._w_ch0 @ c))

    def photon_spectra(self, delta: float, ec_kev: float, n_lt: float, n_leg: float = 0.0
                       ) -> Tuple[np.ndarray, np.ndarray, np.ndarray]:
        """Photon spectra on the grid's photon energies: (loop top, rest, all neutral)."""
        if n_lt < 0 or n_leg < 0:
            raise ValueError("columns must be >= 0")
        e, h = self.grid.e, self.grid.h
        c = injection_weights(e, 1.0, delta, ec_kev)
        cor_lt, _ = zone_operators(h, e, self.target, n_lt)
        cor_all, ch_all = zone_operators(h, e, self.target, n_lt + n_leg)
        _, ch0 = zone_operators(h, e, self.target, 0.0)
        return cor_lt @ c, (cor_all - cor_lt + ch_all) @ c, ch0 @ c

    def r_in_bins(self, phi: float, delta: float, ec_kev: float, n_lt: float, edges_kev: Sequence[float],
                  n_leg: float = 0.0, albedo: float = 0.0) -> np.ndarray:
        """Loop-top / footpoint ratio in energy bins for a re-use fraction phi.

        Under re-use the ratio falls steeply above the knee E* = sqrt(2 K N_lt); a
        calibration error that does not depend on energy only adds a constant, so the
        shape constrains phi even when the absolute level is uncertain.
        """
        if not 0.0 <= phi <= 1.0:
            raise ValueError("phi must be in [0, 1]")
        i_lt, i_rest, i_0 = self.photon_spectra(delta, ec_kev, n_lt, n_leg)
        k, wk = self.grid.k, self.grid.wk
        out = []
        for lo, hi in zip(edges_kev[:-1], edges_kev[1:]):
            w = np.where((k >= lo) & (k <= hi), wk, 0.0)
            lt = phi * float(w @ i_lt)
            fp = (phi * float(w @ i_rest) + (1.0 - phi) * float(w @ i_0)) * (1.0 + albedo)
            out.append(lt / fp)
        return np.array(out)

    def r_predicted(self, delta: float, ec_kev: float, n_lt: float, n_leg: float = 0.0,
                    albedo: float = 0.0) -> float:
        """Loop-top / footpoint ratio if every electron crosses the filled loop (phi = 1)."""
        b = self.band_photons(delta, ec_kev, n_lt, n_leg)
        return b.loop_top / (b.rest * (1.0 + albedo))

    def r_mixture(self, phi: float, delta: float, ec_kev: float, n_lt: float, n_leg: float = 0.0,
                  albedo: float = 0.0) -> float:
        """Ratio when a fraction phi crosses the filled loop and the rest empty loops."""
        if not 0.0 <= phi <= 1.0:
            raise ValueError("phi must be in [0, 1]")
        b = self.band_photons(delta, ec_kev, n_lt, n_leg)
        return phi * b.loop_top / ((phi * b.rest + (1.0 - phi) * b.all_neutral) * (1.0 + albedo))

    def reuse_upper_bound(self, r_obs_max: float, n_lt_min: float, deltas: Sequence[float],
                          ecs_kev: Sequence[float], albedo_max: float = 0.0) -> float:
        """Upper bound on phi, valid over all listed spectral parameters (take their ranges).

        Values >= 1 mean the pulse is not informative.
        """
        if r_obs_max < 0:
            raise ValueError("r_obs_max must be >= 0")
        worst = 0.0
        for d, ec in itertools.product(deltas, ecs_kev):
            b = self.band_photons(d, ec, n_lt_min)
            if b.loop_top <= 0:
                return math.inf
            worst = max(worst, b.all_neutral / b.loop_top)
        return r_obs_max * (1.0 + albedo_max) * worst

    def informative(self, r_min_detectable: float, n_lt_min: float, deltas: Sequence[float],
                    ecs_kev: Sequence[float], albedo_max: float = 0.0, phi_target: float = 0.3) -> bool:
        """True if a non-detection at r_min_detectable would give phi_max <= phi_target."""
        return self.reuse_upper_bound(r_min_detectable, n_lt_min, deltas, ecs_kev, albedo_max) <= phi_target
