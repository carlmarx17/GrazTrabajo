"""Beam-heating tables for successive electron pulses.

Converts a physical description of electron pulses (electron rate, low-energy
cut-off, spectral index, emitting area) into the time-dependent table read by
HYDRAD (Heating_Model/config/beam_heating_model.cfg), and verifies energy
conservation of the encoding.

Physical model of one pulse (collisional thick target, single power law in
electron number above Ec, index delta > 2):

    P = Ndot * Ec * (delta - 1) / (delta - 2)      [erg s^-1]
    F = P / A                                      [erg cm^-2 s^-1]

Ndot is the rate of electrons above Ec [s^-1], Ec is converted from keV to erg,
A is the cross-section of the flux tube at the injection site [cm^2].  Electron
rate, power, energy flux and volumetric deposition are different quantities and
are never mixed here.

HYDRAD reads rows (t, F, Ec, delta), interpolates all three LINEARLY between
rows, and switches the beam off before the first and after the last row.  A
boxcar pulse therefore needs explicit F = 0 rows and a finite ramp; the ramp is
centred on the nominal pulse boundaries so that the integral of F dt equals
F * duration exactly.
"""
from __future__ import annotations

from dataclasses import dataclass
from typing import List, Sequence, Tuple

KEV_TO_ERG = 1.602176634e-9  # erg per keV (HYDRAD hard-wires 1.602e-9; 1e-4 relative difference)

# HYDRAD aborts the heating integral for delta <= 2; keep a margin so that
# (delta - 2) in the denominators is never numerically small.
MIN_DELTA = 2.0 + 1e-6


def power_erg_s(ndot: float, ec_kev: float, delta: float) -> float:
    """Beam power above Ec for a single power law with no upper cut-off."""
    _check_delta(delta)
    return ndot * ec_kev * KEV_TO_ERG * (delta - 1.0) / (delta - 2.0)


def energy_flux(ndot: float, ec_kev: float, delta: float, area_cm2: float) -> float:
    """Energy flux F = P / A [erg cm^-2 s^-1]."""
    if area_cm2 <= 0:
        raise ValueError("area must be positive")
    return power_erg_s(ndot, ec_kev, delta) / area_cm2


def ndot_from_flux(flux: float, ec_kev: float, delta: float, area_cm2: float) -> float:
    """Inverse of energy_flux: electron rate [s^-1] that carries `flux` through `area_cm2`."""
    _check_delta(delta)
    return flux * area_cm2 * (delta - 2.0) / ((delta - 1.0) * ec_kev * KEV_TO_ERG)


def _check_delta(delta: float) -> None:
    if not delta > MIN_DELTA:
        raise ValueError(
            "delta must be > 2 for a power law without upper cut-off (got %r)" % delta
        )


@dataclass(frozen=True)
class Pulse:
    """One boxcar electron pulse injected into one flux tube."""

    t_start: float  # [s] nominal onset
    duration: float  # [s]
    ndot: float  # [electrons s^-1] above Ec
    ec_kev: float  # [keV]
    delta: float  # electron spectral index
    area_cm2: float  # [cm^2] flux-tube cross-section at the injection site
    label: str = ""

    def __post_init__(self) -> None:
        if self.duration <= 0 or self.ndot < 0 or self.ec_kev <= 0 or self.area_cm2 <= 0:
            raise ValueError("duration, ec_kev and area_cm2 must be > 0 and ndot >= 0")
        _check_delta(self.delta)

    @classmethod
    def from_flux(cls, t_start, duration, flux, ec_kev, delta, area_cm2, label=""):
        return cls(t_start, duration, ndot_from_flux(flux, ec_kev, delta, area_cm2),
                   ec_kev, delta, area_cm2, label)

    @property
    def t_end(self) -> float:
        return self.t_start + self.duration

    @property
    def power_erg_s(self) -> float:
        return power_erg_s(self.ndot, self.ec_kev, self.delta)

    @property
    def flux(self) -> float:
        return self.power_erg_s / self.area_cm2

    @property
    def energy_erg(self) -> float:
        return self.power_erg_s * self.duration

    def shifted(self, dt: float) -> "Pulse":
        return Pulse(self.t_start + dt, self.duration, self.ndot, self.ec_kev,
                     self.delta, self.area_cm2, self.label)


Row = Tuple[float, float, float, float]  # (t [s], F [erg cm^-2 s^-1], Ec [keV], delta)


