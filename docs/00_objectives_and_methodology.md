# Do successive hard X-ray pulses re-use flare loops? Evaporated plasma as a tracer of electron paths (v4)

**Author:** Carlos Alberto Martínez Sibaja
**Status:** research plan, version 4 (2026-10-04), to be agreed with the supervisor before the pre-registration (Section 4). It replaces v3, archived in `docs/archive/00_objectives_v3_spectral_memory.md`; Section 14 explains the change. The novelty search for v4 is in `docs/03_novelty_and_prior_work.md`, Section 10; ADS has not been queried yet.

All numbers in this document marked *computed* come from `src/tracer.py` (tested in `tests/test_tracer.py`) or from the STIX catalogue cached by `scripts/stix_event_search.py`. Thresholds marked *proposed* are fixed in the pre-registration.

---

## 0. One-page summary

**Question.** When the second or third hard X-ray (HXR) pulse of a flare arrives, do its electrons travel through the loops that earlier pulses already filled with evaporated plasma (**re-use**), or through new, still empty loops (**new loops**)? What fraction φ of the electrons re-uses the filled loops, and what does it depend on?

**The idea: the memory of the atmosphere is the measuring instrument.**
1. Earlier pulses evaporate chromospheric plasma into the loops they heat. STIX sees it as the thermal loop-top source (6–15 keV), with a measurable emission measure and size.
2. That plasma is dense enough to stop flare electrons in the corona (coronal thick target): a column N stops every electron below E* = √(2KN), about 23 keV for N = 10²⁰ cm⁻² and 40 keV for 3×10²⁰ cm⁻² (*computed*).
3. So if pulse k sends its electrons through the filled loops, the loop top **must** shine in non-thermal HXR. The size of that signal (loop-top/footpoint ratio R, and its fall above E*) follows from the thermal measurements alone, with no free parameter.
4. Comparing the observed R with the predicted one measures φ. Every unknown that could spoil the comparison (filling factor, pitch angle, trapping, residual thermal emission, albedo) makes the derived **upper bound** on φ larger, never smaller, so the bound is robust (Section 3.4).

**Why it matters.** Flare models make opposite assumptions without an observational test:
- Single-loop radiation-hydrodynamic models heat one loop again and again (e.g. Kennedy et al. 2015; the F-CHROMA grid).
- Multithread models assume that every burst lights a new thread (Warren 2006; Reep et al. 2016; Rubio da Costa et al. 2016).

Imaging alone cannot decide, because a new loop next to an old one lies within one resolution element. The tracer decides by physics what the imager cannot resolve. A statistical answer constrains how flare energy release is organized, what HXR pulses and quasi-periodic pulsations represent, and how flare models should be built.

**What is new (to be confirmed in ADS).**
- The qualitative effect, HXR emission moving into the loop as it fills, was reported in single RHESSI flares (Liu et al. 2006; Ning & Cao 2010).
- No quantitative, pulse-by-pulse test of loop re-use was found, nor a conservative bound on φ, nor a statistical sample. STIX makes it possible now: years of data and a large flare catalogue.

**What is used.**
- STIX only for the core measurement: thermal and non-thermal from the same instrument, so one time base and no cross-calibration.
- An analytic thick-target model (already implemented).
- Standard STIX spectroscopy and visibility imaging.
- A computing cluster for the embarrassingly parallel image reconstructions and injection–recovery tests.
- No radiation-hydrodynamic simulation is needed.

**Scale.**
- **Flares:** 167 STIX flares (2021–2026) have a net 25–50 keV peak of ≥ 5×10³ counts per 4 s (*computed*). After the selection of Section 6 an estimated 20–60 flares and 100–300 informative pulses remain.
- **Compute and storage:** order 10³ CPU-hours and 5–15 GB of raw data.
- **People and time:** one doctoral researcher, 20 weeks.

**Product.** One paper (A&A or ApJ), a public pulse-by-pulse catalogue (thermal and non-thermal parameters, loop-top ratios or limits, predicted ratios, bounds on φ) with a DOI, and the pipeline code.

