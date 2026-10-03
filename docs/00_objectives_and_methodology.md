# Bias of STIX electron inference in successive pulses: objectives, hypotheses and methodology

**Author:** Carlos Alberto Martínez Sibaja
**Status:** research proposal (version 2, 2026-10-02). Nothing in this document has been simulated yet; all beam parameters in the repository are synthetic. Thresholds marked *proposed* must be fixed before the production campaign (Section 6.8).

---

## 0. Summary: what is proposed, what will be done

**Problem.** The electron parameters of a flare (rate Ṅ, low-energy cut-off Ec, spectral index δ) are inferred from the hard X-ray (HXR) spectrum with a standard model: an isothermal component plus a cold, collisionally thick target. This is reasonable for the first pulse. A second or third pulse arrives in an atmosphere already changed by the first one: chromospheric evaporation has raised the coronal density, the plasma is hotter and ionized, and the thermal emission is stronger. Order-of-magnitude estimates (not yet verified by a simulation in this project) suggest that the coronal column can become comparable to the stopping column of the electrons, so the target is no longer the one the fitting model assumes (cf. coronal thick-target sources, Veronig & Brown 2004).

**Research question.**

> How much does the atmospheric memory of the previous pulse bias the electron parameters (Ṅ, Ec, δ) inferred with STIX for a second or third pulse, and is it visible in STIX images as a change in the loop-top / footpoint emission ratio?

**Approach: an inject–simulate–reinfer test.**

1. Inject known electron pulses into a 1D radiation-hydrodynamic (RHD) loop that keeps its history between pulses.
2. Compute the synthetic HXR photons (non-thermal bremsstrahlung plus thermal emission of the simulated plasma), by region (loop top, footpoints) and in total.
3. Apply the STIX response and Poisson noise.
4. Fit the result with the same standard model that is applied to real STIX data.
5. Compare with the injected truth: the bias B = θ_fit − θ_true. The memory-induced bias is ΔB = B₂ − B₁, where B₁ is the method's intrinsic bias on a relaxed atmosphere.
6. Apply the same analysis to one real STIX event with at least two pulses and a resolved loop top and footpoints.

**Codes (decided 2026-10-03).** The work is split in two pieces so that no single code is a bottleneck. (i) A 1D hydrodynamic loop code gives the evolving atmosphere with history: HYDRAD first (it already runs), RADYN+FP as an upgrade if access, license and time allow. (ii) The open-source Fokker–Planck solver FP (solarFP/FP, Apache-2.0, Allred et al. 2020), run on the atmosphere snapshots, gives the electron transport with warm target and return current, and the bremsstrahlung photons. The standard inference model is the OSPEX/sunkit-spex isothermal + cold-thick-target fit, with the warm-target variant as contrast. Open point: FP's input format and photon output have not been verified yet (OE4). **Mechanism and controls.** The hydrodynamic memory is measured with a paired counterfactual (run with and without pulse k, same history up to pulse k). Independent filaments (each pulse in its own relaxed tube) are the alternative hypothesis: they must show no memory bias.

**Possible outcomes (all are results).** A significant and visible bias; a significant bias that STIX cannot see in imaging; a negligible bias (STIX inference is robust); or a bias degenerate with the allowed parameter uncertainty.

**First task and decision gate.** Compare the coronal mass column at the onset of pulse 2 with the electron stopping column (Section 4, OE1). If it is below ~10 %, the physical basis of the idea is weak and the project is reconsidered before any cluster time is spent.

**Current state.** Done: beam-pulse table generator, five-experiment matrix (E1–E5), encoder for RADYN's `ftab.dat`, tests, an infrastructure report. Not done: gate test, event selection, STIX fits, RADYN verification and runs, photon computation, re-inference.

---

## 1. Problem statement

During a flare, HXR emission often arrives in **successive pulses**. Each pulse is an injection of non-thermal electrons that stop in the atmosphere, heat it and set it in motion. Variations of δ and Ṅ between pulses are usually interpreted as changes in the acceleration process. That interpretation assumes that each pulse is inferred with the same, correct, target model.

The first pulse acts on a relaxed atmosphere. The second and third act on a modified one. Estimates of order of magnitude (to be verified, OE1):

