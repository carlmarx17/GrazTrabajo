import sys, json, warnings
import numpy as np, astropy.units as u
from astropy.time import Time
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import pulse_imaging as pi
from stixpy.product import Product
from xrayvision.clean import vis_clean
warnings.filterwarnings("ignore")
cpd = Product(sys.argv[1])
res = json.load(open(pi.OUT + "/pulse_images.json"))
tx, ty = [v * u.arcsec for v in res["center_hpc_arcsec"]]
tr = Time(pi.PULSES["P4"]); loc = pi.hpc(tr, tx, ty)
sub, mp = pi.visibilities(cpd, tr, (25, 50), loc)
out = vis_clean(sub, shape=[128,128]*u.pix, pixel_size=[1,1]*u.arcsec/u.pix, clean_beam_width=7*u.arcsec, niter=600, gain=0.05, map=False)
for k, a in zip(("clean", "model", "resid"), out):
    a = np.asarray(getattr(a, "value", a), float)
    nz = np.argwhere(a != 0)
    print(k, a.shape, "sum %.3g max %.3g min %.3g nonzero %d" % (a.sum(), a.max(), a.min(), len(nz)))
    if k == "model":
        ys, xs = nz[:, 0], nz[:, 1]
        print("  model nonzero x range", xs.min(), xs.max(), "y range", ys.min(), ys.max())
        top = np.argsort(a.ravel())[::-1][:8]
        print("  top comps (y,x,val):", [(int(i // 128), int(i % 128), round(float(a.ravel()[i]), 3)) for i in top])
c = np.asarray(getattr(out[0], "value", out[0]), float)
j, i = np.unravel_index(np.argmax(c), c.shape); print("clean peak pixel (y,x):", j, i)