**Timeline.** Twenty weeks, with four decision gates (Section 10). The decisive gate G1 comes at week 3: the synthetic end-to-end test, the X5.0 pilot and the detection limits show whether STIX can reach the required sensitivity.

---

## 1. Scientific context

### 1.1 Two pictures of a multi-pulse flare
- **Same loop, heated repeatedly.** Each pulse deposits energy in a loop already modified by the previous ones. This is what single-loop RHD runs assume when they are driven by a time series of beam parameters (Kennedy et al. 2015).
- **New loops for each pulse.** Reconnection proceeds through the arcade and every burst energizes fresh flux tubes. Multithread models build flares this way (Warren 2006; Reep et al. 2016). Rubio da Costa et al. (2016) start each thread "from the initial atmosphere", by assumption.
- Footpoint motions along and across ribbons (Grigis & Benz 2005; Inglis & Dennis 2012) show that new loops are often involved. But they cannot show whether a given pulse re-uses loops inside the same resolution element.

### 1.2 Evaporation fills the loops, and HXR can follow
- Liu et al. (2006) and Ning & Cao (2010): in single RHESSI flares the HXR sources rise from the footpoints and merge into the loop top as the loop fills. That is what re-use predicts, but it was shown only qualitatively.
- The coronal thick target: dense loops stop electrons in the corona (Veronig & Brown 2004; validated in 3D by Fleishman et al. 2016; reanalysed by Dennis et al. 2018).
- Loop-top electron rates exceed footpoint rates by factors 1.7–8 in some flares, interpreted as trapping (Simões & Kontar 2013). An extra loop-top source is therefore possible and must be allowed for (it only loosens our bound).
- Theory of single elementary events with evaporation: Liu, Han & Fletcher (2010).

### 1.3 The STIX era
- Regularized imaging spectroscopy of electron flux along a loop (Volpara et al. 2024).
- Footpoint heights versus energy and evaporation (Mikuła, Mrozek & Kułaga 2026).
- Faint high-coronal sources, revealed by occultation (Krucker & Masuda 2026; Mrozek et al. 2026).
- Stereoscopy with ASO-S/HXI (Ryan et al. 2024; Matsumoto et al. 2026).
- None of these tests loop re-use pulse by pulse.

### 1.4 The gap
No study uses the evaporated plasma of earlier pulses as a tracer to measure, with a physical prediction and a conservative bound, whether later pulses re-use the same loops, nor does so for a sample of flares.

## 2. Research question and sub-questions

**Main question.** In flares with several HXR pulses, what fraction φ of the electrons of pulse k (k ≥ 2) crosses the loop-top region filled with plasma evaporated by pulses 1 … k−1, and on what does φ depend?

| ID | Sub-question | Observable |
|---|---|---|
| Q1 | Is φ small (new loops) or large (re-use) in bright multi-pulse flares? | Distribution of φ (bound and nominal estimate) over informative pulses |
| Q2 | Does the tracer agree with the imager? Is φ high where footpoints stay put and low where they move? | φ versus footpoint displacement between pulses |
| Q3 | Does re-use depend on the waiting time between pulses relative to the time the plasma takes to cool and drain? | φ versus waiting time and the thermal decay time |
| Q4 | Do confined and eruptive flares differ? | φ by eruption flag |
| Q5 | When re-use is found, does the loop-top non-thermal spectrum show the knee E* predicted from the thermal column? | Measured R(ε) shape versus predicted E* |

## 3. Physical principle: the tracer

### 3.1 From thermal X-rays to a column
At the onset of pulse k, the thermal loop-top source has emission measure EM_LT and occupies a volume no larger than V_max (from its deconvolved size, inflated by its uncertainty). With a filling factor f ≤ 1:

```
n = sqrt(EM_LT / (f V))  >=  n_min = sqrt(EM_LT / V_max)
N_LT >= N_min = n_min * l_min
```

Here l_min is the shortest plausible path of the beam through the source. Half of the smallest source extent is used, which corresponds to injection at the apex. EM_LT is the thermal emission measure attributed to the loop-top aperture by imaging spectroscopy, not the spatially integrated one (attributing hot plasma located elsewhere would overestimate n).

