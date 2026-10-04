import sys, warnings
import numpy as np, astropy.units as u
from astropy.time import Time
from astropy.coordinates import SkyCoord
import matplotlib; matplotlib.use("Agg"); import matplotlib.pyplot as plt
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import pulse_imaging as pi
from stixpy.product import Product
from stixpy.coordinates.frames import STIXImaging
from xrayvision.clean import vis_clean
warnings.filterwarnings("ignore")
N, PIX, CX, CY = 64, 1.0, -154.85, 886.53
cpd = Product(sys.argv[1])
names = ["P2", "P3", "P4", "P5"]
fig, axes = plt.subplots(2, 4, figsize=(11, 5.6))
ext = [-N / 2 * PIX, N / 2 * PIX] * 2
for c, name in enumerate(names):
    tr = Time(pi.PULSES[name])
    loc = SkyCoord(CX * u.arcsec, CY * u.arcsec, frame=STIXImaging(obstime=tr.mean(), observer=pi.solo_frame(tr)))
    m = {}
    for b in ((15, 25), (25, 50)):
        sub, _ = pi.visibilities(cpd, tr, b, loc)
        cm, _, _ = vis_clean(sub, shape=[N, N] * u.pix, pixel_size=[PIX, PIX] * u.arcsec / u.pix,
                             clean_beam_width=7 * u.arcsec, niter=600, gain=0.05, map=False)
        m[b] = np.asarray(getattr(cm, "value", cm), float)
    for r, b in enumerate(((15, 25), (25, 50))):
        ax = axes[r, c]
        img = m[b] / np.nanmax(m[b])
        ax.imshow(img, origin="lower", cmap="Blues", extent=ext, vmin=0, vmax=1)
        ax.contour(m[(15, 25)] / np.nanmax(m[(15, 25)]), levels=[0.5], colors=["#eb6834"], linewidths=1.2, extent=ext)
        ax.contour(img, levels=[0.05, 0.1, 0.3, 0.6], colors=["#0b0b0b"], linewidths=0.5, extent=ext)
        ax.set_title("%s %s–%s UT  %d–%d keV" % (name, pi.PULSES[name][0][11:19], pi.PULSES[name][1][11:19], *b), fontsize=8, loc="left")
        ax.tick_params(labelsize=6)
fig.text(0.01, 0.005, "SOL2023-12-31 X5.0, STIX CLEAN (detectors 3–10, 7\" beam), Solar Orbiter time, axes in arcsec around the flare. "
         "Orange: 50% of the 15–25 keV source (loop top). Black contours: 5, 10, 30, 60% of each panel's peak.", fontsize=7, color="#52514e")
fig.tight_layout(rect=(0, 0.03, 1, 1))
fig.savefig(pi.OUT + "/x5_pulses_15-25_25-50.png", dpi=130)
print("ok")
