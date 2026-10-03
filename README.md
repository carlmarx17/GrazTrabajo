# STIX → RHD: Bias of STIX Electron Inference in Successive Pulses

**Author:** Carlos Alberto Martínez Sibaja ([@carlmarx17](https://github.com/carlmarx17))
**Status:** research proposal and preparatory infrastructure. No physical result has been produced yet; every beam parameter in this repository is synthetic.

## What is proposed

The electron parameters of a flare (rate Ṅ, low-energy cut-off Ec, spectral index δ) are inferred from Solar Orbiter/STIX hard X-ray (HXR) spectra with a standard model: an isothermal component plus a cold, collisionally thick target. That model is reasonable for a first pulse. A second or third pulse arrives in an atmosphere that the first pulse has already evaporated into the corona and heated, so the target is no longer the one the model assumes.

> **Research question.** How much does the atmospheric memory of the previous pulse bias the electron parameters (Ṅ, Ec, δ) inferred with STIX for a second or third pulse, and is it visible in STIX images as a change in the loop-top / footpoint emission ratio?

## What will be done

An **inject–simulate–reinfer** test:

1. Inject known electron pulses into a 1D hydrodynamic loop that keeps its history between pulses (HYDRAD first; RADYN as an optional upgrade).
2. Run the open-source Fokker–Planck solver FP (Allred et al. 2020; warm target and return current) on the simulated atmosphere snapshots to obtain the electron transport and the synthetic HXR photons (non-thermal bremsstrahlung plus thermal emission of the plasma), by region and in total.
3. Apply the STIX response and Poisson noise.
4. Fit with the same standard model used for real data and compare with the injected truth. The memory-induced bias is ΔB = B₂ − B₁ (pulse 2 minus pulse 1).
5. Repeat the analysis on one real STIX event with at least two pulses and a resolved loop top and footpoints.

The hydrodynamic memory is measured with a paired counterfactual (runs with and without a given pulse, sharing the history up to that pulse). Independent filaments, where each pulse hits a relaxed tube, are the alternative hypothesis and should show no memory bias, so the same-tube versus independent-filament comparison is a test rather than an appendix.

Possible outcomes, all of them results: a significant and visible bias; a significant bias that STIX imaging cannot resolve; a negligible bias (STIX inference is robust to memory); or a bias degenerate with the allowed parameter uncertainty.

## First task and decision gate

Before any campaign, compare the coronal mass column at the onset of pulse 2 with the electron stopping column (OE1 in `docs/00_objectives_and_methodology.md`). If it is below about 10 %, the physical basis of the idea is weak and the project is reconsidered. This test uses HYDRAD, which already runs, and does not need RADYN.

## What exists and what does not

| Item | Status |
|---|---|
| Beam-pulse table generator, five-experiment matrix (E1–E5), RADYN `ftab.dat` encoder | Done, synthetic parameters, 38 tests |
| Infrastructure report | Done (`docs/02_pulse_experiments_report.html`) |
| Prior-work review | Done for the previous question; the current question is assessed only preliminarily (`docs/03_novelty_and_prior_work.md`) |
| Column test (gate) | Not started; next task |
| STIX event selection and spectral fits | Not started |
| FP solver (solarFP/FP, Apache-2.0): install, read documentation, verify that it accepts an external atmosphere and outputs photons | Not started |
| RADYN (optional upgrade): compilation, license, verification | Not started (distribution read; no Fortran compiler or CDF library installed; the distribution ships without a license file) |
| Synthetic photons and re-inference | Not implemented |
| HYDRAD with a beam | Ramped pulse tables (F ≈ 1.3×10¹⁰ erg cm⁻² s⁻¹) run cleanly; a constant 5×10¹⁰ beam and an abruptly switched-off 10¹⁰ beam end in NaN (undiagnosed) |

## Documentation

- `docs/00_objectives_and_methodology.md`: research question, hypotheses, specific objectives, methodology, decision rules, phases, risks and open questions.
- `docs/01_hydrad_code.md`: first reading of the HYDRAD beam-heating path.
- `docs/02_pulse_experiments_report.html`: report on the pulse infrastructure (synthetic case).
- `docs/03_novelty_and_prior_work.md`: prior work and novelty assessment.
- `docs/04_radyn_access.md`: what was verified about the RADYN F-CHROMA distribution (optional upgrade) and its verification gate.
- `skills/stix-rhd-memory/SKILL.md`: working guidance for this project.

This is a physical simulation, not a neural network. The atmosphere comes from a 1D hydrodynamic code (HYDRAD, with RADYN+FP as an optional upgrade) and the electron transport and photons from the FP solver; the two are decoupled, so no single code is a bottleneck. HYDRAD heats with an analytic cold-target expression, which is the assumption under test; the comparison of FP's deposition with HYDRAD's on the same snapshot bounds that effect (`docs/00_objectives_and_methodology.md`, OE4). HYDRAD is not equivalent to RADYN+FP.

## Experiment matrix

| ID | Set-up | Role |
|---|---|---|
| E1 | One pulse in a relaxed atmosphere | Baseline response and bias |
| E2 | Two or three pulses in the same, continuously evolving tube | Object of study |
| E5 | First pulse followed by relaxation, no later pulse | Counterfactual that separates residual emission from the new response |
| E3a/E3b | Pulses in independent filaments, two area assignments | Alternative hypothesis |
| E4 | Continuous heating with comparable total energy | Control for the temporal distribution |

The simulation must retain temperature, density, velocity and atomic populations between pulses. Cases compared must have the same total injected energy and emitting area unless the difference is the factor under study.

## Repository contents

- `vendor/HYDRAD/`: upstream HYDRAD source, MIT licensed by the Rice University Solar Physics Research Group. No compiled executable is stored; the shipped `config.h` files do not define `BEAM_HEATING` and the build scripts are Windows `.bat` files. A macOS build worked with `-DBEAM_HEATING -include cstdlib -include cstring -std=gnu++14`.
- `src/beam_tables.py`: electron-pulse parameters (rate, Ec, δ, area) to beam tables, with energy-conservation checks.
- `src/radyn_ftab.py`: encodes the tables as RADYN's `ftab.dat` (Fokker–Planck beam, log-flux interpolation, 0.1 erg cm⁻² s⁻¹ floor).
- `src/experiments.py`: the experiment matrix with comparable energy (synthetic base case, not STIX fits).
- `src/make_figures.py`, `src/make_report.py`: figures and the infrastructure report.
- `tests/`: 38 pytest checks of the above.
- `results/`: generated tables and (later) fits and diagnostics, git-ignored.

Not yet present: STIX/AIA/GOES data (`data/`), STIXpy/SunPy in the environment, any observational fit and any RADYN installation.

Create the local environment and run the checks with:

    python3 -m venv .venv && .venv/bin/pip install -r requirements.txt
    .venv/bin/python -m pytest -q
    .venv/bin/python src/experiments.py

## Data and analysis pipeline

    STIX science spectrum
            ↓
    response-aware thermal + non-thermal fit  (standard model)
            ↓
    Ec(t), δ(t), electron rate or energy flux, uncertainties
            ↓
    Fokker–Planck transport and RHD evolution (history retained)
            ↓
    T(s,t), density(s,t), velocity(s,t), populations(s,t), Q(s,t)
            ↓
    synthetic HXR photons + STIX response and noise
            ↓
    re-inference with the same standard model  →  bias ΔB, loop-top/footpoint ratio

## Reproducibility and cluster work

Before a parameter campaign, reproduce a published reference model and record solver versions, compiler flags, initial atmosphere, input beam, output cadence, wall time, CPU time, memory and storage. Independent parameter cases should be distributed as separate jobs on the cluster. Failed or non-converged cases must remain documented.

Do not compare cases with different total injected energy or emitting area without reporting that difference. Electron rate, total power, energy flux and volumetric deposition are distinct quantities and must retain their units.

## Credits and citations

This repository contains and builds on software and scientific work by the original authors. Please cite the relevant original work in any publication, and preserve the licenses and notices shipped with the upstream code.

### HYDRAD

- Bradshaw & Mason (2003), A self-consistent treatment of thermal conduction in coronal loops, Astronomy & Astrophysics, 401, 699.
- Bradshaw & Cargill (2013), The cooling of coronal plasma, The Astrophysical Journal, 770, 12.
- Reep et al. (2019), Efficient calculation of non-local thermodynamic equilibrium effects in multithreaded hydrodynamic simulations of solar flares, The Astrophysical Journal, 885, 103.
- Upstream source: https://github.com/rice-solar-physics/HYDRAD. The corresponding MIT license is retained in `vendor/HYDRAD/LICENSE`.

### RADYN and Fokker–Planck transport

- Allred, Kowalski & Carlsson (2015), A Unified Computational Model for Solar and Stellar Flares, The Astrophysical Journal, 809, 104, https://doi.org/10.1088/0004-637X/809/1/104.
- Allred et al. (2020), Modeling the Transport of Nonthermal Particles in Flares Using Fokker-Planck Kinetic Theory, The Astrophysical Journal, 902, 16, https://arxiv.org/abs/2008.10671.
- Carlsson et al. (2023), The F-CHROMA grid of 1D RADYN flare models, Astronomy & Astrophysics, 673, A150, https://arxiv.org/abs/2304.02618.

### STIX and analysis software

- Krucker et al. (2020), The Spectrometer/Telescope for Imaging X-rays (STIX), Astronomy & Astrophysics, 642, A15, https://doi.org/10.1051/0004-6361/201937362.
- STIXpy documentation: https://stixpy.readthedocs.io/.
- OSPEX documentation: https://hesperia.gsfc.nasa.gov/ssw/packages/spex/doc/ospex_explanation.htm.

### Project scope and authorship

The research question, design, event selection, fits, simulations and figures in this repository are the work of the author named above. They must not be presented as results of the upstream authors or software teams. Project-specific code is released under the MIT license in `LICENSE`; third-party components retain their own licenses (`THIRD_PARTY_NOTICES.md`). To cite this work, see `CITATION.cff`.
