import pytest

from beam_tables import Pulse, build_table
from experiments import BaseCase, build_experiments
from radyn_ftab import (RADYN_FLUX_FLOOR, RADYN_MAX_ROWS, parse_radyn_ftab, radyn_energy_per_area,
                        radyn_rows, to_radyn_ftab)


def pulse(t0, ec=20.0, delta=5.0):
    return Pulse(t0, 10.0, 3e34, ec, delta, 1e17)


def test_header_and_column_order_match_rftab_fp():
    table = build_table([pulse(1.0)], ramp=0.2)
    text = to_radyn_ftab(table, t_end=60.0)
    (mbeam, charge, patype, sigma), rows = parse_radyn_ftab(text)
    assert (mbeam, charge, patype, sigma) == (511e3, 1.0, 2, 0.1)
    t, delta, ec, f = rows[len(rows) // 2]
    assert delta == pytest.approx(5.0) and ec == pytest.approx(20.0)   # delta before Ec, unlike HYDRAD


def test_table_starts_at_zero_ends_at_t_end_and_is_floored():
    rows = radyn_rows(build_table([pulse(1.0)], ramp=0.2), t_end=60.0)
    assert rows[0][0] == 0.0 and rows[-1][0] == 60.0
    assert min(r[3] for r in rows) == RADYN_FLUX_FLOOR      # never zero: RADYN interpolates log10(F)
    assert all(b[0] > a[0] for a, b in zip(rows, rows[1:]))


def test_t_end_before_last_row_is_rejected():
    with pytest.raises(ValueError):
        radyn_rows(build_table([pulse(1.0)], ramp=0.2), t_end=5.0)


def test_row_limit_is_enforced():
    with pytest.raises(ValueError):
        radyn_rows(build_table([pulse(1.0)], ramp=0.2), t_end=60.0, sample_dt=1e-6)


def test_energy_with_log_linear_interpolation_matches_intended_energy():
    ps = BaseCase().pulses()
    table = build_table(ps, ramp=0.2)
    rows = radyn_rows(table, t_end=100.0, sample_dt=0.02)
    intended = sum(p.flux * p.duration for p in ps)
    assert radyn_energy_per_area(rows) == pytest.approx(intended, rel=5e-3)
    assert len(rows) < RADYN_MAX_ROWS


def test_naive_unsubdivided_ramp_would_lose_energy():
    # a single linear ramp row-to-row, interpolated in log F, behaves like a late step
    table = build_table([pulse(1.0)], ramp=0.2)
    coarse = radyn_rows(table, t_end=60.0, sample_dt=10.0)      # no subdivision of the 0.2 s ramps
    fine = radyn_rows(table, t_end=60.0, sample_dt=0.02)
    assert radyn_energy_per_area(coarse) < radyn_energy_per_area(fine)


def test_all_experiment_tables_encode_within_one_percent():
    for e in build_experiments(BaseCase()):
        for c in e.components:
            rows = radyn_rows(c.table, t_end=c.t_end_sim)
            assert radyn_energy_per_area(rows) == pytest.approx(c.table.energy_per_area(), rel=1e-2), e.name


def test_round_trip_row_count_and_values():
    table = build_table([pulse(1.0), pulse(31.0, ec=25.0, delta=4.0)], ramp=0.2)
    text = to_radyn_ftab(table, t_end=100.0)
    _, rows = parse_radyn_ftab(text)
    assert len(rows) == len(radyn_rows(table, 100.0))
    # Ec and delta of the second pulse appear on its plateau
    assert any(abs(r[2] - 25.0) < 1e-6 and abs(r[1] - 4.0) < 1e-6 and r[3] > 1e9 for r in rows)
