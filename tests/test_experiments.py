import pytest

from experiments import BaseCase, build_experiments


@pytest.fixture(scope="module")
def exps():
    return {e.name: e for e in build_experiments(BaseCase())}


def test_five_experiments_present(exps):
    assert list(exps) == ["E1_single_relaxed", "E2_same_strand", "E3a_independent_same_flux",
                          "E3b_independent_equal_area", "E4_continuous", "E5_relaxation"]


def test_comparable_total_energy(exps):
    base = BaseCase()
    p = base.pulses()[0]
    e_total = base.n_pulses * p.energy_erg
    for name in ("E2_same_strand", "E3a_independent_same_flux",
                 "E3b_independent_equal_area", "E4_continuous"):
        assert exps[name].energy_erg() == pytest.approx(e_total, rel=1e-12), name
    for name in ("E1_single_relaxed", "E5_relaxation"):
        assert exps[name].energy_erg() == pytest.approx(p.energy_erg, rel=1e-12), name


def test_fragmentation_conserves_total_power_time_series(exps):
    e2 = exps["E2_same_strand"]
    peak = max(c.area_cm2 * max(r[1] for r in c.table.rows) for c in e2.components)
    for name in ("E3a_independent_same_flux", "E3b_independent_equal_area"):
        e3 = exps[name]
        for i in range(0, 8200):
            t = i * 0.01
            assert e3.power(t) == pytest.approx(e2.power(t), rel=1e-9, abs=1e-9 * peak), (name, t)


def test_emitting_area_differs_as_documented(exps):
    A = BaseCase().area_cm2
    assert exps["E2_same_strand"].total_area_cm2() == pytest.approx(A)
    assert exps["E3a_independent_same_flux"].total_area_cm2() == pytest.approx(2 * A)
    assert exps["E3b_independent_equal_area"].total_area_cm2() == pytest.approx(A)


def test_equal_area_fragmentation_has_n_times_the_flux(exps):
    f2 = max(r[1] for r in exps["E2_same_strand"].components[0].table.rows)
    f3b = max(r[1] for r in exps["E3b_independent_equal_area"].components[0].table.rows)
    assert f3b == pytest.approx(2 * f2, rel=1e-12)


def test_identical_pulses_make_e1_and_e5_tables_identical(exps):
    a = exps["E1_single_relaxed"].components[0].table.rows
    b = exps["E5_relaxation"].components[0].table.rows
    assert len(a) == len(b)
    for ra, rb in zip(a, b):
        assert ra == pytest.approx(rb, rel=1e-12)


def test_continuous_control_has_lower_flux_over_the_same_window(exps):
    base = BaseCase()
    fc = max(r[1] for r in exps["E4_continuous"].components[0].table.rows)
    fp = base.pulses()[0].flux
    window = base.t_last_end - base.t0
    assert fc == pytest.approx(2 * fp * base.duration / window, rel=1e-12)


def test_runs_cover_the_requested_timeline(exps):
    for e in exps.values():
        for c in e.components:
            assert c.t_end_sim >= c.table.t_last
            assert c.t_end_sim + c.offset >= e.t_end_global - 1e-9


def test_three_pulse_configuration_also_conserves_energy():
    es = {e.name: e for e in build_experiments(BaseCase(n_pulses=3))}
    ref = es["E2_same_strand"].energy_erg()
    for name in ("E3a_independent_same_flux", "E3b_independent_equal_area", "E4_continuous"):
        assert es[name].energy_erg() == pytest.approx(ref, rel=1e-12)
    assert es["E3b_independent_equal_area"].total_area_cm2() == pytest.approx(BaseCase().area_cm2)