*Computed* examples (source sphere of the FWHM, volume inflated by 50 %, Solar Orbiter at 0.95 AU, l_min = FWHM/2):

| EM_LT [cm⁻³] | FWHM 10″ | FWHM 15″ |
|---|---|---|
| 10⁴⁹ | N_min = 6.8×10¹⁹ cm⁻² | 5.6×10¹⁹ |
| 3×10⁴⁹ | 1.2×10²⁰ | 9.6×10¹⁹ |
| 10⁵⁰ | 2.1×10²⁰ | 1.8×10²⁰ |

### 3.2 Electrons crossing the column
Beamed electrons lose energy by Coulomb collisions, dE/dN = −K/E, with K = 2πe⁴Λ (Λ = 20 in ionized plasma). An electron is stopped in the column if its energy is below the knee

```
E* = sqrt(2 K N)  ~  23 keV (N / 1e20 cm^-2)^(1/2)
```

| N [cm⁻²] | 5×10¹⁹ | 10²⁰ | 2×10²⁰ | 3×10²⁰ | 5×10²⁰ | 10²¹ |
|---|---|---|---|---|---|---|
| E* [keV] (*computed*) | 16 | 23 | 32 | 40 | 51 | 72 |

Bremsstrahlung uses the Haug cross-section. The chromosphere below is neutral, where the photon yield per unit energy lost is up to 2.8 times larger (Kontar, Brown & McArthur 2002). Both are implemented in `src/toy_bias.py` and reused by `src/tracer.py`.

### 3.3 Predicted ratio under full re-use
If every electron of pulse k crosses the filled loop top (φ = 1), the loop-top/footpoint photon ratio in 25–50 keV is (*computed*, Ec = 20 keV, footpoint albedo 0.2, no leg column):

| N [cm⁻²] | δ = 4 | δ = 5 | δ = 6 |
|---|---|---|---|
| 5×10¹⁹ | 0.04 | 0.08 | 0.13 |
| 10²⁰ | 0.07 | 0.15 | 0.26 |
| 2×10²⁰ | 0.12 | 0.29 | 0.55 |
| 3×10²⁰ | 0.17 | 0.43 | 0.88 |
| 5×10²⁰ | 0.26 | 0.72 | 1.61 |
| 10²¹ | 0.45 | 1.43 | 3.91 |

The ratio also has a **spectral shape**. It falls steeply above E*, because electrons above the knee cross the loop top and radiate mostly at the footpoints. *Computed* example (δ = 5, Ec = 20 keV, albedo 0.2):

| Bin [keV] | 20–25 | 25–32 | 32–40 | 40–50 | 50–63 | 63–84 |
|---|---|---|---|---|---|---|
| N = 3×10²⁰, φ = 1 | 0.93 | 0.57 | 0.34 | 0.21 | 0.13 | 0.08 |
| N = 3×10²⁰, φ = 0.3 | 0.09 | 0.07 | 0.06 | 0.04 | 0.03 | 0.02 |
| N = 10²⁰, φ = 1 | 0.30 | 0.19 | 0.11 | 0.07 | 0.05 | 0.03 |

An instrumental amplitude error that does not depend on energy only adds a constant to the measured ratio. The fall across E* survives it. This is the second, calibration-robust handle on φ.

### 3.4 Mixture and the conservative bound on re-use
Let a fraction φ of the electrons cross the loop top along paths of column N_h ≥ N_min and the rest along empty paths. Let I_LT, I_rest and I_0 be the band photons emitted in the loop top, further down (legs and chromosphere), and by the same electrons in a fully neutral target (empty loop). Then, with footpoint albedo a:

```
R_obs (1 + a) = phi I_LT / (phi I_rest + (1 - phi) I_0)
```

Two inequalities give the bound:
- Ionized plasma radiates less per unit energy lost than neutral plasma, so I_rest ≤ I_0 (checked numerically in `tests/test_tracer.py`).
- I_LT grows with the column.

Together they give

```
phi  <=  phi_max = R_obs,max (1 + a_max) * max over (delta, Ec) of [ I_0 / I_LT(N_min) ]
```

