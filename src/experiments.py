"""Beam inputs of the experiments: the paired branches of the core and the E1-E5 matrix.

The core experiment (docs/00, Section 3) uses four paired branches, built by
build_paired_branches: A0 (no beam), B0 (test pulse on the relaxed atmosphere),
and, for every waiting time tau, A1 (pulse 1 only) and B1 (pulse 1, then the
same test pulse).  The older E1-E5 matrix is kept for the extensions
(independent threads E3a/E3b, continuous heating E4).

Every experiment is described by one or more *components*.  A component is one
flux tube (filament) simulated by one solver run with its own beam table.  The
physical quantity that is compared across experiments is the total power

    P_total(t) = sum_i A_i * F_i(t - offset_i)        [erg s^-1]

and the total injected energy, which must be equal wherever the project
document demands a "comparable energy" comparison.  The emitting area is NOT
constrained by hard X-rays alone, so the independent-filament case is generated
for two area assignments.

All parameters of the default base case are SYNTHETIC illustrations, not STIX
fits.
"""
from __future__ import annotations

import json
import os
from dataclasses import dataclass, field
from typing import Dict, List, Sequence, Tuple

from beam_tables import (BeamTable, Pulse, build_table, energy_flux, ndot_from_flux)
from radyn_ftab import to_radyn_ftab


@dataclass(frozen=True)
class BaseCase:
    """Identical successive pulses in one flux tube (synthetic)."""

    ndot: float = 3.0e34       # [e- s^-1] above Ec
    ec_kev: float = 20.0
    delta: float = 5.0
    duration: float = 10.0     # [s] per pulse
    gap: float = 20.0          # [s] between end of pulse i and start of pulse i+1
    n_pulses: int = 2
    area_cm2: float = 1.0e17   # reference flux-tube cross-section
    t0: float = 1.0            # [s] onset of the first pulse in solver time
    ramp: float = 0.2          # [s] linear ramp at every boundary
    tail: float = 60.0         # [s] relaxation simulated after the last pulse ends

    def pulses(self) -> List[Pulse]:
        step = self.duration + self.gap
        return [Pulse(self.t0 + i * step, self.duration, self.ndot, self.ec_kev,
                      self.delta, self.area_cm2, "pulse%d" % (i + 1))
                for i in range(self.n_pulses)]

    @property
    def t_last_end(self) -> float:
        return self.pulses()[-1].t_end

    @property
    def t_end_global(self) -> float:
        return self.t_last_end + self.tail


@dataclass(frozen=True)
class Component:
    label: str
    table: BeamTable
    area_cm2: float
    offset: float          # global time = solver time + offset
    t_end_sim: float       # solver time at which this run can stop
    pulses: Tuple[Pulse, ...]


@dataclass
class Experiment:
    name: str
    title: str
    purpose: str
    components: List[Component]
    t_end_global: float
    marks: Dict[str, float] = field(default_factory=dict)  # global-time landmarks

    def power(self, t_global: float) -> float:
        """P_total at global time [erg s^-1]."""
        return sum(c.area_cm2 * c.table.flux_at(t_global - c.offset) for c in self.components)

    def energy_erg(self) -> float:
        return sum(c.area_cm2 * c.table.energy_per_area() for c in self.components)

    def total_area_cm2(self) -> float:
        return sum(c.area_cm2 for c in self.components)

    def manifest(self) -> dict:
        return {
            "name": self.name, "title": self.title, "purpose": self.purpose,
            "t_end_global_s": self.t_end_global,
            "total_energy_erg": self.energy_erg(),
            "total_emitting_area_cm2": self.total_area_cm2(),
            "marks_global_s": self.marks,
            "combination": ("area-weighted sum of component emissions, shifted by offset"
                            if len(self.components) > 1 else "single run"),
            "components": [{
                "label": c.label, "area_cm2": c.area_cm2, "offset_s": c.offset,
                "t_end_sim_s": c.t_end_sim, "energy_erg": c.area_cm2 * c.table.energy_per_area(),
                "peak_flux_erg_cm2_s": max(r[1] for r in c.table.rows),
                "pulses": [{"t_start_s": p.t_start, "duration_s": p.duration,
                            "ndot_s": p.ndot, "ec_kev": p.ec_kev, "delta": p.delta,
                            "power_erg_s": p.power_erg_s, "flux_erg_cm2_s": p.flux}
                           for p in c.pulses],
            } for c in self.components],
        }


def _single(base: BaseCase, p: Pulse, label: str, t_to: float, tail_until_global: float) -> Component:
    """Place pulse p at solver time t_to; offset records its true global time."""
    shifted = p.shifted(t_to - p.t_start)
    table = build_table([shifted], base.ramp)
    offset = p.t_start - t_to
    return Component(label, table, p.area_cm2, offset, tail_until_global - offset, (shifted,))


