import sys, numpy as np
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import io, contextlib
with contextlib.redirect_stdout(io.StringIO()):
    import r_prediction_crossing as cx
k, g = cx.k, cx.g
print("superhot share: thermal / loop non-thermal in 25-50 keV (all of EM at T; real superhot EM is a fraction)")
for delta in (4.0, 5.0):
    ndot = cx.P / (20.0 * (delta - 1) / (delta - 2) / cx.tb.KEV_PER_ERG)
    for n in (1e20, 2e20, 4e20):
        row = []
        for t in (25e6, 30e6, 35e6, 40e6):
            i_cor, i_ch, i_th, em = cx.spectra(ndot, delta, 20.0, n, t)
            s = (k >= 25) & (k <= 50); w = g.wk[s]
            row.append(np.sum(w * i_th[s]) / np.sum(w * i_cor[s]))
        print(" delta %.0f N %.0e EM %.1e : T=25/30/35/40 MK -> %s" % (delta, n, em, " ".join("%.2f" % r for r in row)))
