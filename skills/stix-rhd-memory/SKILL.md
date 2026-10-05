---
name: stix-rhd-memory
description: Guide research design, analysis and writing for the atmospheric-memory project on repeated electron-beam heating, whose core asks when the independent-pulse approximation fails, using paired simulation branches, a fixed decision rule and optional STIX-based extensions.
---

# Atmospheric memory under repeated electron-beam heating (v5.1)

The core question is when treating each electron pulse as if it struck the relaxed atmosphere misrepresents the response to a later pulse by more than the beam, numerical and observational uncertainties of a chosen diagnostic. Everything else is an extension to discuss with the supervisor.

Keep collaborative documentation in English. Do not include the supervisor's name in the public repository.

## Read the current design

The authoritative plan is [docs/00_objectives_and_methodology.md](../../docs/00_objectives_and_methodology.md). Use [docs/03_novelty_and_prior_work.md](../../docs/03_novelty_and_prior_work.md), Section 11, for positioning; earlier sections record historical searches. Archived v2–v4 plans do not override v5.1.

The core is two identical pulses, one loop, one primary diagnostic, waiting time τ as the first control variable and beam flux as the second. Do not widen it (third pulse, benchmark reproduction, observational application, full calibration) without an explicit decision recorded in the plan.

## Preserve the scientific distinctions

- **Four branches** start from the same atmosphere: A0 (no beam), B0 (test pulse b only), A1 (pulse 1 only), B1 (pulse 1, then b after τ). The contrast is M_D = (B1 − A1) − (B0 − A0) at equal time after the onset of b. Keep D in its own units; never divide by B0 − A0.
- **A1 and B1 must be identical before t_k.** With RADYN, branch B1 from A1 by restart; the ftab spline can couple rows across t_k.
- **Relaxation of pulse 1** is judged from state variables of A1 versus A0 at t_k, never from M → 0.
- **The decision rule |M| > k·σ_tot** uses σ_num, σ_beam and σ_obs fixed before computing contrasts. NaN or unconverged runs are failures, not small effects.
- **Same-loop reheating** is the modelling scenario of the core. Footpoint coincidence does not prove the same strand. The core evaluates a modelling approximation; it does not measure a loop re-use fraction.
- **Two experiments must not be mixed:** "same beam, different history" is the physical experiment, and "same STIX data, different history" is the observational one (extension E2). A beam inferred with one transport model is not ground truth.
- **Solver limits:** HYDRAD as shipped (analytic collisional heating, optically thin losses) supports coronal and transition-region proxies, not chromospheric lines. RADYN with FP is the preferred chromospheric route once it is built, an F-CHROMA model is reproduced and restart branching is verified. Post-processing snapshots with FP is not coupled FP–RHD. Do not double-count beam heating.
- **Novelty is incremental.** Cho et al. 2023 already simulated 20 s + 60 s pause + 20 s heating in RADYN at nanoflare fluxes. Kerr et al. 2024 showed that weak preheating changes a later strong response and proposed an observable. The remaining contribution is strong → strong pulses at flare fluxes, a waiting-time scan, paired controls and a decision rule.

## Current assets and limitations

`src/experiments.py` (`build_paired_branches`), `src/memory_contrast.py`, `scripts/build_hydrad_scratch.sh` and `scripts/hydrad_paired_branches.py` implement the core inputs, the analysis and the HYDRAD pilot. Beam tables, RADYN input encoding and FP atmosphere I/O are reusable. The tests do not validate a production solver.

Use [HYDRAD notes](../../docs/01_hydrad_code.md), [RADYN notes](../../docs/04_radyn_access.md) and [FP notes](../../docs/05_fp_solver_verification.md) for technical checks. Existing HYDRAD failures (F ≥ 2.5×10¹⁰, 30 s pulses in 60 Mm loops) concern the tested configurations, not every configuration. The [earlier usefulness tests](../../docs/06_usefulness_tests.md) measured columns and spectral bias, not line responses.

The X5.0 first look is exploratory imaging (CLEAN only); a CLEAN non-detection is not an upper limit. The v4 tracer is optional and archived.

## Progress and deliverables

Follow the phases and review points of the plan (Section 6); there is no fixed deadline, but record the option chosen at each review point. Measure runtime and failure rates before sizing a grid. Keep failed runs in the record. The expected product is one focused paper on when the independent-pulse approximation fails, with reproducible configurations. Documentation work does not imply launching a simulation campaign; follow the user's actual requested scope.
