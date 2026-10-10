import numpy as np
import pytest
from energy_meter.dsp import apparent_power, power_factor, real_power, remove_dc, rms


def sine(amp, n=1000, cycles=10, phase=0.0, dc=0.0):
    t = np.arange(n) / n
    return dc + amp * np.sin(2 * np.pi * cycles * t - phase)


def test_rms_of_sine_is_amplitude_over_sqrt2():
    assert rms(sine(325.0)) == pytest.approx(325.0 / np.sqrt(2), rel=1e-4)


def test_dc_bias_is_removed():
    assert rms(sine(1.0, dc=1.65)) == pytest.approx(1 / np.sqrt(2), rel=1e-4)
    assert abs(remove_dc(sine(1.0, dc=1.65)).mean()) < 1e-12


def test_rms_of_square_wave_is_amplitude():
    sq = np.where(np.arange(1000) % 100 < 50, 1.0, -1.0)
    assert rms(sq) == pytest.approx(1.0)            # true RMS holds for non-sinusoids (peak-to-peak method would not)


def test_zero_signal():
    assert rms(np.zeros(100)) == 0.0


def test_real_power_resistive_equals_vi():
    v, i = sine(325, phase=0), sine(10, phase=0)
    assert real_power(v, i) == pytest.approx(rms(v) * rms(i), rel=1e-4)


@pytest.mark.parametrize("deg", [0, 30, 60, 90])
def test_power_factor_is_cos_of_phase(deg):
    phi = np.deg2rad(deg)
    v, i = sine(325), sine(10, phase=phi)
    pf = power_factor(real_power(v, i), rms(v), rms(i))
    assert pf == pytest.approx(np.cos(phi), abs=1e-3)


def test_apparent_power_overstates_real_power_for_reactive_load():
    v, i = sine(325), sine(10, phase=np.deg2rad(60))
    assert apparent_power(rms(v), rms(i)) > real_power(v, i) * 1.9