- the stopping column of a 20 keV electron is ~10¹⁹–10²⁰ cm⁻²;
- the coronal column goes from ~10¹⁸ cm⁻² (relaxed) to ~10¹⁹–10²⁰ cm⁻² after evaporation;
- a significant fraction of the energy of pulse 2 may then be deposited in the corona, and the cold-thick-target fit no longer describes the target.

Atmospheric memory itself, i.e. that the stopping depth changes with the history, is already known (Kennedy et al. 2015). What is not quantified, and has consequences for the use of STIX spectra, is **how much that memory biases the inferred electron parameters and whether it leaves a signature in the images**.

### 1.1 Research question

> **How much does the atmospheric memory of the previous pulse bias the electron parameters (Ṅ, Ec, δ) inferred with STIX for a second or third pulse, and is it visible in STIX images as a change in the loop-top / footpoint emission ratio?**

### 1.2 Sub-questions

| ID | Sub-question | Main observable |
|---|---|---|
| SQ1 | What fraction of the energy of pulse k is deposited in the corona rather than the chromosphere, and how does it change between pulses 1 and 2? | η_cor(k); coronal column versus stopping column |
| SQ2 | If the HXR photon spectrum is generated from the atmosphere with history and refitted with the standard model, how far do (Ṅ, Ec, δ) deviate from the injected values, and by how much more than for pulse 1? | Bias B = θ_fit − θ_true; ΔB = B₂ − B₁ |
| SQ3 | How much of the bias comes from each mechanism: thermal contamination, warm target, target ionization state, spatial mixing of loop top and footpoints? | Bias decomposition by numerical experiment |
| SQ4 | Does the loop-top / footpoint ratio R_LF change between pulses, and can STIX resolve it (angular resolution, dynamic range, noise)? | R_LF(k), significance of ΔR_LF |
| SQ5 | What does ΔB depend on: waiting time, energy of the previous pulse, Ec and δ, area A? | Parameter sweeps and sensitivity (6.5) |
| SQ6 | In a real event, do the observed pulse-to-pulse changes of δ and R_LF exceed the predicted bias (a sign of changing acceleration) or fit inside it? Can the same-strand scenario be distinguished from independent filaments? | Observed δ₂ − δ₁ versus ΔB; observed R_LF versus E2/E3 |

The paired-counterfactual memory metric (Section 6.6) is kept as a **tool**: it explains where the bias comes from, but it is not the headline result.

### 1.3 Working assumption on geometry

The pulses are provisionally assumed to hit **the same flux tube**. This is an operating hypothesis, not an observational result (Section 12). The comparison with independent filaments (E3) is a **test** of it: in E3 each pulse acts on a relaxed atmosphere and therefore should show neither memory bias nor a change of R_LF.

---

## 2. Falsifiable hypotheses

Each hypothesis has a quantitative prediction and a condition that would refute it. They are stated **before** any result is seen.

| ID | Hypothesis (physical mechanism) | Prediction | Refuted if |
|---|---|---|---|
| **H0** | *Null.* The parameters inferred for pulse 2 with the standard model have the same bias as those of pulse 1: the atmospheric history does not affect the inference. | ΔB ≈ 0 for Ṅ, Ec and δ within the statistical and numerical uncertainty; ΔR_LF ≈ 0 | — (reference) |
| **H1** | *Change of deposition regime.* After evaporation, the coronal column from apex to transition region reaches a significant fraction of the stopping column for part of the STIX electrons. | η_cor(2) > η_cor(1) by more than the numerical uncertainty (*proposed:* difference > 0.05); the density increase dominates over chromospheric compression when τ_w ≲ the drainage time | η_cor(2) − η_cor(1) < 0.05, or coronal column at t₂ < 10 % of N_stop(Ec) |
| **H2** | *Inference bias.* The cold-thick-target fit reproduces (Ṅ, Ec, δ) worse for pulse 2 than for pulse 1. Candidate mechanisms: (i) stronger thermal emission from a denser, hotter plasma that invades the low non-thermal range and shifts Ec and δ; (ii) warm-target effects for E ≲ a few kT; (iii) different ionization of the target; (iv) mixing of loop-top and footpoint emission in an integrated spectrum. **The sign is not predicted a priori**; the simulation determines it. | \|ΔB\| exceeds the statistical uncertainty for the photon counts of the event and exceeds the baseline bias B₁ | \|ΔB\| within the statistical uncertainty: STIX inference is robust to memory (a valid negative result) |
| **H3** | *Imaging signature.* R_LF increases in pulse 2 in the same tube and does not change for independent filaments. | ΔR_LF(E2) > 0 with d/σ > 3 in the synthetic STIX image; ΔR_LF(E3) ≈ 0 | ΔR_LF not significant, or the loop-top–footpoint separation is below the STIX resolution (not observable) |
| **H4** | *Error budget of pulse-to-pulse variation.* In a real event, part of δ₂ − δ₁ and ΔR_LF is explained by the memory bias without a change of acceleration. | observed \|δ₂ − δ₁\| compatible with the predicted ΔB | observed \|δ₂ − δ₁\| ≫ ΔB: the variation is due to acceleration |