`tests/test_tracer.py` checks on 60 random "true" configurations that φ_max never falls below the true φ. That includes filling factors below one, leg columns and albedo.

| Effect | Direction | Treatment |
|---|---|---|
| Filling factor f < 1 | Raises the true column | Use f = 1 (N_min) — conservative |
| Pitch angles (μ < 1) | More coronal stopping | Use beamed electrons — conservative |
| Trapping or an acceleration-region source at the loop top | Raises R_obs | Ignored in the bound — conservative; tested separately by the R(ε) shape |
| Thermal emission left in the loop-top flux | Raises R_obs | Conservative for the bound; must be subtracted before claiming re-use |
| Pre-flare coronal column on empty paths | Raises R_obs | Conservative |
| Albedo | Raises footpoint flux | Use the upper value a_max (heliocentric angle seen from Solar Orbiter) |
| Spectral parameters (δ, Ec) | Change I_0/I_LT | Maximize over the posterior range |
| Warm target | < 1 % at ≥ 25 keV for T ≤ 30 MK | Neglected; to be verified numerically in OE1 |
| **Return current** | **Not covered by the argument** | Bound separately: FP-solver runs for the highest flux densities, or exclusion of pulses above the return-current regime (Alaoui & Holman 2017) |
| Emission-measure attribution | Overestimating EM_LT is not conservative | Use the imaging-derived loop-top share with its lower uncertainty |

### 3.5 What sensitivity the test needs (the main risk)
The loop-top upper limit R_obs,max needed for φ_max ≤ 0.3 is small (*computed*, Ec 15–20 keV, a_max = 0.2):

| N_min [cm⁻²] | δ = 4 | δ = 5 | δ = 6 |
|---|---|---|---|
| 10²⁰ | 0.016 | 0.030 | 0.042 |
| 3×10²⁰ | 0.033 | 0.053 | 0.067 |
| 10²¹ | 0.054 | 0.074 | 0.083 |

These are a few percent of the footpoint flux, at or beyond the dynamic range usually quoted for indirect imaging. Positive detections of re-use (R ≈ R_pred, often 0.2–1) are much easier. Four measures address this:
1. **Use the energy dependence R(ε).** It is calibration-robust (Section 3.3).
2. **Select informative pulses** before measuring: dense, soft-spectrum pulses (N_min ≥ 2×10²⁰ cm⁻², δ ≥ 5), defined only from thermal and spatially integrated quantities.
3. **Use stereoscopic occultation for selected events.** When the footpoints are behind the limb for Solar Orbiter but visible from Earth (ASO-S/HXI), STIX sees the loop top without footpoint contamination.
4. **Report two numbers per pulse:** the conservative φ_max and a nominal φ (best estimates, f = 1), each with its assumptions.

Whether this is enough is decided at gate G1 by measuring R_min on real STIX visibilities.

### 3.6 Physical dimensionality
- **Transport and emission:** 1D along the field line (columns), as in the thick-target model.
- **Measurements:** 2D projected images from one viewpoint.
- **3D:** only for stereoscopic events. No MHD or RHD simulation is part of the core measurement.

## 4. Hypotheses and pre-registered decision rules

| ID | Hypothesis | Prediction | Refuted if |
|---|---|---|---|
| H_new | Later pulses use new loops | Informative pulses give R_obs ≪ R_pred and φ_max well below 1 | R_obs ≈ R_pred with the predicted knee in a substantial fraction of informative pulses |
| H_reuse | Later pulses re-use the filled loops | R_obs ≈ R_pred and the R(ε) knee at E* (from N_min, nominal f = 1) | Non-detection with R_min well below R_pred |
| H_extra | An additional loop-top source (trapping or acceleration region) dominates | R_obs ≫ R_pred, with a smooth R(ε) without the knee | R(ε) follows the column-predicted shape |

The hypotheses can coexist across flares; Q2–Q4 ask when each one holds.

