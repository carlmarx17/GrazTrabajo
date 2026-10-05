# Atmospheric Memory under Repeated Electron-Beam Heating: When Does the Independent-Pulse Approximation Fail?

**Author:** Carlos Alberto Martínez Sibaja ([@carlmarx17](https://github.com/carlmarx17))

**Status:** research plan v5.1, 2026-10-05. The core experiment's inputs and analysis code are implemented and tested; the HYDRAD pilot driver builds and runs, but its first smoke test showed that branch B1 (second pulse) is expensive with the default mesh refinement. Production runs, the chromospheric route and the extensions remain to be done.

## Research question

**When does treating each electron pulse as if it struck the initial, relaxed atmosphere misrepresent the response to a later pulse by more than the beam, numerical and observational uncertainties of a chosen diagnostic?**

Multithread and observation-driven flare models usually heat each strand once from a relaxed state. This project measures, in simulations, when that independent-pulse approximation fails for a loop that is struck again, and why.

## Core experiment

All runs start from the same atmosphere; pulse 1 and the test pulse b are identical:

```text
A0  no beam                         B0  test pulse b on the relaxed atmosphere
A1  pulse 1, no test pulse          B1  pulse 1, waiting time tau, then b

M_D(tau, t') = [D(B1) - D(A1)] - [D(B0) - D(A0)]      at equal time t' after the onset of b
```

- **Error measure:** M_D is the error, for the diagnostic D, of the independent-pulse approximation.
- **Decision rule:** the approximation fails where |M_D| > k·σ_tot. σ_tot combines numerical, beam and observational uncertainties, fixed before any contrast is computed.
- **Relaxation:** whether pulse 1 has relaxed is judged from the state of A1 versus A0, not from M_D → 0.
- **Outputs:** the waiting time τ* below which the approximation fails, its dependence on beam flux, and the physical mechanism.

The pilot uses HYDRAD in its documented stable domain: F ≈ 1.3×10¹⁰ erg cm⁻² s⁻¹, 30 s pulses, 26 Mm loop, with coronal proxies. RADYN with Fokker–Planck transport is the preferred route for chromospheric lines, once it is built and verified.

## Ready to test

```bash
.venv/bin/python -m pytest -q
```

```bash
.venv/bin/python src/experiments.py
```

```bash
scripts/build_hydrad_scratch.sh ../hydrad-scratch
```

```bash
.venv/bin/python scripts/hydrad_paired_branches.py ../hydrad-scratch --taus 10 30 60 120
```

1. The tests cover the beam tables, the paired branches and the contrast/decision code.
2. `src/experiments.py` writes the HYDRAD and RADYN beam tables of the paired branches (`results/paired_branches/`).
3. `build_hydrad_scratch.sh` copies `vendor/HYDRAD` to a scratch directory and builds it with beam heating.
4. `hydrad_paired_branches.py` runs the four branches per waiting time and writes `results/paired_branches_hydrad/summary.json`.
   - The summary contains the pre-test identity check, relaxation at t_k and M_D for coronal proxies.
   - Add `--sigma sigma.json`, written before the run, to apply the decision rule.

## Extensions to discuss

These are not part of the committed core:

- STIX pulse-resolved observations of re-struck footpoints and waiting times;
- STIX-conditioned inference (same HXR, different histories);
- benchmark reproduction of a published case;
- full distinguishability calibration;
- a third pulse;
- independent-thread bookkeeping;
- FP transport sensitivity;
- the X5.0 third hard X-ray source;
- collaboration with groups running RADYN or FLARIX;
- the archived v4 loop-re-use tracer.

See [the plan](docs/00_objectives_and_methodology.md), Section 8.

## Current implementation

| Component | Role |
|---|---|
| `src/experiments.py` | Paired branches A0/B0/A1/B1 (core); E1–E5 matrix kept for extensions |
| `src/memory_contrast.py` | Contrast M_D, σ_tot, k σ rule, τ*, relaxation check |
| `scripts/build_hydrad_scratch.sh`, `scripts/hydrad_paired_branches.py` | HYDRAD pilot of the core |
| `src/beam_tables.py`, `src/radyn_ftab.py` | Beam encoding for HYDRAD and RADYN, with energy checks |
| `src/fp_atmosphere.py` | FP atmosphere file reader/writer |
| `src/toy_bias.py`, `src/tracer.py` | Earlier simplified inference model and archived v4 tracer |
| STIX search and X5.0 first look | Exploratory observational infrastructure (extensions) |

The Python tests validate these utilities. They do not validate a production solver, a published benchmark or a detected memory signature.

## Documentation

- [Objectives and methodology](docs/00_objectives_and_methodology.md): authoritative v5.1 plan with the core experiment, decision rule, ready-to-test list, flexible work plan and extensions.
- [Prior work and novelty](docs/03_novelty_and_prior_work.md): current assessment in Section 11; earlier sections are historical.
- [HYDRAD implementation](docs/01_hydrad_code.md), [RADYN verification notes](docs/04_radyn_access.md) and [FP verification notes](docs/05_fp_solver_verification.md) describe solver capabilities and outstanding checks.
- [Earlier usefulness tests](docs/06_usefulness_tests.md): exploratory column and spectral-bias results; the source of the pilot domain.
- [X5.0 first look](scripts/x5_first_look/README.md): exploratory imaging.
- [Project working guide](skills/stix-rhd-memory/SKILL.md).
- Archived designs: [v4 loop re-use](docs/archive/00_objectives_v4_loop_reuse.md), [v3 spectral memory](docs/archive/00_objectives_v3_spectral_memory.md), [v2 inference bias](docs/archive/00_objectives_v2_inference_bias.md).

## Environments

The base environment runs the models, the HYDRAD drivers and the tests:

```bash
python3 -m venv .venv
```

```bash
.venv/bin/pip install -r requirements.txt
```

STIX analysis uses a separate Python ≥ 3.10 environment:

```bash
uv venv -p 3.12 .venv-stix
```

```bash
uv pip install --python .venv-stix -r requirements-stix.txt
```

HYDRAD is built from `vendor/HYDRAD` with the system C++ compiler. RADYN and FP are not installed by these commands; their requirements are in the solver notes.

Record configuration, beam tables, initial states, code revisions, σ values and failed runs for every production run. Data and generated results are git-ignored.

## Attribution

The repository includes upstream HYDRAD source under its MIT licence. Cite the upstream simulation, transport, atomic-data and observational tools actually used; see [third-party notices](THIRD_PARTY_NOTICES.md).
