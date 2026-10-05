import json

import pytest

from experiments import (PILOT, PILOT_TAUS, BaseCase, build_experiments, build_paired_branches,
                         write_paired_branches)


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


# --- Paired branches of the core experiment (docs/00, Section 3.1) ---

@pytest.fixture(scope="module")
def paired():
    return {e.name: e for e in build_paired_branches(PILOT, PILOT_TAUS)}


def test_paired_branch_names(paired):
    assert list(paired) == ["A0_no_beam", "B0_test_relaxed"] + [
        "%s_tau%gs" % (x, tau) for tau in PILOT_TAUS for x in ("A1", "B1")]


def test_waiting_time_runs_from_end_of_pulse1_to_test_onset(paired):
    for tau in PILOT_TAUS:
        e = paired["B1_tau%gs" % tau]
        p1, b = e.components[0].pulses
        assert b.t_start - p1.t_end == pytest.approx(tau)
        assert e.marks["test_onset"] == b.t_start


def test_a1_and_b1_are_identical_before_the_test_pulse(paired):
    half = PILOT.ramp / 2.0
    for tau in PILOT_TAUS:
        a1 = paired["A1_tau%gs" % tau].components[0].table
        b1 = paired["B1_tau%gs" % tau].components[0].table
        tk = paired["B1_tau%gs" % tau].marks["test_onset"]
        assert b1.rows[:len(a1.rows)] == a1.rows
        t = 0.0
        while t < tk - half:
            assert b1.flux_at(t) == a1.flux_at(t), (tau, t)
            t += 0.05


def test_the_test_pulse_is_the_same_in_every_history(paired):
    b0 = paired["B0_test_relaxed"]
    p0 = b0.components[0].pulses[0]
    for tau in PILOT_TAUS:
        b1 = paired["B1_tau%gs" % tau]
        assert b1.components[0].pulses[1] == p0.shifted(b1.marks["test_onset"] - b0.marks["test_onset"])


def test_test_pulse_adds_the_same_energy_to_every_history(paired):
    e_b = PILOT.pulses()[0].energy_erg
    assert paired["A0_no_beam"].energy_erg() == 0.0
    assert paired["B0_test_relaxed"].energy_erg() == pytest.approx(e_b, rel=1e-12)
    for tau in PILOT_TAUS:
        d = paired["B1_tau%gs" % tau].energy_erg() - paired["A1_tau%gs" % tau].energy_erg()
        assert d == pytest.approx(e_b, rel=1e-12)


def test_every_branch_covers_the_window_after_its_test_onset(paired):
    after = PILOT.duration + PILOT.tail
    for name, e in paired.items():
        if name != "A0_no_beam":
            assert e.components[0].t_end_sim == pytest.approx(e.marks["test_onset"] + after), name
    longest = max(e.marks["test_onset"] for e in paired.values()) + after
    assert paired["A0_no_beam"].components[0].t_end_sim >= longest


def test_invalid_waiting_times_are_rejected():
    with pytest.raises(ValueError):
        build_paired_branches(PILOT, ())
    with pytest.raises(ValueError):
        build_paired_branches(PILOT, (30.0, 30.0))
    with pytest.raises(ValueError):
        build_paired_branches(PILOT, (0.1,))          # not longer than the 0.2 s ramp


def test_paired_branches_write_hydrad_and_radyn_tables(tmp_path):
    exps = write_paired_branches(PILOT, (30.0,), str(tmp_path))
    for e in exps:
        d = tmp_path / e.name / "tube"
        assert (d / "beam_heating_model.cfg").exists() and (d / "ftab.dat").exists()
    m = json.loads((tmp_path / "manifest.json").read_text())
    assert m["waiting_times_s"] == [30.0] and len(m["experiments"]) == 4
