"""The five-experiment matrix of the STIX -> RHD chromospheric-memory project.

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
from typing import Dict, List, Tuple

from beam_tables import (BeamTable, Pulse, build_table, energy_flux, ndot_from_flux)


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
        "E1_single_relaxed", "Un pulso en atmósfera relajada",
        "Respuesta de referencia al pulso %d sin historia previa. Se compara con E2 "
        "alineando los inicios de pulso." % base.n_pulses,
        [c], t_end, {"pulse_onset": last.t_start}))

    # E2: all pulses in the SAME tube, one uninterrupted run.
    table = build_table(ps, base.ramp)
    exps.append(Experiment(
        "E2_same_strand", "Mismo tubo, pulsos sucesivos",
        "Recalentamiento: la atmósfera evoluciona sin reinicio entre pulsos "
        "(temperatura, densidad, velocidad y poblaciones se conservan).",
        [Component("tube", table, base.area_cm2, 0.0, t_end, tuple(ps))], t_end,
        {"pulse%d_onset" % (i + 1): p.t_start for i, p in enumerate(ps)}))

    # E3a/E3b: each pulse in its own tube that was relaxed beforehand.
    for tag, frac, text in (
            ("E3a_independent_same_flux", 1.0,
             "cada filamento tiene el área de referencia: mismo F por pulso, área emisora total N·A"),
            ("E3b_independent_equal_area", 1.0 / base.n_pulses,
             "el área de referencia se reparte entre filamentos: F×N por pulso, área total A")):
        comps = []
        for i, p in enumerate(ps):
            area = base.area_cm2 * frac
            q = Pulse.from_flux(p.t_start, p.duration, energy_flux(p.ndot, p.ec_kev, p.delta,
                                base.area_cm2) / frac, p.ec_kev, p.delta, area, p.label)
            comps.append(_single(base, q, "filament%d" % (i + 1), base.t0, t_end))
        exps.append(Experiment(
            tag, "Filamentos independientes (%s)" % ("área %.2g·A" % frac),
            "Pulsos en tubos distintos, sin memoria entre ellos; %s. P_total(t) = Σ A_i F_i "
            "coincide con E2." % text, comps, t_end,
            {"pulse%d_onset" % (i + 1): p.t_start for i, p in enumerate(ps)}))

    # E4: continuous heating with the same total energy over the same window.
    ec_w, d_w = _energy_weighted(ps)
    window = base.t_last_end - base.t0
    e_total = sum(p.energy_erg for p in ps)
    f_c = e_total / base.area_cm2 / window
    cont = Pulse(base.t0, window, ndot_from_flux(f_c, ec_w, d_w, base.area_cm2), ec_w, d_w,
                 base.area_cm2, "continuous")
    exps.append(Experiment(
        "E4_continuous", "Calentamiento continuo, misma energía",
        "Control de la distribución temporal: la misma energía total repartida de forma "
        "uniforme en la ventana (Ec y δ ponderados por energía; elección documentada).",
        [Component("tube", build_table([cont], base.ramp), base.area_cm2, 0.0, t_end, (cont,))],
        t_end, {"window_start": base.t0, "window_end": base.t_last_end}))

    # E5: first pulse, then relaxation for the whole timeline.
    exps.append(Experiment(
        "E5_relaxation", "Primer pulso y enfriamiento",
        "Control del residuo del pulso 1 sin pulso posterior: restar de E2 distingue la "
        "emisión residual de la respuesta al nuevo haz.",
        [Component("tube", build_table([first], base.ramp), base.area_cm2, 0.0, t_end, (first,))],
        t_end, {"pulse1_onset": first.t_start, "pulse2_onset_reference": ps[-1].t_start}))
    return exps


def write_experiments(base: BaseCase, outdir: str) -> List[Experiment]:
    exps = build_experiments(base)
    for e in exps:
        for c in e.components:
            d = os.path.join(outdir, e.name, c.label)
            os.makedirs(d, exist_ok=True)
            with open(os.path.join(d, "beam_heating_model.cfg"), "w") as fh:
                fh.write(c.table.to_cfg())
    with open(os.path.join(outdir, "manifest.json"), "w") as fh:
        json.dump({"base_case": base.__dict__, "synthetic": True,
                   "experiments": [e.manifest() for e in exps]}, fh, indent=2)
    return exps


if __name__ == "__main__":
    here = os.path.dirname(os.path.abspath(__file__))
    out = os.path.join(here, "..", "results", "experiments")
    for e in write_experiments(BaseCase(), out):
        print("%-28s E = %.4e erg  A_tot = %.2e cm2  components = %d"
              % (e.name, e.energy_erg(), e.total_area_cm2(), len(e.components)))
