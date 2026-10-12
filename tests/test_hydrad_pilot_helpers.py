import os
import sys

import numpy as np
import pytest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "scripts"))
import hydrad_paired_branches as hp  # noqa: E402


def write_profiles(d, times):
    for i, t in enumerate(times):
        with open(os.path.join(d, "profile%d.amr" % i), "w") as fh:
            fh.write("%.4f\n%d\n2.6e9\n0\n" % (t, i))


def test_profile_times_reads_amr_headers(tmp_path):
    write_profiles(tmp_path, [0.0, 1.0009, 2.0004])
    (tmp_path / "profile0.phy").write_text("")
    assert hp.profile_times(str(tmp_path)) == {0: 0.0, 1: 1.0009, 2: 2.0004}


def test_restart_index_is_the_last_profile_before_the_test_ramp(tmp_path):
    times = {i: i + 0.0009 for i in range(70)}
    assert hp.restart_index(times, 60.9) == 60       # tau = 30 s: ramp starts at 60.9 s
    assert hp.restart_index(times, 41.9) == 41
    with pytest.raises(ValueError):
        hp.restart_index(times, 0.0)


def test_restart_never_uses_a_profile_written_inside_the_ramp():
    times = {60: 60.0, 61: 60.95}
    assert hp.restart_index(times, 60.9) == 60


def test_restart_refuses_a_profile_far_before_t_k():
    times = {i: float(i) for i in range(133)}      # run stopped at 132 s
    with pytest.raises(ValueError, match="last profile"):
        hp.restart_index(times, 150.9)
    times = {0: 0.0, 1: 1.0, 2: 90.6, 3: 271.6}    # output times jump after a failure
    with pytest.raises(ValueError, match="last profile"):
        hp.restart_index(times, 120.9)


def test_totals_of_a_uniform_loop():
    ds = np.full(10, 1e8)
    p = {"nh": np.full(10, 1e9), "ne": np.full(10, 1e9), "te": np.full(10, 1e6), "th": np.full(10, 1e6),
         "v": np.zeros(10), "ds": ds}
    tot = hp.totals(p)
    assert tot["N_total"] == pytest.approx(1e18)
    assert tot["E_total"] == pytest.approx(3.0 * 1e9 * hp.K_B * 1e6 * 1e9)


def test_mass_window_ends_before_the_first_departure():
    t = np.arange(0.0, 10.0)
    n = np.array([1.0, 1.0, 1.005, 0.999, 0.98, 0.9, 1.0, 1.0, 1.0, 1.0])
    assert hp.mass_valid_until(t, n, 1.0) == 3.0
    assert hp.mass_valid_until(t, np.ones(10), 1.0) == 9.0
    assert hp.mass_valid_until(t, np.full(10, 0.5), 1.0) == float("-inf")


def test_ic_config_sets_length_and_chromosphere_depth():
    text = hp.ic_config(6.0e9, 8e8).splitlines()
    assert text[2] == "6.0000E+09" and text[4] == "8.0000E+08"
    assert hp.ic_config(2.6e9).splitlines()[4] == "5.0000E+08"


def test_grid_scale_oscillation_is_detected():
    smooth = np.linspace(1e6, 5e6, 200)
    zigzag = smooth + np.where(np.arange(200) % 2, 1e6, -1e6)
    assert hp.oscillating_fraction(smooth) < 0.1
    assert hp.oscillating_fraction(zigzag) > 0.9
    t = np.arange(5.0)
    assert hp.stable_until(t, [0.3, 0.3, 0.9, 0.95, 0.99]) == 1.0
    assert hp.stable_until(t, [0.3] * 5) == 4.0
