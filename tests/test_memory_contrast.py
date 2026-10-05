import math

import numpy as np
import pytest

from memory_contrast import (combined_sigma, exceeds, history_contrast, on_common_grid,
                             peak_abs, relaxation_check, tau_star)

T_REL = np.arange(0.0, 90.0, 1.0)


def response(t_rel):
    """Synthetic response of D to one pulse, zero before the onset."""
    t_rel = np.asarray(t_rel, float)
    return np.where(t_rel >= 0, t_rel * np.exp(-t_rel / 15.0), 0.0)


def branches(baseline, interaction, onset0=1.0, tk=41.0):
    """D of the four runs on T_REL for D = baseline + r(pulse 1) + r(b) + interaction(b)."""
    a0 = baseline + 0 * T_REL
    b0 = a0 + response(T_REL)
    a1 = a0 + response(T_REL + tk - onset0)          # pulse 1 seen from the test onset
    b1 = a1 + response(T_REL) + interaction
    return b1, a1, b0, a0


def test_additive_responses_give_zero_contrast():
    m = history_contrast(*branches(3.0, 0.0))
    assert np.max(np.abs(m)) == pytest.approx(0.0, abs=1e-12)


def test_known_interaction_is_recovered_exactly():
    inter = -0.3 * response(T_REL)                    # history weakens the response by 30 %
    m = history_contrast(*branches(3.0, inter))
    assert m == pytest.approx(inter, abs=1e-12)


def test_runs_with_different_output_cadences_are_aligned():
    t_fine = np.arange(0.0, 200.0, 0.1)
    t_coarse = np.arange(0.0, 200.0, 1.0)
    f = lambda t: np.sin(t / 20.0)
    a = on_common_grid(t_fine, f(t_fine), 41.0, T_REL)
    b = on_common_grid(t_coarse, f(t_coarse), 41.0, T_REL)
    assert a == pytest.approx(f(41.0 + T_REL), abs=1e-4)
    assert b == pytest.approx(f(41.0 + T_REL), abs=2e-3)


def test_no_extrapolation_outside_the_run():
    t = np.arange(0.0, 100.0, 1.0)
    with pytest.raises(ValueError, match="outside the run"):
        on_common_grid(t, t, 41.0, T_REL)            # needs t up to 130 s


def test_branches_on_different_grids_are_rejected():
    with pytest.raises(ValueError):
        history_contrast(np.zeros(3), np.zeros(3), np.zeros(3), np.zeros(4))


def test_nan_is_a_failed_run_not_a_small_effect():
    with pytest.raises(ValueError, match="NaN"):
        peak_abs(np.array([0.1, math.nan]))
    assert peak_abs(np.array([0.1, -0.5])) == 0.5


def test_combined_sigma_adds_in_quadrature():
    assert combined_sigma(3.0, 4.0, 0.0) == pytest.approx(5.0)
    assert combined_sigma([3.0, 0.0], 4.0, [0.0, 3.0]) == pytest.approx([5.0, 5.0])
    with pytest.raises(ValueError):
        combined_sigma(-1.0, 0.0, 0.0)


def test_exceeds_uses_k_sigma():
    assert list(exceeds([2.9, 3.1, -3.1], 1.0, k=3.0)) == [False, True, True]
    with pytest.raises(ValueError):
        exceeds([1.0], 1.0, k=0.0)


def test_tau_star_for_a_decaying_contrast():
    r = tau_star([120.0, 10.0, 60.0, 30.0], [0.5, 10.0, 1.0, 4.0], 1.0, k=3.0)
    assert r == {"tau_star_s": 60.0, "fails_at_s": [10.0, 30.0], "adequate_everywhere": False}


def test_tau_star_when_the_approximation_always_fails_or_always_holds():
    never = tau_star([10.0, 30.0], [9.0, 8.0], 1.0)
    assert never["tau_star_s"] is None and never["fails_at_s"] == [10.0, 30.0]
    always = tau_star([10.0, 30.0], [0.1, 0.2], 1.0)
    assert always == {"tau_star_s": 10.0, "fails_at_s": [], "adequate_everywhere": True}


def test_tau_star_needs_adequacy_at_every_longer_tau():
    r = tau_star([10.0, 30.0, 60.0, 120.0], [10.0, 1.0, 5.0, 0.5], 1.0)
    assert r["tau_star_s"] == 120.0 and r["fails_at_s"] == [10.0, 60.0]


def test_relaxation_is_judged_from_state_variables():
    a0 = {"N_cor": 1.7e18, "n_apex": 1.0e9, "T_apex": 1.0e6}
    near = {"N_cor": 1.75e18, "n_apex": 1.02e9, "T_apex": 1.0e6}
    far = {"N_cor": 5.0e19, "n_apex": 1.02e9, "T_apex": 1.0e6}
    tol = {"N_cor": 0.05, "n_apex": 0.05, "T_apex": 0.05}
    assert relaxation_check(near, a0, tol)["relaxed"] is True
    out = relaxation_check(far, a0, tol)
    assert out["relaxed"] is False and out["variables"]["N_cor"]["within"] is False
    with pytest.raises(ValueError):
        relaxation_check(near, a0, {"TR_column_mass": 0.05})
