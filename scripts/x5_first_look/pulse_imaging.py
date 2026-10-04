"""First look: STIX images per pulse of SOL2023-12-31 X5.0 and loop-top / footpoint flux at 25-50 keV.

Times are Solar Orbiter (on-board) UTC. stixpy builds calibrated visibilities; xrayvision does
back-projection and Hogbom CLEAN. Images are offsets (arcsec) in the STIX imaging frame around the
phase centre; only relative positions are used here.
"""
import json
import os
import re
import sys
import warnings

import astropy.units as u
import matplotlib
import numpy as np
from astropy.coordinates import SkyCoord
from astropy.time import Time

matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402
from stixpy.calibration.visibility import calibrate_visibility, create_meta_pixels, create_visibility  # noqa: E402
from stixpy.coordinates.transforms import get_hpc_info  # noqa: E402
from stixpy.product import Product  # noqa: E402
from sunpy.coordinates import HeliographicStonyhurst, Helioprojective  # noqa: E402
from xrayvision.clean import vis_clean  # noqa: E402
from xrayvision.imaging import vis_to_image  # noqa: E402

warnings.filterwarnings("ignore")
OUT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "..", "results", "x5_first_look")

# pulse windows with constant attenuator / rate-control state (pixel data: attenuator in from 21:40:04)
PULSES = {
    "P1": ("2023-12-31T21:40:06", "2023-12-31T21:41:20"),
    "P2": ("2023-12-31T21:42:16", "2023-12-31T21:43:40"),
    "P3": ("2023-12-31T21:43:40", "2023-12-31T21:45:20"),
    "P4": ("2023-12-31T21:47:00", "2023-12-31T21:48:20"),
    "P5": ("2023-12-31T21:48:40", "2023-12-31T21:49:50"),
}
BANDS = {"6-10": (6, 10), "15-25": (15, 25), "25-50": (25, 50), "50-84": (50, 84)}
N, PIX = 128, 1.5            # CLEAN image: 128 x 1.5" = 192"
SOURCE_HGS = (-73.0, 4.0)    # AR 13536, approximate Stonyhurst lon/lat of the flare (first guess only)


def solo_frame(tr):
    roll, solo_xyz, pointing = get_hpc_info(tr[0], tr[1])
    return HeliographicStonyhurst(*solo_xyz, representation_type="cartesian", obstime=tr.mean())


def visibilities(cpd, tr, band, loc):
    mp = create_meta_pixels(cpd, time_range=tr, energy_range=band * u.keV, flare_location=loc, no_shadowing=True)
    cvis = calibrate_visibility(create_visibility(mp), flare_location=loc)
    res = np.array([int(re.match(r"\d+", s).group()) for s in cvis.meta["vis_labels"]])
    idx = np.argwhere((res >= 3) & (res <= 10)).ravel()          # sub-collimators 3-10 (24 visibilities)
    return cvis[idx], mp


def hpc(tr, tx, ty):
    return SkyCoord(tx, ty, frame=Helioprojective(obstime=tr.mean(), observer=solo_frame(tr)))


def locate(cpd):
    tr = Time(PULSES["P3"])
    guess = SkyCoord(SOURCE_HGS[0] * u.deg, SOURCE_HGS[1] * u.deg, frame=HeliographicStonyhurst(obstime=tr.mean()))
    c0 = guess.transform_to(Helioprojective(obstime=tr.mean(), observer=solo_frame(tr)))
    print("first guess HPC (SolO view): %.0f %.0f" % (c0.Tx.to_value("arcsec"), c0.Ty.to_value("arcsec")), flush=True)
    for n, pix in ((128, 4.0), (128, 1.5)):
        sub, _ = visibilities(cpd, tr, (25, 50), c0)
        img = vis_to_image(sub, shape=[n, n] * u.pix, pixel_size=[pix, pix] * u.arcsec / u.pix, scheme="uniform").value
        j, i = np.unravel_index(np.nanargmax(img), img.shape)
        dx, dy = (i - (n - 1) / 2) * pix, (j - (n - 1) / 2) * pix
        print("  back-projection %d x %.1f\": peak offset %.1f, %.1f arcsec" % (n, pix, dx, dy), flush=True)
        c0 = hpc(tr, c0.Tx + dx * u.arcsec, c0.Ty + dy * u.arcsec)
    return c0.Tx, c0.Ty


def main(path):
    cpd = Product(path)
    tx, ty = locate(cpd)
    result = dict(center_hpc_arcsec=[float(tx.to_value("arcsec")), float(ty.to_value("arcsec"))], pulses={})
    fig, axes = plt.subplots(len(PULSES), len(BANDS), figsize=(2.6 * len(BANDS), 2.6 * len(PULSES)))
    ext = [-(N / 2) * PIX, (N / 2) * PIX] * 2
    for r, (name, times) in enumerate(PULSES.items()):
        tr = Time(times)
        loc = hpc(tr, tx, ty)
        maps, rates = {}, {}
        for band_name, band in BANDS.items():
            sub, mp = visibilities(cpd, tr, band, loc)
            cmap, comp, resid = vis_clean(sub, shape=[N, N] * u.pix, pixel_size=[PIX, PIX] * u.arcsec / u.pix,
                                          clean_beam_width=8 * u.arcsec, niter=300, gain=0.05, map=False)
            maps[band_name] = np.asarray(getattr(cmap, "value", cmap), float)
            rates[band_name] = float(np.nansum(mp["abcd_rate_kev_cm"].value))
        result["pulses"][name] = dict(times=times, rates=rates, maps={b: m.tolist() for b, m in maps.items()})
        th = maps["6-10"]
        for c, (band_name, m) in enumerate(maps.items()):
            ax = axes[r, c]
            ax.imshow(m, origin="lower", cmap="magma", extent=ext)
            ax.contour(th, levels=[0.5 * np.nanmax(th)], colors=["#86b6ef"], linewidths=0.8, extent=ext)
            ax.set_title("%s  %s keV" % (name, band_name), fontsize=8)
            ax.tick_params(labelsize=6)
        print("imaged", name, flush=True)
    fig.suptitle("SOL2023-12-31 X5.0, STIX CLEAN per pulse (SolO time); blue contour: 50%% of 6-10 keV (thermal)",
                 fontsize=8, x=0.01, ha="left")
    fig.tight_layout()
    fig.savefig(OUT + "/pulse_images.png", dpi=110)
    json.dump(result, open(OUT + "/pulse_images.json", "w"))
    print("written", OUT + "/pulse_images.png")


if __name__ == "__main__":
    main(sys.argv[1])