*Proposed* rules, to be fixed in the pre-registration before the full sample is measured:
- A pulse is **informative** if a non-detection at the measured R_min would give φ_max ≤ 0.5.
- A pulse is classed **new loops** if φ_max ≤ 0.5, and **re-use** if the nominal φ ≥ 0.7 with the knee detected at the 3σ level.
- A sample statement "pulses predominantly use new loops" requires ≥ 75 % of informative pulses to be classed new loops, with a 95 % bootstrap interval excluding 50 %.

The definition of informative uses only thermal and spatially integrated quantities, so selection cannot follow the answer.

## 5. Objectives

**General objective.** Measure, with STIX and a physically conservative method, whether successive HXR pulses re-use the loops filled by earlier pulses, and in which conditions, delivering a public pulse-by-pulse catalogue.

| ID | Objective | Output | Success criterion | Weeks |
|---|---|---|---|---|
| OE1 | **Validate the method** end-to-end: synthetic STIX visibilities with known φ and N; positive controls; warm-target and return-current checks | Validation report; recovery and coverage tables | Coverage of φ_max ≥ 95 % on synthetic data; positive controls within a factor of 3 of R_pred | 1–4 |
| OE2 | **Pilot** on X5.0 2023-12-31 and benchmark X1.3 2022-03-30 | R_pred, R_min, φ_max per pulse | Gate G1 (Section 10) | 1–3 |
| OE3 | **Sample** from the STIX catalogue with pre-registered criteria | Event list with selection log | ≥ 15 flares with informative pulses (G2) | 3–8 |
| OE4 | **Measurements** per pulse on the cluster: spectroscopy, thermal geometry, non-thermal imaging in energy bins, detection limits | Catalogue v1 | Every pulse has values or flagged failures | 5–10 |
| OE5 | **Analysis**: distribution of φ; dependence on footpoint displacement, waiting time, eruption, pulse index; robustness | Results and figures | Conclusions stable across algorithms and bands (G3) | 9–13 |
| OE6 | **Publication**: paper, catalogue with DOI, code | Submitted manuscript; Zenodo record; tagged release | Submitted by week 20 | 13–20 |

## 6. Data and sample

### 6.1 Sources
- **STIX L1 data from SOAR:** pixel data (cpd, 8 pixels, 0.5 s bins where available) and spectrograms. Access is via the SOAR TAP service; the working queries are recorded in the project notes and `scripts/stix_event_search.py`.
- **STIX data center API:** flare list, quick-look light curves, ephemerides.
- **SDO/AIA** (Earth view), for loop geometry when the flare is visible from Earth.
- **ASO-S/HXI**, for stereoscopic events, if access is obtained.
- **CME catalogues** (SOHO/LASCO CDAW) and EUI/AIA eruption signatures, for the confined/eruptive flag.

### 6.2 Catalogue numbers (*computed*, flare list cached 2021-01-01 to 2026-10-02)

| Net 25–50 keV peak [counts / 4 s] | ≥ 2×10³ | ≥ 5×10³ | ≥ 2×10⁴ | ≥ 10⁵ |
|---|---|---|---|---|
| Flares (particle-background entries removed) | 364 | 167 | 49 | 11 |

### 6.3 Selection criteria (*proposed*, pre-registered)
1. Net 25–50 keV peak ≥ 5×10³ counts per 4 s.
2. At least two resolvable non-thermal pulses after the first (k ≥ 2), from the 25–50 keV light curve.
3. Pixel data with 8 pixels available for the pulse windows; attenuator and rate-control state constant within each window.
4. Loop-top/footpoint separation ≥ 2 imaging resolution elements (≈ 14″ with sub-collimators 3–10) as seen from Solar Orbiter, or a stereoscopic configuration.
5. At least one informative pulse (Section 4).

**Expected yield:** 20–60 flares, 100–300 informative pulses (estimate, verified at G2).

### 6.4 Controls
- **Positive controls:** STIX flares with a strong non-thermal loop-top source of coronal-thick-target type, or with an evaporation sequence like Liu et al. (2006). Chosen with the supervisor before the main sample is measured.
- **Negative control:** the first pulse of each flare, where little evaporated plasma exists yet, so R_pred is small and no "re-use" should be found.

## 7. Method, step by step