**Negative results that are also results:** a negligible ΔB (STIX is robust), or a ΔR_LF that cannot be observed because of resolution (memory exists but STIX cannot see it).

---

## 3. General objective

Quantify, with self-consistent RHD simulation and synthetic HXR photons, **the bias that atmospheric memory introduces in the electron parameters inferred with STIX for successive pulses**, determine whether it is visible in the images, and deliver a reproducible pipeline "STIX spectrum → atmosphere → synthetic photons → re-inference".

---

## 4. Specific objectives

### OE1 — Cheap prior gate: column test (no RADYN needed)
- **Method:** with HYDRAD output for E2 and E5 (the ramped tables already run), compute at the onset of pulse 2 the mass column from the apex to the transition region and compare it with N_stop(E) for E = 10, 20, 50 keV.
- **Success/abandon criterion:** if the coronal column is < 10 % of N_stop(Ec_STIX) with real parameters, H1 loses its basis and the project is reconsidered; if ≳ 50 %, continue.
- **Inputs:** HYDRAD installed (not stored in the repository as an executable); synthetic parameters first, real ones when available.
- **Outputs:** table N_cor(t)/N_stop(E) for E1, E2, E5.
- **Caveat:** HYDRAD has no Fokker–Planck transport; the test measures only the column structure of the plasma, not the deposition.

### OE2 — Select and characterize the event
- **Criteria (Section 6.1):** at least two pulses separated by ~30–200 s, and a STIX image with resolvable loop top and footpoints.
- **Outputs:** event dossier (D1).
- **Success:** ≥ 2 resolvable pulses, estimated loop geometry, GOES/AIA/EUI coverage (IRIS/EIS/SPICE if possible), and a documented estimate of the area A with uncertainty.

### OE3 — Infer the beam of each real pulse
- Spectral fit with the full instrument response, thermal + thick target (and alternatives), covariances, A with uncertainty. This is also the **standard inference model** applied to the synthetic data in OE6, so that it is identical in both cases.

### OE4 — Verified atmosphere and transport chain
- **Atmosphere:** HYDRAD ramped-pulse runs with convergence and energy-balance checks (criteria in 6.8); RADYN+FP is an optional upgrade, requiring a verified compilation, a confirmed license and a reproduced F-CHROMA model. **Transport:** install FP (solarFP/FP), read its documentation (`doc/FP.pdf`), reproduce a published FP result, and verify that it accepts an externally supplied atmosphere (n, T, ionization) and returns the electron distribution, the heating rate Q(s) and the photon spectrum. **Consistency check:** compare FP's deposition profile with HYDRAD's Hawley–Fisher profile on the same snapshot; a large difference limits how far the HYDRAD-evolved atmosphere can be trusted for pulse 2.

### OE5 — Simulations E1, E2, E5, E3 with the real parameters
- Experiment matrix (6.4) with the parameters of OE3. Output: n(s,t), T(s,t) and ionization snapshots at the onset of each pulse (HYDRAD; RADYN if available), which are the input of the FP transport in OE6.

### OE6 — Synthetic HXR photons and re-inference (**core of the project**)
- **Method:** see 6.7. Compute the HXR photon spectrum (integrated and by region) of the beam propagating in the simulated atmosphere **with history**, add the thermal emission of the simulated plasma, apply the STIX response and noise, **fit with the same standard model as in OE3** and compare with the injected values.
- **Outputs:** B₁, B₂, ΔB with uncertainties, decomposition by mechanism (SQ3), R_LF (D6, D7).
- **Success:** bias quantified for Ṅ, Ec and δ with its statistical uncertainty and the uncertainty of the photon computation itself declared.

