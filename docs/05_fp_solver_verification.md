# FP solver: what the manual and source say, and how it fits the project

**Author:** Carlos Alberto Martínez Sibaja
**Date:** 2026-10-03
**Sources read:** the manual `doc/FP.pdf` of [solarFP/FP](https://github.com/solarFP/FP) (10 pages, 532 895 bytes; read, not stored in the repository), plus `python/readatm.py` and `python/fpbrem.py` (viewed online). At the initial documentation pass the FP code had **not** been downloaded, compiled or run (Section 6 records later file-I/O and Python checks); the paper (Allred et al. 2020, ApJ 902, 16) was read only at abstract level. The initial capability assessment is documentation-based; Section 6 identifies the tests that were subsequently executed.

> **Current role (v5.1, 2026-10-05):** these are dated capability and verification notes, not evidence of a completed solver run. Section 6 supersedes the earlier missing-writer status: `src/fp_atmosphere.py` exists and its file-format checks passed. The Fortran transport solve and production FP–RHD feedback remain unverified here. Snapshot post-processing is exploratory; the current solver routes are in [the methodology](00_objectives_and_methodology.md), Section 4; standalone FP is the transport-sensitivity extension E7. Legacy SQ labels below refer to earlier designs.

**Licence:** Apache-2.0 (keep the NOTICE/licence text if code is redistributed; cite Allred et al. 2020; the repository provides `paper.bib`).

## 1. What FP is, according to its manual

- Fortran 95 + MPI + HDF5 (with Fortran bindings); Python ≥ 3.4 and IDL wrappers (numpy, scipy, h5py, matplotlib). Tested on macOS and Linux, not Windows.
- Solves a **steady-state** Fokker–Planck problem for one given loop stratification and one injected distribution. It has no time stepping and no hydrodynamics: the atmosphere must come from another code (it has been used as input to RADYN).
- Forces (switches): relativity, Coulomb collisions, synchrotron, magnetic mirroring, return current. Pitch-angle grid (1.5D) or fully 1D.
- **Inputs of the injected beam:** `Ecut` [keV], `dlt` (power-law index), `Eflux` [erg cm⁻² s⁻¹], pitch-angle type and width, energy grid (`Emin` 1 keV, `Emax` 2000·Ecut, `nE` 100 by default).
- **Atmosphere (`atmfile`)**: z, gas temperature, magnetic field, ion densities (per species), neutral densities (per species), masses, charges, atomic numbers and ionization energies of the neutrals.
- **Outputs:** distribution `f(z, μ, E)`, `heatrate(z)` [erg cm⁻³ s⁻¹], `momrate(z)`, energy and number fluxes, and for electrons the bremsstrahlung `brem(E, z)` [ph cm⁻³ s⁻¹ keV⁻¹] and `totbrem(E)` integrated over z.
- **Bundled validation examples:** `compare_fp_e78` (cold-target electrons versus Emslie 1978, with and without return current), `compare_fp_h12` (return current versus Holman 2012), `compare_fp_t86` (protons, cold versus warm target, Tamres et al. 1986).

## 2. Alignment with the project

| Project need | What FP offers | Verdict |
|---|---|---|
| Beam parameters from STIX fits (F = P/A, Ec, δ) | `Eflux`, `Ecut`, `dlt` are the same quantities as our beam tables | **Aligned** |
| Arbitrary atmosphere with history | `atmfile` accepts any stratification (T, B, ion and neutral densities) | **Aligned**, with the writer caveat in Section 3 |
| Warm target | Collisions use the gas temperature; the paper states no cold- or warm-target assumption | **Aligned**; bundled warm-target validation is for protons only (Section 3) |
| Return current | `inc_rc` on by default, self-consistent | **Aligned** |
| Fraction of energy deposited in the corona (η_cor, SQ1) | `heatrate(z)` | **Aligned and better than the column test** (Section 4) |
| Photon spectra for the re-inference (SQ2) | `brem(E, z)`, `totbrem(E)` | **Aligned** (limits in Section 3) |
| Loop-top / footpoint ratio R_LF (SQ4) | `brem` is resolved in z, so it can be integrated over regions | **Aligned** |
| Decomposition of the bias by mechanism (SQ3) | Switches for collisions and return current; densities of ions and neutrals set the ionization state; thermal emission is separate | **Partly aligned**: there is no cold-target switch; a cold case is emulated by setting the temperature low |
| Atmosphere that evolves between pulses | Not provided: no time dependence | **By design decoupled**: HYDRAD (or RADYN) supplies snapshots; FP is quasi-static |
| Thermal emission of the hot plasma | Not provided | **Must be added** (isothermal/multithermal from the simulated T and EM, e.g. with sunkit-spex) |
| STIX response and fit | Not provided; the paper says FP can be a plug-in to OSPEX | **Outside FP**: OSPEX or sunkit-spex |
| Sweeps | MPI-parallel; cost per run not documented | **Unknown**: measure in a pilot |

## 3. Gaps and cautions found

1. **Atmosphere file format.** `readatm.py` reads an unformatted Fortran file (SciPy `FortranFile`): three int32 (`nz`, `nions`, `nneutrals`), then one real array in the order `zin`, `tg`, `bfield`, `dni[nz,nions]`, `dnn[nz,nneutrals]`, `mion`, `Zion`, `Zn`, `Enion`. At the initial inspection there was **no project writer**; Section 6 records the subsequently implemented writer and its validation by reading back the bundled example atmospheres (`examples/atm.13Mm.3MK.dat`). The example-file checks resolved the record layout and precision; physically valid conversion of production atmospheres remains a separate task.
2. **Ionization state from HYDRAD.** FP needs ion and neutral densities per species. HYDRAD gives total density and temperature and its own hydrogen ionization treatment (to be checked). The corona is fully ionized, which is where η_cor is decided; the chromospheric neutral fraction affects where the rest of the beam stops.
3. **Quasi-static assumption.** The electron transit time over a 13–26 Mm path is about 0.3 s for 20 keV, short compared with the 10 s pulses but comparable to the 0.2 s ramps. Declare it and exclude the ramps from the photon comparison.
4. **Bremsstrahlung treatment** (`fpbrem.py`): Haug (1997) electron–ion cross-section; **no electron–electron bremsstrahlung, no angular dependence, no albedo**; ions through a mean-Z² factor. This is adequate for a *differential* result: the same treatment applies to pulse 1 and pulse 2, so ΔB = B₂ − B₁ largely cancels common systematics, whereas the absolute B₁ does not. The standard cold-thick-target fit uses another cross-section, so B₁ ≠ 0 is expected and is part of the baseline. Albedo should be added to both or to neither.
5. **No bundled warm-target electron photon validation.** `compare_fp_t86` covers protons; `compare_fp_e78` covers cold electrons. We must validate the electron photons in a warm target ourselves, for example FP on an isothermal uniform atmosphere versus the analytic warm-target function of OSPEX (`f_thick_warm`). This is a potential transport-verification check, distinct from the history-omission controls in v5; match assumptions before interpreting agreement.
6. **Energy grid.** The default `Emax = 2000·Ecut` (tens of MeV) with `nE = 100` would be coarse in the 4–100 keV STIX range; set `Emax` lower and test convergence in `nE`. `Emin = 1 keV` is adequate for kT of a few keV.
7. **Geometry.** The beam is injected at the loop top (z measured from the photosphere in `zin`, from the loop top in `z`); only a half loop is described. Our HYDRAD loop has to be mapped to a half loop with a uniform field (`inc_magmirror` off).
8. **Build.** Needs a Fortran compiler, MPI and HDF5 with Fortran bindings. None is installed on this Mac; it needs either a package-manager install or the cluster. Smaller dependency chain than RADYN (no NASA CDF library), but not trivial.
9. **Cost unknown.** Each run is an iterative nonlinear solve (`maxiter` 100, tolerances in the manual); the wall time per snapshot and beam is not documented.

## 4. Consequences for the v5 plan

- **Exploratory transport check:** FP on relaxed and previously heated HYDRAD snapshots with the same test beam can reveal changes in energy deposition and photons. This is useful before a large ensemble, but does not reproduce a published atmospheric benchmark or establish the feedback on the atmosphere.
- **Production requirement:** establish a verified coupled route that updates transport with the evolving atmosphere and uses consistent deposition and applicable atomic source terms. Compare FP and analytic heating as a sensitivity check; a difference in deposition must be propagated through the dynamics or bounded before treating snapshot post-processing as an adequate approximation.
- **Reusable work:** the atmosphere writer is implemented and its file format tested. Physical species/ionization mapping, actual FP execution, energy accounting, convergence and production diagnostic synthesis remain to be verified.
- **Science endpoint:** the main v5 quantity is the incremental atmospheric and observable response to a later pulse, and whether it can be distinguished under uncertainty. Spectral-inference bias remains an optional consequence; a small bias is not a reason by itself to reject the atmospheric-memory study.

## 5. Next verification steps (cheap, in this order)

1. Install the toolchain (compiler, MPI, HDF5 with Fortran bindings) or use the cluster; build FP and run the bundled examples `compare_fp_e78` and `compare_fp_h12`.
2. File-format writer verification is completed in Section 6; next validate the species, geometry and ionization mapping for actual solver snapshots.
3. Convert one HYDRAD snapshot (E5 at pulse-2 onset) to an FP atmosphere and run FP with the base beam.
4. Time the run and check convergence in `nE`, `nmu` and `Emax`.

## 6. Tests actually run (2026-10-03)

The FP repository was cloned (shallow, outside this repository) and everything that does not need a Fortran compiler was executed in an isolated Python environment (numpy 2.0, scipy 1.13). **The Fortran solver itself was not compiled or run**: no Fortran compiler, MPI or HDF5 is installed on this machine. Scripts were run interactively; the reusable part is `src/fp_atmosphere.py` with `tests/test_fp_atmosphere.py`.

| Test | Result |
|---|---|
| FP's own `readatm.py` on the example atmosphere `atm.13Mm.3MK.dat` | Works (nz = 191, 4 ion species, 2 neutral species, half loop 13.1 Mm, T from 4.4×10³ to 3.4×10⁶ K, B from 75 to 1000 G) |
| Decoding of the file layout and writing it back with our own writer | **Byte-identical for all three example atmospheres.** Species 0 of the ions is the electron population, then H⁺, He⁺, He⁺⁺; neutrals H and He. Densities are depth-major `(nz, nspecies)`; physical sanity of the apex and bottom values confirms the ordering |
| `src/fp_atmosphere.py` unit tests | 4 tests pass (round trip, record layout, depth-major order, rejection of inconsistent or corrupt files) |
| FP's analytic cold-target heating (`qh_e78`: Emslie 1978 with Hawley & Fisher 1994, the formula HYDRAD also uses) on the example loop | Conserves energy (91 % and 89 % of the injected flux for δ = 4, Ec = 20 keV and δ = 5, Ec = 13.4 keV; the rest is cut off by the grid) |
| FP's analytic warm-target heating (`qh_warmtarget`, Tamres et al. 1986) applied to electrons in the same 3 MK loop | **Not trustworthy as an independent reference for electrons:** it deposits 100 % of the energy in the corona (T > 10⁵ K), and for δ = 5, Ec = 13.4 keV it returns 116 % of the injected energy; the root finder warns of poor convergence. The authors validate it for protons only. Do not use it as a benchmark here |
| Toy decision gate: fraction of the energy deposited at T > 10⁵ K, cold target (E78+HF94), when the coronal density of the example loop is scaled by k (coronal column to 10⁵ K is 1.1×10¹⁹ cm⁻² at k = 1) | δ = 4, Ec = 20 keV: 4.5 % (k = 1), 15 % (3), 64 % (10), 88 % (30). δ = 5, Ec = 13.4 keV: 13 %, 56 %, 92 %, 98 %. See the caveat below |
| `Brm_BremCross` (Haug cross-section) used to build a thick-target photon spectrum from a power-law electron distribution | Photon index 2.76 for δ = 4 and 3.87 for δ = 5 between 40 and 120 keV, against δ − 1 = 3 and 4. Consistent within 0.13–0.24; this is an order-of-magnitude sanity check and not a validation (the standard model, OSPEX `thick2`, should be compared directly) |

**Caveat on the toy gate.** It scales all species of the coronal part of a 3 MK model by a constant and uses the cold-target formula, not FP and not a hydrodynamic atmosphere. It shows that the deposition regime is very sensitive to the coronal density in the range expected after evaporation (a factor of a few to ten), which supports H1; it does not show that HYDRAD will produce such a density at F ≈ 1.3×10¹⁰, which is what the column test must establish.

### Findings about the code itself

- **Maintenance:** 11 commits; the last one is 2021-04-23. The GitHub page shows 9 stars and no issues. No independent report of a standalone installation was found; the documented uses are inside RADYN (several RADYN papers from the Goddard and Colorado groups describe RADYN as updated to use FP) and as an OSPEX plug-in for RHESSI inversions.
- **Bug fix after the release:** the commit of 2021-04-23 corrects, among other things, the normalisation of the Gaussian pitch-angle distribution (a misplaced parenthesis in `beam.F90`) and the pitch-angle solid-angle weighting of the injected distribution, and rewrites parts of the boundary conditions. **Use the master branch (a7c7f31), not the v1.0 tag of September 2020**, and treat the energy-flux normalisation as something to verify (injected flux versus `eflux` at the top).
- **Bremsstrahlung:** `fpbrem` uses hydrogen densities (`dnn[:,0] + dni[:,1]`) times Z² with a single mean atomic number (default 1.2) and no neutral-atom screening.

### What is still unknown

Whether FP compiles and runs on this machine or on the cluster, its run time, and whether its photon spectra, fitted with the standard model, give a ΔB above the Poisson noise of a real STIX event.

