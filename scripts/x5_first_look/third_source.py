import sys, json, warnings
import numpy as np, astropy.units as u
from astropy.time import Time
from astropy.coordinates import SkyCoord
from scipy.ndimage import maximum_filter
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import pulse_imaging as pi
from stixpy.product import Product
from stixpy.coordinates.frames import STIXImaging
from xrayvision.clean import vis_clean
from xrayvision.imaging import vis_to_image
warnings.filterwarnings("ignore")
N, PIX, CX, CY = 64, 1.0, -154.85, 886.53
yy, xx = (np.mgrid[0:N, 0:N] - (N - 1) / 2) * PIX
cpd = Product(sys.argv[1])
FP_A, FP_B, NORTH = (0.0, -2.5), (18.0, -14.0), (2.0, 15.5)
def at(img, p, r=3.0):
    return float(np.nanmax(img[np.hypot(xx - p[0], yy - p[1]) <= r]))
def ap(model, p, r=5.0):
    return float(model[np.hypot(xx - p[0], yy - p[1]) <= r].sum())
print("pulse band | north/FPpeak (CLEAN map) | north/FPsum (components) | north/FPpeak (back-proj, natural) | counts in band")
for name in pi.PULSES:
    tr = Time(pi.PULSES[name])
    loc = SkyCoord(CX * u.arcsec, CY * u.arcsec, frame=STIXImaging(obstime=tr.mean(), observer=pi.solo_frame(tr)))
    for b in ((25, 50), (50, 84)):
        sub, mp = pi.visibilities(cpd, tr, b, loc)
        cm, model, _ = vis_clean(sub, shape=[N, N] * u.pix, pixel_size=[PIX, PIX] * u.arcsec / u.pix,
                                 clean_beam_width=7 * u.arcsec, niter=600, gain=0.05, map=False)
        cm = np.asarray(getattr(cm, "value", cm), float); model = np.asarray(getattr(model, "value", model), float)
        bp = vis_to_image(sub, shape=[N, N] * u.pix, pixel_size=[PIX, PIX] * u.arcsec / u.pix, scheme="natural").value
        fpk = max(at(cm, FP_A), at(cm, FP_B)); fpb = max(at(bp, FP_A), at(bp, FP_B))
        print("%s %d-%d | %5.2f | %5.2f | %5.2f |" % (name, b[0], b[1], at(cm, NORTH) / fpk,
              ap(model, NORTH) / (ap(model, FP_A) + ap(model, FP_B)), at(bp, NORTH) / fpb), flush=True)