### OE7 — Sweeps and sensitivity
- Waiting time, energy ratio, Ec, δ, A (6.5). Map of ΔB in the (τ_w, E_prev/E_new) plane.

### OE8 — Comparison with the real event and detectability
- Apply H3 and H4 to the real event: compare the observed δ₂ − δ₁ and R_LF with the prediction with memory (E2) and without it (E3). Decision rule in 6.8.

### OE9 — Package and write
- Reproducible pipeline and a proof-of-concept manuscript for one event.

---

## 5. Expected results

Open possibilities, not promises.

| Scenario | What would be seen | Contribution |
|---|---|---|
| **A. Significant and visible bias** | Large ΔB in δ or Ec; observable ΔR_LF | Error budget for pulse-to-pulse variation in STIX; guidance against over-interpreting changes of δ |
| **B. Significant bias, not visible in imaging** | Large ΔB, but loop-top–footpoint separation below STIX resolution | Lower bound on the error of isolated spectral inference |
| **C. Negligible bias** | ΔB within the statistical error | STIX is robust to memory in that regime; justifies treating each pulse in isolation |
| **D. Degeneracy** | The bias cannot be told apart from parameter variations allowed by STIX | Conditions under which memory and acceleration cannot be separated |

All four are publishable if the regime is well delimited; **A** would be the most citable. No detection, novelty or specific journal is promised.

---

## 6. Methodology

### 6.1 Event selection criteria

| Criterion | Requirement | Type |
|---|---|---|
| HXR pulses | ≥ 2 pulses separated by 30–200 s; enough photons for a per-pulse fit | Mandatory |
| Imaging | STIX reconstruction with separable loop top and footpoints (angular resolution of STIX, to be checked in Krucker et al. 2020, and Solar Orbiter–Sun distance at the event date) | **Mandatory** |
| Spectra | Science data, no saturation; attenuator state identified | Mandatory |
| Context | GOES and AIA | Mandatory |
| Resolution in other diagnostics | EUI, IRIS, EIS or SPICE for the geometry test | Desirable |
| Geometry | Visibility from Earth and Solar Orbiter; light-travel-time correction | Mandatory |

Candidates, with the criteria met and failed, are recorded. **The event is chosen for the observable (resolvable R_LF), not for convenience.**

### 6.2 STIX data analysis
1. Reduction: background, attenuator, pile-up, integration per pulse.
2. Standard model: isothermal + cold thick target; warm-target variant as a contrast.
3. Fit with the full response; posterior of θ = (Ṅ, Ec, δ, T, EM) per pulse and covariances.
4. Cautions: STIX observes photons; the photon index is not the electron index; Ec may be weakly constrained; thermal/non-thermal degeneracy at low energy; albedo.
5. Conversion: P = Ṅ·Ec·(δ−1)/(δ−2); F = P/A, propagating A and its uncertainty.

### 6.3 Transport and RHD chain

| Stage | Physical requirement | Methodological consequence |
|---|---|---|
| Transport | Fokker–Planck with collisions, warm target and return current | FP (solarFP/FP, Allred et al. 2020; Apache-2.0) states that it makes no cold- or warm-target assumption (general Rosenbluth potentials) and solves the return-current field self-consistently. The RADYN F-CHROMA distribution has the older 2015 FP (gas temperature in collisions, thermalization energy, optional return current). **FP input/output compatibility with an external atmosphere is to be verified** |
| Coupling | Q(s,t) recomputed with the evolving atmosphere | A Q profile precomputed on a static atmosphere is not valid |
| Atmosphere | 1D hydrodynamics with history; chromospheric NLTE only if Hα/IRIS diagnostics are added | HYDRAD (works, MIT license) for the evolution; RADYN+FP as an upgrade; FLARIX is not accessible. **Limitation:** HYDRAD heats with the analytic cold-target expression (Hawley & Fisher, normal incidence), which is the assumption under test; the FP-versus-HYDRAD deposition comparison in OE4 bounds this effect |
| HYDRAD role | Analytic heating, optically thin radiation | Evolves the atmosphere for the column test (OE1) and the main runs; not used for deposition conclusions, which come from FP on its snapshots |

