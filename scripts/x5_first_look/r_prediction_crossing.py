"""Imaging observable: photon energy where coronal (loop) and chromospheric (footpoint)
non-thermal emission are equal, vs coronal column; with and without the thermal emission
of the same column (EM = 2 N^2 A / L)."""
import sys, numpy as np
import os
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "..", "src"))
import toy_bias as tb

g = tb.make_grid()
tgt = tb.Target()
k = g.k
A, L = 1.0e18, 2.1e9                       # Ryan et al. 2024 loop: length 42 Mm
geo = tb.Geometry(area_cm2=A, half_length_cm=L)

def spectra(ndot, delta, ec, n_cor, t_k):
    c = tb.injection_weights(g.e, ndot, delta, ec)
    cor, ch = tb.zone_operators(g.h, g.e, tgt, n_cor)
    i_cor, i_ch = cor @ c, ch @ c
    em = geo.em_from_column(n_cor)
    i_th = em * (g.sigma @ (tb.maxwellian_vf(g.e, t_k) * g.we))
    return i_cor, i_ch, i_th, em

def crossing(top, fp, lo=8.0):
    """Highest photon energy where top >= fp (loop-top dominates below, footpoints above)."""
    sel = k >= lo
    d = np.log(top[sel]) - np.log(fp[sel])
    idx = np.nonzero(d >= 0)[0]
    if idx.size == 0:
        return np.nan
    j = idx[-1]
    if j + 1 >= d.size:
        return np.inf
    kk = k[sel]
    return float(np.exp(np.interp(0.0, [d[j + 1], d[j]], [np.log(kk[j + 1]), np.log(kk[j])])))

P = 3e29                                    # erg/s non-thermal power (X-class)
print("A=%.0e L=%.1e  P=%.0e erg/s" % (A, L, P))
print(" delta  Ec  N_cor     E_stop | eps_x(nonthermal) eps_x(+thermal 20MK) eps_x(+thermal 30MK) | thermal share of loop-top at eps_x(NT)  EM")
for delta in (4.0, 6.0):
    ec = 20.0
    mean_e = ec * (delta - 1) / (delta - 2) / tb.KEV_PER_ERG
    ndot = P / mean_e
    for n in (3e19, 1e20, 3e20, 1e21):
        e_stop = float(np.sqrt(2 * tgt.k_ion * n))
        out = []
        for t in (20e6, 30e6):
            i_cor, i_ch, i_th, em = spectra(ndot, delta, ec, n, t)
            out.append(crossing(i_cor + i_th, i_ch))
        x_nt = crossing(i_cor, i_ch)
        i_cor, i_ch, i_th20, em = spectra(ndot, delta, ec, n, 20e6)
        j = np.argmin(abs(k - (x_nt if np.isfinite(x_nt) else 30)))
        share = i_th20[j] / (i_th20[j] + i_cor[j])
        print("  %.0f   %.0f  %.0e  %5.1f | %6.1f            %6.1f              %6.1f              | %.2f   %.1e" % (
            delta, ec, n, e_stop, x_nt, out[0], out[1], share, em))

print("\nLoop/footpoint non-thermal flux ratio per band, and thermal(25 MK)/loop non-thermal in the band")
bands = ((15, 25), (25, 50), (50, 84))
print(" delta  N_cor   EM      | " + " | ".join("R%d-%d  th/LT" % b for b in bands))
for delta in (3.5, 4.0, 5.0, 6.0):
    ec = 20.0
    ndot = P / (ec * (delta - 1) / (delta - 2) / tb.KEV_PER_ERG)
    for n in (5e19, 1e20, 2e20, 4e20):
        i_cor, i_ch, i_th, em = spectra(ndot, delta, ec, n, 25e6)
        cells = []
        for lo, hi in bands:
            s = (k >= lo) & (k <= hi); w = g.wk[s]
            a, b, t = np.sum(w * i_cor[s]), np.sum(w * i_ch[s]), np.sum(w * i_th[s])
            cells.append("%5.2f %6.2f" % (a / b, t / a))
        print("  %.1f  %.0e %.1e | %s" % (delta, n, em, " | ".join(cells)))
