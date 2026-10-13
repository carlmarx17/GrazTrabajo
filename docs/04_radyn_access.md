# RADYN verification notes and v5 production requirements

**Current role (v5.1, 2026-10-05):** RADYN with verified FP coupling is the preferred route for chromospheric diagnostics of the core experiment, once it is built, one F-CHROMA model is reproduced and restart branching is verified (test T6). HYDRAD is the pilot route. See [the methodology](00_objectives_and_methodology.md), Sections 4 and 5. The technical findings below record the distribution inspected in October 2026; no production RADYN run has been validated here. Installation/access notes must be rechecked before execution.

**Source of what was verified:** the downloaded distribution (`radyn_fchroma.tar`, 87 844 352 bytes, SHA-256 `827948d913cdb33768a6f501cf42a7c8c3d6935fcd264b16a183f070ba70bf14`) from [folk.universitetetioslo.no/matsc/radyn](https://folk.universitetetioslo.no/matsc/radyn/), with its manual (`doc/radyn_manual.pdf`, dated February 2023) and its source code. It is not included in this repository (Section 1).

## 1. License: unresolved

- The distribution **ships without a license file** and the download page states no conditions.
- The manual says: "We are in the process of getting a permanent home (with proper DOI and license) on Zenodo". That publication was not found.
- The code includes `cdf.inc` with NASA's license for the CDF library; that does not cover RADYN.
- **Consequence:** RADYN is **not copied or redistributed** in this repository. Confirmation of the license and of permission of use must be requested from Mats Carlsson before publishing anything that depends on it.
- The F-CHROMA model database does ask for acknowledgement of the funding (FP7, no. 606862) and for publications to be notified to L. Fletcher ([QUB](https://star.pst.qub.ac.uk/wiki/public/solarmodels/start.html)).

## 2. What the distribution includes (read from the manual and the code)

| Capability | Result | Evidence |
|---|---|---|
| **Fokker–Planck** | **Yes**, `ibeam = 8`. This is the version of Allred et al. (2015). The version of Allred et al. (2020) is **not** included; the manual says it is planned to be released on GitHub. | `doc/radyn_manual.tex`, `prog/fp_solver.f` |
| Transport physics | Pitch-angle diffusion by collisions, magnetic mirroring and **return current** (`irc`), with the gas temperature and a thermalization energy (`thermE`) | `prog/fp_solver.f`, `prog/beamrat.f` |
| FP solution | **Steady state at each step**, on the current atmosphere; therefore Q(s,t) is recomputed with the evolving atmosphere | header of `fp_solver.f` |
| Time-dependent beam | Yes, `ftab.dat` table (Section 3) | `prog/rftab.f` |
| **Restart** | Yes: `itime0 > 0` restarts from that step of `radyn_out.cdf`; `itime0 < 0` from the last one. It allows **branching** runs with a common history | manual, Section 7 |
| Parallelism | Serial version and MPI version (parallel in frequency and transitions) | manual, Section 2 |
| Geometry | 1D, semi-symmetric loop, beam injected at the top; example with a half-length of 10 Mm | manual, Sections 4–5 |
| Initial atmospheres | VAL3C and 1 MK loops already prepared in `input/` | distribution |
| Output | CDF files; analysis with IDL (not available here) or with [RadynPy](https://pypi.org/project/radynpy/) | manual |

**Not verified:** whether the FP output stores the electron distribution (flux by position and energy), which would be needed for HXR photon synthesis in the selected production route, and whether the treatment of the gas temperature and `thermE` is an adequate warm-target description for pulse 2.

**Adaptive grid:** variable indices do not correspond to a fixed height; the analysis routines handle it. Energy conservation is formulated on that grid and is not trivial to interpret (manual, Section 1).

## 3. Beam format (`ftab.dat`, FP) and how it is adapted

```
* comments (lines starting with '*')
511d3  1.0  2  0.1        mass [eV]  |charge|  pitch-angle distribution type  sigma
npts                      at most 5000 rows
t [s]   δ   Ec [keV]   F [erg cm⁻² s⁻¹]
```

Particularities that constrain the design (`prog/rftab.f`, `prog/beam.f`):

1. **Column order different from HYDRAD:** time, δ, Ec, F.
2. **F cannot be zero.** `log10(F)` is interpolated and a floor of 0.1 erg cm⁻² s⁻¹ is imposed.
3. **Interpolation uses taut splines** (tension 5.5) of δ, Ec and log₁₀F. A linear ramp between the floor and 10¹⁰ erg cm⁻² s⁻¹ would behave like a late step.
4. **The table must cover the whole run:** if the time exceeds the last row, RADYN stops.
5. The example in the distribution is a **20 s triangular** pulse with a fluence of 10¹¹ erg cm⁻².

**Implemented adaptation:** [`src/radyn_ftab.py`](../src/radyn_ftab.py) subdivides each ramp into 0.02 s segments following the linear shape, applies the 0.1 floor, extends the table to the end of the run and checks the energy assuming log-linear interpolation between rows. In the six experiments the encoded energy matches the intended one within **−0.03 %** (all repository tests pass). `src/experiments.py` now writes one `ftab.dat` per component.

**Pending:** RADYN's actual tensioned spline has **not been executed** (no compiler). The definitive check is to integrate the beam flux that RADYN writes in its own output.

## 4. Physical particularities that change the design

- **Permanent background heating.** So that the initial atmosphere does not cool without a beam, RADYN adds a non-radiative term that balances the initial state (`xnrh0 = 1e-21` in the example). Relaxation between pulses is therefore **toward the initial equilibrium** and not free cooling. The relaxation time τ_rel of the E5 counterfactual must be measured **with that same term**, and the report must declare it.
- **Reflecting upper boundary** (`ibc0 = 6`, symmetric loop) and **lower boundary** reflecting (`ibcx = -1`) or transparent (`ibcx = 4`) depending on the time studied; for long times the transparent one must be used.
- **Maximum time step** of 0.1 s recommended (`dtmax`) and frequent output.
- The flux is an energy flux at the loop top; the area A remains unconstrained by STIX and is kept as a parameter with uncertainty.

## 5. Verification gate before production use

1. Install a Fortran compiler and NASA's CDF library (**neither is installed**; it requires downloads that must be authorized).
2. Compile the dynamic version (`dyn`) and reproduce a model of the public F-CHROMA database (96 models, VAL3C, δ = 3–8, Ec = 10–25 keV, 20 s triangular pulse) comparing with its published CDF.
3. Measure wall time and memory of a 2-pulse run.
4. Test **restart** to confirm that it restores the complete state (including atomic populations) before using it for branching.
5. Check whether the FP output contains the electron flux needed for the photon computation.
6. Confirm the license with Mats Carlsson.

Completing these checks does not require removing `vendor/HYDRAD/`; retain useful reference and comparison infrastructure. For the core experiment, steps 2–5 plus synthesis of the chosen diagnostic are enough (test T6 in the methodology). Reproducing a published flare simulation is extension E3.

## 6. Risks

| Risk | Effect | Mitigation |
|---|---|---|
| License unconfirmed | Derived code cannot be published | Ask for confirmation; do not redistribute RADYN |
| 2015 FP without the 2020 improvements | Differences in warm target and return current | Document it; ask for the latest version |
| Compilation (F77/F90 + CDF) on macOS | Delay | Try on the cluster |
| Hard convergence of new atmospheres | Failed cases | Use already prepared atmospheres; record failures |
| Unknown cost per run | Mis-sized campaign | Pilot before budgeting |

## Cluster access: the concrete path, and the actual blocker (recorded 2026-10-13)

Gate item "build on the cluster" is **not** blocked by the account. It is blocked by the network.

**The machine.** COSMA, at Durham, through DiRAC. Project code **dp433**, held by a collaborator at a partner institution who supplied the account route (2026-03-31):

1. Register on SAFE: <https://safe.epcc.ed.ac.uk/dirac/> (docs: <https://epcced.github.io/safe-docs/>) with full name, **institutional** e-mail (private addresses are refused), nationality and department.
2. In SAFE, choose **Request login account**.
3. Enter project code **dp433** and select the DiRAC system (cosma).
4. The PI or project manager approves; an e-mail confirms it.
5. The **SSH key pair is generated on the machine you will connect from**, and the public key goes into the SAFE request (confirmed 2026-04-01).

**Status.** The account exists and is live: a DiRAC SAFE 2FA recovery token was issued on 2026-04-15, and COSMA support notices arrive directly (downtime 5–9 October 2026, including `/snap*` cleaning). A collaborator's note of useful COSMA commands is held outside this repository.

**The blocker.** From the Uni Graz network the VPN works (Cisco Secure Client on Fedora) but **outgoing SSH on port 22 is blocked**, so COSMA is unreachable. This was reported to uniIT on **2026-09-08** (ticket **IT-143898**) and, as of 2026-10-13, **there is no reply** — five weeks open. Nothing on the RADYN gate can proceed from Graz until this is resolved.

**Options, in order of cost.**

1. **Chase IT-143898.** Ask explicitly for outbound TCP/22, or for the documented alternative (a jump host, or SSH over 443). This is a one-line request and it is the whole blocker.
2. **Work outside the university network** (home connection or tether) to confirm the account and key work at all — this isolates the Graz firewall as the cause and takes minutes.
3. **Ask whether Graz has its own compute** for this project, which would avoid the dp433 question entirely.

**An allocation question to settle before counting on COSMA.** dp433 is the DiRAC project of the mirror-instability work, not of this flare project. Running RADYN under it may be outside its allocation. Confirm with the project PI and with the supervisor whether this work may use dp433, or whether it needs its own project code or a local machine.

**Credentials.** The external university account needed for the VPN is managed through the IT service desk; MFA setup and password rotation are at the addresses that desk provides. No account name, ticket contact or credential is recorded in this repository.