Each flare is one cluster job (steps S1–S9); S10 runs on the catalogue.

| Step | What | How | Output |
|---|---|---|---|
| S1 | Retrieve data | SOAR TAP queries; cpd and spectrogram files | Local files with checksums |
| S2 | Define pulses | 25–50 keV light curve (0.5–4 s); background; pulses separated by significant minima; check attenuator and rate-control state | Pulse windows (onset, peak, end) |
| S3 | Integrated spectroscopy per pulse and at each onset | Isothermal (+ superhot second component if needed) + cold thick target + albedo; MCMC posteriors; sunkit-spex or OSPEX, cross-checked on the benchmark | T, EM, δ, Ec, Ṅ with uncertainties |
| S4 | Thermal geometry at each onset | 6–10 and 10–15 keV visibilities: forward fit (ellipse or loop) plus CLEAN; deconvolved size; loop-top share of the thermal flux; loop length from footpoint separation (and AIA or stereo where possible) | EM_LT, V_max, l_min, N_min, E* |
| S5 | Non-thermal imaging per pulse in energy bins (20–25, 25–32, 32–40, 40–50, 50–84 keV) | Visibility forward fit with two footpoints + a loop-top component fixed at the thermal position and shape (optionally a free fourth source); MCMC; CLEAN and MEM_GE as cross-checks; bootstrap of counts | R_obs(ε) with posterior; footpoint positions |
| S6 | Detection limits | Inject synthetic loop-top sources (R = 0.01–0.5) into the observed visibilities with matched noise; refit | R_min(ε) at 95 % recovery |
| S7 | Prediction and bound | `src/tracer.py`: R_pred(ε); φ_max (conservative); nominal φ from fitting R_obs(ε) with the mixture model plus an energy-independent offset | φ_max, φ_nominal, flags |
| S8 | Covariates | Footpoint displacement between pulses (S5), waiting time, thermal decay time, flux density (return-current check), eruption flag, flare class | Covariates per pulse |
| S9 | Catalogue entry | All quantities with uncertainties and flags | One row per pulse |
| S10 | Sample analysis | Classification (Section 4); distributions; dependence on covariates with flare-level bootstrap (or a hierarchical model with a random effect per flare); robustness across algorithms, bands and assumptions | Results, figures |

## 8. Validation

1. **Synthetic end-to-end (must pass before the sample).** Simulated STIX visibilities (two footpoints and a loop top, realistic counts, noise and calibration errors) with known φ ∈ {0, 0.3, 1} and N, run through S5–S7. Required: coverage of φ_max ≥ 95 %, and the power to recover the knee when φ = 1.
2. **Positive controls** (Section 6.4): R_obs within a factor of 3 of R_pred, with the knee where predicted.
3. **Negative control:** first pulses show no re-use signal beyond the false-positive rate.
4. **Physics checks:**
   - warm-target correction at ≥ 25 keV;
   - return current: FP-solver runs (`docs/05_fp_solver_verification.md`) for the highest flux densities, or an exclusion rule;
   - albedo model as a function of the heliocentric angle from Solar Orbiter.
5. **Robustness:** conclusions unchanged across CLEAN, MEM_GE and forward fitting, across energy bins, and across the conservative and nominal assumptions.

## 9. What is used and at what scale

### 9.1 Software

| Purpose | Tool |
|---|---|
| STIX data, visibilities, calibration | stixpy 0.3.0 (`requirements-stix.txt`, Python ≥ 3.10) |
| Imaging | xrayvision (CLEAN, MEM), own visibility forward fit with MCMC (numpy, scipy, emcee) |
| Spectroscopy | sunkit-spex (or OSPEX in IDL if preferred by the group), with the STIX response |
| Physics of the tracer | `src/tracer.py` on `src/toy_bias.py` (thick target, ionized and neutral zones, Haug cross-section) |
| Context and geometry | sunpy, AIA data; ASO-S/HXI where available |
| Workflow | Slurm job arrays (one flare per job), pinned environments, fixed random seeds, a run manifest per flare |