def _energy_weighted(pulses: List[Pulse]) -> Tuple[float, float]:
    """Energy-weighted mean Ec and delta.  A choice, not a measurement: document it."""
    e = [p.energy_erg for p in pulses]
    w = sum(e)
    return (sum(p.ec_kev * x for p, x in zip(pulses, e)) / w,
            sum(p.delta * x for p, x in zip(pulses, e)) / w)


def build_experiments(base: BaseCase = BaseCase()) -> List[Experiment]:
    ps = base.pulses()
    t_end = base.t_end_global
    first, last = ps[0], ps[-1]
    exps: List[Experiment] = []

    # E1: the response to the LAST pulse in an atmosphere that has not been heated before.
    c = _single(base, last, "pulse%d_alone" % base.n_pulses, base.t0,
                last.t_end + base.tail)
    exps.append(Experiment(
        "E1_single_relaxed", "One pulse in a relaxed atmosphere",
        "Reference response to pulse %d with no previous history. It is compared with E2 "
        "by aligning the pulse onsets." % base.n_pulses,
        [c], t_end, {"pulse_onset": last.t_start}))

    # E2: all pulses in the SAME tube, one uninterrupted run.
    table = build_table(ps, base.ramp)
    exps.append(Experiment(
        "E2_same_strand", "Mismo tubo, pulsos sucesivos",
        "Reheating: the atmosphere evolves without a restart between pulses "
        "(temperature, density, velocity and populations are conserved).",
        [Component("tube", table, base.area_cm2, 0.0, t_end, tuple(ps))], t_end,
        {"pulse%d_onset" % (i + 1): p.t_start for i, p in enumerate(ps)}))

    # E3a/E3b: each pulse in its own tube that was relaxed beforehand.
    for tag, frac, text in (
            ("E3a_independent_same_flux", 1.0,
             "each filament has the reference area: same F per pulse, total emitting area N·A"),
            ("E3b_independent_equal_area", 1.0 / base.n_pulses,
             "the reference area is shared among filaments: F×N per pulse, total area A")):
        comps = []
        for i, p in enumerate(ps):
            area = base.area_cm2 * frac
            q = Pulse.from_flux(p.t_start, p.duration, energy_flux(p.ndot, p.ec_kev, p.delta,
                                base.area_cm2) / frac, p.ec_kev, p.delta, area, p.label)
            comps.append(_single(base, q, "filament%d" % (i + 1), base.t0, t_end))
        exps.append(Experiment(
            tag, "Independent filaments (%s)" % ("area %.2g·A" % frac),
            "Pulses in different tubes, with no memory between them; %s. P_total(t) = Σ A_i F_i "
            "matches E2." % text, comps, t_end,
            {"pulse%d_onset" % (i + 1): p.t_start for i, p in enumerate(ps)}))

    # E4: continuous heating with the same total energy over the same window.
    ec_w, d_w = _energy_weighted(ps)
    window = base.t_last_end - base.t0
    e_total = sum(p.energy_erg for p in ps)
    f_c = e_total / base.area_cm2 / window
    cont = Pulse(base.t0, window, ndot_from_flux(f_c, ec_w, d_w, base.area_cm2), ec_w, d_w,
                 base.area_cm2, "continuous")
    exps.append(Experiment(
        "E4_continuous", "Continuous heating, same energy",
        "Control of the temporal distribution: the same total energy spread uniformly "
        "over the window (energy-weighted Ec and δ; a documented choice).",
        [Component("tube", build_table([cont], base.ramp), base.area_cm2, 0.0, t_end, (cont,))],
        t_end, {"window_start": base.t0, "window_end": base.t_last_end}))

    # E5: first pulse, then relaxation for the whole timeline.
    exps.append(Experiment(
        "E5_relaxation", "First pulse and relaxation",
        "Control for the residue of pulse 1 with no later pulse: subtracting it from E2 separates the "
        "residual emission from the response to the new beam.",
        [Component("tube", build_table([first], base.ramp), base.area_cm2, 0.0, t_end, (first,))],
        t_end, {"pulse1_onset": first.t_start, "pulse2_onset_reference": ps[-1].t_start}))
    return exps


#: Core pilot (docs/00, Section 3.2): the stable HYDRAD case with the largest column growth
#: (F = 1.3e10 erg cm^-2 s^-1, 30 s pulse; run it in a 26 Mm loop, docs/06 variant V5).
PILOT = BaseCase(duration=30.0)
PILOT_TAUS = (10.0, 30.0, 60.0, 120.0)


def _no_beam_table(t_end: float, ec_kev: float, delta: float) -> BeamTable:
    """Zero-flux table over the whole run (A0).  RADYN still applies its 0.1 floor."""
    return BeamTable(((0.0, 0.0, ec_kev, delta), (t_end, 0.0, ec_kev, delta)))