No-double-counting rule: the beam heating enters the energy equation only once.

### 6.4 Experiment matrix

| ID | Set-up | Role |
|---|---|---|
| E1 | One pulse in a relaxed atmosphere | Baseline bias B₁ and reference R_LF |
| E2 | 2 or 3 pulses in the same tube, no restart | **Object of study:** B₂, ΔB, ΔR_LF |
| E5 | Pulse 1 and relaxation, no pulse 2 | Counterfactual: separates residual emission from the response to pulse 2 |
| E3a/E3b | Independent filaments (two area assignments) | Alternative hypothesis: ΔB and ΔR_LF should be ≈ 0 |
| E4 | Continuous heating, equal energy | Control of the temporal distribution |

For pulse 3, E5′ (pulses 1 and 2 without pulse 3) is also needed. The input tables are already generated by `src/experiments.py` (synthetic parameters until OE3).

### 6.5 Factorial design and uncertainty propagation
Factors: number of pulses (1, 2, 3), waiting time τ_w (relative to the estimated drainage time), energy ratio previous/new pulse, Ec and δ within the STIX-allowed range, area A. One-factor-at-a-time from the central case, then a space-filling design over the STIX posterior. **Statistical uncertainty** (Poisson photon noise) is propagated with noise replicas for each simulation. The number of samples is decided after pilots. Compared cases have the same total energy and area unless the difference is the factor under study.

### 6.6 Operational definition of memory (tool)
Paired counterfactual: R_hist(τ) = X_with k − X_without k, with common history up to t_k (for k = 2, E2 − E5); R_rel(τ) = X_E1 − X₀; memory M = R_hist − R_rel, normalized with a norm fixed in advance. τ_rel is measured with the background heating term of RADYN declared. The **coronal column N_cor(t)** and η_cor(k) are added as memory variables relevant to the inference.

### 6.7 Synthetic photons, re-inference and imaging (**core**)

**Inject–recover pipeline:**
1. *Truth:* (Ṅ, Ec, δ) of each pulse injected in E1 and E2.
2. *Photons:* non-thermal bremsstrahlung of the beam propagating in the simulated atmosphere and thermal emission of the simulated plasma, by region (loop top, footpoints) and total.
3. *Instrument:* STIX response, attenuator, cadence, Poisson noise.
4. *Re-inference:* fit with **the same standard model and the same fitting procedure applied to the real data** (OE3).
5. *Bias:* B = θ_fit − θ_true per pulse; ΔB = B₂ − B₁; B₁ measures the intrinsic bias of the method, already present for a relaxed pulse.

**Two routes for step 2, to be checked in OE4:**
- (a) **Main route:** run the open-source FP solver (solarFP/FP) on the n, T, ionization snapshots of the simulation to obtain the electron distribution, the deposition and the bremsstrahlung photons (**input/output compatibility not yet verified**);
- (b) fallback: own post-processing transport (Coulomb collisions) on the same snapshots, validated against FP or a published result. It also enables the quick level-1 test with HYDRAD.

**Imaging:** R_LF from the emission distribution along the loop, projected; evaluate whether STIX resolves it (resolution, dynamic range between sources, noise) and with what significance. A full STIX visibility simulation is applied only if the simple estimate shows signal.

**Other diagnostics (secondary):** SXR/GOES and AIA with their responses; Fe XVIII only for T > ~6 MK; Hα/IRIS with adequate transfer (not equated with HYDRAD). **Neupert test** pulse by pulse as a complementary check, without readjusting the beam to force agreement.

### 6.8 Decision rules (to be fixed before simulating)
- **Significant bias:** |ΔB| > k·σ_stat with k = 3 (*proposed*), σ_stat from Poisson replicas for the photon counts of the event.
- **Imaging:** d/σ > 3 for ΔR_LF (*proposed*).
- **Numerical tolerances:** convergence in grid and time step; energy balance (< 1 % of injected energy, *proposed*); reproduction of F-CHROMA (differences in T and n < 10 %, *proposed*).
- **Failed cases:** are recorded and reported.
- **Pre-registration:** thresholds, norms and statistics are written in the repository **before** the production campaign.

### 6.9 Verification, validation and uncertainty quantification