### 9.2 Compute and storage (estimates, to be measured in the pilot)
- **Data:** the X5.0 pixel-data file is 153 MB; typical flares need 10–150 MB, so 5–15 GB of raw data for 60 flares, plus products.
- **Per pulse:**

  | Task | CPU-minutes |
  |---|---|
  | Spectral fits with MCMC | 5–20 |
  | Forward-fit imaging with MCMC, 5 bins | 25–100 |
  | Cross-check images | ~10 |
  | Injection–recovery (6 amplitudes × 20 noise realizations × 5 bins) | 60–150 |

  Total: about 100–300 CPU-minutes per pulse, so **0.5–1.5 thousand CPU-hours for 300 pulses**. This is small for a cluster and runs in days.

### 9.3 People and roles (no names in the public repository)
- **Doctoral researcher:** all steps.
- **Supervisor:** physics of the coronal thick target, choice of controls, pre-registration, framing and journal.
- **STIX imaging and calibration experts:** forward-fit validation, attenuator and calibration limits.
- **A modelling colleague (optional):** implications of φ for multithread and single-loop models.

### 9.4 Parked from earlier versions
The radiation-hydrodynamic codes (RADYN, HYDRAD, FP) are not needed for the core result. They remain available for the return-current check and for the discussion. The v3 spectral-break regression is archived.

## 10. Timeline and gates (20 weeks)

| Weeks | Work | Gate |
|---|---|---|
| 0–1 | ADS novelty check; agree the plan; write the one-page pre-registration | **G0:** no prior quantitative re-use test found; pre-registration signed |
| 1–3 | Synthetic end-to-end test; X5.0 pilot (onset thermal fits, R_pred, R_min, φ_max); benchmark X1.3 | **G1:** synthetic coverage ≥ 95 %; on real visibilities R_min ≤ R_pred/2 for dense pulses; positive control within a factor of 3 |
| 3–8 | Sample selection; cluster pipeline; catalogue v0 | **G2:** ≥ 15 flares with informative pulses |
| 8–12 | Full measurements; robustness | **G3:** conclusions stable across algorithms and bands |
| 12–16 | Interpretation (multithread versus single-loop, QPP, energetics); figures; draft | — |
| 16–20 | Internal review; submission; catalogue and code release | — |

**Kill criteria and fallbacks:**

| Gate failure | Fallback |
|---|---|
| G1: STIX cannot reach R_min ≲ R_pred/2 even with R(ε) and selection | Stereoscopic occultation case studies (fewer events, cleaner loop tops); or a short paper on the X5.0 third source if it proves robust; or the archived v3 with per-footpoint control |
| G2: fewer than 15 flares | Case-study paper on the best 3–5 flares (lower impact, same method) |
| G3: results depend on the algorithm | Report as a limit on the method; restrict to the robust subset |

## 11. Risks

| Risk | Effect | Mitigation |
|---|---|---|
| Dynamic range of STIX imaging (Section 3.5) | Non-detections uninformative | R(ε) shape, selection of dense pulses, stereo cases; measured at G1 |
| Superhot thermal emission at 25–50 keV | Mimics a loop-top signal | Two-temperature fits; for re-use claims, subtract and require the knee |
| Emission-measure attribution to the loop top | Non-conservative bound if overestimated | Imaging-derived share with lower uncertainty |
| Return current at high flux densities | Bound argument not covering it | FP-solver check or exclusion rule |
| Attenuator and pile-up in large flares | Biased spectra and images | Windows with constant state; flag and test |
| Small sample after cuts | Weak statistics | Gate G2; lower brightness threshold (364 flares at 2×10³ counts) |
| Prior or parallel work | Lower novelty | ADS check (G0); ask the supervisor and the STIX team |

## 12. Deliverables
1. Paper (A&A or ApJ; no venue promised): *Do successive hard X-ray pulses re-use flare loops? Evaporated plasma as a tracer of electron paths with STIX* (working title).
2. Public pulse-by-pulse catalogue with a DOI.
3. Pipeline code and the pre-registration, released with the paper.
4. Optional: a short note on the third 25–50 keV source of the X5.0 flare, only if robust across algorithms and consistent with HXI.

