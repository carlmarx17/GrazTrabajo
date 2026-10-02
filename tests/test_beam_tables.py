import math

import pytest

from beam_tables import (KEV_TO_ERG, BeamTable, Pulse, build_table, energy_flux,
                         naive_table, ndot_from_flux, power_erg_s)


def make(t_start=1.0, duration=10.0, ndot=3e34, ec=20.0, delta=5.0, area=1e17):
    return Pulse(t_start, duration, ndot, ec, delta, area)


def test_power_matches_hand_calculation():
    # Ndot = 1e35 e/s, Ec = 20 keV, delta = 5 -> P = 1e35 * 20 keV * 4/3
    expected = 1e35 * 20.0 * 1.602176634e-9 * 4.0 / 3.0
    assert power_erg_s(1e35, 20.0, 5.0) == pytest.approx(expected, rel=1e-12)
    assert energy_flux(1e35, 20.0, 5.0, 1e17) == pytest.approx(expected / 1e17, rel=1e-12)


def test_flux_ndot_round_trip():
    f = energy_flux(3e34, 15.0, 3.7, 4e16)
    assert ndot_from_flux(f, 15.0, 3.7, 4e16) == pytest.approx(3e34, rel=1e-12)


@pytest.mark.parametrize("delta", [2.0, 1.5, 0.0, -3.0, float("nan")])
def test_delta_not_above_two_is_rejected(delta):
    with pytest.raises(ValueError):
        power_erg_s(1e35, 20.0, delta)
    with pytest.raises(ValueError):
        make(delta=delta)


def test_single_pulse_energy_is_exact():
    p = make()
    t = build_table([p], ramp=0.2)
    assert t.energy_per_area() == pytest.approx(p.flux * p.duration, rel=1e-12)


def test_plateau_gap_and_outside_values():
    p1, p2 = make(1.0), make(31.0)
    t = build_table([p1, p2], ramp=0.2)
    assert t.flux_at(6.0) == pytest.approx(p1.flux)
    assert t.flux_at(21.0) == 0.0          # middle of the gap
    assert t.flux_at(36.0) == pytest.approx(p2.flux)
    assert t.flux_at(0.0) == 0.0           # before first row
    assert t.flux_at(1e3) == 0.0           # after last row
    assert t.flux_at(1.0) == pytest.approx(0.5 * p1.flux)  # centre of a centred ramp


def test_numerical_integration_agrees_with_analytic_energy():
    ps = [make(1.0), make(31.0), make(61.0, duration=4.0)]
    t = build_table(ps, ramp=0.3)
    t0, t1 = t.t_first, t.t_last
    h = (t1 - t0) / 40000  # midpoint rule, independent of the analytic trapezoid sum
    num = sum(t.flux_at(t0 + (i + 0.5) * h) * h for i in range(40000))
    assert num == pytest.approx(sum(p.flux * p.duration for p in ps), rel=2e-4)


def test_cfg_round_trip_and_header_token_count():
    t = build_table([make(1.0), make(31.0)], ramp=0.2)
    text = t.to_cfg()
    tokens = text.split()
    assert int(tokens[0]) == len(t.rows) == 8
    # HYDRAD skips exactly 7 header tokens after the count
    assert tokens[1:8] == ["Time", "Energy_flux", "Cut-off", "Spectral_index",
                           "[s]", "[erg/cm^2/s]", "[keV]"]
    back = BeamTable.from_cfg(text)
    assert len(back.rows) == len(t.rows)
    for a, b in zip(back.rows, t.rows):
        assert a == pytest.approx(b, rel=1e-9)


def hydrad_interpolation(rows, t):
    """Line-by-line port of CHeat::CalculateBeamParameters (heat.cpp), n >= 2."""
    n = len(rows)
    if t < rows[0][0] or t > rows[n - 1][0]:
        return None
    i = 0
    while i < n - 1:
        if t < rows[i + 1][0]:
            break
        i += 1
    i = min(i, n - 2)
    out = []
    for k in (1, 2, 3):
        x1, x2 = rows[i][0], rows[i + 1][0]
        y1, y2 = rows[i][k], rows[i + 1][k]
        grad = (y2 - y1) / (x2 - x1)
        out.append(grad * (t - x2) + y2)
    return tuple(out)


def test_python_interpolation_matches_hydrad_port():
    t = build_table([make(1.0, ec=20, delta=5), make(31.0, ec=30, delta=4)], ramp=0.2)
    for x in [0.95, 1.05, 3.3, 10.9, 11.2, 20.0, 30.95, 31.0, 31.05, 40.0]:
        ref = hydrad_interpolation(t.rows, x)
        assert t.at(x) == pytest.approx(ref, rel=1e-12), x
    # outside the table HYDRAD's CalculateBeamHeating returns zero heating
    assert hydrad_interpolation(t.rows, 41.2) is None and t.flux_at(41.2) == 0.0


def test_delta_stays_above_two_between_rows_with_different_pulses():
    t = build_table([make(1.0, delta=2.5), make(31.0, delta=6.0)], ramp=0.2)
    for i in range(0, 4200):
        assert t.at(i * 0.01)[2] > 2.0


def test_naive_two_row_encoding_injects_energy_in_the_gap():
    ps = [make(1.0), make(31.0)]
    good, bad = build_table(ps, 0.2), naive_table(ps)
    f = ps[0].flux
    assert good.energy_per_area() == pytest.approx(2 * f * 10.0, rel=1e-12)
    assert bad.energy_per_area() == pytest.approx(f * 40.0, rel=1e-12)   # fills the 20 s gap
    assert bad.flux_at(21.0) == pytest.approx(f)


@pytest.mark.parametrize("ps, ramp", [
    ([make(1.0), make(11.1)], 0.2),            # gap 0.1 s <= ramp
    ([make(1.0), make(31.0, area=2e17)], 0.2),  # different tube areas in one table
    ([make(0.05)], 0.2),                       # ramp would start before t = 0
    ([make(1.0, duration=0.2)], 0.2),          # pulse not longer than ramp
    ([make(1.0)], 0.0),                        # zero ramp -> HYDRAD divides by zero
    ([], 0.2),
])
def test_invalid_tables_are_rejected(ps, ramp):
    with pytest.raises(ValueError):
        build_table(ps, ramp)


def test_rows_must_increase_strictly():
    with pytest.raises(ValueError):
        BeamTable(((0.0, 0.0, 20.0, 5.0), (0.0, 1.0, 20.0, 5.0)))
