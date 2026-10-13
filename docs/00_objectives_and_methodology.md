# Atmospheric Memory under Repeated Electron-Beam Heating

## 0. Project definition

**Author:** Carlos Alberto Martínez Sibaja

**Version:** 5.1, 2026-10-05. Version 5 narrowed to its core after an internal critical review.

**Working subtitle:** When does the independent-pulse approximation fail?

**Main question:** When does treating each electron pulse as if it struck the initial, relaxed atmosphere misrepresent the response to a later pulse by more than the beam, numerical and observational uncertainties of a chosen diagnostic? This treatment is called here the *independent-pulse approximation*.

**Core objective (committed; reordered 2026-10-13).** For two identical pulses in one loop and one primary diagnostic, in this order of priority:

- **O3 (primary):** state the range of τ in which the approximation is **adequate**, and the range in which it fails. τ*(F) is the deliverable a multithread modeller can act on, and the only one of the three that no prior study provides;
- **O1 (the means):** measure the history contrast M_D with four matched paired branches, as a function of the waiting time τ and of the beam energy flux;
- **O2 (evidence):** explain it through the atmospheric state left by the first pulse, which shows M_D is causal rather than numerical. The mechanism itself is prior work (Section 2).

The reordering follows the literature verification of 2026-10-13: the effect, its mechanism and the waiting-time dependence are all published, so the boundary is the contribution. See [the prior-work review](03_novelty_and_prior_work.md), Sections 11.11 and 11.12.

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
| [Bakke et al. 2022](https://arxiv.org/abs/2201.11961) | RADYN nanoflare loops at 1 and 3 MK. In the denser loop the electrons "deposit more of their energy in the corona" and the response is slower; the 3 MK loop "represents a previously heated strand". Read 2026-10-13 | **The mechanism of this core is already published as an initial-condition effect.** What remains is history delivered by a simulated earlier pulse, a waiting time, paired controls and a decision rule |
| [Reep, Warren, Crump & Simões 2016](https://arxiv.org/abs/1607.06684) | **§3.1 and Fig. 2 place seven beam bursts on one HYDRAD loop beside seven strands heated once each**, and show the synthetic Si IV response differs because evaporation has filled the corona ("later heating bursts cannot cause a strong velocity flow … due to the increased inertia"). Ec ≈ 11 keV, δ ≈ 6, peak 5×10⁹. Verified 2026-10-13 | **The qualitative contrast and its mechanism are theirs.** What remains: their comparison is 1 loop vs 7 strands, so history is confounded with area and thread count; there is no no-beam baseline and no isolated test pulse, no τ or F scan, no error budget, and sub-flare flux. Also the cheapest available benchmark for this pipeline |
| [Emslie, Li & Mariska 1992](https://ui.adsabs.harvard.edu/abs/1992ApJ...399..714E) | Electron-heated flare hydrodynamics comparing preheated with non-preheated atmospheres (initial chromospheric pressure), Ca XIX: the preheated atmosphere "responds slowly". Abstract only | **Preheated versus relaxed dates to 1992.** Preheating as an initial condition, not as a simulated pulse's end state. Obtain the full text before the introduction |
| [Lörinčík, Polito, Kerr, Hayes & Russell 2025](https://arxiv.org/abs/2504.10619) | High-cadence IRIS Si IV / C II / Mg II timing versus RADYN grids; §6.3: "all models considered in our study for simplicity assume a single instance of constant heating" and whether "repeated heating of a single loop" reproduces the quasi-periodic peaks "remains to be simulated in the future" | **The published opening this project answers** — but their question is multi-line chromospheric timing, which HYDRAD cannot address. An argument for the RADYN route at R2 |
| [Barnes, Bradshaw & Viall 2019](https://arxiv.org/abs/1906.03350); Cargill 2014 | Repeated same-strand nanoflares with heating frequency ε = ⟨t_wait⟩/τ_cool; a high-frequency strand "is not allowed to fully cool before being heated again". Verified 2026-10-13 | **Same-strand waiting-time dependence is established; do not claim it.** But ad-hoc volumetric heating, no beam, two-fluid EBTEL integrated over the corona, no modelled evaporation, and t_wait coupled to event energy. Report τ* in units of τ_cool |
| [Cho, Testa, De Pontieu & Polito 2023](https://arxiv.org/abs/2211.06832) | A RADYN model with 20 s of heating, a 60 s pause and 20 s more (F = 6×10⁸ erg cm⁻² s⁻¹, Ec = 10 keV, δ = 7, 15 Mm loop), compared statistically with IRIS footpoint brightenings | Two separated heating episodes are not new. **Full text read 2026-10-13:** that model (E6) is one entry in a 13-model grid, with no fresh-atmosphere control and no analysis of what the first episode left behind; the paper does not discuss preheating, memory or waiting times |
| [Kerr, Polito, Xu & Allred 2024](https://arxiv.org/abs/2405.02799) | 100 s of weak electron heating (5×10⁸) before flare fluxes (10¹⁰–10¹¹) changes the Mg II ribbon-front response; the front lifetime is proposed as a measure of the weak-heating duration | Weak → strong preconditioning, with an observable, is done. **Full text read 2026-10-13:** no pause between the weak and the strong phase, no strong-only control, no waiting-time scan and no comparison against uncertainties; the scan is over the weak-phase duration at matched total energy. Strong → strong pulses separated by τ, with paired controls, remain |
| [Litwicka, Heinzel & Kašparová 2025](https://doi.org/10.3847/1538-4357/adc393) | FLARIX: continuous heating versus four consecutive filamentary pulses, on VAL-C and preheated VAL-C; Hα and Mg II change | Same-strand temporal memory must be separated from filamentation, area and flux changes |
| [Kašparová et al. 2009](https://arxiv.org/abs/0904.2084) | Sub-second electron-beam pulses and time-dependent hydrogen lines | Pulse trains on sub-second time scales, not waiting times of tens of seconds |
| [Rubio da Costa et al. 2016](https://arxiv.org/abs/1603.04951); [Reep et al. 2018](https://arxiv.org/abs/1802.08884) | Observation-driven multithread modelling; duration of heating on unresolved loops | Users of the approximation under test |
| Allred et al. [2020](https://arxiv.org/abs/2008.10671) (and 2015); [Carlsson et al. 2023](https://arxiv.org/abs/2304.02618); [Collier et al. 2024](https://arxiv.org/abs/2411.09319) | FP transport in RADYN; the public F-CHROMA grid (20 s triangular beam plus 30 s of evolution, closed boundaries, 10 Mm loop); STIX-driven RADYN modelling of a first burst | Tools, data and an optional benchmark, not competitors |

**Gap, after three targeted passes and the closest full texts (2026-10-13).** Repeated same-strand heating with a waiting time normalised by the cooling time is standard in nanoflare modelling (Cargill 2014; Barnes et al. 2019); **Reep et al. 2016 placed seven beam bursts on one HYDRAD loop beside seven freshly heated strands and showed the synthetic Si IV response differs, with the mechanism**; two separated beam episodes have been simulated at nanoflare fluxes (Cho et al. 2023); weak earlier heating is known to change a later strong response (Kerr et al. 2024); and the *mechanism* — a denser loop stops more of the beam in the corona — is published as an initial-condition effect going back to Emslie, Li & Mariska (1992), and again in Polito et al. 2018 and Bakke et al. 2022. None of them contains:

- a paired-branch measurement, at flare fluxes, of the error of the independent-pulse approximation;
- as a function of τ;
- judged against the uncertainties of a specified diagnostic.

**What this project may not claim as its own:** the mechanism, repeated same-strand heating, waiting-time dependence, repeated beam bursts in one loop, or the qualitative finding that a re-struck loop responds differently. **What remains, and it is the whole contribution:** *how large the error is and where it matters* — four matched branches holding geometry, area and test pulse fixed so history is the only variable, scanned in τ and F at flare fluxes, with a decision rule fixed in advance. This makes **O3, the range where the approximation is adequate, the most valuable objective**, not a fallback: it is the only part no prior study provides. That is an incremental contribution. It stays provisional for the remaining items of Section 11.6 of [the prior-work review](03_novelty_and_prior_work.md): the full text of Litwicka et al. 2025, still inaccessible, and the exhaustive ADS sweep.

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
  - **With HYDRAD, the primary candidate is Si IV 1402.77 Å — intensity and Doppler shift.** It is a transition-region line, inside what the shipped solver supports, and [Reep et al. 2016](https://arxiv.org/abs/1607.06684) already synthesized it from HYDRAD under beam heating, which both proves it is computable here and makes their Figure 2 a reproducible benchmark. It is also the currency the multithread literature actually fits (Rubio da Costa et al. 2016; Reep et al. 2018, 2020) and the line whose repeated-heating timing [Lörinčík et al. 2025](https://arxiv.org/abs/2504.10619) leave open. **σ_obs is then nameable: IRIS**, with published noise and calibration. *Caveat to declare:* Si IV formation is sensitive to non-equilibrium ionization (Nóbrega-Siverio et al. 2018) and HYDRAD assumes ionization equilibrium with n_e = n_H; Reep et al. 2016 carried the same limitation. State it, bound it, do not hide it.
  - Fallback and cross-check with HYDRAD: coronal proxies, namely the emission measure and EM-weighted temperature of the T > 1 MK plasma. These are the stable pair measured in the pilot, but no target community fits them; the apex point diagnostics and the coronal column failed robustness ([docs/07](07_core_pilot_hydrad.md), Section 7.3).
  - With RADYN: a chromospheric line such as Mg II k or Hα, which needs NLTE transfer and therefore the RADYN gate or a collaborator.

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
| **HYDRAD (available now)** | Pilot and coronal/transition-region proxies. Analytic collisional beam heating; optically thin power-law losses as shipped | The pilot ([docs/07](07_core_pilot_hydrad.md)) needs `SAFETY_CONDUCTION = 0.2`. With the shipped 5 Mm isothermal chromosphere the loop loses mass from ~50 s after a 30 s pulse at 1.3×10¹⁰, so only τ ≲ 30 s and the impulsive window are usable. A deeper or optically thick chromosphere is needed for the waiting-time scan. It cannot support chromospheric-line claims ([HYDRAD notes](01_hydrad_code.md)) |
| **RADYN with FP (preferred for chromospheric lines)** | F-CHROMA distribution with FP (Allred et al. 2015 version), restart branching, NLTE radiative transfer | Build on the cluster (Fortran, NASA CDF); reproduce one F-CHROMA model; verify that restart preserves atomic populations; measure wall time; confirm the licence and permission with M. Carlsson ([RADYN notes](04_radyn_access.md)) |
| **Collaborator runs** | RADYN or FLARIX run by a group where the solver already works | To be discussed (Section 8, E9) |
| **Standalone FP on snapshots** | Transport sensitivity only | Build and bundled examples ([FP notes](05_fp_solver_verification.md)); not a substitute for coupled FP–RHD |

In every branch, account for injected versus deposited energy. Do not add FP heating on top of the analytic heating of the same beam. For RADYN, compare the energy encoded in `ftab.dat` with the beam flux that RADYN writes.

## 5. Ready-to-test components

| ID | Test | What it shows | Status and command |
|---|---|---|---|
| T1 | Paired-branch inputs | A0, B0, A1 and B1 beam tables per τ; identical rows before t_k; equal test-pulse energy | Implemented and tested (`build_paired_branches` in `src/experiments.py`). `.venv/bin/python src/experiments.py` writes `results/paired_branches/` |
| T2 | Contrast and decision code | M_D on a common t′ grid, σ_tot, the k σ rule, τ*, relaxation check; NaN rejected | Implemented and tested (`src/memory_contrast.py`, `tests/test_memory_contrast.py`) |
| T3 | HYDRAD pilot | Four branches per τ; pre-test identity; relaxation at t_k; M_D for coronal proxies | `scripts/build_hydrad_scratch.sh <scratch dir>`, then `.venv/bin/python scripts/hydrad_paired_branches.py <scratch dir> [--sigma sigma.json]`. Run on 2026-10-05 for 26 and 60 Mm loops; results in [docs/07](07_core_pilot_hydrad.md) |
| T4 | Numerical error | σ_num from a second time step or resolution, plus the restart error | `scripts/hydrad_numerical_error.py`; restart error measured, time-step variant in [docs/07](07_core_pilot_hydrad.md) |
| T5 | F-CHROMA reading | Read public RADYN outputs; compare the end state (t = 50 s) with the initial one; deposition of b on both | Needs a download of a few models; whether radynpy reads the CDF files without the NASA library is to be checked. Covers τ ≤ 30 s only, with closed boundaries |
| T6 | RADYN build and branching | One F-CHROMA model reproduced; restart preserves populations; wall time | Needs the cluster toolchain and licence confirmation |
| T7 | Diagnostic synthesis | D from solver output for the chosen diagnostic | After the route is chosen |

## 6. Work plan

The phases have indicative durations and review points; there is no fixed deadline. At each review point, choose among the listed options and record the decision.

| Phase | Content | Indicative length |
|---|---|---|
| 0. Essentials | T1–T3 pilot; targeted ADS search on the precedents of Section 2; choose the diagnostic and the solver route; start T5/T6 in parallel | 2–4 weeks |
| **Review R1** | Do the four branches run cleanly, with identical pre-test states and a contrast above σ_num for at least one proxy? Is a RADYN route within reach? | — |
| 1a. Gates | Spatial σ_num; σ_obs from the named instrument, pre-registered; a τ grid that reaches relaxation; Si IV synthesis plus the Reep et al. 2016 benchmark; the beam-degeneracy limit | 6 weeks |
| 1b. Core map | τ grid × 2–3 flux levels; mechanism at t_k | 4 weeks |
| **Review R2** | Is M understood and robust to resolution? Add a chromospheric diagnostic or any extension? | — |
| 2. Write-up | Paper on when the independent-pulse approximation fails; reproducible configuration | ~1 month |

Options at R1:

- (a) continue with HYDRAD and coronal proxies;
- (b) move to RADYN for a chromospheric diagnostic;
- (c) ask a group with a working solver for runs;
- (d) if M stays below σ_num throughout the stable domain, extend flux or duration only where the solver is stable, or report the bound in a short note.

**R1 outcome (2026-10-05).** Option (a): the four branches run cleanly with `SAFETY_CONDUCTION = 0.2` and an 8 Mm chromosphere, and the contrast exceeds σ_num for four coronal proxies, so the core map continues with HYDRAD while the RADYN gate (T5, T6) runs in parallel. The reasoning and the five items Phase 1 must settle first are in [docs/07](07_core_pilot_hydrad.md), Section 7.

The core is expected to take roughly 3–6 months, depending on the route. Extensions add time and are agreed with the supervisor.

## 7. Implementation status

| Asset | Role |
|---|---|
| `src/beam_tables.py` | Core: pulse, flux and energy encoding for HYDRAD tables |
| `src/experiments.py` | Core: paired branches (T1). The E1–E5 matrix is kept for extensions (E3a/E3b independent threads, E4 continuous heating) |
| `src/memory_contrast.py` | Core: contrast and decision rule (T2) |
| `scripts/build_hydrad_scratch.sh`, `scripts/hydrad_paired_branches.py`, `scripts/hydrad_numerical_error.py`, `scripts/hydrad_beam_error.py`, `scripts/pilot_uncertainty.py`, `scripts/plot_paired_branches.py` | Core: HYDRAD pilot (T3, T4). The B1 runaway was a conduction time-step instability, fixed with `SAFETY_CONDUCTION = 0.2`. Branches restart from A1, run in parallel and are masked where the loop mass is not conserved. First contrasts are in the impulsive window at τ = 10–30 s ([docs/07](07_core_pilot_hydrad.md)) |
| `src/radyn_ftab.py` | RADYN route: beam tables. Energy checked under log-linear interpolation only |
| `src/fp_atmosphere.py` | Extension: FP atmosphere file I/O |
| `src/toy_bias.py` | Extension E2: STIX-conditioned inference |
| `src/tracer.py` | Archived v4 tracer; optional |
| STIX search scripts and the X5.0 first look | Extensions E1 and E8 |

The Python tests verify these utilities. They do not validate a production solver, a published benchmark or a detected memory signature.

## 8. Extensions to discuss with the supervisor (not committed)

**Sequencing of the STIX work, decided 2026-10-13.** STIX is already inside the committed core, as the source of σ_beam: the beam variants follow a STIX fit (electron rate ±12 %, cutoff ±4 %, δ ±0.1, after Collier et al. 2024) and run in `scripts/hydrad_beam_error.py`. Beyond that:

- **E1 is modular and belongs after the core.** Pulse-resolved beam parameters and observed waiting times set *which part* of the τ × F map matters. It constrains the domain; it does not change the simulation design, the branches or the decision rule. Nothing in the core has to wait for it, and nothing in it has to be redone if the core moves.
- **E2 is not a bolt-on.** "Same STIX data, different histories" needs photon synthesis from the transport, i.e. RADYN+FP or the standalone FP solver. It is a second machine, not an addition.
- **With Si IV as the primary diagnostic, IRIS becomes the observational partner and STIX the beam-side constraint.** That division is cleaner than before: IRIS fixes σ_obs and therefore the boundary; STIX fixes the input beam and its uncertainty.
- **Collision warning.** STIX + IRIS on a multipulse flare is the Litwicka group's own approach (their 2026 abstract: FLARIX, the X9 of 3 October 2024, STIX + IRIS + CHASE). If E1 is taken up, pick a different event and a different question from theirs, as already noted in [the prior-work review](03_novelty_and_prior_work.md), Section 5.

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