## 13. Status (2026-10-04)
- **Catalogue search:** reproducible (`scripts/stix_event_search.py`); numbers in Section 6.2.
- **X5.0 first look** (`scripts/x5_first_look/`, recovered from a temporary folder):
  - five pulses;
  - footpoints stable within ~2″ from P2 to P5;
  - no non-thermal loop-top component in CLEAN at 25–50 keV, which is a CLEAN threshold, not yet a limit;
  - a third source in P4–P5;
  - loop-top/footpoint separation ~8″, below the sample criterion, so the event is a pilot only.
- **Physics of the tracer:** `src/tracer.py` with 10 tests, including the check that the bound is conservative.
- **Missing:**
  - synthetic visibility test;
  - onset thermal fits and R_min for the X5.0;
  - positive controls;
  - forward-fit imaging code;
  - ADS check;
  - pre-registration.

## 14. Relation to earlier versions
| Version | Question | Why it changed |
|---|---|---|
| v1 (2026-10-01) | How large is the chromospheric memory after a 2nd or 3rd pulse (RHD)? | The answer, that memory exists, was near-certain and known (Kennedy et al. 2015) |
| v2 (2026-10-02) | How much does memory bias the STIX electron inference? | Real but small and conditional |
| v3 (2026-10-03) | Separate target memory, return current and acceleration by the time dependence of spectra | Effect sizes near systematics; time and cumulative energy are collinear without spatial control |
| **v4 (2026-10-04)** | **Do later pulses re-use the filled loops? Memory used as a tracer** | Keeps the original question (same strand or independent filaments) with a simpler, more robust and more decisive design |

## 15. Questions for the supervisor
1. Which STIX flares are good positive controls (coronal thick target, evaporation sequences)?
2. What dynamic range do STIX experts consider realistic for a faint loop top next to bright footpoints, and with which algorithm?
3. Is ASO-S/HXI access possible for stereoscopic cases?
4. OSPEX or sunkit-spex for the spectroscopy?
5. Is there related, possibly unpublished, work in the group or in the STIX team?
6. Which journal fits best once G1 is passed?

## References (verified at least at abstract level unless noted)
- Dennis et al. 2018, ApJ, "Coronal hard X-ray sources revisited", doi:10.3847/1538-4357/aae0f5
- Fleishman et al. 2016, ApJ 816, 62, doi:10.3847/0004-637X/816/2/62
- Grigis & Benz 2005, ApJ, doi:10.1086/431147 (title only)
- Inglis & Dennis 2012, ApJ 748, 139, doi:10.1088/0004-637X/748/2/139 (title only)
- Kennedy et al. 2015, A&A, arXiv:1504.07541
- Kontar, Brown & McArthur 2002, Solar Physics 210, 419 (from the earlier search)
- Krucker & Masuda 2026, A&A, doi:10.1051/0004-6361/202557120
- Liu, Han & Fletcher 2010, ApJ 709, 58, arXiv:0912.0402
- Liu et al. 2006, ApJ 649, 1124, arXiv:astro-ph/0603510
- Matsumoto et al. 2026, arXiv:2606.29979
- Mikuła, Mrozek & Kułaga 2026, A&A 706, A379, doi:10.1051/0004-6361/202555337
- Mrozek et al. 2026, arXiv:2609.16862
- Ning & Cao 2010, ApJ 717, 1232, doi:10.1088/0004-637X/717/2/1232
- Reep et al. 2016, ApJ, arXiv:1607.06684
- Rubio da Costa et al. 2016, ApJ, arXiv:1603.04951
- Ryan et al. 2024, triangulation of the X5 flare of 2023-12-31 with ASO-S/HXI and STIX (PMC11339132)
- Simões & Kontar 2013, A&A 551, A135, arXiv:1301.7591
- Veronig & Brown 2004, ApJ 603, L117, doi:10.1086/383199
- Volpara et al. 2024, A&A, doi:10.1051/0004-6361/202348553
- Warren 2006, ApJ (multithread flare model; cited via Rubio da Costa et al. 2016, not read)
- Alaoui & Holman 2017, ApJ, doi:10.3847/1538-4357/aa98de