| Level | What is checked | How |
|---|---|---|
| Code | Tables, units, conservation | 38 existing tests; new tests for the photon computation and the fit |
| Synthetic test with known answer | The fit recovers the parameters when the target is the one of the model (bias ≈ 0) | **Essential negative control** to validate OE6 |
| Physical negative control | Two pulses with τ_w ≫ drainage time: ΔB → 0 | Detects numerical artifacts |
| Numerical | Convergence and energy balance | Refinement |
| Physical | Published case reproduced | OE4 |
| Observational | Real data versus E2/E3 | OE8 |

### 6.10 Reproducibility and cluster use
Record versions, compiler flags, initial atmosphere, beam, output cadence, wall time, CPU, memory and storage. Independent cases as separate jobs. A manifest per run; an end-to-end pipeline with one documented command.

---

## 7. Deliverables

| ID | Deliverable | Acceptance criterion | Status |
|---|---|---|---|
| D0 | Column test N_cor/N_stop (OE1) | Table for E1, E2, E5 | Pending |
| D1 | Event dossier | Criteria 6.1, with resolvable R_LF | Pending |
| D2 | Beam parameters per pulse with covariances | Uncertainties declared | Pending |
| D3 | Table generator and experiment matrix | Energy conserved; 38 tests | **Done (synthetic)** |
| D4 | Solver verification report | Published case reproduced | Pending |
| D5 | Simulation database | Schema with units | Pending |
| D6 | Synthetic photons and recovery test | Negative control passed; B₁, B₂, ΔB | Pending |
| D7 | R_LF and imaging detectability | Rule 6.8 | Pending |
| D8 | Comparison with the real event | δ₂ − δ₁ and R_LF versus E2/E3 | Pending |
| D9 | Reproducible pipeline | A third party reproduces the figures | Partial |
| D10 | Proof-of-concept manuscript | Methods, uncertainties, limits | Pending |
| D11 | Pulse-infrastructure report | `docs/02_pulse_experiments_report.html` | **Done** |

---

## 8. Phases and decision gates

| Phase | Content | Exit gate |
|---|---|---|
| F0 | Synthetic pulse infrastructure (done) | Tests pass |
| **F0.5** | **Column test with HYDRAD (OE1)** | **N_cor/N_stop ≥ ~10 %; otherwise reconsider** |
| F1 | Choose event for resolvable R_LF and fit STIX | D1, D2 |
| F2 | Transport: install FP, reproduce a published result, verify the atmosphere input and photon output. In parallel and time-boxed (3 weeks): try RADYN compilation and the license question | FP verified; RADYN is optional |
| F3 | Cluster cost pilots; synthetic-photon pilot with one case | Realistic budget; negative control passes |
| F4 | Pre-register thresholds and design | Signed document |
| F5 | E1/E2/E5/E3 campaign and sweeps | Documented cases |
| F6 | Recovery test, imaging, real event | D6–D8 |
| F7 | Writing and packaging | D9–D10 |

F1 and F2 can proceed in parallel; F5 requires F1, F2 and F4. Durations are to be agreed with the supervisor.

---

## 9. Risks and mitigations

| Risk | Effect | Mitigation |
|---|---|---|
| **Negligible bias** | Negative result | Publishable if the regime is delimited; the column test and the pilot anticipate it |
| **Bias dominated by the already known thermal contamination** | Contribution perceived as incremental | Decompose the bias by mechanism (SQ3) and quantify it as a function of τ_w |
| **Loop-top–footpoint separation below STIX resolution** | H3 not observable | Choose the event for R_LF; report scenario B |
| FP does not accept an external atmosphere or does not output photons | Photons cannot be computed directly | Route (b); or couple through RADYN, where FP is native |
| FP (2015) without an adequate warm target | Underestimates the central effect | Verify in OE4; document; request a newer version |
| Source area not constrained by STIX | σ_tot dominated by A | Constrain it with images before simulating; treat it as a parameter |
| Competing work (Litwicka et al.; Collier/Kennedy with STIX) | Loss of priority | Repeat the literature search before the manuscript; consult the supervisor |
| RADYN license unconfirmed | Derived code cannot be published | RADYN is optional; confirm with the Oslo group before any use; do not redistribute |
| Pulses at different locations | Same-tube hypothesis false | Evaluate position (OE2); treat the case as E3 |

