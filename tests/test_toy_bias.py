import math

import numpy as np
import pytest

import toy_bias as tb


@pytest.fixture(scope="module")
def model():
    grid = tb.make_grid(ne=600, nk=200)
    return tb.ForwardModel(grid=grid, instrument=tb.make_instrument(grid))


def _bethe_heitler_nr_elwert(e, k, z=1.2):
    """Non-relativistic Bethe-Heitler (Koch & Motz 3BN(a)) times the Elwert factor."""
    p0 = np.sqrt(2 * e / tb.MC2_KEV)
    p = np.sqrt(2 * (e - k) / tb.MC2_KEV)
    bh = (8.0 / 3.0) * z * z * tb.ALPHA * tb.R0_CM ** 2 * tb.MC2_KEV / (e * k) * np.log((p0 + p) / (p0 - p))
    a1, a2 = tb.ALPHA * z / p0, tb.ALPHA * z / p
    elwert = (a2 / a1) * (1 - np.exp(-2 * np.pi * a1)) / (1 - np.exp(-2 * np.pi * a2))
    return bh * elwert


def test_haug_cross_matches_nonrelativistic_limit_and_vanishes_above_the_tip():
    e = 10.0
    k = np.array([1.0, 3.0, 5.0, 8.0, 9.5])
    ratio = tb.haug_cross(e, k) / _bethe_heitler_nr_elwert(e, k)
    assert np.all(np.abs(ratio - 1) < 0.05)
    assert np.all(tb.haug_cross(e, np.array([10.0, 12.0])) == 0)


def test_thick_target_with_kramers_cross_section_gives_delta_minus_one():
    grid = tb.make_grid(ne=1500, nk=60, k_range=(30.0, 150.0),
                        cross=lambda ee, kk: np.where(ee > kk, 1.0 / (kk * ee), 0.0))
    c = tb.injection_weights(grid.e, 1e35, 4.0, 10.0)
    spec = (grid.h / tb.Target().k_ion) @ c
    sel = (grid.k > 40) & (grid.k < 120)
    gamma = -np.polyfit(np.log(grid.k[sel]), np.log(spec[sel]), 1)[0]
    assert abs(gamma - 3.0) < 0.01


def test_injection_weights_conserve_number_and_power_and_are_continuous():
    e = np.geomspace(1, 3000, 1000)
    ndot, delta, ec = 3.4e34, 4.97, 13.4
    c = tb.injection_weights(e, ndot, delta, ec)
    assert abs(c.sum() / ndot - 1) < 5e-4      # trapezoid error on a 0.8 % log grid
    power = ndot * ec * (delta - 1) / (delta - 2)
    assert abs((c * e).sum() / power - 1) < 1e-3
    c2 = tb.injection_weights(e, ndot, delta, ec * (1 + 1e-7))
    assert np.abs(c2 - c).sum() / c.sum() < 1e-5


def test_two_zone_limits_and_yield_ratio(model):
    e = model.grid.e
    cor0, ch0 = tb.zone_operators(model.grid.h, e, model.target, 0.0)
    assert np.allclose(cor0, 0)
    cori, chi = tb.zone_operators(model.grid.h, e, model.target, np.inf)
    assert np.allclose(chi, 0)
    assert np.allclose(ch0, cori * model.target.ion_to_neutral_loss)


def test_coronal_energy_fraction_limits_and_monotonicity(model):
    fr = [model.coronal_energy_fraction(tb.Pulse(n_cor=n)) for n in (0.0, 1e19, 1e20, 1e21, 1e24)]
    assert fr[0] == 0 and fr[-1] > 0.999
    assert all(b > a for a, b in zip(fr, fr[1:]))
    # electrons below sqrt(2 K N) stop in the corona: at N = N_stop(Ec) the fraction is substantial
    n_ec = float(model.target.stopping_column(13.4))
    assert model.coronal_energy_fraction(tb.Pulse(n_cor=n_ec)) > 0.3


