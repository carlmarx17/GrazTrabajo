# Prior work and novelty assessment

**Author:** Carlos Alberto Martínez Sibaja
**Search date:** 2026-10-02 (second pass, deeper than the earlier one on the same day). **Closest full texts read 2026-10-13: see Section 11.6.**

> **Current scope (v5.1, 2026-10-05):** the active question is when the independent-pulse approximation (each pulse treated as if it struck the relaxed atmosphere) fails for a chosen diagnostic. See **Section 11** for the current assessment and [the methodology](00_objectives_and_methodology.md). Sections 1–10 preserve the searches and provisional verdicts for earlier versions; they do not establish novelty for v5.1. No exhaustive updated ADS search has been completed.

**Summary of the v1 assessment:** there is a real but **narrow** gap. The STIX → RHD pipeline, the qualitative effect that the stopping depth changes with the atmosphere, and the "filaments versus continuous" comparison are **already done**. No study was found that quantifies the **pulse-by-pulse memory of the same tube** with a controlled counterfactual, nor its **detectability** with STIX uncertainties.

## 1. Search method and its limits

| Tool | Use | Observed limit |
|---|---|---|
| General web search | Locate works | Its automatic summaries **are wrong at times** (it attributed RADYN+FP to Litwicka 2025; that is FLARIX). Every fact was checked at the source. |
| arXiv API | Date-targeted queries | **Incomplete index:** `all:RADYN` gives only 53 results, `all:FLARIX` gives 3 and Litwicka 2025 does not appear. A result of 0 does **not** prove absence. |
| Semantic Scholar | Forward citations of Litwicka 2025, Kennedy 2015 and Collier 2024 | Later queries returned HTTP 429 (rate limit); partial coverage. |
| **Full text** | Kennedy 2015, Rubio da Costa 2016, Collier 2024 (extracted and keyword-searched) | The only full reading; the rest are abstracts. |

**Not read** (access denied or unavailable): full text of Litwicka et al. 2025; Polito et al. 2022 and A&A 710, A105 (2026), both with error 403; "STIX observation of chromospheric evaporation" (A&A, 2026), 403. They must be read by hand.

## 2. What already exists

### 2.1 Closest to "memory" (read in full text)

