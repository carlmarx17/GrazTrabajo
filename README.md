# Does the Flaring Chromosphere Remember? Target Memory, Return Current or Acceleration in Successive STIX Hard X-ray Pulses

**Author:** Carlos Alberto Martínez Sibaja ([@carlmarx17](https://github.com/carlmarx17))
**Status:** research proposal, version 3 (2026-10-03), with preparatory infrastructure, executable usefulness tests and a reproducible event search. No STIX science data have been analysed yet.

## What is proposed

When a flare produces several hard X-ray pulses, the spectrum can change from one pulse to the next for three different physical reasons:

| Process | Fingerprint in time |
|---|---|
| **Target memory**: earlier pulses ionize and evaporate the chromosphere, so later electrons cross a larger ionized column (nonuniform ionization) | The spectral break moves up with the **energy already deposited** at the same footpoints. Hardening is confined near the break. It resets when **new footpoints** light up. Hysteresis at equal flux |
| **Return current**: ohmic losses set by the instantaneous beam flux | The break follows the **instantaneous flux**; no hysteresis |
| **Acceleration**: the injected spectrum itself changes (soft-hard-soft, soft-hard-harder) | The index changes **at all energies**, tied to amplitude or time |

> **Research question.** In bright flares with several hard X-ray pulses, does the X-ray spectrum depend on the energy previously deposited at the same footpoints, on the instantaneous beam flux, or on neither, and how much of the observed pulse-to-pulse spectral evolution, including progressive hardening, does each explain?

Each process has been studied before, but separately and mostly at the X-ray peak. This project uses the **time dependence** of the spectra (cumulative versus instantaneous), together with **footpoint novelty from STIX imaging**, to discriminate them. Full design: `docs/00_objectives_and_methodology.md`.

## What will be done

1. Select bright multi-pulse flares reproducibly from the STIX data-center catalogue (`scripts/stix_event_search.py`; Figure 7 in `docs/00`). Primary events: X5.0 on 2023-12-31 and X5.2 on 2025-11-11, both seen from near the Earth direction. Benchmark: X1.3 on 2022-03-30. Stress case: X9.1 on 2024-10-03.
2. Fit STIX spectra in time bins with four models: standard; broken power law; two-zone nonuniform ionization; and, as cross-checks, warm target or return current.
3. Build per bin the cumulative deposited energy, the instantaneous flux density and the footpoint displacement from imaging.
4. Regress the break and the curvature on these quantities, test hysteresis at matched flux, and compare the hardening in a low and a high energy band.
5. Use forward models (two-zone toy model with a return-current module and the real STIX response; HYDRAD, FP and optionally RADYN) for injection–recovery and for the expected size of each effect.

A null result for target memory is a result: an upper limit on spectral memory in bright flares.

## Decision gates

- **G1:** no prior paper doing this test (ADS search), and the science data obtained.
- **G2 (power test):** injection–recovery with the real STIX response shows that the memory effect predicted for the event is detectable at ≥ 3σ.
- **G3:** pile-up and attenuator systematics are under control.

The earlier gate (coronal column test) and the toy inject-reinfer test are done (`docs/06_usefulness_tests.md`).

## What exists and what does not

| Item | Status |
|---|---|
| Beam-pulse table generator, five-experiment matrix (E1–E5), RADYN `ftab.dat` encoder | Done, synthetic parameters; 50 tests in total |
| Infrastructure report | Done (`docs/02_pulse_experiments_report.html`) |
| Prior-work review | Done for v1 and v2 (`docs/03_novelty_and_prior_work.md`); v3 checked by web search (`docs/00`, Sections 0–1; `docs/03`, Section 9); ADS search pending (gate G1) |
| Column test (gate) and toy inject-reinfer test | Done (`docs/06_usefulness_tests.md`): the bias is material only for energetic first pulses in short loops and ≳10⁵ counts per pulse; the repository base case gives a negligible bias; HYDRAD fails (NaN) for F ≥ 2.5×10¹⁰ |
| Event search in the STIX catalogue (quick-look level) | Done: candidate table and light curves in `docs/00`, Section 5; science data not yet retrieved |
| Pulse-resolved spectroscopy, regressors, discriminating test (v3 core) | Not started |
| FP solver (solarFP/FP, Apache-2.0) | Manual and source read; atmosphere format decoded and reproduced byte-for-byte; Python parts run; Fortran solver not compiled (`docs/05`) |
| RADYN (optional upgrade): compilation, license, verification | Not started (distribution read; no Fortran compiler or CDF library installed; the distribution ships without a license file) |
| Synthetic photons and re-inference | Done in the two-zone toy model (`src/toy_bias.py`); return-current module and real STIX response pending; FP photons pending |
| HYDRAD with a beam | Ramped pulse tables at F ≈ 1.3×10¹⁰ erg cm⁻² s⁻¹ with 10 s pulses run cleanly; F ≥ 2.5×10¹⁰ (even ramped) and a 30 s pulse in a 60 Mm loop end in NaN (undiagnosed; `docs/06`, Section 7) |

## Documentation

- `docs/00_objectives_and_methodology.md`: research question (v3), hypotheses, objectives, event selection, methodology, decision rules, timeline, risks and open questions.
- `docs/archive/00_objectives_v2_inference_bias.md`: the previous (v2) design, kept for reference.
- `docs/01_hydrad_code.md`: first reading of the HYDRAD beam-heating path.
- `docs/02_pulse_experiments_report.html`: report on the pulse infrastructure (synthetic case).
- `docs/03_novelty_and_prior_work.md`: prior work and novelty assessment.
- `docs/04_radyn_access.md`: what was verified about the RADYN F-CHROMA distribution (optional upgrade) and its verification gate.
- `docs/06_usefulness_tests.md`: executable tests of the project's usefulness (toy inject-reinfer model, HYDRAD column test and variants) and what they imply.
- `docs/05_fp_solver_verification.md`: what the manual and source of the open-source FP solver say, and how they fit the project (documented, not yet tested).
- `skills/stix-rhd-memory/SKILL.md`: working guidance for this project.

The core of the project is observational (STIX spectroscopy and imaging); simulations support the interpretation and the power test. No neural network is involved. In the forward modelling, the atmosphere comes from a 1D hydrodynamic code (HYDRAD, with RADYN+FP as an optional upgrade) and the electron transport and photons from the two-zone toy model or the FP solver. HYDRAD heats with an analytic cold-target expression; the comparison of FP's deposition with HYDRAD's on the same snapshot bounds that effect. HYDRAD is not equivalent to RADYN+FP.

## Simulation experiment matrix (forward-modelling support)

| ID | Set-up | Role |
|---|---|---|
| E1 | One pulse in a relaxed atmosphere | Baseline response and bias |
| E2 | Two or three pulses in the same, continuously evolving tube | Main simulated case |
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
- `src/fp_atmosphere.py`: reader/writer of the FP solver's atmosphere file (validated byte-for-byte against FP's examples).
- `src/toy_bias.py`: toy inject-reinfer model (two-zone target, Haug bremsstrahlung, STIX-like response, Cash fits).
- `scripts/`: the toy sweep and its figure, the HYDRAD column test and its variants, the STIX catalogue search (`stix_event_search.py`) and the candidate light curves (`plot_stix_candidates.py`).
- `tests/`: 50 pytest checks of the above.
- `results/`: generated tables and (later) fits and diagnostics, git-ignored.

Not yet present: STIX/AIA/GOES data (`data/`), STIXpy/SunPy in the environment, any observational fit and any RADYN installation.

Create the local environment and run the checks with:

    python3 -m venv .venv && .venv/bin/pip install -r requirements.txt
    .venv/bin/python -m pytest -q
    .venv/bin/python src/experiments.py

## Data and analysis pipeline

    STIX catalogue query + quick-look light curves  →  event selection
            ↓
    STIX science data (spectrograms, pixel data), response, background, attenuator / live time
            ↓
    time-binned fits: standard | broken power law | two-zone (nonuniform ionization) | warm target / return current
            ↓
    per bin: break energy, low- and high-band indices, cumulative deposited energy,
             instantaneous flux density (imaging area), footpoint displacement (imaging)
            ↓
    regression + hysteresis + two-band tests  →  share of target memory, return current, acceleration
            ↑
    forward models: two-zone toy (+ return current) with the STIX response; HYDRAD / FP / RADYN
    for the expected size of each effect; injection–recovery for the power of the test

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
