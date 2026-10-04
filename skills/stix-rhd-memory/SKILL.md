---
name: stix-rhd-memory
description: Guide the design, analysis and writing of the STIX paper (v4) that tests whether successive flare hard X-ray pulses re-use the loops filled by earlier pulses, using the evaporated plasma as a tracer (predicted versus observed loop-top/footpoint ratio and a conservative bound on the re-use fraction). Use when working on this project, its STIX data, its tracer physics, its pipeline, catalogue or manuscript.
---

# STIX v4: do successive hard X-ray pulses re-use flare loops?

Author of the project: Carlos Alberto Martínez Sibaja. Do not write the supervisor's name in the public repository.

## Question and idea

**Question.** When pulse k ≥ 2 of a flare arrives, what fraction φ of its electrons crosses the loop-top region already filled with plasma evaporated by pulses 1 … k−1, and on what does φ depend (footpoint motion, waiting time, confined or eruptive flare)? Flare models assume either "same loop" (single-loop RHD) or "new loop per burst" (multithread) without an observational test; imaging cannot separate neighbouring loops within one resolution element.

**Tracer.** At each pulse onset the thermal loop-top source (emission measure EM_LT, volume ≤ V_max, beam path ≥ l_min) gives a column N_min = sqrt(EM_LT / V_max) · l_min. Electrons below E* = sqrt(2KN) stop in it, so re-use predicts a non-thermal loop-top/footpoint ratio R_pred(ε) that falls above E*. The observed R(ε) gives the conservative bound

    phi <= R_obs,max (1 + a_max) · max over (delta, Ec) of I_0 / I_LT(N_min)

implemented in `src/tracer.py`; `tests/test_tracer.py` checks that it never falls below the true φ. Full design: `docs/00_objectives_and_methodology.md` (v4); earlier versions in `docs/archive/`.

## Rules that keep the physics honest

- **Conservative only where proven.** Filling factor, pitch angles, trapping or other extra loop-top sources, residual thermal emission, pre-flare corona on empty paths and a larger albedo only loosen the bound. Two effects are **not** covered and must be handled explicitly:
  - **Return current:** check it with the FP solver for the highest flux densities, or exclude those pulses.
  - **Emission-measure attribution:** use the imaging-derived loop-top share with its lower uncertainty, never the spatially integrated EM.
- **Use the onset EM** of pulse k, not its peak value, so that only the memory of earlier pulses enters.
- **A CLEAN non-detection is not an upper limit.** Detection limits come from injection–recovery on the observed visibilities with matched noise.
- **Use the energy dependence R(ε).** Energy-independent amplitude errors only add a constant offset, so the shape constrains φ when the absolute level does not.
- **Re-use claims need the knee.** Claiming re-use requires R_obs ≈ R_pred **and** the knee at E*, with thermal emission subtracted. An extra loop-top source has a smooth R(ε).
- **Units are not interchangeable.** Electron rate [s⁻¹], power [erg s⁻¹], energy flux [erg cm⁻² s⁻¹] and column [cm⁻²] are different quantities. STIX observes photons; the photon index is not δ. Ec may be weakly constrained: use its posterior range.

## Data, selection and controls

- **STIX alone for the core measurement**, from SOAR L1 pixel data (8 pixels) and spectrograms; thermal and non-thermal on one time base.
  - Context: AIA (Earth view) for geometry; ASO-S/HXI for stereoscopic occultation cases if accessible; CME catalogues for the eruption flag.
  - Environment: `requirements-stix.txt` (Python ≥ 3.10); the base `.venv` (3.9) is for models and tests.
- **Selection** (pre-registered before measuring the sample):
  - net 25–50 keV peak ≥ 5×10³ counts/4 s (167 flares, 2021–2026);
  - ≥ 2 pulses after the first;
  - constant attenuator state in each window;
  - loop-top/footpoint separation ≥ 2 resolution elements;
  - at least one informative pulse, defined from thermal and integrated quantities only.
- **Controls:**
  - synthetic end-to-end visibilities with known φ;
  - positive controls (coronal thick-target or evaporation-sequence flares) chosen with the supervisor;
  - negative control: the first pulse of each flare.
- **The X5.0 of 2023-12-31 is a pilot only.** Its loop-top/footpoint separation is about 8″. First-look scripts and caveats are in `scripts/x5_first_look/`.

## Gates and kill criteria

| Gate | Week | Condition |
|---|---|---|
| G0 | 1 | ADS novelty check passed; pre-registration agreed |
| G1 | 3 | Synthetic coverage ≥ 95 %; R_min ≤ R_pred/2 for dense pulses on real visibilities; positive control within ×3 |
| G2 | 8 | ≥ 15 flares with informative pulses |
| G3 | 12 | Conclusions stable across algorithms and bands |

**The main risk is the STIX imaging dynamic range.** A bound φ ≤ 0.3 needs loop-top limits of a few percent of the footpoints. If G1 fails, the fallbacks are:
- stereoscopic occultation case studies;
- a note on the X5.0 third source if robust;
- the archived v3 with per-footpoint control.

## Cluster use

- **Jobs:** one flare per job (Slurm array), pinned environments, fixed seeds and a manifest per flare.
- **Expected budget:** order 10³ CPU-hours and 5–15 GB of raw data. Measure it in the pilot before budgeting.
- **No simulation campaign by default:** the RHD codes (HYDRAD, FP, RADYN) are not needed for the core result. Do not launch simulation campaigns unless a concrete check requires one.
- **Record failures:** keep failed fits and images in the record.

## Deliverables

1. The paper (no venue promised).
2. A public pulse-by-pulse catalogue with a DOI.
3. The pipeline code and the pre-registration.

Installing tools or making demonstration figures is not completing an objective. Always distinguish pilot results, sample results and predictions. This skill does not authorize sending e-mails, publishing results or using an unagreed cluster allocation.

## Prior work to cite and position against

- **Qualitative re-use in single flares:** Liu et al. 2006; Ning & Cao 2010.
- **Physics:** Veronig & Brown 2004 (coronal thick target); Fleishman et al. 2016; Dennis et al. 2018.
- **Trapping alternative:** Simões & Kontar 2013.
- **STIX methods and sources:** Volpara et al. 2024; Mikuła et al. 2026; Krucker & Masuda 2026; Mrozek et al. 2026.
- **Pilot geometry:** Ryan et al. 2024.
- **Model assumptions:** Reep et al. 2016; Rubio da Costa et al. 2016; Kennedy et al. 2015.

Details and ADS queries: `docs/03_novelty_and_prior_work.md`, Section 10. The contribution is the quantitative tracer test with a conservative bound and a sample, not the use of STIX or of loop-top sources as such.

## Operating context when resuming

- **Read first:** the current files and `docs/00`, Section 13 (status), and verify installed capabilities.
- **At this version:** the tracer physics is implemented and tested; the X5.0 first look exists; no onset thermal fits, forward-fit imaging, injection–recovery or sample yet.
- **Scope of each request:** when the user asks only for an explanation, review or edit, do that; do not launch the campaign.