| Work | What it really does | Implication |
|---|---|---|
| **Kennedy et al. (2015)**, [arXiv](https://arxiv.org/abs/1504.07541) | RADYN driven by RHESSI fits every 12 s along the whole impulsive phase of an X1.5 flare (110 s of heating, 300 s of relaxation). The parameters harden at two HXR peaks. Using the expression of Emslie (1978) they compute **the stopping height of 5–200 keV electrons during the simulation**: for 50 keV it goes from ≈1.1 Mm (t = 0) to ≈0.75 Mm (t = 70 s) and to ≈5 Mm at the end of heating. | **Already shows that the stopping depth changes in both directions with the history.** They neither separate pulses nor define a memory metric; the heating is continuous for ≈100 s. |
| **Rubio da Costa et al. (2016)**, [arXiv](https://arxiv.org/abs/1603.04951) | 16-thread model (RADYN, RHESSI). **Each burst is a new thread and "each new simulation starts from the initial atmosphere".** Threads are defined from the peaks of the GOES derivative (Neupert effect) and three times the duration is assumed as the relaxation phase. | The independence between bursts is a **starting assumption, not a tested result**. It is the gap a same-tube/independent contrast would address. |
| **Collier et al. (2024)**, A&A, [arXiv](https://arxiv.org/abs/2411.09319) | OSPEX fit (4–36 keV) of **the first burst** of a STIX flare: Ṅ = (0.34 ± 0.04)×10³⁵ s⁻¹, δ = 4.97 ± 0.09, Ec = 13.37 ± 0.57 keV; area A ≈ 10¹⁷ cm² (30 % AIA contour); a **45 s triangular** beam in RADYN on VAL3C with the apex at 3 MK; compared with EUI/FSI 174 Å. Observationally they note a "previously heated" loop in the later frames. | **STIX → RADYN already exists, but only for the first pulse.** The second burst is not simulated. (Their area and Ṅ match, in order of magnitude, the synthetic case of this project.) |

### 2.2 Filaments and successive heating

| Work | What it does | Source |
|---|---|---|
| **Litwicka, Heinzel & Kašparová (2025)**, ApJ 983, 155 | FLARIX. Continuous (10¹⁰, 6.5 s) versus 4 consecutive pulses in filaments (25 % of the area each, 4×10¹⁰, 2 s, 0.5 s overlap). Initial condition VAL-C and preheated VAL-C. **No data analysed.** Hα −36–46 %, Mg II k −51–53 %. | [IOP](https://iopscience.iop.org/article/10.3847/1538-4357/adc393) |
| **Litwicka et al. (abstract, March 2026)** | FLARIX, X9 flare of 3 October 2024, STIX + IRIS + CHASE; the filamentary model comes closer to Hα and Mg II k. **Conference abstract**; no paper found. | [Abstract](https://plan.events.mpg.de/event/453/contributions/3104/) |
| **Reep et al. (2016)** | Multithread RHD: a succession of independent strands (intervals < 10 s) reproduces long redshifts; a single loop does not. | [arXiv](https://arxiv.org/abs/1607.06684) |
| **Radziszewski et al. (2024)**, ApJ | FLARIX with **RHESSI** parameters every 4 s (OSPEX, 6–70 keV) modulated at 0.25 s, for a C1.6 flare with four HXR pulses (H1–H4); **they model only pulse H3**; they do not treat the history between pulses. | [IOP](https://iopscience.iop.org/article/10.3847/1538-4357/ad8ba9) |

### 2.3 Other relevant prior work

- **Mrozek, Falewicz, Kołomański & Litwicka (2021)**: 1D hydrodynamics + Fokker–Planck with RHESSI; focuses on a non-thermal burst and on the altitude of HXR sources versus energy ([arXiv](https://arxiv.org/abs/2112.11392)).
- **Awasthi et al. (2024)**: STIX, ≈200 weak flares, 1D PH code; thermal/non-thermal partition, no memory between pulses ([arXiv](https://arxiv.org/abs/2402.01936)).
- **Polito et al. (2018)**: RADYN with nanoflare heating; **the initial apex temperature (1 or 3 MK) and Ec change where the beam stops**, so it is already known that the previous loop density matters ([arXiv](https://arxiv.org/abs/1804.05970)). This is preheating as an initial condition, not as the history of a pulse.
- **Dennis & Zarro (1993)**: in 20 of 66 events the SXR derivative remains high when the HXR falls; interpreted as energy released in an already affected loop (figures seen in a search summary, to be verified) ([Springer](https://link.springer.com/doi/10.1007/BF00662178)).
- **Qiu (2021)**: many impulsive events reproduce SXR poorly; a two-phase model does better ([arXiv](https://arxiv.org/abs/2101.11069)).
- **Reep & Airapetian (2023)**: flare duration by wavelength and evaporation via RHD ([arXiv](https://arxiv.org/abs/2306.03765)).
- **Allred et al. (2026-10-01)**: ARMS + kglobal + RADYN+FP framework for a flare; does not treat successive pulses or STIX ([arXiv](https://arxiv.org/abs/2610.02149)). **Granovsky et al. (2025)**: 3D RMHD with beams versus 1D RADYN ([arXiv](https://arxiv.org/abs/2512.24507)).

### 2.4 Forward citations (Semantic Scholar)

- **Litwicka 2025:** two citing works, Kowalski 2025 (RHD of condensations in the X9 flare) and a DKIST fine-structure paper. Neither treats memory between pulses.
- **Kennedy 2015:** 36 citing works (2013–2025); flagged as possibly related: Singh 2025 (episodic injection), Lörinčík 2022 (Si IV pulsations), Sellers 2022, Rubio da Costa 2016. **None** presents a pulse-by-pulse memory study in the descriptions seen.
- **Collier 2024:** five citing works (2025–2026); none combines STIX parameters with multi-pulse RHD.

## 3. What was not found (v1 question)

Within the limits of Section 1, **no study was found** with:

1. A **memory metric** defined as a paired counterfactual (same history up to t_k, with and without pulse k).
2. A **regime map** as a function of the waiting time/τ_rel and the energy ratio.
3. A **same-tube versus independent-thread** test for each pulse instead of assuming independence.
4. A **detectability limit** with the STIX uncertainty propagated.
5. A **STIX-driven RHD** simulating more than one burst.

## 4. Novelty assessment (v1 question)

| Approach | Novelty | Reason |
|---|---|---|
| "STIX spectrum → atmospheric response" pipeline | **Low** | Collier 2024; Kennedy 2015 and Rubio da Costa 2016 with RHESSI |
| "Stopping depth changes with history" | **Low** | Kennedy 2015, with figures (1.1 → 0.75 → 5 Mm) |
| "Filaments versus continuous" | **Low and risky** | Litwicka 2025 and the 2026 abstract |
| "Preheating changes the deposition" | **Low** | Polito 2018; Litwicka 2025 |
| **Quantify same-tube memory (counterfactual) + regime map + test against independent threads + detectability with STIX** | **Moderate** | It is the gap left by Kennedy (continuous, no separated pulses) and Rubio da Costa (assumed independence) |

**Honest reading:** the novelty is defensible **only if the paper is defined by quantification and hypothesis testing**, not by what happens. A reviewer who knows Kennedy 2015 will consider it trivial that the depth changes. It must show *how much*, *when* (regime), *with what uncertainty* and *whether it can be observed*. This reading motivated the change of question (Section 8).

## 5. Consequences for the design (v1)

1. **Correction of H1.** The hypothesis "pulse 2 deposits at a higher altitude" had been stated with a single direction. Kennedy 2015 shows that the stopping height of a given energy **goes down** with chromospheric compression (1.1 → 0.75 Mm) and then **goes up** with the coronal density (≈5 Mm). Two competing effects exist and the sign depends on time and parameters. H1 is reformulated without a sign.
2. **The null case is already partly refuted.** With continuous heating of ≈100 s there are large changes; the interesting regime is that of **short pulses with gaps**, where the memory depends on τ_w/τ_rel.
3. **Testing the hypothesis of Rubio da Costa** (each burst = a new thread) with the counterfactual is a concrete, differentiating objective.
4. **Avoid the 3 October 2024 X9 flare** and the "filaments versus continuous with STIX/IRIS" approach, which the Litwicka group presents.

## 6. Publication risks

- **Active competition** from the Wrocław/Ondřejov group (Litwicka, Mrozek, Falewicz, Berlicki, Heinzel), which uses FLARIX with STIX and RHESSI. Their 2026 abstract may become a paper.
- **Incomplete search coverage:** ADS was not queried and several texts were not read.
- **Solver:** using RADYN+FP (instead of FLARIX) gives independence but requires access.
- **A single event** limits generality.

## 7. What is missing before committing months of work

1. **Search ADS** (not accessible from here): `abs:("RADYN" OR "FLARIX" OR "Fokker-Planck") AND abs:("successive" OR "consecutive" OR "multiple" OR "repeated" OR "preheat*" OR "memory") AND abs:"flare"`, and `abs:"STIX" AND abs:("radiative hydrodynamic" OR "RADYN" OR "FLARIX")`; then the citations of Kennedy 2015, Rubio da Costa 2016, Collier 2024, Radziszewski 2024 and Litwicka 2025.
2. **Read by hand** what was blocked: Litwicka 2025 (full text), Polito 2022, A&A 710, A105 and "STIX observation of chromospheric evaporation".
3. **Ask the supervisor** about preprints or plans of the Litwicka group and about works she knows on successive bursts in the same loop.
4. Repeat the search right before submitting the manuscript.

## 8. Addendum (2026-10-02): new question, novelty not yet assessed

The project now asks about the **bias that atmospheric memory introduces in the electron inference from STIX** and its imprint on the loop-top/footpoint ratio (`docs/00`, v2). Sections 1 to 7 evaluate the previous question and **cannot be reused as they are**.

What is known:
- A coronal thick-target HXR source in dense loops exists as a concept (Veronig & Brown 2004; only the abstract was read).
- A quick web search, without access to ADS, did not find an inject–recover study with self-consistent RHD and successive pulses for STIX. **This is not conclusive**: the search engine omits works that do exist.

Pending before committing months:
1. ADS: `abs:("warm-target" OR "thick-target") AND abs:("RADYN" OR "hydrodynamic") AND abs:("hard X-ray")`, and `abs:"STIX" AND abs:("spectral index" OR "photon spectrum") AND abs:("bias" OR "forward model")`; citations of Kontar et al. on the warm target.
2. Read Veronig & Brown 2004 and the warm-target works; check whether the central effect (bias in δ and Ec from a dense, hot target) has already been quantified for RHESSI.
3. Confirm that RADYN+FP of the F-CHROMA version includes a warm target and what it gives as electron-flux output (`docs/04_radyn_access.md`).
4. Ask the supervisor and repeat the search before the manuscript.
5. **FP solver (added 2026-10-03):** Allred et al. (2020) released the FP solver as open source ([solarFP/FP](https://github.com/solarFP/FP), Apache-2.0; Fortran/MPI with Python and IDL wrappers). It states that it makes no cold- or warm-target assumption and solves the return current self-consistently, and it can be used as a plug-in to OSPEX for forward fitting. Check whether FP-based forward modelling already quantifies the bias of the cold-target fit in dense or hot targets (the question here is the pulse-to-pulse case with a history-dependent atmosphere).

## 9. Addendum (2026-10-03): prior work for the v3 question

The project question is now v3 (`docs/00`): separating target memory, return current and acceleration through the time dependence of pulse-resolved STIX spectra. Web searches on 2026-10-03 found the following closest work. ADS has still not been queried.

| Work | What it does | Relation to v3 |
|---|---|---|
| Kontar, Brown & McArthur (2002) | Nonuniform target ionization: yield up to ×2.8 higher in neutral gas; upward and downward knees whose energy depends on the transition-zone column | Mechanism of target memory |
| Su, Holman, Dennis et al. (2009), ApJ 705, 1584 | Nonuniform ionization cannot produce Δγ above ~0.2–0.7 | Limits what memory can explain |
| Su, Holman & Dennis (2011), ApJ 731, 106 | One RHESSI X1.2 flare: both breaks (~49 and ~134 keV) at the peak; their time evolution agrees with nonuniform ionization | **Closest prior work.** Time evolution in one flare, without a test against instantaneous flux or footpoint novelty |
| Alaoui & Holman (2017) | Co-spatial return current explains strong breaks in 19 RHESSI flares | Mechanism R |
| Alaoui, Krucker & Saint-Hilaire (2019), Solar Physics 294, 105 | 65 RHESSI flares above 150 keV; most show a downward break near 55 keV with Δγ ≈ 0.3–1; studied at the peak | Statistics of breaks; no time dependence |
| Grigis & Benz (2004, 2005, 2008); Kiplinger (1995) | Soft-hard-soft within peaks, with different rise and decay branches; soft-hard-harder across peaks, associated with proton events; interpreted as acceleration and trapping | Mechanism A; a target-memory contribution to progressive hardening has not been tested |
| Bhattacharjee, Kontar & Luo (2025), ApJ (arXiv:2506.08310) | Warm-target fits in time for RHESSI and STIX flares: cut-off high-low-high around bursts, electron rate low-high-low | Time evolution with a target-aware model, interpreted as acceleration; no test of history dependence |
| Collier et al. (2024), A&A (arXiv:2402.10546) | STIX + EOVSA pulsations of the X1.3 flare of 2022-03-30: images per peak, high-cadence spectral fits | Data benchmark for v3 |
| STIX superhot study (A&A 2026, arXiv:2511.09108) | Superhot (> 30 MK) components in 32 large STIX flares | Systematic: thermal emission can hide breaks below ~25–30 keV |
| Triangulation of the X5 flare of 2023-12-31 with ASO-S/HXI and STIX | Three distinct hard X-ray peaks; 3D source positions | Primary event already studied for geometry, not for spectral memory |

**Preliminary verdict:** the mechanisms are known. The **discriminating design** found no precedent in these searches:
- cumulative energy versus instantaneous flux as regressors for the break;
- hysteresis at matched flux;
- confinement of the hardening to the band around the break;
- reset with new footpoints.

Novelty is plausible but **not yet confirmed**.

ADS queries to run (gate G1):
1. `abs:("spectral break" OR "nonuniform ionization" OR "return current") AND abs:("time evolution" OR "hysteresis" OR "successive" OR "cumulative") AND abs:("hard X-ray")`
2. `abs:"soft-hard-harder" AND abs:("ionization" OR "target" OR "transport")`
3. `abs:"STIX" AND abs:("spectral break" OR "broken power law" OR "return current" OR "nonuniform ionization")`
4. Citations of Su et al. 2011 and Alaoui et al. 2019.


## 10. Addendum (2026-10-04): prior work for the v4 question

The project question is now v4 (`docs/00`): do successive hard X-ray pulses re-use the loops filled by earlier pulses, measured with the evaporated plasma as a tracer (predicted versus observed loop-top/footpoint ratio, conservative bound on the re-use fraction φ)?

**Search method.** Forward citations in OpenAlex of five seed papers (Su et al. 2011, Su et al. 2009, Liu et al. 2006, Veronig & Brown 2004 and Kong et al. 2022, the last one picked up by a search meant for Alaoui et al. 2019), about 375 citing works screened by title. About 20 abstracts were read. Targeted web and arXiv searches were run on 2026-10-04. ADS and Google Scholar were not used. Two works below were classified from their titles only, as marked.

| Work | What it does | Relation to v4 | Overlap |
|---|---|---|---|
| Liu, Liu, Jiang & Petrosian 2006, ApJ 649, 1124 | RHESSI M1.7: HXR sources rise from the footpoints and merge into a loop-top source as evaporation fills the loop | The qualitative behaviour expected under re-use, in one flare | High |
| Ning & Cao 2010, ApJ 717, 1232; Ning 2011, Sol. Phys. | Footpoints converging into the loop top in a Neupert-type flare; speeds of merging sources | Same, qualitative | High |
| Veronig & Brown 2004, ApJ 603, L117 | Coronal thick target in dense loops | The physics used by the tracer | High (physics) |
| Simões & Kontar 2013, A&A 551, A135 | Loop-top electron rates 1.7–8 times the footpoint rates, interpreted as trapping | An extra loop-top source that the bound must tolerate (it does) | High (observable) |
| Dennis et al. 2018, ApJ | Coronal HXR sources revisited, 13 flares | Systematics of loop-top sources | Medium |
| Fleishman et al. 2016, ApJ 816, 62 | 3D validation of the coronal thick-target model | Physics | Medium |
| Liu, Han & Fletcher 2010, ApJ 709, 58 | Model of elementary energy-release events in single loops with evaporation | Theory of single-loop events | Medium |
| Volpara et al. 2024, A&A | Regularized imaging spectroscopy with STIX along a loop | Tool for R(ε); competitor in method | High (method) |
| Mikuła, Mrozek & Kułaga 2026, A&A 706, A379 | STIX footpoint heights versus energy, plateau attributed to evaporation | Column memory seen with STIX | Medium |
| Krucker & Masuda 2026, A&A | Faint high-coronal HXR sources seen through occultation | Dynamic-range problem; occultation strategy | Medium |
| Mrozek et al. 2026, arXiv:2609.16862 | Three coronal sources with STIX in a failed eruption | Coronal sources at 5–20 % of the main one, invisible without occultation | Medium |
| Ryan et al. 2024 | HXI + STIX triangulation of the X5 flare of 2023-12-31 | Pilot event geometry | High (event) |
| Matsumoto et al. 2026, arXiv:2606.29979 | Stereoscopic HXR + microwave, X7.1 of 2024-10-01 | Stereo methods | Low |
| Grigis & Benz 2005; Inglis & Dennis 2012 (titles only) | Reconnection progressing along the arcade; pulse timing versus footpoint location | New loops per pulse seen by imaging | Medium |
| Reep et al. 2016; Rubio da Costa et al. 2016 | Multithread models that assume a new thread per burst | The assumption the test addresses | Medium |

**Verdict.**
- Found: the qualitative re-use behaviour (Liu 2006; Ning & Cao 2010), the coronal thick-target physics and the observable.
- Not found: a quantitative, pulse-by-pulse test of loop re-use with a physical prediction from the thermal emission, a conservative bound on φ, or a statistical sample.
- Novelty estimate: 3–4 out of 5, pending ADS.

ADS queries to run (gate G0):
1. `abs:("coronal thick target" OR "loop-top" OR "looptop") AND abs:("evaporation" OR "emission measure") AND abs:("successive" OR "repeated" OR "same loop" OR "new loops")`
2. `abs:("multithread" OR "multi-thread") AND abs:("hard X-ray") AND abs:("imaging" OR "loop top")`
3. `abs:"STIX" AND abs:("loop-top" OR "coronal source") AND abs:("footpoint")`
4. Citations of Liu et al. 2006, Ning & Cao 2010 and Simões & Kontar 2013.


## 11. Current assessment (v5.1, 2026-10-05): when does the independent-pulse approximation fail?

### 11.1 What the paper proposes

For two identical pulses in one loop, compare the response to the second pulse with the response of a relaxed atmosphere using four paired branches (no beam; test pulse only; pulse 1 only; pulse 1 and the test pulse). The contrast M_D(τ) is the error of the independent-pulse approximation for a diagnostic D. Map it against the waiting time τ and the beam flux, explain it with the state left by pulse 1, and judge it against numerical, beam and observational uncertainties fixed in advance ([methodology](00_objectives_and_methodology.md), Section 3). Benchmark reproduction, observational application and full distinguishability calibration are extensions, not the core.

This update incorporates a focused review of primary papers made during the project discussion and a critical review of v5. It is not an exhaustive literature search or evidence that no equivalent study exists.

### 11.2 Closest precedents and the distinction to establish

| Prior work | Established contribution | Required distinction for this project |
|---|---|---|
| [Kennedy et al. 2015](https://arxiv.org/abs/1504.07541) | Observed RHESSI beam evolution drives RADYN; atmospheric response and changing stopping depths are studied | History is retained implicitly; isolate its effect with paired branches |
| [Polito et al. 2018](https://arxiv.org/abs/1804.05970) | RADYN nanoflare strands; the initial loop state and Ec change where the beam deposits energy | Preheating as an initial condition, not as the history of an earlier pulse |
| [Bakke et al. 2022](https://arxiv.org/abs/2201.11961) | RADYN nanoflare loops at 1 and 3 MK; the 3 MK loop "represents a previously heated strand" and its electrons "deposit more of their energy in the corona" | **The mechanism, published as an initial condition.** Distinction: history delivered by a simulated earlier pulse, with a waiting time and paired controls |
| [Reep, Warren, Crump & Simões 2016](https://arxiv.org/abs/1607.06684) | **Seven electron-beam heating bursts on a single HYDRAD loop** (Emslie thick target, Ec ≈ 11 keV, δ ≈ 6, peak flux 5×10⁹ erg cm⁻² s⁻¹), rejected against observed Si IV / C II redshifts: "woefully inadequate" | **Closest precedent in code and physics.** But: no relaxed-loop control (the comparison is against observations), intervals neither stated nor scanned, sub-flare flux, and the aim is to reject the single-loop model for a TR diagnostic, not to measure the approximation's error |
| [Barnes, Bradshaw & Viall 2019](https://arxiv.org/abs/1906.03350); [Cargill 2014](https://ui.adsabs.harvard.edu/abs/2014ApJ...784...49C) | Repeated same-strand nanoflares with the heating frequency defined as ε = ⟨t_wait⟩/τ_cool (ε = 0.1 / 1 / 5), where a high-frequency strand "is not allowed to fully cool before being heated again"; forward-modelled AIA EM slopes and time lags | **Same-strand waiting time controlling a diagnostic is established; do not claim it.** But: ad-hoc volumetric heating with no beam ("does not assume any specific physical heating mechanism"), two-fluid EBTEL integrated over the corona rather than a resolved loop, no modelled chromospheric evaporation, waiting time coupled to event energy (t_wait ∝ q), and no paired counterfactual. It cannot address where a beam stops. **Report τ* in units of τ_cool to connect to this literature** |
| [Cho, Testa, De Pontieu & Polito 2023](https://arxiv.org/abs/2211.06832) | Table 2 includes a RADYN model with 20 s of heating, a 60 s pause and 20 s more (F = 6×10⁸ erg cm⁻² s⁻¹, Ec = 10 keV, δ = 7); models are compared statistically with IRIS footpoint brightenings | Simulating two separated episodes is not new. Distinction: flare fluxes, a waiting-time scan and a paired fresh-atmosphere control. Read the full text to confirm that the second response is not compared with a fresh one |
| [Kerr, Polito, Xu & Allred 2024](https://arxiv.org/abs/2405.02799) | 100 s of weak electron heating (5×10⁸) before flare fluxes changes the Mg II ribbon-front response; front lifetime measures the weak-heating duration | Weak → strong preconditioning with an observable is established. Distinction: strong → strong pulses separated by τ, with paired controls and a decision rule |
| [Litwicka, Heinzel & Kašparová 2025](https://doi.org/10.3847/1538-4357/adc393) | Filamentary (four consecutive pulses) versus continuous beam heating, on VAL-C and preheated VAL-C, changes synthetic chromospheric emission | Separate same-strand temporal memory from spatial mixing, pulse shape, area and energy-flux differences |
| [Litwicka et al., 2026 conference abstract](https://plan.events.mpg.de/event/453/contributions/3104/) | Nearby work on STIX/IRIS-constrained filamentary heating | Check subsequent publications and precise overlap; an abstract is not a completed peer-reviewed result |
| [Kašparová et al. 2009](https://arxiv.org/abs/0904.2084) | Sub-second electron-beam pulses and time-dependent hydrogen lines | Sub-second pulse trains, not waiting times of tens of seconds |
| [Rubio da Costa et al. 2016](https://arxiv.org/abs/1603.04951); [Reep et al. 2018](https://arxiv.org/abs/1802.08884) | Observation-driven multithread modelling; duration of heating on unresolved loops | They use the approximation under test; the result tells when it holds |
| [Allred et al. 2020](https://arxiv.org/abs/2008.10671); [Carlsson et al. 2023](https://arxiv.org/abs/2304.02618) | FP transport and radiation/deposition modelling; the public F-CHROMA grid (20 s triangular beam plus 30 s, closed boundaries, 10 Mm loop) | Tools and data: use and verify them; the grid alone covers τ ≤ 30 s |
| [Collier et al. 2024](https://arxiv.org/abs/2411.09319) | STIX fits drive a RADYN first-burst calculation with an EUV comparison | Optional benchmark (extension); a first burst carries no history |
| [Druett, Ruan & Keppens 2023](https://arxiv.org/abs/2310.11226) | Beam-driven evaporation in multidimensional MHD modelling | Adding MHD is not automatically novel; the core stays within prescribed geometry |

### 11.3 Strength of the proposed claim

- **Not novel by itself:** simulating two heating episodes; showing that preheating changes deposition or a line; STIX → RHD input tables; using FP; releasing a pipeline.
- **Incremental contribution:** a paired-branch map, at flare fluxes, of the error of the independent-pulse approximation versus τ and flux, with its physical origin, judged against uncertainties fixed before the contrast is computed.
- **Stronger result (extensions):** observed pulses struck again within the waiting times where the approximation fails, or a diagnostic that separates histories given the same STIX data.
- **Useful bound:** the approximation is adequate in the explored domain for the chosen diagnostic. Solver failures, or no visible effect without stated uncertainties, do not establish that.

Do not describe the work as the first such study before completing the targeted search. No journal outcome or impact level is guaranteed by this design.

### 11.4 Searches needed before the core runs

Search abstracts and full texts for repeated, successive, intermittent or recurrent electron-beam heating; reheating of the same strand; atmospheric preconditioning; time-dependent ionization and recombination; restart or counterfactual experiments. Include RADYN, HYDRAD, FLARIX and FP, and both solar and relevant stellar studies. Read the full texts of Cho et al. 2023, Kerr et al. 2024 and Litwicka et al. 2025 first.

Suggested ADS starting queries (adapt syntax as required):

```text
abs:("RADYN" OR "HYDRAD" OR "FLARIX") AND abs:("repeated" OR "successive" OR "intermittent" OR "reheating" OR "preheated" OR "memory")
abs:("electron beam" OR "electron-beam") AND abs:("preheating" OR "preconditioning" OR "pause" OR "waiting time") AND abs:"flare"
abs:("multithread" OR "multi-thread") AND abs:("flare") AND abs:("RADYN" OR "HYDRAD")
citations(identifier:"arXiv:2405.02799") OR citations(identifier:"arXiv:2211.06832") OR citations(doi:"10.3847/1538-4357/adc393")
```

Follow citations of the closest studies, read methods rather than only abstracts, record search dates and access limits, and revisit the assessment before submission.

### 11.5 Corrections to the historical v4 interpretation

[Liu et al. 2006](https://arxiv.org/abs/astro-ph/0603510) inferred an evolving density profile from loop brightness as well as describing source evolution; characterizing that precedent as only qualitative understates its scope.

The old tracer's EM-derived rms density is not a general lower bound on density along an electron path in nonuniform unresolved plasma. Tests that impose a true column above the estimated column verify the model conditional on that assumption. A monotonically declining ratio spectrum also does not establish a uniquely identifiable knee or exclude every trapping/acceleration alternative. These issues motivate keeping the tracer as optional historical infrastructure, not the premise of v5 or v5.1.

### 11.6 Gate 0: the closest full texts, read 2026-10-13

**Search and reading date:** 2026-10-13. This closes the Phase 0 item left open at R1. It is **not** the exhaustive ADS sweep of Section 11.4, which remains to be run.

**Read in full text.**

| Paper | Access | What the full text settles |
|---|---|---|
| [Cho et al. 2023](https://arxiv.org/abs/2211.06832) | arXiv full text | Model **E6** is the only two-episode run: 20 s heating, 60 s pause, 20 s again, F = 6×10⁸ erg cm⁻² s⁻¹, Ec = 10 keV, δ = 7, 15 Mm loop, one of 13 models. **No control containing only the second pulse, no statement about what the first episode changed, and no discussion of preheating, memory or waiting times anywhere in the paper.** E6 appears only in the grid, the Table 2 listing and the Figure 2 overlays, compared statistically with IRIS. The distinction assumed in Section 11.2 is therefore confirmed, not assumed |
| [Kerr et al. 2024](https://arxiv.org/abs/2405.02799) | arXiv full text | 100 s of weak heating at 5×10⁸ followed directly by an ad-hoc ramp to 1×10¹¹ over 100 s, on an 11 Mm half-loop. **No pause between the phases, no strong-only control on the relaxed atmosphere, no waiting-time scan, and no estimate of how much the preheated atmosphere changes the strong-phase response.** The scan is over the weak-phase duration (25–150 s) at matched total energy. The paper calls its own experiments "overly simplified" and the post-weak timing "arbitrary" |

**New precedent found, not previously in this review.**

[Bakke et al. 2022](https://arxiv.org/abs/2201.11961) (A&A 659, A186) — six RADYN nanoflare runs, 15 Mm half-loop, one 10 s beam each, F ≈ 1.2×10⁹ erg cm⁻² s⁻¹, δ = 7, Ec = 5/10/15 keV, apexes at 1 and 3 MK. The paper calls the 3 MK loop "pre-heated" and says it "represents a previously heated strand", and reports that "due to the higher initial density of the loops, the injected electrons deposit more of their energy in the corona" with a slower atmospheric response.

**Consequence for the claim.** This is the physical mechanism of the core, published as an **initial-condition** effect, as in Polito et al. 2018. The project must stop presenting the mechanism as its own finding. Objective O2 (explaining M through the state left by pulse 1) stays necessary as evidence that M is causal and not numerical, but it is **not** the novel element.

**Still inaccessible.**

[Litwicka, Heinzel & Kašparová 2025](https://doi.org/10.3847/1538-4357/adc393) (ApJ 983, 155) — HTTP 403 at IOP on 2026-10-02 and again on 2026-10-13; no arXiv preprint found by title, author or DOI. A paper citing it ([arXiv:2508.05875](https://arxiv.org/html/2508.05875v1)) describes it as FLARIX modelling in which flare heating is delivered as short pulses in unresolved filaments, to reduce the mismatch between modelled and observed chromospheric line intensities. **Second-hand, and not usable as a verdict.** To obtain: institutional access, the supervisor, or a request to the authors. The distinction to establish is unchanged from Section 11.2: separate same-strand temporal memory from spatial filamentation, area and flux differences.

### 11.7 Positioning sentence (written 2026-10-13)

> Two separated heating episodes have been simulated before, at nanoflare fluxes and without a fresh-atmosphere control (Cho et al. 2023); weak preheating is known to change a later strong response, without a waiting time or a paired control (Kerr et al. 2024); and a denser, previously heated strand is known to stop more of a beam in the corona, as an initial condition (Polito et al. 2018; Bakke et al. 2022). What this work adds is the **measurement of the error itself**: a paired-branch contrast, at flare fluxes, between the response of a re-struck loop and the response of a relaxed one, as a function of the waiting time and the beam flux, judged against numerical, beam and observational uncertainties fixed before the contrast is computed.

**Superseded by Section 11.8**, which concedes two further precedents found on the same day. Use the sentence in 11.8.

### 11.8 Third targeted pass, verified (2026-10-13): nanoflare frequency and repeated beam bursts

**What this pass was and was not.** A further targeted public-web pass was run on 2026-10-13 for repeated, recurrent and intermittent beam heating, same-strand waiting times and atmospheric preconditioning. **The NASA ADS search was again inaccessible**, so the exhaustive sweep of Section 11.4 is *still outstanding* and no absence-of-prior-work claim follows from this pass. Two precedents it surfaced were then checked by this author against the primary full texts, because an earlier pass in this same session wrongly reported that Bakke et al. 2022 contained two separated episodes.

**Verified precedent 1 — [Barnes, Bradshaw & Viall 2019](https://arxiv.org/abs/1906.03350)** (ApJ 880, 56). Confirmed from the full text: discrete triangular heating pulses of 200 s on a single strand, event energies from a power law of slope −2.5, heating frequency ε = ⟨t_wait⟩/τ_cool with ε = 0.1 (high), 1 (intermediate) and 5 (low), the waiting time defined as the gap between the end of one event and the start of the next, and a high-frequency strand that "is not allowed to fully cool before being heated again", with "multiple reheatings before the end of the cooling and draining cycle".

*Correction to the report that surfaced it,* which described this as field-aligned hydrodynamics with high core overlap. The code is **two-fluid EBTEL**, which "solves the time-dependent, two-fluid hydrodynamic equations spatially-integrated over the corona": not a resolved loop. Heating is **ad hoc and volumetric** into the electrons, and the paper "does not assume any specific physical heating mechanism" — there is no beam, no stopping column and **no modelled chromospheric evaporation**. The waiting time is **coupled to the event energy** (t_wait ∝ q, after Cargill 2014), so it is not a controlled scan, and the single-event "cooling" model is a population baseline, not a paired counterfactual.

*Consequence.* The nanoflare-frequency literature owns the idea that same-strand waiting time, measured against the cooling time, controls what a diagnostic shows. **This project must cite it and must not present waiting-time dependence as its own idea.** It cannot address the mechanism at issue here. Actionable improvement: report τ* **in units of τ_cool** as well as in seconds, so the result is legible to that community.

**Verified precedent 2 — [Reep, Warren, Crump & Simões 2016](https://arxiv.org/abs/1607.06684)** (ApJ 827, 145). The report inferred this from the introduction of Reep et al. 2018 and asked for verification. Verified, and **stronger than the report thought**: §III.1 states "We first attempted to model this event with a single loop, on which seven heating bursts occurred", with an **electron beam** under the collisional thick-target model of Emslie (1978), Ec ≈ 11 keV, δ ≈ 6, peak flux 5×10⁹ erg cm⁻² s⁻¹, **in HYDRAD** — the same code as this pilot. The conclusion is that "a persistent down-flow cannot be explained by constant heating, or with any number of heating bursts on a single loop", and §IV calls the single-loop model "woefully inadequate".

*Consequence.* Repeated electron-beam bursts in one HYDRAD loop have been run before. The framing "nobody has fired repeated beam pulses into the same loop" is dead. What survives: there is no relaxed-loop control (the comparison is against observations), the intervals are neither stated nor scanned, the flux is sub-flare, and the purpose is to reject a single-loop model for Si IV and C II rather than to measure the error of an approximation. The full figures of Reep et al. 2016 should still be read before the write-up.

**Litwicka et al. 2025 — partially cracked, and it helps.** A ResearchGate entry exposes substantial indexed primary text of *Filamentary Electron-beam Heating in Solar Flares*. The indexed passages state that the heated area is divided into **four subareas, each heated by one pulse in succession**, with the emergent Hα and Mg II k emission averaged over the subareas. The four pulses therefore **do not re-heat one strand**: the contrast is filamentary sequential-area heating versus continuous heating, which is a spatial experiment, not a same-strand temporal one. Status: **substantial primary text read in indexed extract; the PDF is still not verified page by page** (the page then returned HTTP 429). Not "fully read", and no longer "second-hand only".

**What the claim is now.** Three successive honest passes have each narrowed it. Conceded to prior work: repeated same-strand heating; waiting-time dependence normalised by a cooling time; repeated beam bursts in one HYDRAD loop; two separated beam episodes; preheating changing deposition; the mechanism itself. **What remains is purely methodological**, and that is the whole contribution: the paired counterfactual, the pre-registered uncertainty rule, and the resulting τ × F map at flare fluxes for a named diagnostic.

**Positioning sentence — superseded by Section 11.11.** Kept for the record:

> Repeated heating of the same strand is standard in nanoflare modelling, where the waiting time relative to the cooling time defines the heating frequency and controls the predicted diagnostics (Cargill 2014; Barnes et al. 2019); repeated electron-beam bursts on a single loop have been run in HYDRAD and rejected against observed transition-region redshifts (Reep et al. 2016); two separated beam episodes have been simulated at nanoflare fluxes without a fresh-atmosphere control (Cho et al. 2023); weak preheating is known to change a later strong response, without a waiting time or a paired control (Kerr et al. 2024); and a denser, previously heated strand stops more of a beam in the corona, as an initial condition (Polito et al. 2018; Bakke et al. 2022). This work adds none of those. It measures **the error itself**: a paired-branch contrast, at flare fluxes, between the response of a re-struck loop and that of a relaxed one, mapped against the waiting time and the beam flux, and judged against numerical, beam and observational uncertainties fixed before the contrast is computed.

**Still open, in priority order.**

1. **The ADS sweep of Section 11.4 has never been run** — three passes, three failures to reach it. It needs a human with ADS access, or the [search prompt](novelty_search_prompt.md) given to an agent that can actually query ADS. Until then, no first-of-its-kind claim.
2. Read the Litwicka et al. 2025 PDF end to end.
3. Read the full figures and methods of Reep et al. 2016 for its repeated-single-loop tests.
4. Screen the nanoflare-frequency literature properly (Cargill, Klimchuk, Bradshaw, Viall, Barnes) — it was absent from every earlier pass of this review and is the body of work this result must be legible to.
5. Repeat the search immediately before submission.

### 11.11 Fourth pass, verified (2026-10-13): Reep et al. 2016 already ran the contrast

**A correction of this review's own earlier statement.** Section 11.8 of this document reported, from a summarised read of Reep et al. 2016, that the seven-burst single loop was "compared against observations, not against a relaxed loop" and that "no relaxed-loop control is described". **That was wrong.** A direct re-read of the primary text settles it.

**Verified verbatim, Reep, Warren, Crump & Simões 2016, §3.1 and Figure 2:**

- "We first attempted to model this event with a single loop, on which seven heating bursts occurred."
- "We also attempted to model this event using a multi-threaded loop composed of seven strands, on each of which one heating burst occurred."
- Figure 2 caption: "Synthesized Si iv emission relative to IRIS for the two simulations: seven bursts of heating on a single loop (left) and seven threads with one heating burst each (right). The top plots show the synthesized intensity as a function of time while the bottom plots show the Doppler shift as a function of time."
- "in the monolithic loop simulation, the Doppler velocity shows only a single strong red-shift at the time of the first heating burst", against "the multi-threaded simulation shows seven strong red-shifts, corresponding to a heating event on each thread".
- Mechanism: "once evaporation brings material into the corona, later heating bursts cannot cause a strong velocity flow" … "due to the increased inertia".

**So, in 2016, in HYDRAD, with an electron beam (Ec ≈ 11 keV, δ ≈ 6, peak 5×10⁹ erg cm⁻² s⁻¹):** re-heating one loop was placed side by side with heating fresh strands, the synthetic diagnostic was shown to differ, and the difference was explained by the corona already being filled. **That is the qualitative contrast of this project, published, with a mechanism, ten years earlier.** No claim of discovering it can stand.

**What their experiment does not do, and this is now the whole distinction.**

1. **It is not a matched contrast.** One loop with seven bursts versus *seven* strands with one burst each differ in thread count, area and total mass, not only in history. That seven fresh strands give seven redshifts is in part a consequence of there being seven of them. Their design therefore cannot separate history from area and multiplicity. M_D is defined per unit area of **one** loop, with A0, B0, A1 and B1 sharing an identical geometry and an identical test pulse, so history is the only thing that varies.
2. **No difference-in-differences.** There is no no-beam baseline and no "test pulse alone on the relaxed atmosphere" branch, so the *incremental* response to a single later pulse is never isolated.
3. **No scan.** The burst times come from the observed hard X-ray light curve; neither the waiting time nor the flux is varied.
4. **No error budget and no threshold** fixed in advance, and the flux is below flare level.
5. **The aim is the opposite:** both toy models are rejected in favour of a >60-thread model. The question "when is the independence assumption adequate?" is never asked.

**An opportunity, from the same paper.** Reep et al. 2016 is HYDRAD with a beam and synthetic Si IV — the same solver as this pilot. It is therefore the **cheapest available benchmark** for this project's pipeline, and reproducing its Figure 2 qualitatively would answer the standing criticism that nothing here has been validated against a published result (extension E3), in the code that is already built. The biggest threat to the novelty claim is also the best validation target.

**Earlier still — [Emslie, Li & Mariska 1992](https://ui.adsabs.harvard.edu/abs/1992ApJ...399..714E)** (ApJ 399, 714), *Diagnostics of electron-heated solar flare models. III. Effects of tapered loop geometry and preheating*. Access level: **abstract only** (the full article was not obtained). Hydrodynamic simulations of electron-heated flare atmospheres compare preheated with non-preheated conditions, preheating parameterised by the initial upper-chromospheric pressure, with synthetic Ca XIX: in the preheated case "the atmosphere responds slowly" to collisional electron heating. Preheating there is an **initial condition**, as in Polito et al. 2018 and Bakke et al. 2022, not the end state of a simulated pulse — but it dates the preheated-versus-relaxed comparison to **1992**. Any framing in which that comparison is new is dead. Obtain the full text before writing the introduction.

**A verified opening, and it is the best card in this file — [Lörinčík, Polito, Kerr, Hayes & Russell 2025](https://arxiv.org/abs/2504.10619)** (ApJ 986, 73). Verified verbatim, §6.3: "all models considered in our study for simplicity assume a single instance of constant heating", and "Whether repeated heating of a single loop can reproduce the quasi-periodic intensity peaks … remains to be simulated in the future." Their observed Si IV peaks before Mg II by 1–6 s, quasi-periodic at 16–18 s, and §5.2 notes that "the modeled Si IV and Mg II lightcurves usually consisted of a single peak only".

*Why it matters:* Polito and Kerr are authors of Cho et al. 2023 and Kerr et al. 2024, the closest precedents in this file. In 2025 they state in print that repeated heating of a single loop remains to be simulated. That is the sentence this project's introduction should open on. *The caveat, which must not be dropped:* their open question is about multi-line chromospheric timing — Si IV, C II, Mg II — which the HYDRAD route **cannot** answer (no NLTE transfer). Pointing at this opening is an argument for the RADYN route or a collaborator at R2, not a claim the current route fulfils.

**Governing positioning sentence (current; overrides Sections 11.7, 11.8 and 11.9).**

> That a previously heated atmosphere responds differently to an electron beam has been modelled since Emslie, Li & Mariska (1992); that the waiting time relative to the cooling time controls a strand's predicted emission is standard in nanoflare modelling (Cargill 2014; Barnes et al. 2019); and Reep et al. (2016) placed seven beam bursts on one loop beside seven freshly heated strands and showed that the synthetic Si IV response differs, because evaporation has already filled the corona. This work claims none of that. It asks the question those studies leave open, and which Lörinčík et al. (2025) state remains to be simulated: **how large is the error**, for a stated diagnostic, of modelling a later flare-strength pulse on a relaxed atmosphere instead of the one its predecessor left — measured with four matched branches that hold geometry, area and test pulse fixed so that history is the only variable, mapped against the waiting time and the beam flux, and judged against numerical, beam and observational uncertainties declared before the contrast is computed.

**Standing after four passes.** Each pass has narrowed the claim, and this one removed its qualitative core. What remains is a **validity-boundary study**: not that memory exists, not that it changes a diagnostic, but *where the independence assumption is and is not good enough*, at matched conditions, with a pre-declared rule. That is a legitimate contribution and a modest one. It also makes Objective **O3 — the range where the approximation is adequate — the most valuable part of the project**, not a fallback: it is the only part no prior study provides.

**Open, and unchanged in priority.** The ADS sweep has still never been run (four passes, four failures to reach it). Then: the Emslie et al. 1992 full text; Reep et al. 2016 Figure 2 in detail, as a benchmark target rather than only a precedent; the Litwicka et al. 2025 PDF; and forward-citation screening of Reep 2016, Emslie 1992, Barnes 2019 and Lörinčík 2025 up to the submission date.

### 11.12 Systematic forward-citation screen (2026-10-13), and why the keyword half failed

**First reproducible step in this file.** Run against the OpenAlex REST API (open, no token; ADS still unreachable). Script kept with the session notes; it is reproducible from the seed list below.

**Part A — keyword sweep: UNRELIABLE, do not cite its counts.** `title_and_abstract.search` is a fuzzy relevance search, not a boolean operator. Two demonstrations: ANDing *RADYN OR HYDRAD OR FLARIX* with *repeated OR successive OR intermittent OR reheating* returned **0 hits**, which is impossible; and a flare + "same loop" + "repeated" query returned poetry, hydroponics and dermatology papers. Twenty such queries were run and discarded. Keyword coverage of this literature still requires ADS.

**Part B — forward-citation screen: reliable, and complete for its seeds.** Each seed resolved by DOI or exact title to an OpenAlex work id, then every citing work retrieved through the `cites:` filter with full pagination, and title **plus** indexed abstract screened against a concept pattern (repeat, reheat, preheat, memory, waiting time, second/later pulse, multiple heating, counterfactual, same loop/strand/thread, pulse train, recurrent, multi-episode, heating frequency, episodic, intermittent).

| Seed | Citing works screened | Flagged | Collision? |
|---|---|---|---|
| Reep et al. 2016 | 36 | 5 | No |
| Reep et al. 2018 | 28 | 3 | No |
| Cho et al. 2023 | 12 | 3 | No |
| Kerr et al. 2024 | 10 | 0 | No |
| Barnes et al. 2019 (2021 companion) | 9 | 2 | No |
| Bakke et al. 2022 | 10 | 1 | No |
| Litwicka et al. 2025 | 2 | 0 | No |
| Lörinčík et al. 2025 | 8 | 1 | No |
| Emslie, Li & Mariska 1992 | 50 | 10 | No |
| Rubio da Costa et al. 2016 | 30 | 0 | No |
| **Total** | **195** | **25** | **none** |

Most flags are pattern false positives ("independent", "successful"). **No citing work contains a paired-branch measurement of the approximation's error, a scanned waiting time at flare fluxes with matched controls, or a pre-declared adequacy threshold.** This is the first systematic screening in this review, and it does not overturn Section 11.11.

**Items to add to the citation list** (relevant, not collisions):

- [Tian et al. 2018](https://doi.org/10.3847/1538-4357/aaad10), *Multi-episode Chromospheric Evaporation Observed in a Solar Flare* — **observational motivation**: repeated evaporation episodes in one event. The best available answer to "does this happen in real flares?" without claiming same-strand re-use.
- Hori et al. 1997, 1998 — *Pseudo-two-dimensional hydrodynamic modeling* and *Single and Multiple Solar Flare Loops*: successive-loop hydrodynamics with Ca XIX, 1990s. Multi-loop rather than same-loop, but early and worth reading before the introduction.
- [Reep et al. 2020](https://doi.org/10.3847/1538-4357/ab75ac), *Simulating Solar Flare Irradiance with Multithreaded Models of Flare Arcades* — another user of the approximation under test; a natural citer of the boundary (O3).
- Nóbrega-Siverio et al. 2018 — non-equilibrium ionization of Si IV and O IV: the ionization channel of memory that HYDRAD cannot represent.
- Mondal et al. 2024; Sow Mondal et al. 2025 — nanoflare heating-frequency determination: the community that τ* in units of τ_cool speaks to.

**Limits of this pass, stated.** Not ADS. OpenAlex abstract coverage of older solar papers is patchy, so some citing works were screened on title alone; a collision with an uninformative title and no indexed abstract would be missed. No backward (reference-list) screening. Conference proceedings and pre-1990 literature are thin. The two closest seeds initially failed to resolve by guessed DOI and were recovered through their arXiv DOIs — a reminder that a null result here depends on the seed resolving at all.

**Standing.** The residual novelty risk is lower than after any previous pass, and for the first time it is quantified rather than asserted. ADS remains necessary for a priority claim, but it is no longer the only evidence: 195 citing works of the ten closest papers have now been screened without a collision.
