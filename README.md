# STIX → RHD: Chromospheric Memory After Successive Electron Pulses

This repository develops a reproducible solar-flare case study anchored to observed
Solar Orbiter/STIX hard-X-ray spectra. The scientific target is the atmospheric
response to a second or third non-thermal electron pulse after an earlier pulse has
already changed the chromosphere.

The central question is:

> How does the solar atmosphere respond to a second or third non-thermal electron
> pulse, when the pulses are constrained by observed STIX spectra, and how does that
> response differ from that of a first pulse on a relaxed atmosphere?

A secondary comparison asks whether reheating of the same magnetic strand can be
distinguished from successive heating of unresolved, independent filaments when both
are compatible with the STIX hard-X-ray signal.

Objectives, hypotheses, methodology, expected results and deliverables are in
docs/00_objetivos_y_metodologia.md.

This is a physical radiation-hydrodynamic simulation, not a neural network. The
production model is RADYN with its Fokker–Planck electron transport; a single solver is
used. HYDRAD was explored first and is retained only until RADYN reproduces a published
F-CHROMA model (see docs/04_acceso_a_radyn.md); it is not equivalent to RADYN+FP.

## Scientific experiments

The minimum experiment set is:

1. one pulse in a relaxed atmosphere;
2. two or three pulses in the same continuously evolving atmosphere;
3. pulses in independent unresolved filaments;
4. a continuous-heating control with comparable total energy;
5. a first-pulse relaxation control with no later pulse.

The simulation must retain temperature, density, velocity and atomic populations
between pulses. The analysis will quantify deposition depth, atmospheric memory,
chromospheric and coronal emission, and the detectability of the difference after
instrument cadence, exposure, spatial mixing and STIX parameter uncertainties are
included.

The detailed design is in docs/00_objetivos_y_metodologia.md; the working guidance for
this project is in skills/stix-rhd-memory/SKILL.md.

## Current repository state

The project currently contains:

- vendor/HYDRAD/: upstream HYDRAD source, MIT licensed by the Rice University Solar
  Physics Research Group. No compiled executable is stored here; the shipped config.h
  files do not define BEAM_HEATING and the build scripts are Windows .bat files. A macOS
  build worked with `-DBEAM_HEATING -include cstdlib -include cstring -std=gnu++14`;
  a constant 5e10 erg cm^-2 s^-1 beam, and a 1e10 beam switched off abruptly, end in NaN
  (undiagnosed), while the ramped 1.3e10 pulse tables of src/experiments.py run cleanly
  (E2, 101 s of model time, in ~41 s wall);
- src/beam_tables.py: electron-pulse parameters (rate, Ec, delta, area) to beam tables, with
  energy-conservation checks; src/radyn_ftab.py: encodes them as RADYN's ftab.dat
  (Fokker–Planck beam, log-flux interpolation, 0.1 erg cm^-2 s^-1 floor);
- src/experiments.py: the five-experiment matrix with comparable energy (synthetic base
  case, not STIX fits);
- src/make_figures.py, src/make_report.py: figures and docs/02_informe_experimentos_pulsos.html;
- tests/: 38 pytest checks of the above;
- docs/00_objetivos_y_metodologia.md: research question, hypotheses, specific objectives,
  methodology, expected results and deliverables;
- docs/04_acceso_a_radyn.md: what was verified about the RADYN F-CHROMA distribution
  (FP, ftab format, restart, license status) and the verification gate;
- docs/03_novedad_y_antecedentes.md: prior work and novelty assessment;
- docs/01_hydrad_code.md: initial code-oriented guide to the installed solver;
- results/: generated tables and (later) fits and diagnostics, git-ignored.

Not yet present: STIX/AIA/GOES data (data/), STIXpy/SunPy in the environment, any
observational fit, and any RADYN installation (the F-CHROMA distribution was downloaded and read, but no Fortran
compiler or NASA CDF library is installed yet).

Create the local environment and run the checks with:

    python3 -m venv .venv && .venv/bin/pip install -r requirements.txt
    .venv/bin/python -m pytest -q
    .venv/bin/python src/experiments.py

No flare has yet been selected, no observational spectrum has yet been fit, and no
production RADYN run has yet been completed.

## Reproducibility and cluster work

Before a parameter campaign, reproduce a published reference model and record solver
versions, compiler flags, initial atmosphere, input beam, output cadence, wall time,
CPU time, memory and storage. Independent parameter cases should be distributed as
separate jobs on the cluster. Failed or non-converged cases must remain documented.

Do not compare cases with different total injected energy or emitting area without
reporting that difference. Electron rate, total power, energy flux and volumetric
deposition are distinct quantities and must retain their units.

## Data and analysis pipeline

    STIX science spectrum
            ↓
    response-aware thermal + non-thermal fit
            ↓
    Ec(t), δ(t), electron rate or energy flux, uncertainties
            ↓
    Fokker–Planck transport and RHD evolution
            ↓
    T(s,t), density(s,t), velocity(s,t), populations(s,t), Q(s,t)
            ↓
    Hα / IRIS / Fe XVIII / AIA / GOES / STIX synthetic diagnostics
            ↓
    comparison of reheating and independent-filament scenarios

## Credits and citations

This repository contains and builds on software and scientific work by the original
authors. Please cite the relevant original work in any publication, and preserve the
licenses and notices shipped with the upstream code.

### HYDRAD

- Bradshaw & Mason (2003), A self-consistent treatment of thermal conduction in
  coronal loops, Astronomy & Astrophysics, 401, 699.
- Bradshaw & Cargill (2013), The cooling of coronal plasma, The Astrophysical
  Journal, 770, 12.
- Reep et al. (2019), Efficient calculation of non-local thermodynamic equilibrium
  effects in multithreaded hydrodynamic simulations of solar flares, The Astrophysical
  Journal, 885, 103.
- Upstream source: https://github.com/rice-solar-physics/HYDRAD. The corresponding
  MIT license is retained in vendor/HYDRAD/LICENSE.

### RADYN and Fokker–Planck transport

- Allred, Kowalski & Carlsson (2015), A Unified Computational Model for Solar and
  Stellar Flares, The Astrophysical Journal, 809, 104,
  https://doi.org/10.1088/0004-637X/809/1/104.
- Allred et al. (2020), Modeling the Transport of Nonthermal Particles in Flares
  Using Fokker-Planck Kinetic Theory, The Astrophysical Journal, 902, 16,
  https://arxiv.org/abs/2008.10671.
- Carlsson et al. (2023), The F-CHROMA grid of 1D RADYN flare models, Astronomy
  & Astrophysics, 673, A150, https://arxiv.org/abs/2304.02618.

### STIX and analysis software

- Krucker et al. (2020), The Spectrometer/Telescope for Imaging X-rays (STIX),
  Astronomy & Astrophysics, 642, A15,
  https://doi.org/10.1051/0004-6361/201937362.
- STIXpy documentation: https://stixpy.readthedocs.io/.
- OSPEX documentation:
  https://hesperia.gsfc.nasa.gov/ssw/packages/spex/doc/ospex_explanation.htm.

### Project scope

The scientific interpretation, event selection, fits, simulations and figures in
this repository are project work. They must not be presented as results of the
upstream authors or software teams. Project-specific code is released under the MIT
license in LICENSE; third-party components retain their own licenses.
