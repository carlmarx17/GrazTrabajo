import math

import numpy as np
import pytest

from toy_bias import Target, make_grid
from tracer import (TracerModel, column_lower_bound, density_lower_bound, knee_energy_kev)


@pytest.fixture(scope="module")
def model():
    return TracerModel(make_grid(ne=600, nk=200))


def test_filling_factor_below_one_raises_the_column():
    em, v, path = 1e49, 1e27, 1e9
    n1 = column_lower_bound(em, v, path)
    assert n1 == pytest.approx(math.sqrt(em / v) * path)
    for f in (0.5, 0.1, 0.01):
        assert math.sqrt(em / (f * v)) * path > n1
    with pytest.raises(ValueError):
        density_lower_bound(1e49, 0.0)


def test_knee_energy_stops_at_that_column():
    t = Target()
    for n in (1e19, 1e20, 5e20):
        e_star = knee_energy_kev(n, t)
        assert float(t.stopping_column(e_star)) == pytest.approx(n, rel=1e-12)
    # about 23 keV for 1e20 cm^-2 with Lambda = 20
    assert knee_energy_kev(1e20) == pytest.approx(22.8, abs=0.5)


def test_no_column_gives_no_loop_top_emission(model):
    b = model.band_photons(5.0, 20.0, 0.0)
    assert b.loop_top == pytest.approx(0.0, abs=1e-30)
    assert b.rest == pytest.approx(b.all_neutral, rel=1e-9)
    assert model.r_predicted(5.0, 20.0, 0.0) == pytest.approx(0.0, abs=1e-12)


def test_prediction_grows_with_column_and_with_softer_spectra(model):
    r = [model.r_predicted(5.0, 20.0, n) for n in (3e19, 1e20, 3e20, 1e21)]
    assert all(b > a for a, b in zip(r, r[1:]))
    rd = [model.r_predicted(d, 20.0, 2e20) for d in (3.5, 4.5, 5.5, 6.5)]
    assert all(b > a for a, b in zip(rd, rd[1:]))


def test_ionized_column_radiates_less_than_neutral(model):
    # the key inequality behind the bound: I_rest <= I_0 and I_LT + I_rest <= I_0
    for d in (3.5, 5.0, 7.0):
        for n_lt, n_leg in ((1e19, 0), (2e20, 0), (2e20, 3e20), (1e21, 1e21)):
            b = model.band_photons(d, 18.0, n_lt, n_leg)
            assert b.rest <= b.all_neutral * (1 + 1e-9)
            assert b.loop_top + b.rest <= b.all_neutral * (1 + 1e-9)


def test_mixture_limits(model):
    assert model.r_mixture(0.0, 5.0, 20.0, 2e20) == 0.0
    assert model.r_mixture(1.0, 5.0, 20.0, 2e20, 1e20, 0.2) == pytest.approx(
        model.r_predicted(5.0, 20.0, 2e20, 1e20, 0.2), rel=1e-12)


def test_bound_is_conservative_for_random_truths(model):
    """The bound must never fall below the true re-use fraction."""
    rng = np.random.default_rng(1)
    deltas, ecs = (3.5, 4.5, 5.5, 6.5), (12.0, 18.0, 24.0)
    for _ in range(60):
        phi = rng.uniform(0.0, 1.0)
        d = rng.uniform(3.5, 6.5)
        ec = rng.uniform(12.0, 24.0)
        n_min = 10 ** rng.uniform(19.0, 20.7)
        n_true = n_min * 10 ** rng.uniform(0.0, 0.7)          # filling factor < 1 -> larger column
        n_leg = 10 ** rng.uniform(18.0, 20.5)
        a_true = rng.uniform(0.0, 0.4)
        r_obs = model.r_mixture(phi, d, ec, n_true, n_leg, a_true)
        bound = model.reuse_upper_bound(r_obs, n_min, deltas, ecs, albedo_max=0.4)
        assert bound >= phi * (1 - 1e-9), (phi, bound)


def test_non_detection_is_informative_only_for_dense_loops(model):
    # the conservative bound needs loop-top limits of a few percent of the footpoints
    deltas, ecs = (5.0, 6.0), (15.0, 20.0)
    assert model.informative(0.03, 3e20, deltas, ecs, albedo_max=0.2)
    assert not model.informative(0.03, 1e19, deltas, ecs, albedo_max=0.2)
    assert not model.informative(0.10, 3e20, deltas, ecs, albedo_max=0.2)


def test_ratio_spectrum_has_a_knee_under_reuse(model):
    edges = [20.0, 25.0, 32.0, 40.0, 50.0, 63.0, 84.0]
    n = 3e20                                   # E* ~ 40 keV
    r1 = model.r_in_bins(1.0, 5.0, 20.0, n, edges)
    assert all(b < a for a, b in zip(r1, r1[1:]))           # falls with energy
    assert r1[0] / r1[-1] > 5.0                              # strongly, across the knee
    assert np.all(model.r_in_bins(0.0, 5.0, 20.0, n, edges) == 0.0)
    # the band ratio is the photon-weighted combination of the binned ratios
    assert model.r_in_bins(1.0, 5.0, 20.0, n, [25.0, 50.0])[0] == pytest.approx(
        model.r_predicted(5.0, 20.0, n), rel=2e-2)


def test_invalid_inputs():
    with pytest.raises(ValueError):
        TracerModel(make_grid(ne=200, nk=80), band=(50.0, 25.0))
    m = TracerModel(make_grid(ne=200, nk=80))
    with pytest.raises(ValueError):
        m.band_photons(5.0, 20.0, -1.0)
    with pytest.raises(ValueError):
        m.r_mixture(1.5, 5.0, 20.0, 1e20)
