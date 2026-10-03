---
name: stix-rhd-memory
description: Guide the design, analysis and writing of the STIX paper that separates target memory, return current and acceleration in successive flare hard X-ray pulses, with forward modelling support (toy two-zone model, HYDRAD, FP, RADYN). Use when working on this project, its RADYN/FP experiments, its synthetic photons and re-inference, or its reproducible pipeline.
---

# STIX: target memory, return current or acceleration in successive hard X-ray pulses

Author of the project: Carlos Alberto Martínez Sibaja.

## Purpose and project decisions

The final product is a scientific paper and a reproducible pipeline. The pipeline tests, with STIX spectroscopy and imaging of bright multi-pulse flares, whether later hard X-ray pulses see a target modified by earlier ones, and separates that target memory from return-current losses and from acceleration changes. Forward modelling (two-zone toy model, HYDRAD, FP, RADYN) supports the interpretation and the power test. The project is physical data analysis and simulation, not neural-network training. Cluster resources and quota have not been specified.

Working hypothesis: the pulses hit the **same flux tube**. This is probable but is an operating hypothesis, to be confirmed with the supervisor. Do not treat it as observational evidence.

Decision (2026-10-03, replaces the single-RADYN decision of 2026-10-02): the work is split in two decoupled pieces so that no single code is a bottleneck. The atmosphere with history comes from HYDRAD (works, MIT license; its analytic cold-target heating is the assumption under test, so compare its deposition with FP's on the same snapshot). The electron transport (warm target, return current) and the bremsstrahlung photons come from the open-source FP solver (solarFP/FP, Apache-2.0, Allred et al. 2020) run on the snapshots; its input/output compatibility is to be verified. RADYN with FP (F-CHROMA distribution, 2015 FP, no license file, not compiled) is an optional upgrade, not a requirement; details in `docs/04_radyn_access.md`. FLARIX is not accessible. Never equate HYDRAD's analytic heating with Fokker–Planck.

## Question and the result to reach

Question (v3, 2026-10-03; supersedes v2): in bright flares with several hard X-ray pulses, does the X-ray spectrum depend on the energy previously deposited at the same footpoints (target memory: nonuniform ionization and evaporation), on the instantaneous beam flux (return current), or on neither (acceleration: soft-hard-soft, soft-hard-harder)? How much of the pulse-to-pulse spectral evolution does each explain? Full design in `docs/00_objectives_and_methodology.md`; v2 is archived in `docs/archive/`.

Core method: STIX time-binned spectroscopy with four models (standard; broken power law; two-zone nonuniform ionization; warm target or return current), plus per-bin regressors: cumulative deposited energy (count-based first, because model-based estimates are biased by memory), instantaneous flux density (imaging area) and footpoint displacement (imaging). Then regression with a random effect per flare, hysteresis at matched flux, and a low-band versus high-band hardening test. Decision rules are pre-registered (Section 6.7 of `docs/00`).

Forward models support, not replace, the observations: the two-zone toy model (`src/toy_bias.py`, return-current module still to be added, real STIX response to be used), HYDRAD, FP and optionally RADYN, for the expected size of each effect and for injection–recovery (the power test, gate G2).

Events (from the reproducible catalogue search `scripts/stix_event_search.py`): primary X5.0 2023-12-31 and X5.2 2025-11-11 (seen from near the Earth direction); benchmark X1.3 2022-03-30 (published pulse-resolved fits); stress case X9.1 2024-10-03 (pile-up risk; studied by another group). Quick-look counts rank events; they are not spectroscopic data.

Systematics that can imitate the signal: pile-up and live time (flux-correlated hardening), attenuator steps, superhot thermal emission hiding breaks below ~25–30 keV, high-energy background. A null result for target memory is a result (an upper limit). Do not promise detection, novelty, acceptance or a journal.

## Scientific objectives

1. Select an event with STIX science spectra and several resolvable pulses, with GOES and AIA; prioritize IRIS spectroscopy and Hα data if they are central diagnostics. AIA/HMI and IRIS do not replace an Hα observation. Check visibility, saturation, cadence, spatial evolution and the Solar Orbiter–Earth time corrections before attributing pulses to the same place.
2. Infer from the count fit and instrument response the beam parameters and their evolution: Ec, electron index δ and injection rate. Keep their joint uncertainties and thermal/non-thermal degeneracies; Ec may be weakly constrained. STIX observes photons, not electrons directly, and the photon index is not interchangeable with δ.
3. Transport the beam in an evolving atmosphere and compute the deposition Q(s,t). Couple it consistently to the RHD; verify which physics the specific FP version includes, including collisions and, where applicable, return current. Avoid counting the beam heating twice.
4. Quantify the change between pulses in temperature, density, velocity, ionization, deposition depth and energy partition, separating the effects of waiting time, previous energy and initial conditions.
5. Compute the synthetic HXR photons and re-infer the electron parameters; decompose the bias by mechanism (thermal contamination, warm target, ionization, loop-top/footpoint mixing).
6. Synthesize a viable set of other diagnostics according to real coverage: Hα, IRIS lines, coronal/Fe XVIII emission, GOES/AIA/STIX curves. Do not identify AIA 94 Å with Fe XVIII without more. The Neupert comparison is complementary, not a sole test of the heating geometry nor a reason to readjust the beam to force agreement.
7. Evaluate whether the differences between scenarios survive noise, exposure, spatial and temporal resolution, mixing of structures and beam uncertainties.

## Experiments that must support the comparison

| Experiment | Function |
| --- | --- |
| Isolated pulse in a relaxed atmosphere | Reference response and baseline bias |
| Two or three pulses in the same atmosphere | Measure effects of the thermal and dynamic history |
| Pulses in independent filaments | Spatially unresolved alternative; expected no memory bias |
| Continuous heating with comparable total energy | Control of duration and temporal distribution of energy |
| First pulse followed by cooling, no second pulse | Distinguish residual emission from the response to the new beam |

Evolve continuously between pulses: do not reset temperature, velocities or atomic populations. A restart must keep the necessary solver state. Do not add up isolated-pulse responses to represent non-linear reheating; the sum of emissions only represents independent structures under documented geometric and radiative assumptions.

Compare total power and areas explicitly. Electron rate [s⁻¹], power [erg s⁻¹], energy flux [erg cm⁻² s⁻¹] and Q [erg cm⁻³ s⁻¹] are different quantities. For a simple power law with no upper cut-off, δ > 2: P = Ndot × Ec × (δ−1)/(δ−2), with Ec converted to erg; F = P/A. Adapt that conversion to finite cut-offs or other distributions. Propagate the uncertainty of A and the assignment to each footpoint/filament; conserve P_total(t) = Σ A_i F_i(t) in equivalent fragmentation comparisons.

## Cluster use and validation

Start by reproducing a published case with documented version and configuration. Measure wall time, CPU, memory, storage and stability in representative pilots before budgeting the campaign. Tens of pilots and hundreds of cases are a planning possibility, not a requirement nor a performance estimate. Favour independent jobs in parallel; do not assume MPI/GPU scaling of one run because many cores are available.

Choose a parameter sampling informed by the pilots and by the observed uncertainties. Check spatial/temporal convergence and energy balance in decisive cases, as well as persistence of the diagnostics against initial conditions. Record convergence failures and do not silently exclude them from the analysis. A comparison with another solver is a useful extension if it answers a concrete doubt. 3D MHD needs a physical motivation and its own scope; having a cluster does not automatically make it the next step.

## Deliverables and completion criteria

- Event, data, intervals, calibrations and fits, traceable and with uncertainties.
- Experiment matrix and justification of the controls and explored parameters.
- Reproducible runs: solver versions, inputs, initial state, cluster scripts, execution logs and outputs with clear units and coordinates.
- Quantitative evidence of the bias, its mechanism, numerical robustness and detectability or degeneracy between scenarios; include discrepancies that the STIX-allowed parameters do not resolve.
- Reusable pipeline from STIX data/fits to results and figures, documenting any manual step, license or external dependency.
- Proof-of-concept manuscript with background, methods, uncertainties, results, limits and enough material to reproduce the conclusions.

Installing, compiling or producing demonstration figures is not the same as completing the objective. Always distinguish test results, observational results and predictions to be verified. A skill with this scope does not by itself authorize sending e-mails, publishing results or consuming a cluster allocation that has not been agreed.

## Prior work to delimit the contribution

When preparing the novelty or the manuscript, review these works and update the search; this list comes from a preliminary exploration, not an exhaustive review:

- [Kennedy et al. (2015)](https://arxiv.org/abs/1504.07541): RADYN driven by HXR spectra and evolution of the stopping depth.
- [Allred et al. (2020)](https://arxiv.org/abs/2008.10671): FP transport.
- [Carlsson et al. (2023)](https://arxiv.org/abs/2304.02618): F-CHROMA and its public RADYN version; verify differences with respect to the latest RADYN+FP.
- [Litwicka et al. (2025)](https://doi.org/10.3847/1538-4357/adc393): FLARIX; continuous heating versus pulses in different filaments, with a preheated VAL-C as initial condition; no observational data.
- [Litwicka et al., March 2026 conference](https://plan.events.mpg.de/event/453/contributions/3104/): application with STIX, IRIS and CHASE; distinguish a conference abstract from a paper.
- [Veronig & Brown (2004)](https://eprints.gla.ac.uk/1317): coronal thick-target HXR sources (abstract only read).

Novelty assessment and further prior work: `docs/03_novelty_and_prior_work.md` (its Sections 1–7 refer to the previous question).

The possible contribution is to quantify how the memory of a reheated atmosphere biases STIX inference and whether it is observable, not to claim novelty for the mere use of STIX, several pulses or preheated conditions.

## Operating context when resuming

Read the current files first and verify the installed capabilities. At the creation of this skill, a compiled HYDRAD and a Python STIXpy/SunPy/AIApy environment had been reported, but no validated physical run, definitive event or RADYN installation. Do not treat that historical inventory as a perpetual state. Keep the objectives in mind when solving each concrete task; do not launch the whole campaign when the user asks only for an explanation, review or edit.
