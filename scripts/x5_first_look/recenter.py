import sys, json, warnings
import numpy as np, astropy.units as u
from astropy.time import Time
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import pulse_imaging as pi
from stixpy.product import Product
from xrayvision.imaging import vis_to_image
warnings.filterwarnings("ignore")
cpd = Product(sys.argv[1])
res = json.load(open(pi.OUT + "/pulse_images.json"))
tr = Time(pi.PULSES["P4"])
def offset(tx, ty, n=128, pix=1.5):
    sub, _ = pi.visibilities(cpd, tr, (25, 50), pi.hpc(tr, tx * u.arcsec, ty * u.arcsec))
    img = vis_to_image(sub, shape=[n, n] * u.pix, pixel_size=[pix, pix] * u.arcsec / u.pix, scheme="uniform").value
    j, i = np.unravel_index(np.nanargmax(img), img.shape)
    return (i - (n - 1) / 2) * pix, (j - (n - 1) / 2) * pix
tx, ty = res["center_hpc_arcsec"]
dx, dy = offset(tx, ty); print("offset at stored centre:", dx, dy)
best = None
for sx in (1, -1):
    for sy in (1, -1):
        o = offset(tx + sx * dx, ty + sy * dy); print("signs", sx, sy, "->", o)
        if best is None or np.hypot(*o) < np.hypot(*best[2]): best = (sx, sy, o, tx + sx * dx, ty + sy * dy)
print("best", best)
res["center_hpc_arcsec"] = [best[3], best[4]]; res["sign_xy"] = [best[0], best[1]]
json.dump({k: v for k, v in res.items() if k != "pulses"}, open(pi.OUT + "/center.json", "w"))
