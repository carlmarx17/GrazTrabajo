# FP solver: what the manual and source say, and how it fits the project

**Author:** Carlos Alberto Martínez Sibaja
**Date:** 2026-10-03
**Sources read:** the manual `doc/FP.pdf` of [solarFP/FP](https://github.com/solarFP/FP) (10 pages, 532 895 bytes; read, not stored in the repository), plus `python/readatm.py` and `python/fpbrem.py` (viewed online). The FP code itself was **not** downloaded, compiled or run, and the paper (Allred et al. 2020, ApJ 902, 16) was read only at abstract level. Everything below is therefore "documented", not "tested".

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

1. **Atmosphere file format.** `readatm.py` reads an unformatted Fortran file (SciPy `FortranFile`): three int32 (`nz`, `nions`, `nneutrals`), then one real array in the order `zin`, `tg`, `bfield`, `dni[nz,nions]`, `dnn[nz,nneutrals]`, `mion`, `Zion`, `Zn`, `Enion`. There is **no writer** in the repository, so we must write one and validate it by reading back the bundled example atmospheres (`examples/atm.13Mm.3MK.dat`). Real-precision (single or double) and index order must be checked against those files.
2. **Ionization state from HYDRAD.** FP needs ion and neutral densities per species. HYDRAD gives total density and temperature and its own hydrogen ionization treatment (to be checked). The corona is fully ionized, which is where η_cor is decided; the chromospheric neutral fraction affects where the rest of the beam stops.
3. **Quasi-static assumption.** The electron transit time over a 13–26 Mm path is about 0.3 s for 20 keV, short compared with the 10 s pulses but comparable to the 0.2 s ramps. Declare it and exclude the ramps from the photon comparison.
4. **Bremsstrahlung treatment** (`fpbrem.py`): Haug (1997) electron–ion cross-section; **no electron–electron bremsstrahlung, no angular dependence, no albedo**; ions through a mean-Z² factor. This is adequate for a *differential* result: the same treatment applies to pulse 1 and pulse 2, so ΔB = B₂ − B₁ largely cancels common systematics, whereas the absolute B₁ does not. The standard cold-thick-target fit uses another cross-section, so B₁ ≠ 0 is expected and is part of the baseline. Albedo should be added to both or to neither.
5. **No bundled warm-target electron photon validation.** `compare_fp_t86` covers protons; `compare_fp_e78` covers cold electrons. We must validate the electron photons in a warm target ourselves, for example FP on an isothermal uniform atmosphere versus the analytic warm-target function of OSPEX (`f_thick_warm`). This validation is also the negative control of `docs/00` (Section 6.9).
6. **Energy grid.** The default `Emax = 2000·Ecut` (tens of MeV) with `nE = 100` would be coarse in the 4–100 keV STIX range; set `Emax` lower and test convergence in `nE`. `Emin = 1 keV` is adequate for kT of a few keV.
7. **Geometry.** The beam is injected at the loop top (z measured from the photosphere in `zin`, from the loop top in `z`); only a half loop is described. Our HYDRAD loop has to be mapped to a half loop with a uniform field (`inc_magmirror` off).
8. **Build.** Needs a Fortran compiler, MPI and HDF5 with Fortran bindings. None is installed on this Mac; it needs either a package-manager install or the cluster. Smaller dependency chain than RADYN (no NASA CDF library), but not trivial.
9. **Cost unknown.** Each run is an iterative nonlinear solve (`maxiter` 100, tolerances in the manual); the wall time per snapshot and beam is not documented.

## 4. Consequence for the plan

- **A more decisive first test.** With FP the gate no longer needs to rest on the column ratio. Take two HYDRAD snapshots (relaxed atmosphere and atmosphere at the onset of pulse 2), run FP with the same beam on both and compare the fraction of `heatrate` deposited above the transition region (η_cor) and the photon spectra. This addresses the criticism that the column ratio was neither necessary nor sufficient for the inference bias. It requires the FP build (Section 3, item 8) and the atmosphere writer (item 1). The column ratio stays as a first, cheaper look.
- **The forward model shrinks.** The expensive custom-transport step of the 20-week plan is replaced by an existing, published solver. What remains to build: the atmosphere writer, the thermal-emission calculation, the STIX response, the fit, and the validation of item 5.
- **Consistency check.** `heatrate(z)` from FP on a snapshot can be compared directly with HYDRAD's Hawley–Fisher heating on the same snapshot, bounding the circularity of letting HYDRAD heat the atmosphere with the cold-target assumption.
- **Still open:** whether the photon spectra of FP, fitted with the standard model, give a ΔB larger than the Poisson noise of a real STIX event. This is the value question and is not answered by any documentation.

## 5. Next verification steps (cheap, in this order)

1. Install the toolchain (compiler, MPI, HDF5 with Fortran bindings) or use the cluster; build FP and run the bundled examples `compare_fp_e78` and `compare_fp_h12`.
2. Write the atmosphere writer and verify it by round trip with `readatm.py` and by reproducing an example.
3. Convert one HYDRAD snapshot (E5 at pulse-2 onset) to an FP atmosphere and run FP with the base beam.
4. Time the run and check convergence in `nE`, `nmu` and `Emax`.