def build_paired_branches(base: BaseCase = PILOT,
                          taus: Sequence[float] = PILOT_TAUS) -> List[Experiment]:
    """A0, B0 and, for every waiting time tau, A1 and B1 (docs/00, Section 3.1).

    Pulse 1 and the test pulse b are identical copies of the base pulse.  Every
    branch is one run in its own solver time from the same initial atmosphere;
    marks["test_onset"] is the solver time at which b starts (or would start),
    so responses are compared at equal t' = t - test_onset.  tau runs from the
    end of pulse 1 to the onset of b.  A0 runs as long as the longest branch: it
    is the baseline of B0 and the relaxed reference of every A1 at its t_k.
    """
    if not taus:
        raise ValueError("at least one waiting time is needed")
    if len(set(taus)) != len(taus):
        raise ValueError("waiting times must be distinct")
    p = base.pulses()[0]
    after = p.duration + base.tail                # simulated time after every test onset
    t_k = {tau: p.t_end + tau for tau in taus}    # build_table rejects tau <= ramp
    t_end_max = max(t_k.values()) + after
    one = build_table([p], base.ramp)

    marks0 = {"test_onset": p.t_start}
    marks0.update({"t_k(tau=%gs)" % tau: t for tau, t in t_k.items()})
    exps = [
        Experiment("A0_no_beam", "Initial atmosphere, no beam",
                   "Baseline of B0 at equal solver time, and relaxed reference for A1 at t_k.",
                   [Component("tube", _no_beam_table(t_end_max, p.ec_kev, p.delta),
                              base.area_cm2, 0.0, t_end_max, ())], t_end_max, marks0),
        Experiment("B0_test_relaxed", "Test pulse on the relaxed atmosphere",
                   "Response assumed by the independent-pulse approximation: Delta D_0 = B0 - A0.",
                   [Component("tube", one, base.area_cm2, 0.0, p.t_start + after, (p,))],
                   p.t_start + after, {"test_onset": p.t_start}),
    ]
    for tau in taus:
        b = p.shifted(t_k[tau] - p.t_start)
        end = t_k[tau] + after
        marks = {"pulse1_onset": p.t_start, "test_onset": t_k[tau]}
        exps.append(Experiment(
            "A1_tau%gs" % tau, "Pulse 1 only (tau = %g s)" % tau,
            "State left by pulse 1 without the test pulse; identical to B1 before t_k.",
            [Component("tube", one, base.area_cm2, 0.0, end, (p,))], end, dict(marks)))
        exps.append(Experiment(
            "B1_tau%gs" % tau, "Pulse 1, then the test pulse after %g s" % tau,
            "Response with history: Delta D_1 = B1 - A1; M = Delta D_1 - Delta D_0.",
            [Component("tube", build_table([p, b], base.ramp), base.area_cm2, 0.0, end, (p, b))],
            end, dict(marks)))
    return exps


def _write(exps: List[Experiment], outdir: str, header: dict) -> None:
    for e in exps:
        for c in e.components:
            d = os.path.join(outdir, e.name, c.label)
            os.makedirs(d, exist_ok=True)
            with open(os.path.join(d, "beam_heating_model.cfg"), "w") as fh:   # HYDRAD
                fh.write(c.table.to_cfg())
            with open(os.path.join(d, "ftab.dat"), "w") as fh:                  # RADYN ibeam = 8
                fh.write(to_radyn_ftab(c.table, c.t_end_sim, note=e.name + "/" + c.label))
    with open(os.path.join(outdir, "manifest.json"), "w") as fh:
        json.dump(dict(header, experiments=[e.manifest() for e in exps]), fh, indent=2)


def write_experiments(base: BaseCase, outdir: str) -> List[Experiment]:
    exps = build_experiments(base)
    _write(exps, outdir, {"base_case": base.__dict__, "synthetic": True})
    return exps


def write_paired_branches(base: BaseCase, taus: Sequence[float], outdir: str) -> List[Experiment]:
    """Beam tables of the core branches.  With RADYN, branch B1 from A1 by restart: the
    tensioned spline of ftab.dat can couple rows on both sides of t_k."""
    exps = build_paired_branches(base, taus)
    _write(exps, outdir, {"base_case": base.__dict__, "synthetic": True,
                          "waiting_times_s": list(taus),
                          "contrast": "M = (B1 - A1) - (B0 - A0) at equal t' = t - test_onset"})
    return exps


if __name__ == "__main__":
    here = os.path.dirname(os.path.abspath(__file__))
    for name, exps in (
            ("paired_branches", write_paired_branches(PILOT, PILOT_TAUS,
                                                      os.path.join(here, "..", "results", "paired_branches"))),
            ("experiments", write_experiments(BaseCase(), os.path.join(here, "..", "results", "experiments")))):
        print("results/%s:" % name)
        for e in exps:
            print("  %-28s E = %.4e erg  A_tot = %.2e cm2  components = %d"
                  % (e.name, e.energy_erg(), e.total_area_cm2(), len(e.components)))
