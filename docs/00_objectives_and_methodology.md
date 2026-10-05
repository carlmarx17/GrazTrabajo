# Atmospheric Memory under Repeated Electron-Beam Heating

## 0. Project definition

**Author:** Carlos Alberto Martínez Sibaja

**Version:** 5.1, 2026-10-05. Version 5 narrowed to its core after an internal critical review.

**Working subtitle:** When does the independent-pulse approximation fail?

**Main question:** When does treating each electron pulse as if it struck the initial, relaxed atmosphere misrepresent the response to a later pulse by more than the beam, numerical and observational uncertainties of a chosen diagnostic? This treatment is called here the *independent-pulse approximation*.

**Core objective (committed):** For two identical pulses in one loop and one primary diagnostic:

- measure the history contrast M_D with paired simulation branches, as a function of the waiting time τ and of the beam energy flux;
- explain it through the atmospheric state left by the first pulse;
- state the range of τ in which the approximation fails or is adequate.

**Why it matters:** multithread and observation-driven flare models usually heat each strand once, from a relaxed state. If a strand is struck again within the waiting times where the approximation fails, those models misstate its response. Otherwise the approximation is justified in the explored domain. Either answer can be reported.

**Outside the core:** the following are candidate extensions, to be discussed with the supervisor (Section 8):

- proving that observed pulses re-use the same loop;
- reproducing a published flare simulation;
- a third pulse;
- a full statistical calibration of observational distinguishability;
- a flare catalogue.

Archived designs: [v4 loop re-use](archive/00_objectives_v4_loop_reuse.md), [v3 spectral memory](archive/00_objectives_v3_spectral_memory.md), [v2 inference bias](archive/00_objectives_v2_inference_bias.md).

## 1. Terms

- **Independent-pulse approximation:** the response to a pulse is computed on the initial atmosphere and added to whatever earlier pulses left behind. A multithread model that places each pulse in a fresh strand makes the same assumption whenever the strand is in fact struck again.
- **Waiting time τ:** time from the end of pulse 1 to the onset of the test pulse b.
- **Diagnostic D:** one quantity computed identically in every run, for example an emission measure, a line intensity or a Doppler centroid.
- **History contrast M_D(τ, t′):** defined in Section 3.1; t′ is the time since the onset of b.
- **Same-loop reheating** is the modelling scenario of the core, not a claim about any observed flare.
- **FP and RHD:** Fokker–Planck (FP) transport computes electron propagation and energy deposition in a given atmosphere. Radiation hydrodynamics (RHD) evolves the atmosphere along a prescribed magnetic field. A steady FP solve at every RHD update is a quasi-static coupling. Neither is full MHD.

## 2. Essential precedents

