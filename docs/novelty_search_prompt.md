# Prompt for the exhaustive novelty search

Hand the block below to a research-capable AI with web/literature access. It implements
[03, §11.4](03_novelty_and_prior_work.md) and finishes what [§11.6](03_novelty_and_prior_work.md)
started on 2026-10-13. Paste it verbatim; it is self-contained.

---

## The task

You are doing a prior-art search for a solar-physics simulation paper in preparation. Your job is to **try to
break its novelty claim**, not to support it. A null result (nothing found) is a valuable answer, but only if the
search was real. Err towards reporting a collision.

## The claim under test

> Two identical electron-beam pulses are fired into the same 1D flare loop. Four simulation branches start from
> the same atmosphere: A0 (no beam), B0 (test pulse only, on the relaxed atmosphere), A1 (first pulse only),
> B1 (first pulse, a waiting time τ, then the test pulse). The contrast
> `M_D(τ,t′) = [D(B1) − D(A1)] − [D(B0) − D(A0)]`, at equal time t′ after the onset of the test pulse, **is the
> error of treating the second pulse as if it had struck the initial, relaxed atmosphere** (the
> "independent-pulse approximation"). The claimed contribution is the *measurement of that error* at flare
> fluxes (~10¹⁰ erg cm⁻² s⁻¹), mapped against the waiting time τ and the beam energy flux, judged against
> numerical, beam and observational uncertainties fixed **before** the contrast is computed.

The claim is **not** about the mechanism (a denser, previously heated corona stops more of the beam higher up).
That is already published as an initial-condition effect and is conceded.

## What is already established — do not spend effort re-deriving these

Full texts already read, with verdicts:

- **Cho, Testa, De Pontieu & Polito 2023** (arXiv:2211.06832): model E6 = 20 s heating, 60 s pause, 20 s again,
  F = 6×10⁸ erg cm⁻² s⁻¹, Ec = 10 keV, δ = 7, 15 Mm loop; one entry of a 13-model grid. No fresh-atmosphere
  control, no analysis of what the first episode left, no mention of preheating, memory or waiting times.
- **Kerr, Polito, Xu & Allred 2024** (arXiv:2405.02799): 100 s of weak heating at 5×10⁸ followed *directly* by a
  ramp to 1×10¹¹; 11 Mm half-loop. No pause, no strong-only control, no waiting-time scan, no error estimate.
  Scan is over weak-phase duration at matched total energy.
- **Bakke et al. 2022** (arXiv:2201.11961): six single-pulse RADYN nanoflare runs; the 3 MK loop is called
  "pre-heated" and "represents a previously heated strand", and electrons "deposit more of their energy in the
  corona". The mechanism, as an initial condition.
- **Polito et al. 2018** (arXiv:1804.05970): initial loop state and Ec change where the beam deposits energy.

Known and conceded as **not novel**: simulating two heating episodes; showing that preheating changes deposition
or a line; driving RHD with observed hard X-ray fits; using Fokker–Planck transport; releasing a pipeline.

## Deliverable 1 — retrieve one blocked paper

**Litwicka, Heinzel & Kašparová 2025**, ApJ 983, 155, doi `10.3847/1538-4357/adc393`. HTTP 403 at IOP on
2026-10-02 and 2026-10-13; no arXiv preprint found by title, author or DOI. Find any legitimate full text
(author copy, institutional repository, ADS full-text link, conference proceedings version, or the authors'
own page). If you retrieve it, answer: does any later pulse get compared against a relaxed-atmosphere control?
Is a pause between pulses varied? Is the error of the per-pulse initial-atmosphere assumption quantified? How is
the "preheated VAL-C" atmosphere obtained — as an initial condition or as the end state of a simulated pulse?
If you cannot retrieve it, say so plainly and list exactly what you tried.

## Deliverable 2 — the sweep

