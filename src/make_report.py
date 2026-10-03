"""Builds docs/02_pulse_experiments_report.html (single file, figures embedded).

Every number in the tables is read from the experiment objects, never typed.
"""
from __future__ import annotations

import base64
import math
import os

from beam_tables import KEV_TO_ERG, build_table, naive_table
from experiments import BaseCase, build_experiments

HERE = os.path.dirname(os.path.abspath(__file__))
FIG = os.path.join(HERE, "..", "docs", "figures")
OUT = os.path.join(HERE, "..", "docs", "02_pulse_experiments_report.html")


def img(name: str, alt: str) -> str:
    with open(os.path.join(FIG, name), "rb") as fh:
        b64 = base64.b64encode(fh.read()).decode()
    return '<figure><img src="data:image/png;base64,%s" alt="%s"></figure>' % (b64, alt)


def sci(x: float, d: int = 3) -> str:
    m, e = ("%.*e" % (d - 1, x)).split("e")
    return "%s×10<sup>%d</sup>" % (m, int(e))


def main() -> None:
    base = BaseCase()
    exps = build_experiments(base)
    ps = base.pulses()
    p = ps[0]
    good, bad = build_table(ps, base.ramp), naive_table(ps)
    n_arcsec2 = base.area_cm2 / (7.25e7) ** 2
    avg_e = p.ec_kev * (p.delta - 1) / (p.delta - 2)

    rows = ""
    descr = {
        "E1_single_relaxed": ("1 tube, 1 pulse", "Reference response to a pulse on an atmosphere with no history."),
        "E2_same_strand": ("1 tube, %d pulses" % base.n_pulses, "Reheating: solver state conserved between pulses."),
        "E3a_independent_same_flux": ("%d tubes, 1 pulse each" % base.n_pulses, "Independent filaments with the same F per pulse (larger total emitting area)."),
        "E3b_independent_equal_area": ("%d tubes, 1 pulse each" % base.n_pulses, "Independent filaments with the area shared: F×%d per pulse, total area equal to E2." % base.n_pulses),
        "E4_continuous": ("1 tube, 1 long pulse", "Same energy spread uniformly: control of the temporal distribution."),
        "E5_relaxation": ("1 tube, 1 pulse", "First pulse and relaxation: separates the residue from the response to the new pulse."),
    }
    for e in exps:
        m = e.manifest()
        pk = max(c["peak_flux_erg_cm2_s"] for c in m["components"])
        rows += ("<tr><td><b>%s</b><br><span class='sm'>%s</span></td><td>%s</td><td>%s</td><td>%s</td><td>%s</td><td>%s</td></tr>"
                 % (e.name, e.title, descr[e.name][0], sci(m["total_energy_erg"]), sci(m["total_emitting_area_cm2"]),
                    sci(pk), descr[e.name][1]))

    # neutral / ionized stopping-column ratio at the reference Ec (same expression as heat.cpp)
    e_avg = p.ec_kev * KEV_TO_ERG * (p.delta - 1) / (p.delta - 2)
    lam1 = 66.0 + 1.5 * math.log(e_avg) - 0.5 * math.log(1e11)
    lam2 = 25.1 + math.log(e_avg)
    nc = lambda g: (p.ec_kev * KEV_TO_ERG) ** 2 / (g * 1.0006128424679109e-36)
    nc_n, nc_i = nc(lam2), nc(lam1)

    html = """<!doctype html>
<html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<title>Report: successive electron pulses, input infrastructure</title>
<style>
:root{--bg:#fff;--fg:#1d2430;--mut:#5b6575;--ln:#d9dee6;--acc:#1f4e79;--warn:#fff4e0;--wb:#e0a030;--ok:#e8f5ec;--okb:#1b7a3d;--tb:#f4f6f9}
@media (prefers-color-scheme:dark){:root{--bg:#14171c;--fg:#e4e8ee;--mut:#9aa5b5;--ln:#2e3540;--acc:#7fb2e5;--warn:#2d2616;--wb:#b88a2a;--ok:#16281d;--okb:#4cae6e;--tb:#1c2027}
figure img{background:#fff;border-radius:6px}}
body{background:var(--bg);color:var(--fg);font:16px/1.55 -apple-system,Segoe UI,Helvetica,Arial,sans-serif;margin:0}
main{max-width:920px;margin:0 auto;padding:28px 18px 60px}
h1{font-size:1.65rem;margin:.2em 0 .1em}h2{font-size:1.25rem;margin:2em 0 .5em;border-bottom:1px solid var(--ln);padding-bottom:.25em;color:var(--acc)}
h3{font-size:1.02rem;margin:1.4em 0 .3em}
p,li{max-width:75ch}.sub{color:var(--mut);margin:0 0 1.2em}
table{border-collapse:collapse;width:100%%;font-size:.9rem;margin:.8em 0}
th,td{border:1px solid var(--ln);padding:6px 8px;text-align:left;vertical-align:top}th{background:var(--tb)}
.sm{color:var(--mut);font-size:.82rem}
code,.mono{font-family:ui-monospace,Menlo,Consolas,monospace;font-size:.88em}
.eq{background:var(--tb);border-left:3px solid var(--acc);padding:.5em .9em;margin:.8em 0;overflow-x:auto}
.box{padding:.7em 1em;border-radius:6px;margin:1em 0;border-left:4px solid}
.warn{background:var(--warn);border-color:var(--wb)}.ok{background:var(--ok);border-color:var(--okb)}
figure{margin:1em 0}figure img{max-width:100%%;height:auto}
figcaption{color:var(--mut);font-size:.86rem}
.tablewrap{overflow-x:auto}
</style></head><body><main>

<h1>Successive electron pulses: input infrastructure</h1>
<p class="sub">Author: Carlos Alberto Martínez Sibaja · report on the experiment infrastructure (points 1 and 2 of the plan) · all parameters are <b>synthetic</b></p>

<div class="box warn"><b>Scope.</b> This report describes what will be simulated and prepares the inputs of the five experiments
with comparable energy. <b>It contains no observational results and no physical conclusions.</b> The beam parameters are
illustrative values, not STIX fits; no event has been selected. It covers only the input side: the photon computation, the STIX response and the re-inference described below are not implemented yet.</div>

<h2>1. What the project asks</h2>
<p><b>How much does the atmospheric memory of the previous pulse bias the electron parameters (Ṅ, Ec, δ) inferred with STIX for a second or third pulse, and is it visible in STIX images as a change in the loop-top / footpoint ratio?</b>
The method injects known pulses into an RHD atmosphere that keeps its history, computes the synthetic hard X-ray photons, fits them with the standard STIX model and compares with the injected truth.
The hydrodynamic memory (deposition depth, temperature, density, velocity, ionization, energy partition) is the mechanism. As a test of the geometry, reheating of the same tube is contrasted with <b>independent filaments</b> compatible with the same hard X-ray signal.
The full design (hypotheses, objectives, methods and deliverables) is in <code>docs/00_objectives_and_methodology.md</code>.</p>
%(fig0)s
<p>Working hypothesis (still to be confirmed with the supervisor): the pulses hit the same flux tube. It is a hypothesis, not evidence.
A well-established limit of detectability, i.e. cases where the scenarios cannot be distinguished, would also be a result.</p>

<h2>2. Physics of the forcing</h2>
<p>Each pulse is described as an electron beam with a power law in number above a cut-off energy Ec, which stops collisionally
(thick target). For an index δ &gt; 2 and no upper cut-off:</p>
<div class="eq mono">P = Ṅ · Ec · (δ − 1)/(δ − 2)  [erg s⁻¹] &nbsp;&nbsp;&nbsp; F = P / A  [erg cm⁻² s⁻¹]</div>
<table><tr><th>Quantity</th><th>Symbol and unit</th><th>Note</th></tr>
<tr><td>Electron rate above Ec</td><td>Ṅ [s⁻¹]</td><td>What the photon spectrum fit gives, together with Ec and δ</td></tr>
<tr><td>Beam power</td><td>P [erg s⁻¹]</td><td>What is conserved when comparing scenarios</td></tr>
<tr><td>Energy flux</td><td>F [erg cm⁻² s⁻¹]</td><td>HYDRAD input; depends on the tube area A, which STIX does not fix</td></tr>
<tr><td>Volumetric deposition</td><td>Q(s,t) [erg cm⁻³ s⁻¹]</td><td>Output computed by the solver; it is what heats</td></tr></table>
<p>Conditions respected: Ec is converted from keV to erg (1 keV = 1.602×10⁻⁹ erg); δ ≤ 2 is rejected because the mean energy diverges; the photon Ec and δ
are not interchanged with the electron ones. With the base values, the mean energy per electron is %(avg_e).1f keV.</p>

<h3>Where the beam stops</h3>
<p>The stopping column N<sub>c</sub> grows as Ec² and depends on the state of the gas. With the expression of <code>Heating_Model/source/heat.cpp</code>, for
Ec = %(ec).0f keV and δ = %(delta).0f, N<sub>c</sub> ≈ %(ncn)s cm⁻² in neutral gas and ≈ %(nci)s cm⁻² in ionized gas (×%(ratio).1f). A pulse that ionizes or compresses
the plasma therefore changes <i>where</i> the next one deposits its energy: this is one of the physical channels of the "memory" to be measured, and one reason why the target seen by a second pulse differs from the cold target assumed in the standard fit.</p>
%(fig1)s

<div class="box warn"><b>Limits of HYDRAD's beam model.</b> It is the analytic collisional heating of Hawley &amp; Fisher with fixed normal incidence (μ₀ = 1):
no pitch-angle scattering, no return current and no Fokker–Planck transport. In addition, the radiation of the shipped configuration is optically thin, with no NLTE or Hα.
It serves to test the pulse mechanics, the evaporation into the corona and the column test; it is not meant to decide the chromospheric memory, for which RADYN+FP is preferred.</div>

<h2>3. How the pulses are encoded for HYDRAD</h2>
<p>HYDRAD reads rows (t, F, Ec, δ), <b>interpolates the three quantities linearly</b> between rows and switches the beam off before the first and after the last one.
A two-rows-per-pulse encoding looks natural, but it fills the gap between pulses. With the base parameters it would inject
%(ebad)s erg cm⁻² instead of the correct %(egood)s (×%(rat).1f).</p>
%(fig2)s
<p>The generator (<code>src/beam_tables.py</code>) uses rows with F = 0 and a ramp of %(ramp).1f s <b>centred</b> on each boundary, so that ∫F dt = F·duration exactly.
It also requires: pulses longer than the ramp, gaps larger than the ramp, start ≥ ramp/2 (HYDRAD time starts at 0), a single area per table
(F only makes sense for one tube) and δ &gt; 2 in every row, including those with F = 0, so that the interpolation never crosses δ = 2.</p>

<h2>4. The experiment matrix</h2>
<p>The five experiments of the plan, with the fragmentation into filaments generated with <b>two area assignments</b> because hard X-rays fix P(t) but not A.
Base parameters (synthetic): Ṅ = %(ndot)s s⁻¹, Ec = %(ec).0f keV, δ = %(delta).0f, %(npul)d pulses of %(dur).0f s separated by %(gap).0f s, A<sub>ref</sub> = %(area)s cm²
(≈ %(arc).0f arcsec² at 1 AU), giving P = %(pw)s erg s⁻¹ and F = %(fl)s erg cm⁻² s⁻¹ per pulse.</p>
<div class="tablewrap"><table>
<tr><th>Experiment</th><th>Set-up</th><th>Total energy [erg]</th><th>Total emitting area [cm²]</th><th>Peak F [erg cm⁻² s⁻¹]</th><th>Role</th></tr>
%(rows)s</table></div>
%(fig3)s
%(fig4)s
<p><b>What is conserved and what is not.</b> E2, E3a, E3b and E4 inject the same total energy, and E2, E3a and E3b the same P<sub>total</sub>(t) = Σ A<sub>i</sub>F<sub>i</sub>(t) (verified
numerically). The emitting area and the flux per pulse do not match; reporting it is mandatory, because comparing cases with different energy or area without declaring it invalidates the comparison.</p>
%(fig5)s

<h3>How the memory will be read when outputs exist</h3>
<ul>
<li><b>Response with history (paired counterfactual):</b> R<sub>hist</sub>(τ) = X<sub>with pulse 2</sub>(t₂ + τ) − X<sub>without pulse 2</sub>(t₂ + τ), with the same history up to t₂. For pulse 2 this is E2 − E5, which discounts the residue of pulse 1.</li>
<li><b>Response in a relaxed atmosphere:</b> R<sub>rel</sub>(τ) = X<sub>E1</sub>(t₀ + τ) − X₀. The <b>memory</b> is M(τ) = R<sub>hist</sub>(τ) − R<sub>rel</sub>(τ), with X = T, n, v, ionization, Q(s,t) and deposition depth, aligning the pulse onsets.</li>
<li><b>Pulse 3:</b> requires the counterfactual "pulses 1 and 2 without pulse 3", not yet generated.</li>
<li><b>Independent filaments (test of the geometry):</b> the emission is the area-weighted sum, I(t) = Σ A<sub>i</sub> I<sub>i</sub>(t − offset<sub>i</sub>), valid only under the documented geometric and radiative assumptions.</li>
<li><b>Continuous control (E4):</b> isolates the effect of the temporal distribution of energy; its Ec and δ are energy-weighted means, a choice and not a measurement.</li>
</ul>
<p>Responses of isolated pulses are not added up to represent reheating: the physics is non-linear and that sum only describes independent filaments.</p>

<h2>5. Checks performed</h2>
<div class="box ok"><b>50 automatic tests pass</b> (<code>pytest</code>): power formula against hand calculation; Ṅ↔F round trip; rejection of δ ≤ 2;
exact energy of each table and independent numerical integration; values on the plateau, in the gap and outside the table; round trip of the <code>.cfg</code> format and the 7 header tokens that HYDRAD skips;
equivalence with a line-by-line replica of <code>CalculateBeamParameters</code>; rejection of invalid tables; equal total energy in E2/E3a/E3b/E4; conservation of P<sub>total</sub>(t) in the fragmentation (2 and 3 pulses);
RADYN <code>ftab.dat</code> encoder: header and column order, 0.1 erg cm⁻² s⁻¹ floor, table covering the whole run, 5000-row limit, and encoded energy within 1%% of the intended energy for every experiment; round trip and layout of the FP solver's atmosphere file; and the toy inject-reinfer model of <code>docs/06_usefulness_tests.md</code>.</div>
<p><b>Test with a real HYDRAD</b> (copy compiled on macOS, 6 s of physical time with the E2 table): the executable reads the table without errors and the heating starts at t ≈ 1 s. E2 and E5 were then run in full (101 s). The maximum temperature goes from
1.6 to 3.4 MK and the upflows reach ≈ 73 km/s, with no NaN. This is a check of format and start-up, <b>not a validation of the physics</b>.</p>
<div class="box warn"><b>Open problem in HYDRAD, and its scope.</b> In initial tests, a constant beam of 5×10¹⁰ erg cm⁻² s⁻¹ (Ec = 15 keV, δ = 5) left all cells as NaN before t = 2 s (dt ≈ 10⁻²⁰ s), and a 10¹⁰ beam abruptly switched off at 10 s failed later. It is reproduced without optimization (-O0). By contrast, the tables of this report (boxcars with ramps, F = 1.3×10¹⁰) ran in full: E2 (101 s, with the second pulse) in ≈41 s of wall time and E5 in ≈19 s, with no NaN. The cause remains undiagnosed (high flux or abrupt switch-off are the suspects); it must be clarified before extending the sweep to larger fluxes.</div>

<h2>6. What this work is not yet</h2>
<ul>
<li>There is no event, no spectral fit and no STIX uncertainties; Ṅ, Ec, δ and A are illustrative.</li>
<li>The energy of the base case (%(etot)s erg) is only a plausible order of magnitude for a small flare, not an estimate.</li>
<li>The pulses are identical boxcars. Real data will have variable Ec(t) and δ(t) and covariances; the generator accepts different pulses, but the fit by intervals remains to be done.</li>
<li>The filament area is not constrained; E3a and E3b are two points of a family, not a sweep.</li>
<li>The synthetic HXR photons, the STIX response and the re-inference (the core of the project) are not implemented.</li>
</ul>

<h2>7. Next steps and questions for the supervisor</h2>
<ol>
<li>Column test: coronal mass column at the onset of pulse 2 versus the electron stopping column, using the stable HYDRAD outputs (decision gate of the project).</li>
<li>Diagnose the HYDRAD NaN (first cell and first instant, energy balance ∫Q<sub>beam</sub>dV against F·A·t) or discard HYDRAD as a test bench.</li>
<li>Choose an event with resolvable loop top and footpoints in STIX and fit the spectra; feed this generator with Ec(t), δ(t), Ṅ(t) and their uncertainties.</li>
<li><b>Questions:</b> Is the bias of STIX inference in successive pulses of interest as the main contribution? Which events are good candidates? Which RADYN+FP version and cluster allocation are available, and does the FP include warm-target physics and give the electron flux? Should RHESSI events be used as an additional proof of concept?</li>
</ol>

<h2>Reproduce</h2>
<div class="eq mono">.venv/bin/python -m pytest -q<br>.venv/bin/python src/experiments.py &nbsp;&nbsp;# writes results/experiments/*/beam_heating_model.cfg, ftab.dat and manifest.json<br>.venv/bin/python src/make_figures.py<br>.venv/bin/python src/make_report.py</div>
<p class="sub">Code: <code>src/beam_tables.py</code>, <code>src/radyn_ftab.py</code>, <code>src/experiments.py</code>, <code>tests/</code>. Based on HYDRAD (Bradshaw &amp; Mason 2003; Reep et al. 2019; MIT).
The interpretation is the project's, not that of the HYDRAD authors.</p>
</main></body></html>
""" % dict(
        fig0=img("fig0_scenarios.png", "Schematic of the two scenarios") + "<figcaption>Figure 0. The two scenarios to be distinguished.</figcaption>",
        fig1=img("fig1_stopping_column.png", "Stopping column versus Ec") + "<figcaption>Figure 1. Stopping column as a function of Ec; expression from heat.cpp, normal incidence.</figcaption>",
        fig2=img("fig2_table_encoding.png", "Beam table encoding") + "<figcaption>Figure 2. Correct versus naive encoding; below, the cumulative energy per unit area.</figcaption>",
        fig3=img("fig3_experiments_flux.png", "Energy flux per experiment") + "<figcaption>Figure 3. Energy flux of each tube in each experiment. Filaments are shown in global time.</figcaption>",
        fig4=img("fig4_energy_ledger.png", "Energy ledger") + "<figcaption>Figure 4. Left: cumulative energy. Right: emitting area and peak flux, which are not conserved.</figcaption>",
        fig5=img("fig5_degeneracy.png", "Degeneracy of the total power") + "<figcaption>Figure 5. P<sub>total</sub>(t) is identical for E2, E3a and E3b; the flux per pulse depends on the assumed area.</figcaption>",
        avg_e=avg_e, ec=p.ec_kev, delta=p.delta, ncn=sci(nc_n, 2), nci=sci(nc_i, 2), ratio=nc_n / nc_i,
        ebad=sci(bad.energy_per_area(), 3), egood=sci(good.energy_per_area(), 3),
        rat=bad.energy_per_area() / good.energy_per_area(), ramp=base.ramp,
        ndot=sci(base.ndot, 2), npul=base.n_pulses, dur=base.duration, gap=base.gap, area=sci(base.area_cm2, 2),
        arc=n_arcsec2, pw=sci(p.power_erg_s, 3), fl=sci(p.flux, 3), rows=rows,
        etot=sci(sum(q.energy_erg for q in ps), 2))
    with open(OUT, "w", encoding="utf-8") as fh:
        fh.write(html)
    print("report written to", os.path.normpath(OUT), "(%d kB)" % (len(html) // 1024))


if __name__ == "__main__":
    main()
