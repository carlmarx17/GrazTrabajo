import sys, json, warnings
import numpy as np, astropy.units as u
from astropy.time import Time
from astropy.coordinates import SkyCoord
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import pulse_imaging as pi
from stixpy.product import Product
from stixpy.coordinates.frames import STIXImaging
from xrayvision.imaging import vis_to_image
warnings.filterwarnings("ignore")
cpd = Product(sys.argv[1])
res = json.load(open(pi.OUT + "/pulse_images.json"))
tr = Time(pi.PULSES["P4"])
solo = pi.solo_frame(tr)
c = pi.hpc(tr, *[v * u.arcsec for v in res["center_hpc_arcsec"]]).transform_to(STIXImaging(obstime=tr.mean(), observer=solo))
x, y = c.Tx.to_value("arcsec"), c.Ty.to_value("arcsec")
print("start STIXImaging centre", x, y)
def offset(x, y, n=128, pix=1.5):
    loc = SkyCoord(x * u.arcsec, y * u.arcsec, frame=STIXImaging(obstime=tr.mean(), observer=solo))
    sub, _ = pi.visibilities(cpd, tr, (25, 50), loc)
    img = vis_to_image(sub, shape=[n, n] * u.pix, pixel_size=[pix, pix] * u.arcsec / u.pix, scheme="uniform").value
    j, i = np.unravel_index(np.nanargmax(img), img.shape)
    return (i - (n - 1) / 2) * pix, (j - (n - 1) / 2) * pix
dx, dy = offset(x, y); print("offset", dx, dy)
for sx in (1, -1):
    for sy in (1, -1):
        print("signs", sx, sy, "->", offset(x + sx * dx, y + sy * dy))
