# Prior work and novelty assessment

**Author:** Carlos Alberto Martínez Sibaja
**Search date:** 2026-10-02 (second pass, deeper than the earlier one on the same day).

> **Scope warning.** Sections 1–7 assess the **previous** research question (v1: "how much atmospheric memory is there after successive pulses"). The project question is now the **bias of STIX electron inference in successive pulses** (`docs/00_objectives_and_methodology.md`, v2). Sections 1–7 remain valid as a literature map but the novelty verdict does **not** transfer; the current question is assessed only preliminarily in Section 8.

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
