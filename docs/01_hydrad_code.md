# First reading of HYDRAD

HYDRAD does not solve the full MHD equations. Along a fixed field line it solves mass, momentum and electron and ion energy, with gravity, thermal conduction, radiation and heating. For this project the decisive term is the beam heating, `Q_beam(s,t)`.

## Execution path

`HYDRAD/source/main.cpp` is deliberately short: it creates `CAdaptiveMesh`. The constructor of that class, in `HYDRAD/source/mesh.cpp`, reads the configuration, builds the adaptive mesh and runs the time advance. The physics of each cell lives in `HYDRAD/source/eqns.cpp`.

The dependency is:

```text
main.cpp → CAdaptiveMesh (mesh.cpp) → CEquations (eqns.cpp)
                                      ├─ CHeat (Heating_Model/source/heat.cpp)
                                      ├─ CRadiation (Radiation_Model/source/)
                                      └─ CKinetic (Kinetic_Model/source/)
```

`CEquations::Initialise()` opens `HYDRAD/config/hydrad.cfg`, loads the initial profile, the gravity and the run time. It then creates `CHeat` and the radiation objects. The mesh decides where to refine in order to resolve the chromosphere–corona transition during evaporation.

## Electron beam input

The input is `Heating_Model/config/beam_heating_model.cfg`. Each row has:

```text
time [s]    energy flux [erg cm^-2 s^-1]    Ec [keV]    δ
```

`CHeat::GetBeamHeatingData()` reads that table. With a single row it applies a constant beam for the stated time; with several rows, `CHeat::CalculateBeamParameters()` interpolates linearly between rows and switches the beam off before the first and after the last row. This is exactly the interface that will be built from STIX fits: each spectral interval produces one row.

`CHeat::CalculateBeamHeating()` converts `(F, Ec, δ)` into deposited energy per column depth. `CEquations` adds that rate to the energy equations. The expected physical outcome is chromospheric heating, a pressure increase and an upflow: chromospheric evaporation.

## What is changed and what is not

The HYDRAD solver is not modified. The code in `src/` does the reproducible translation:

```text
STIX fit(t) → F(t), Ec(t), δ(t) → beam_heating_model.cfg → Q_beam(s,t) profile
```

No compiled executable is stored in the repository. The upstream configuration does not define `BEAM_HEATING` and the build scripts are Windows `.bat` files; a macOS build worked with `-DBEAM_HEATING -include cstdlib -include cstring -std=gnu++14` (see the README for the known NaN failure with strong or abruptly switched-off beams).

## Important limit for the diagnostics

HYDRAD includes radiation and a forward model for optically thin lines, useful for AIA/Fe XVIII. Its treatment does not replace the NLTE radiative transfer of RADYN for an Hα profile. HYDRAD is also not equivalent to RADYN with Fokker–Planck transport: its beam heating is analytic (collisional, fixed normal incidence). In this project it is used for the column test and as a coronal fallback until RADYN is verified (`docs/00_objectives_and_methodology.md`, Section 6.3).