---

## 10. Scope limits

- Physical simulation; not a neural network.
- A single event as a proof of concept.
- 1D along one flux tube; no 3D MHD.
- STIX alone does not determine geometry or area.
- The computed bias depends on the chosen standard inference model and on the transport physics included; both must be declared with the result.
- No detection, novelty or specific journal is promised.
- No e-mails are sent, no results are published and no cluster allocation is consumed without prior agreement.

---

## 11. Current state against the plan

| Element | Status |
|---|---|
| Table generator and E1–E5 matrix | Done, **synthetic** |
| Infrastructure report | Done |
| Column test (OE1) | **Not started; this is the next task** |
| Event, STIX fit, data | Not started |
| RADYN (F-CHROMA) | Optional upgrade. Downloaded and read; **not compiled**; the distribution ships without a license file |
| FP solver (solarFP/FP) | Open source (Apache-2.0); located 2026-10-03; **not installed, documentation not read; input/output compatibility not verified** |
| HYDRAD with beam | Ramped tables (F ≈ 1.3×10¹⁰) run; an abrupt pulse gives NaN |
| HXR photon computation and re-inference | Not implemented |

---

## 12. Open questions for the supervisor

1. Is the **bias of STIX inference** in successive pulses of interest as the main contribution, rather than the atmospheric response itself?
2. Which flares or STIX events would be good candidates (resolved loop top and footpoints; pulses separated by 30–200 s)?
3. Does the group already have RADYN compiled or an electron-transport code? Is the standalone FP solver (solarFP/FP) coupled to an external atmosphere an accepted approach for the photon computation?
4. Is the recovery test (inject, simulate, re-infer) acceptable as the definition of bias, and the paired counterfactual as the definition of memory?
5. Which thresholds and tolerances are considered adequate?
6. Are there known works or plans (e.g. from the Litwicka or Collier/Kennedy groups) on successive pulses with STIX?
7. Should RHESSI events (finer angular resolution, larger archive) be used as an additional or alternative proof of concept to the STIX event?

---

## 13. References

Included in the repository (README and `docs/03_novelty_and_prior_work.md`):

- Allred, Kowalski & Carlsson (2015), ApJ 809, 104.
- Allred et al. (2020), ApJ 902, 16 (FP solver; code at https://github.com/solarFP/FP, Apache-2.0).
- Carlsson et al. (2023), A&A 673, A150.
- Kennedy et al. (2015), RADYN driven by HXR spectra.
- Krucker et al. (2020), A&A 642, A15 (STIX).
- Veronig & Brown (2004), coronal thick-target HXR sources, [Glasgow eprints](https://eprints.gla.ac.uk/1317) (only the abstract has been read; read the paper before citing).
- Bradshaw & Mason (2003); Bradshaw & Cargill (2013); Reep et al. (2019) (HYDRAD).
- Litwicka et al. (2025), ApJ 983, 155 (FLARIX; continuous versus pulsed filament heating with a preheated VAL-C); March 2026 conference abstract with STIX/IRIS/CHASE (distinguish abstract from paper).
- Warm-target formulation (Kontar and collaborators): **to be verified**, which work to cite.

Classical concepts are cited by their classical source (check the exact reference before citing): Brown (1971) and Emslie (1978) for the collisional thick target; Hawley & Fisher (1994) for the beam heating implemented in HYDRAD; Neupert (1968) for the relation between SXR and HXR.

This list comes from a preliminary exploration, not from an exhaustive review; it must be updated when the manuscript is prepared. The novelty assessment is in `docs/03_novelty_and_prior_work.md` and **does not yet cover the current question** (see its Section 8).

---

## 14. History of the question

- **v1:** *How does the atmosphere respond to the 2nd and 3rd pulse compared with a first pulse on a relaxed atmosphere?* A critical scientific review (2026-10-02) concluded that the qualitative outcome is nearly certain and already known (Kennedy et al. 2015), that the null hypothesis was a straw man, and that the interest had to come from magnitude and observability.
- **v2 (this document):** the focus is the **bias of STIX inference** and its imprint on the image, with atmospheric memory as the mechanism. All infrastructure is kept (tables, E1–E5, RADYN ftab encoder).
