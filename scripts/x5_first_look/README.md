# First look at SOL2023-12-31 X5.0 (historical v4 pilot)

> **Current status (v5.1):** this remains an exploratory imaging dataset. It belongs to the extensions to discuss (E1 observational part, E8 third source), not to the core; see [the active plan](../../docs/00_objectives_and_methodology.md), Section 8.

Recovered on 2026-10-04 from a temporary session folder; paths are now relative to the
repository. Run with the STIX environment (`requirements-stix.txt`, Python >= 3.10).

Data (git-ignored, in `data/stix/`, from SOAR): the pixel-data file
`solo_L1_stix-sci-xray-cpd_20231231T212110-20231231T220527_V02_2312319684-50157.fits`
(8 pixels, 0.5 s bins; the smaller cpd file of the same flare has summed pixels and is
rejected by stixpy).

| Script | What it does | Output (`results/x5_first_look/`) |
|---|---|---|
| `pulse_imaging.py <cpd>` | Locates the flare, defines the five pulse windows (constant attenuator state), back-projection and CLEAN images per pulse in 6–10, 15–25, 25–50, 50–84 keV | `pulse_images.json` |
| `recenter.py`, `recenter2.py` | Refines the phase centre | `center.json` |
| `lt_fp_ratio.py <cpd>` | Loop-top (15–25 keV peak) and two footpoints (25–50 keV peaks); CLEAN-component flux in 4" apertures | `lt_fp_ratio.json` |
| `third_source.py <cpd>` | Flux ratio of the source ~15" north of the thermal peak to the footpoints, three estimators | printed |
| `fig_pulses.py`, `diag.py` | Figures and diagnostics | `*.png` |
| `r_prediction_crossing.py`, `r_prediction_superhot.py` | Early toy predictions of the loop-top ratio and of the superhot share (superseded by `src/tracer.py`) | printed |

**Status of the results (do not over-read):**
- CLEAN components give R = 0 at 25–50 keV in all five pulses. That means "below the CLEAN threshold", not a measured upper limit; the restored-map level (4–10 % of the footpoint peak) is beam leakage.
- Footpoints are stable within ~2" from P2 to P5.
- A source ~15" north of the thermal peak appears in P4–P5 at 25–50 keV.
- Single algorithm, no uncertainties, no injection–recovery yet. The loop-top/footpoint separation (~8") is below two STIX resolution elements, so this event is a pilot, not a sample member by the v4 criteria.