@dataclass(frozen=True)
class BeamTable:
    """Rows of beam_heating_model.cfg with HYDRAD's interpolation semantics."""

    rows: Tuple[Row, ...]

    def __post_init__(self) -> None:
        if len(self.rows) < 2:
            # HYDRAD treats a single row as "constant beam of duration t"; we never emit that.
            raise ValueError("a table needs at least two rows")
        times = [r[0] for r in self.rows]
        if any(b <= a for a, b in zip(times, times[1:])):
            raise ValueError("row times must be strictly increasing")
        if times[0] < 0:
            raise ValueError("HYDRAD time starts at 0; first row is at t < 0")
        for t, f, ec, d in self.rows:
            if f < 0 or ec <= 0:
                raise ValueError("F must be >= 0 and Ec > 0 in every row")
            _check_delta(d)

    def at(self, t: float) -> Tuple[float, float, float]:
        """(F, Ec, delta) as HYDRAD's CHeat::CalculateBeamParameters would give; F = 0 outside."""
        r = self.rows
        if t < r[0][0] or t > r[-1][0]:
            return 0.0, r[0][2], r[0][3]
        i = 0
        while i < len(r) - 2 and not t < r[i + 1][0]:
            i += 1
        (t0, f0, e0, d0), (t1, f1, e1, d1) = r[i], r[i + 1]
        w = (t - t0) / (t1 - t0)
        return f0 + w * (f1 - f0), e0 + w * (e1 - e0), d0 + w * (d1 - d0)

    def flux_at(self, t: float) -> float:
        return self.at(t)[0]

    @property
    def t_first(self) -> float:
        return self.rows[0][0]

    @property
    def t_last(self) -> float:
        return self.rows[-1][0]

    def energy_per_area(self) -> float:
        """Integral of F dt [erg cm^-2]; exact because F is piecewise linear."""
        return sum(0.5 * (f0 + f1) * (t1 - t0)
                   for (t0, f0, _, _), (t1, f1, _, _) in zip(self.rows, self.rows[1:]))

    def to_cfg(self) -> str:
        """Text accepted by HYDRAD's GetBeamHeatingData (count, 7 header tokens, rows)."""
        lines = [str(len(self.rows)),
                 "Time\tEnergy_flux\tCut-off\tSpectral_index",
                 "[s]\t[erg/cm^2/s]\t[keV]"]
        lines += ["%.10g\t%.10e\t%.10g\t%.10g" % row for row in self.rows]
        return "\n".join(lines) + "\n"

    @classmethod
    def from_cfg(cls, text: str) -> "BeamTable":
        tok = text.split()
        n = int(tok[0])
        if n < 2:
            raise ValueError("single-row (constant beam) tables are not supported")
        body = tok[1 + 7:]  # skip count and the 7 header tokens HYDRAD skips
        vals = [float(x) for x in body[:4 * n]]
        if len(vals) != 4 * n:
            raise ValueError("table is shorter than its declared row count")
        return cls(tuple(tuple(vals[4 * i:4 * i + 4]) for i in range(n)))  # type: ignore[arg-type]


def build_table(pulses: Sequence[Pulse], ramp: float = 0.2) -> BeamTable:
    """Encode boxcar pulses of ONE flux tube as a HYDRAD table.

    Each boundary is a linear ramp of width `ramp` centred on the nominal time,
    so the encoded energy equals sum(F_i * duration_i) exactly.  Requirements:
    pulses sorted and separated by more than `ramp`, each longer than `ramp`,
    and a common cross-section A (the table stores F, which only has meaning
    for one tube).  The zero-F rows carry the Ec and delta of the adjacent
    pulse so the interpolated delta never leaves (2, inf).
    """
    if ramp <= 0:
        raise ValueError("ramp must be > 0 (HYDRAD divides by the row spacing)")
    ps = sorted(pulses, key=lambda p: p.t_start)
    if not ps:
        raise ValueError("no pulses")
    if len({p.area_cm2 for p in ps}) != 1:
        raise ValueError("pulses in one table must share one flux-tube area; "
                         "use one table per tube/filament")
    half = ramp / 2.0
    rows: List[Row] = []
    for i, p in enumerate(ps):
        if p.duration <= ramp:
            raise ValueError("pulse %d is not longer than the ramp" % i)
        if i > 0 and not (p.t_start - ps[i - 1].t_end > ramp):
            raise ValueError("gap before pulse %d must exceed the ramp (%.3g s)" % (i, ramp))
        if p.t_start - half < 0:
            raise ValueError("pulse %d starts before t = ramp/2; HYDRAD time starts at 0" % i)
        f = p.flux
        rows += [(p.t_start - half, 0.0, p.ec_kev, p.delta),
                 (p.t_start + half, f, p.ec_kev, p.delta),
                 (p.t_end - half, f, p.ec_kev, p.delta),
                 (p.t_end + half, 0.0, p.ec_kev, p.delta)]
    return BeamTable(tuple(rows))


def naive_table(pulses: Sequence[Pulse]) -> BeamTable:
    """The tempting but WRONG encoding: two rows per pulse, no zero rows.

    HYDRAD interpolates linearly between the end of one pulse and the start of
    the next, so it injects energy during the gap.  Kept only to quantify the
    error in the report and in the tests.
    """
    ps = sorted(pulses, key=lambda p: p.t_start)
    rows: List[Row] = []
    for p in ps:
        rows += [(p.t_start, p.flux, p.ec_kev, p.delta), (p.t_end, p.flux, p.ec_kev, p.delta)]
    return BeamTable(tuple(rows))
