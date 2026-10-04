# Do Successive Hard X-ray Pulses Re-use Flare Loops? Evaporated Plasma as a Tracer of Electron Paths with STIX

**Author:** Carlos Alberto Martínez Sibaja ([@carlmarx17](https://github.com/carlmarx17))
**Status:** research plan, version 4 (2026-10-04). Pilot data of one event (X5.0, 2023-12-31) retrieved and looked at; the tracer physics is implemented and tested. The full design is in `docs/00_objectives_and_methodology.md`; earlier versions are in `docs/archive/`.

## The question

When the second or third hard X-ray pulse of a flare arrives, do its electrons travel through the loops that earlier pulses already filled with evaporated plasma (**re-use**), or through new, still empty loops? Flare models assume either answer without an observational test:
- single-loop radiation-hydrodynamic runs heat the same loop again;
- multithread models light a new thread for every burst.

Imaging alone cannot decide, because a new loop next to an old one lies within one resolution element.

## The idea: the atmosphere's memory is the measuring instrument

1. Earlier pulses evaporate plasma into their loops. STIX sees it as the thermal loop-top source, with a measurable emission measure and size.
2. That plasma is dense enough to stop electrons in the corona: a column N stops every electron below E* = √(2KN), about 23 keV for 10²⁰ cm⁻² and 40 keV for 3×10²⁰ cm⁻².
3. If a later pulse uses those loops, the loop top **must** shine in non-thermal hard X-rays. The ratio of loop-top to footpoint flux, and its fall above E*, follows from the thermal data alone.
4. Comparing the observed ratio with the predicted one measures the re-use fraction φ. All the usual unknowns (filling factor, pitch angles, trapping, residual thermal emission, albedo) can only make the derived **upper bound on φ** larger, so the bound is robust. The return current is the exception and is checked separately.

## What will be done

1. Select bright multi-pulse STIX flares reproducibly. 167 flares from 2021–2026 have a net 25–50 keV peak of ≥ 5×10³ counts per 4 s; an estimated 20–60 survive the cuts.
2. For each pulse:
   - fit the spatially integrated spectrum (thermal + thick target);
   - measure the thermal loop-top source at the pulse onset, giving the column and E*;
   - image the non-thermal emission in energy bins with visibility forward fitting, giving the loop-top/footpoint ratio R(ε);
   - obtain detection limits by injection–recovery.
3. Compute the predicted ratio and the conservative bound on φ with `src/tracer.py`.
4. Study how φ depends on footpoint motion, waiting time between pulses, and confined versus eruptive flares.
5. Publish a paper, a public pulse-by-pulse catalogue and the pipeline.

The core needs STIX only (thermal and non-thermal from one instrument), an analytic thick-target model and a cluster for the parallel imaging and injection–recovery runs. No radiation-hydrodynamic simulation is required.

## Decision gates (20-week plan)

| Gate | Week | Passes if |
|---|---|---|
| G0 | 1 | ADS finds no prior quantitative re-use test; pre-registration agreed |
| G1 | 3 | Synthetic end-to-end test recovers φ with ≥ 95 % coverage; on real STIX visibilities the loop-top detection limit is ≤ half the predicted ratio for dense pulses; a positive control agrees within a factor of 3 |
| G2 | 8 | ≥ 15 flares with informative pulses |
| G3 | 12 | Conclusions stable across imaging algorithms and energy bins |

The main risk is the dynamic range of STIX imaging. A conservative bound φ ≤ 0.3 needs loop-top limits of a few percent of the footpoint flux (`docs/00`, Section 3.5). G1 measures it before any large investment.

## What exists and what does not

| Item | Status |
|---|---|
| Tracer physics: column bound, knee energy, predicted ratio R(ε), conservative bound on φ | Done (`src/tracer.py`); 10 tests, including a check that the bound never falls below the true φ |
| STIX catalogue search and candidate light curves | Done (`scripts/stix_event_search.py`) |
| X5.0 2023-12-31 pilot: data, pulse images, first loop-top/footpoint ratios | First look done (`scripts/x5_first_look/`); CLEAN only, no uncertainties, no detection limits yet |
| Onset thermal fits, visibility forward fitting, injection–recovery, synthetic end-to-end test | Not started |
| Sample selection, catalogue, analysis | Not started |
| Earlier infrastructure (beam tables, HYDRAD runs, FP and RADYN notes, toy inject-reinfer model) | Kept; not needed for the core result (`docs/01`–`docs/06`) |

## Documentation

- `docs/00_objectives_and_methodology.md`: v4 plan. Question, tracer physics with computed numbers, hypotheses and decision rules, objectives, data, step-by-step method, validation, tools, scale, timeline, risks.
- `docs/03_novelty_and_prior_work.md`: prior work. Section 10 covers v4.
- `docs/archive/`: v2 and v3 designs.
- `docs/01`, `docs/02`, `docs/04`, `docs/05`, `docs/06`: infrastructure and tests from earlier versions (HYDRAD, pulse report, RADYN access, FP solver, usefulness tests).
- `scripts/x5_first_look/README.md`: what the pilot scripts do and how far their results go.
- `skills/stix-rhd-memory/SKILL.md`: working guidance for this project.

## Repository contents

- `src/tracer.py`: the tracer physics (v4 core).
- `src/toy_bias.py`: thick-target transport and bremsstrahlung (two zones, Haug cross-section) used by the tracer, plus the earlier inject-reinfer toy.
- `scripts/x5_first_look/`: pilot imaging of the X5.0 flare and early ratio predictions.
- `scripts/stix_event_search.py`, `scripts/plot_stix_candidates.py`: catalogue search.
- `src/beam_tables.py`, `src/radyn_ftab.py`, `src/experiments.py`, `src/fp_atmosphere.py`, `src/make_*.py`, HYDRAD scripts: earlier forward-modelling infrastructure.
- `vendor/HYDRAD/`: upstream HYDRAD source (MIT, Rice University Solar Physics Research Group).
- `tests/`: 60 pytest checks.
- `data/`, `results/`: STIX data and products, git-ignored.

## Environments

Two environments are used. The base one (Python 3.9) runs the models and tests:

    python3 -m venv .venv && .venv/bin/pip install -r requirements.txt
    .venv/bin/python -m pytest -q

The STIX one (Python ≥ 3.10; stixpy, sunpy, xrayvision) runs the data analysis:

    uv venv -p 3.12 .venv-stix && uv pip install --python .venv-stix -r requirements-stix.txt

## Pipeline

    STIX catalogue → selection (brightness, ≥ 3 pulses, loop-top/footpoint separation, informative pulses)
            ↓
    per pulse: integrated spectrum (T, EM, δ, Ec)  +  thermal loop-top image at onset (EM_LT, size)
            ↓                                               ↓
    non-thermal images in energy bins                 column N_min, knee E*, predicted R(ε)  [src/tracer.py]
    (forward fit; CLEAN, MEM_GE)
            ↓                                               ↓
    observed R(ε) + detection limits (injection–recovery)  →  φ_max (conservative), φ (nominal)
            ↓
    catalogue → distribution of φ and its dependence on footpoint motion, waiting time, eruption

## Reproducibility and cluster work

- **One flare per job:** pinned environments, fixed seeds and a manifest recording data files, versions, settings, wall time and failures.
- **Failures stay in the record:** failed fits and images are kept and reported, never silently dropped.
- **Pre-registration first:** selection criteria and decision thresholds are fixed before the full sample is measured.
