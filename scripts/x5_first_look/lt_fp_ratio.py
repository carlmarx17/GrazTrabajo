"""Loop-top / footpoint flux per pulse from CLEAN components (first look, SOL2023-12-31 X5.0)."""
import sys, json, warnings
import numpy as np, astropy.units as u
from astropy.time import Time
from scipy.ndimage import maximum_filter
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import pulse_imaging as pi
from stixpy.product import Product
from xrayvision.clean import vis_clean
from astropy.coordinates import SkyCoord
from stixpy.coordinates.frames import STIXImaging
warnings.filterwarnings("ignore")
N, PIX, R_AP = 96, 1.0, 4.0
CX, CY = -154.85, 886.53   # flare centre in the STIX imaging frame (recenter2.py)
cpd = Product(sys.argv[1])
res = json.load(open(pi.OUT + "/pulse_images.json"))
tx, ty = [v * u.arcsec for v in res["center_hpc_arcsec"]]
yy, xx = (np.mgrid[0:N, 0:N] - (N - 1) / 2) * PIX

def comps(sub):
    cmap, model, resid = vis_clean(sub, shape=[N, N] * u.pix, pixel_size=[PIX, PIX] * u.arcsec / u.pix,
                                   clean_beam_width=7 * u.arcsec, niter=600, gain=0.05, map=False)
    return np.asarray(getattr(cmap, "value", cmap), float), np.asarray(getattr(model, "value", model), float)

def peaks(img, n, min_sep=8.0):
    loc = (img == maximum_filter(img, size=5)) & (img > 0.1 * img.max())
    cand = sorted(zip(img[loc], xx[loc], yy[loc]), reverse=True)
    out = []
    for v, x, y in cand:
        if all(np.hypot(x - a, y - b) > min_sep for _, a, b in out):
            out.append((v, x, y))
        if len(out) == n: break
    return out

def ap(model, x, y):
    return float(model[np.hypot(xx - x, yy - y) <= R_AP].sum())

print("pulse | LT pos (15-25)   FP1 pos     FP2 pos    | dLT-FP [\"] | R25-50 (LT/FPsum) | R50-84 | 15-25 total rate")
rows = {}
for name, times in pi.PULSES.items():
    tr = Time(times); loc = SkyCoord(CX * u.arcsec, CY * u.arcsec, frame=STIXImaging(obstime=tr.mean(), observer=pi.solo_frame(tr)))
    out = {}
    for b in ((15, 25), (25, 50), (50, 84)):
        sub, mp = pi.visibilities(cpd, tr, b, loc)
        out[b] = comps(sub) + (float(np.nansum(mp["abcd_rate_kev_cm"].value)),)
    cl1525 = out[(15, 25)][0]
    lt = peaks(cl1525, 1)[0]
    fps = peaks(out[(25, 50)][0], 2)
    d = min(np.hypot(lt[1] - f[1], lt[2] - f[2]) for f in fps)
    r = {}
    for b in ((25, 50), (50, 84)):
        model = out[b][1]
        f_lt = ap(model, lt[1], lt[2]); f_fp = sum(ap(model, f[1], f[2]) for f in fps)
        r[b] = f_lt / f_fp if f_fp > 0 else np.nan
    model = out[(25, 50)][1]; cmapr = out[(25, 50)][0]
    tot = model.sum(); fp_tot = sum(ap(model, f[1], f[2]) for f in fps)
    jl, il = int(round(lt[2] / PIX + (N - 1) / 2)), int(round(lt[1] / PIX + (N - 1) / 2))
    fpk = max(cmapr[int(round(f[2] / PIX + (N - 1) / 2)), int(round(f[1] / PIX + (N - 1) / 2))] for f in fps)
    print("   25-50: model in FP apertures %.0f%%, elsewhere %.0f%%; restored map at LT / FP peak = %.2f; n comps %d" % (
        100 * fp_tot / tot, 100 * (1 - fp_tot / tot), cmapr[jl, il] / fpk, int((model > 0).sum())), flush=True)
    rows[name] = dict(lt=lt[1:], fps=[f[1:] for f in fps], d_lt_fp=d, R2550=r[(25, 50)], R5084=r[(50, 84)], rate1525=out[(15, 25)][2])
    print("%s | (%5.1f,%5.1f)  (%5.1f,%5.1f) (%5.1f,%5.1f) | %5.1f | %5.2f | %5.2f | %.1f" % (
        name, lt[1], lt[2], fps[0][1], fps[0][2], fps[1][1], fps[1][2], d, r[(25, 50)], r[(50, 84)], out[(15, 25)][2]), flush=True)
json.dump(rows, open(pi.OUT + "/lt_fp_ratio.json", "w"), indent=1, default=float)