Search ADS, arXiv, A&A, ApJ, ApJL, Solar Physics, MNRAS and relevant conference proceedings. Cover solar **and**
stellar flare work. Starting queries, to be adapted and extended:

```text
abs:("RADYN" OR "HYDRAD" OR "FLARIX" OR "RADYN+FP") AND abs:("repeated" OR "successive" OR "intermittent" OR "recurrent" OR "reheating" OR "preheated" OR "memory")
abs:("electron beam" OR "electron-beam") AND abs:("preheating" OR "preconditioning" OR "pause" OR "waiting time" OR "quiescent interval") AND abs:"flare"
abs:("multithread" OR "multi-thread" OR "multi-stranded") AND abs:"flare" AND abs:("RADYN" OR "HYDRAD")
abs:("same strand" OR "same thread" OR "same loop") AND abs:("re-energized" OR "restruck" OR "repeatedly heated")
abs:("time-dependent ionization" OR "non-equilibrium ionization") AND abs:("flare" OR "beam") AND abs:("recombination" OR "memory")
citations(identifier:"arXiv:2405.02799") OR citations(identifier:"arXiv:2211.06832") OR citations(doi:"10.3847/1538-4357/adc393")
citations(identifier:"arXiv:2201.11961") OR citations(identifier:"arXiv:1804.05970")
full:("counterfactual" OR "control simulation" OR "paired simulation") AND abs:("flare" AND "heating")
```

Also search for the concept under other vocabularies, because the field may not call it "memory": atmospheric
preconditioning, hysteresis, loop history, cumulative heating, pulse train, burst-to-burst variation, secondary
heating episode, and the stellar-flare equivalents.

## Deliverable 3 — classify every hit

For each relevant paper, state: reference; whether you read the **full text** or only the abstract; and which of
these it contains:

| Ingredient | Yes / No / Unclear |
|---|---|
| Two or more *separated* heating episodes in the same loop or strand |  |
| Flare-level energy flux (≳10¹⁰ erg cm⁻² s⁻¹) in the later episode |  |
| A control run with **only** the later pulse, on the relaxed atmosphere |  |
| An explicit contrast or difference between the re-struck and the fresh response |  |
| A waiting time / pause that is **varied or scanned** |  |
| Any error or uncertainty budget the difference is judged against |  |
| A decision rule or threshold fixed before the comparison |  |

Then rate the collision: **kills the claim** (all of rows 1–5 present) / **narrows it** (rows 1–4) /
**adjacent** (rows 1–2) / **background**.

## Rules you must follow

1. **Verify everything against the primary text.** Do not trust secondary descriptions, citing papers, review
   summaries, or your own recollection. A previous search of this literature returned a confident claim that
   Bakke et al. 2022 contained "two 20 s episodes separated by 60 s"; the full text has single 10 s pulses only.
   Quote the sentences you rely on, **verbatim**, with section numbers.
2. **Never fabricate** a reference, DOI, arXiv ID, author list, model parameter or quotation. If you are not
   sure a paper exists, say so and stop.
3. **Distinguish what you read from what you inferred.** Abstract-only hits are labelled abstract-only.
4. **Record the search**: dates, databases, the exact queries you ran, result counts, and every paywall or 403.
5. **Exclude the project's own material from the evidence.** A public GitHub repository named `GrazTrabajo`
   (user `carlmarx17`), and any plan or note inside it, is *this project's own design*. Search engines surface it
   as a near match. It is not prior art, and it is not independent confirmation. Say if you encounter it, then
   ignore it.
6. **Read methods, not abstracts**, for anything you rate as killing or narrowing the claim.

## Output

1. **Verdict in one paragraph**: does the claim survive? If narrowed, give the narrowed version in one sentence.
2. The classification table for every hit, most threatening first.
3. The Litwicka result, or what you tried.
4. The search record (queries, dates, counts, access failures).
5. **Up to five concrete suggestions** for sharpening the contribution, each tied to a specific paper.
6. Anything you were unable to check, stated as a gap rather than left out.
