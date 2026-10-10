import numpy as np
import pytest
from energy_meter.simulate import calibrate_frontend, measure
from energy_meter.waveforms import LSB_MV, Frontend, load_current, mains_voltage, quantize


def test_lsb_of_12_bit_adc():
    assert LSB_MV == pytest.approx(0.806, abs=0.001)


def test_quantize_clips_and_rounds():
    q = quantize(np.array([-1.0, 1.65, 5.0]))
    assert q[0] == 0 and q[2] == pytest.approx(3.3) and q[1] == pytest.approx(1.65, abs=0.001)


def test_load_current_pf_and_rms():
    t = np.arange(1000) / 1000 * 0.2
    i = load_current(t, 230.0, pf=0.5)
    assert np.sqrt(np.mean(i ** 2)) == pytest.approx(230 / (230 * 0.5), rel=1e-3)
    v = mains_voltage(t)
    assert np.mean(v * i) == pytest.approx(230.0, rel=1e-2)       # real power preserved


@pytest.fixture(scope="module")
def setup():
    rng = np.random.default_rng(3)
    fe = Frontend()
    vs, is_ = calibrate_frontend(fe, rng)
    return rng, fe, vs, is_


def test_mid_range_load_is_measured_within_two_percent(setup):
    rng, fe, vs, is_ = setup
    r = measure(1000, 1.0, fe, vs, is_, rng)
    assert r["v_rms"] == pytest.approx(230, rel=0.01)
    assert r["i_rms"] == pytest.approx(r["i_true"], rel=0.02)
    assert r["real_w"] == pytest.approx(1000, rel=0.02)


def test_low_current_rms_is_noise_dominated_but_real_power_is_not(setup):
    """The study's headline: at ~5 W the V x I product overstates, mean(v*i) does not."""
    rng, fe, vs, is_ = setup
    runs = [measure(4.8, 1.0, fe, vs, is_, rng) for _ in range(30)]
    assert np.mean([r["apparent_va"] for r in runs]) > 4.8 * 1.5       # V x I badly overstated
    assert np.mean([r["real_w"] for r in runs]) == pytest.approx(4.8, rel=0.1)


def test_reactive_load_apparent_power_exceeds_real_power(setup):
    rng, fe, vs, is_ = setup
    r = measure(100, 0.5, fe, vs, is_, rng)
    assert r["apparent_va"] == pytest.approx(200, rel=0.03)
    assert r["real_w"] == pytest.approx(100, rel=0.03)
    assert r["pf_est"] == pytest.approx(0.5, abs=0.03)