def test_thermal_born_limit_matches_rybicki_lightman_with_born_gaunt_factor():
    """With the non-relativistic Born (Bethe-Heitler) cross-section, the thermal spectrum must
    equal the Kramers formula of Rybicki & Lightman (Eq. 5.14a) times the thermally averaged
    Born Gaunt factor (sqrt(3)/pi) e^(u/2) K0(u/2), u = eps/kT. The code uses the relativistic
    electron speed, which lowers the result by v_rel/v_nr (0.99 at 5 keV, 0.95 at 40 keV)."""
    from scipy.special import k0

    def born(ee, kk):
        ee, kk = np.broadcast_arrays(ee, kk)
        out = np.zeros(ee.shape)
        ok = kk < ee
        e, k = ee[ok], kk[ok]
        p0, p = np.sqrt(2 * e / tb.MC2_KEV), np.sqrt(2 * (e - k) / tb.MC2_KEV)
        out[ok] = (8 / 3) * tb.ALPHA * tb.R0_CM ** 2 * tb.MC2_KEV / (e * k) * np.log((p0 + p) / (p0 - p))
        return out

    grid = tb.make_grid(ne=3000, nk=20, e_range=(0.05, 3000.0), k_range=(2.0, 40.0), cross=born)
    t, em = 2e7, 1e48
    flux = em / (4 * math.pi * tb.AU_CM ** 2) * (grid.sigma @ (tb.maxwellian_vf(grid.e, t) * grid.we))
    pref = (2 ** 5 * math.pi * tb.E_ESU ** 6 / (3 * 9.1093837e-28 * tb.C_CM_S ** 3)
            * math.sqrt(2 * math.pi / (3 * 1.380649e-16 * 9.1093837e-28)))          # 6.8e-38 cgs
    u = grid.k / (tb.KB_KEV_PER_K * t)
    gaunt = (math.sqrt(3) / math.pi) * np.exp(u / 2) * k0(u / 2)
    expected = pref / 6.62607015e-27 / (4 * math.pi * tb.AU_CM ** 2) * em * gaunt * np.exp(-u) / (grid.k * math.sqrt(t))
    ratio = flux / expected
    gam = 1 + grid.k / tb.MC2_KEV
    rel = np.sqrt(1 - 1 / gam ** 2) / np.sqrt(2 * grid.k / tb.MC2_KEV)   # speed correction at E = k
    assert np.all(np.abs(ratio - 1) < 0.07)
    assert np.all(ratio[grid.k < 10] > 0.98)
    assert np.all(ratio <= 1.0 + 1e-3) and np.all(ratio >= rel - 0.01)


def test_instrument_redistribution_conserves_photons():
    grid = tb.make_grid(ne=50, nk=200)
    ins = tb.make_instrument(grid, exposure_s=1.0, area_cm2=1.0)
    aeff = np.exp(-(3.2 / grid.k) ** 3) * (1 - np.exp(-(130.0 / grid.k) ** 2.5))
    prob = ins.response.sum(axis=0) / (aeff * grid.wk)
    sel = (grid.k > 8) & (grid.k < 100)
    assert np.all(np.abs(prob[sel] - 1) < 1e-3)


def test_negative_control_fit_recovers_truth_when_target_matches_the_model(model):
    # standard model generated and fitted: no bias
    truth = tb.Pulse(n_cor=np.inf, t_k=2e7, em=1e47)
    x, _, _ = tb.asimov_fit(model, truth)
    xt = tb.truth_vector(model, truth)
    assert np.all(np.abs(x - xt) < 2e-3 * np.maximum(1, np.abs(xt)))
    # two-zone model generated and fitted with the two-zone model: no bias either
    truth2 = tb.Pulse(n_cor=1e20, t_k=2e7, em=1e47)
    x2, _, _ = tb.asimov_fit(model, truth2, two_zone=True)
    xt2 = tb.truth_vector(model, truth2, two_zone=True)
    assert np.all(np.abs(x2 - xt2) < 5e-3 * np.maximum(1, np.abs(xt2)))