| Work | What it established | What remains for this project |
|---|---|---|
| [Kennedy et al. 2015](https://arxiv.org/abs/1504.07541) | Observed RHESSI beam evolution drives RADYN; stopping depths change as the atmosphere evolves | History is retained implicitly; its effect is not isolated with a counterfactual |
| [Polito et al. 2018](https://arxiv.org/abs/1804.05970) | RADYN nanoflare strands: the initial loop temperature and density and the cutoff energy Ec change where the beam deposits energy | Preheating enters as an initial condition, not as the history of an earlier pulse |
| [Cho, Testa, De Pontieu & Polito 2023](https://arxiv.org/abs/2211.06832) | A RADYN model with 20 s of heating, a 60 s pause and 20 s more (F = 6×10⁸ erg cm⁻² s⁻¹, Ec = 10 keV, δ = 7), compared statistically with IRIS footpoint brightenings | Two separated heating episodes are not new. A controlled comparison of the second response with a fresh-atmosphere response was not found; the full text is still to be read |
| [Kerr, Polito, Xu & Allred 2024](https://arxiv.org/abs/2405.02799) | 100 s of weak electron heating (5×10⁸) before flare fluxes (10¹⁰–10¹¹) changes the Mg II ribbon-front response; the front lifetime is proposed as a measure of the weak-heating duration | Weak → strong preconditioning, with an observable, is done. Strong → strong pulses with a waiting time and paired controls remain |
| [Litwicka, Heinzel & Kašparová 2025](https://doi.org/10.3847/1538-4357/adc393) | FLARIX: continuous heating versus four consecutive filamentary pulses, on VAL-C and preheated VAL-C; Hα and Mg II change | Same-strand temporal memory must be separated from filamentation, area and flux changes |
| [Kašparová et al. 2009](https://arxiv.org/abs/0904.2084) | Sub-second electron-beam pulses and time-dependent hydrogen lines | Pulse trains on sub-second time scales, not waiting times of tens of seconds |
| [Rubio da Costa et al. 2016](https://arxiv.org/abs/1603.04951); [Reep et al. 2018](https://arxiv.org/abs/1802.08884) | Observation-driven multithread modelling; duration of heating on unresolved loops | Users of the approximation under test |
| Allred et al. [2020](https://arxiv.org/abs/2008.10671) (and 2015); [Carlsson et al. 2023](https://arxiv.org/abs/2304.02618); [Collier et al. 2024](https://arxiv.org/abs/2411.09319) | FP transport in RADYN; the public F-CHROMA grid (20 s triangular beam plus 30 s of evolution, closed boundaries, 10 Mm loop); STIX-driven RADYN modelling of a first burst | Tools, data and an optional benchmark, not competitors |

**Provisional gap.** Two separated heating episodes have been simulated (Cho et al. 2023), and weak earlier heating is known to change a later strong response (Kerr et al. 2024). This focused review did not find:

- a paired-branch measurement, at flare fluxes, of the error of the independent-pulse approximation;
- as a function of τ;
- judged against the uncertainties of a specified diagnostic.

That is an incremental contribution. It stays provisional until the targeted search of Phase 0 (Section 6). The full comparison is in [the prior-work review](03_novelty_and_prior_work.md), Section 11.

## 3. Core experiment

### 3.1 Four paired branches

All runs start from the same initial atmosphere. In the core, pulse 1 and the test pulse b are identical.

```text
A0  no beam (background heating only)      B0  test pulse b on the relaxed atmosphere
A1  pulse 1, no test pulse                 B1  pulse 1, waiting time tau, then b

t'               = time since the onset of b (t_k = end of pulse 1 + tau in A1 and B1)
Delta D_0(t')    = D[B0] - D[A0]       at equal t'
Delta D_1(t')    = D[B1] - D[A1]       at equal t'
M_D(tau, t')     = Delta D_1(t') - Delta D_0(t')
```

M_D is the error, for D, of adding the response of a relaxed atmosphere onto the state left by pulse 1. That is the independent-pulse approximation for a re-struck loop. M_D is a causal contrast inside the model and does not assume that emission adds linearly. It is defined per unit area of one loop. Allocating area and power among threads (inputs E3a/E3b) is an extension.

Rules:

- **Same setup and grid.** Use the same solver, configuration and output cadence in all branches. Compare at matched t′, on a common time grid. Compare profiles on a common mass or column coordinate.
- **Identical history before t_k.** A1 and B1 must coincide before t_k. Check it (test T3). With RADYN, start B1 from A1 by restart, because the tensioned spline of `ftab.dat` can couple table rows on both sides of t_k.
- **Profile-derived quantities** such as Doppler centroids and widths: synthesize the profile in each branch, measure D, then form the contrast.

### 3.2 Minimal parameters

- **Pilot pulse:** an identical boxcar for pulse 1 and b, in the stable HYDRAD domain documented in [docs/06](06_usefulness_tests.md): F ≈ 1.3×10¹⁰ erg cm⁻² s⁻¹ (δ = 5, Ec = 20 keV), 30 s pulses, 26 Mm loop. In that case pulse 1 raised the coronal column to about 65 % of the 20 keV stopping column, the largest growth among the stable runs.
- **Waiting times:** start with τ = 10, 30, 60 and 120 s. Extend until the relaxation criterion of Section 3.4 is met.
- **Flux:** add 2–3 flux levels after the pilot, only where all four branches run cleanly and converge.
- **Diagnostic:** choose one before the runs, according to the solver route (Section 4).
  - With HYDRAD: coronal proxies, namely the emission measure and EM-weighted temperature of the T > 1 MK plasma, the apex density and the coronal column.
  - With RADYN: one chromospheric or transition-region line, such as Mg II k, Si IV or Hα, chosen for data relevance and for the synthesis the solver supports.

### 3.3 Mechanism

At t_k, record the coronal column, the transition-region position and column mass, the temperature and ionization profiles, and the flows. Then compare B1 with B0:

- the deposition profile of b, on a column coordinate;
- the energy that reaches the chromosphere;
- the evaporation and condensation flows.

The mechanism must explain M_D. Different peak times are not a simultaneous difference.

### 3.4 Relaxation, judged independently of M

Pulse 1 counts as relaxed at t_k when the state of A1 matches A0 at the same solver time, within tolerances declared before the runs. The state variables are:

- the coronal column;
- apex density and temperature;
- the column mass above the transition region;
- atomic populations, where available.

This avoids inferring relaxation from M_D → 0, which is what the experiment measures. The pilot script declares 5 % provisional tolerances.

### 3.5 Decision rule, fixed before computing M

```text
the approximation fails for D where   |M_D| > k * sigma_tot
sigma_tot^2 = sigma_num^2 + sigma_beam^2 + sigma_obs^2      (in the units of D)
```

- **σ_num:** difference between runs at two spatial or temporal resolutions, together with the A1/B1 pre-test identity check.
- **σ_beam:** spread of ΔD₀ when b varies within typical STIX fit uncertainties of Ṅ, Ec and δ (a few runs).
- **σ_obs:** noise and calibration of the instrument that would measure D.
- **k:** 3 by default; change it only with a recorded reason.

Record the values in the run manifest (`--sigma` in the pilot script) before computing any contrast. Nothing is divided by ΔD₀, which can be close to zero.

τ* is the shortest sampled waiting time from which |M_D| ≤ k σ_tot at every longer sampled τ. It is a property of the sampled grid.

### 3.6 Reportable outcomes

1. The approximation fails for τ < τ*(F).
2. M is appreciable in state variables but below σ_tot in D: this diagnostic cannot see it.
3. M is below σ_tot everywhere in the explored domain: the approximation is adequate there; report the domain.

A crashed or unconverged run is not a physical result. The analysis code rejects NaN contrasts.

## 4. Solver routes

| Route | Use | Required before production |
|---|---|---|
| **HYDRAD (available now)** | Pilot and coronal/transition-region proxies. Analytic collisional beam heating; optically thin power-law losses as shipped | Stable four-branch runs in the adopted domain; σ_num from a second resolution. It cannot support chromospheric-line claims ([HYDRAD notes](01_hydrad_code.md)) |
| **RADYN with FP (preferred for chromospheric lines)** | F-CHROMA distribution with FP (Allred et al. 2015 version), restart branching, NLTE radiative transfer | Build on the cluster (Fortran, NASA CDF); reproduce one F-CHROMA model; verify that restart preserves atomic populations; measure wall time; confirm the licence and permission with M. Carlsson ([RADYN notes](04_radyn_access.md)) |
| **Collaborator runs** | RADYN or FLARIX run by a group where the solver already works | To be discussed (Section 8, E9) |
| **Standalone FP on snapshots** | Transport sensitivity only | Build and bundled examples ([FP notes](05_fp_solver_verification.md)); not a substitute for coupled FP–RHD |

In every branch, account for injected versus deposited energy. Do not add FP heating on top of the analytic heating of the same beam. For RADYN, compare the energy encoded in `ftab.dat` with the beam flux that RADYN writes.

## 5. Ready-to-test components

| ID | Test | What it shows | Status and command |
|---|---|---|---|
| T1 | Paired-branch inputs | A0, B0, A1 and B1 beam tables per τ; identical rows before t_k; equal test-pulse energy | Implemented and tested (`build_paired_branches` in `src/experiments.py`). `.venv/bin/python src/experiments.py` writes `results/paired_branches/` |
| T2 | Contrast and decision code | M_D on a common t′ grid, σ_tot, the k σ rule, τ*, relaxation check; NaN rejected | Implemented and tested (`src/memory_contrast.py`, `tests/test_memory_contrast.py`) |
| T3 | HYDRAD pilot | Four branches per τ; pre-test identity; relaxation at t_k; M_D for coronal proxies | `scripts/build_hydrad_scratch.sh <scratch dir>`, then `.venv/bin/python scripts/hydrad_paired_branches.py <scratch dir> [--sigma sigma.json]`. Status: see Section 7 |
| T4 | Numerical error | σ_num from a second resolution | Configure after T3 |
| T5 | F-CHROMA reading | Read public RADYN outputs; compare the end state (t = 50 s) with the initial one; deposition of b on both | Needs a download of a few models; whether radynpy reads the CDF files without the NASA library is to be checked. Covers τ ≤ 30 s only, with closed boundaries |
| T6 | RADYN build and branching | One F-CHROMA model reproduced; restart preserves populations; wall time | Needs the cluster toolchain and licence confirmation |
| T7 | Diagnostic synthesis | D from solver output for the chosen diagnostic | After the route is chosen |

## 6. Work plan

The phases have indicative durations and review points; there is no fixed deadline. At each review point, choose among the listed options and record the decision.

| Phase | Content | Indicative length |
|---|---|---|
| 0. Essentials | T1–T3 pilot; targeted ADS search on the precedents of Section 2; choose the diagnostic and the solver route; start T5/T6 in parallel | 2–4 weeks |
| **Review R1** | Do the four branches run cleanly, with identical pre-test states and a contrast above σ_num for at least one proxy? Is a RADYN route within reach? | — |
| 1. Core map | τ grid × 2–3 flux levels; σ_num and σ_beam; mechanism | 1–2 months |
| **Review R2** | Is M understood and robust to resolution? Add a chromospheric diagnostic or any extension? | — |
| 2. Write-up | Paper on when the independent-pulse approximation fails; reproducible configuration | ~1 month |

Options at R1:

- (a) continue with HYDRAD and coronal proxies;
- (b) move to RADYN for a chromospheric diagnostic;
- (c) ask a group with a working solver for runs;
- (d) if M stays below σ_num throughout the stable domain, extend flux or duration only where the solver is stable, or report the bound in a short note.

The core is expected to take roughly 3–6 months, depending on the route. Extensions add time and are agreed with the supervisor.

## 7. Implementation status

| Asset | Role |
|---|---|
| `src/beam_tables.py` | Core: pulse, flux and energy encoding for HYDRAD tables |
| `src/experiments.py` | Core: paired branches (T1). The E1–E5 matrix is kept for extensions (E3a/E3b independent threads, E4 continuous heating) |
| `src/memory_contrast.py` | Core: contrast and decision rule (T2) |
| `scripts/build_hydrad_scratch.sh`, `scripts/hydrad_paired_branches.py` | Core: HYDRAD pilot (T3). Build verified on 2026-10-05. Smoke test at τ = 30 s: A0, B0 and A1 completed; in B1 the adaptive mesh grew from ~630 to ~28 000 cells once the test pulse started, slowing the run to ~30 s of wall time per model second. Run cost of B1 is the first thing to resolve at R1 (refinement settings, or a coarser grid for the pilot) |
| `src/radyn_ftab.py` | RADYN route: beam tables. Energy checked under log-linear interpolation only |
| `src/fp_atmosphere.py` | Extension: FP atmosphere file I/O |
| `src/toy_bias.py` | Extension E2: STIX-conditioned inference |
| `src/tracer.py` | Archived v4 tracer; optional |
| STIX search scripts and the X5.0 first look | Extensions E1 and E8 |

The Python tests verify these utilities. They do not validate a production solver, a published benchmark or a detected memory signature.

## 8. Extensions to discuss with the supervisor (not committed)

| ID | Extension | Why it may be worth it | Cost and risk |
|---|---|---|---|
| E1 | **STIX observational part:** pulse-resolved beam parameters with area from imaging; footpoints struck again within resolution; waiting times. Start with the X5.0 of 2023-12-31, then 10–20 multipulse flares | Sets the (F, τ) domain of the core from data; publishable on its own; within the supervisor's field | Coincident footpoints are not proof of the same strand. X5.0 imaging is CLEAN-only so far. Precedents: [Collier et al. 2024a](https://arxiv.org/abs/2402.10546) (X1.3, pulsations at several ribbon sites), [HXI+STIX triangulation of the X5.0](https://pmc.ncbi.nlm.nih.gov/articles/PMC11339132/), [Aditya-L1/SUIT X5.0](https://arxiv.org/abs/2504.04793) |
| E2 | **STIX-conditioned inference:** which combinations of beam and history fit the same STIX data (fixed HXR, not fixed beam), and whether another diagnostic separates them | Connects the core with what STIX actually measures (target ionization, NUI) | Needs photon synthesis from transport; `src/toy_bias.py` is only a toy |
| E3 | **Benchmark reproduction** of a published STIX- or RHESSI-driven case (Collier et al. 2024; Kennedy et al. 2015); if done, compare against a *second* pulse | Credibility of the production route | Input availability; months of work; a first burst alone says nothing about history |
| E4 | **Full distinguishability calibration:** synthetic recovery, false-positive rates, confusion matrices | Turns M into an observational detection statement | Of order 10²–10³ production runs |
| E5 | **Third pulse**, with a control that keeps pulses 1 and 2 and omits only the third | Accumulation or saturation | The current E5 input keeps only pulse 1 and is not that control |
| E6 | **Independent threads** with area and power bookkeeping (E3a/E3b) | Re-struck loop versus new thread at equal total power | Area is not constrained by HXR alone |
| E7 | **FP transport sensitivity:** standalone FP on snapshots; FP 2015 versus 2020 | Warm-target and return-current treatment | Build effort; a snapshot is not feedback |
| E8 | **Third 25–50 keV source of the X5.0** (pulses 4–5) | Possibly a new observational finding | Needs validated imaging with uncertainties first; possible tension with Ryan et al. 2024 |
| E9 | **Collaboration** with a group running RADYN or FLARIX | Fastest route to chromospheric diagnostics | Agree contributions and authorship early |
| E10 | **v4 loop re-use tracer** | Archived idea | Geometry and path assumptions limit it ([archive](archive/00_objectives_v4_loop_reuse.md)) |

## 9. Reproducibility

For every run, record:

- configuration, initial state, beam tables and code revisions;
- output cadence, σ values and tolerances, written down before the contrasts;
- wall time, storage and failed runs. Failed runs stay in the record.

Data and generated results are git-ignored. Cite the upstream solvers and data actually used, within their licence terms.
