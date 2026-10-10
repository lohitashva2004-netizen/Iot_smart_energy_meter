"""End-to-end simulation of one measurement window through the model front end."""

from __future__ import annotations

import numpy as np

from .calibration import current_scale, voltage_scale
from .dsp import apparent_power, power_factor, real_power, rms
from .waveforms import Frontend, load_current, mains_voltage

FS = 5000            # samples per second per channel (assumed achievable on the ESP32)
CYCLES = 10          # 200 ms window = 10 mains cycles at 50 Hz, so no partial-cycle bias


def window_times(fs: int = FS, cycles: int = CYCLES, f: float = 50.0):
    return np.arange(int(fs * cycles / f)) / fs


def calibrate_frontend(fe: Frontend, rng, vrms: float = 230.0, p_ref_w: float = 100.0):
    """Calibrate against a 230 V reference and a 100 W resistive load, like a bench procedure."""
    t = window_times()
    v_adc, i_adc = fe.sample(mains_voltage(t, vrms), load_current(t, p_ref_w, 1.0, vrms), rng)
    return (voltage_scale(vrms, rms(v_adc) * 1000),
            current_scale(p_ref_w / vrms, rms(i_adc) * 1000))


def measure(p_real_w: float, pf: float, fe: Frontend, v_scale: float, i_scale: float,
            rng, vrms: float = 230.0) -> dict:
    t = window_times()
    v_adc, i_adc = fe.sample(mains_voltage(t, vrms), load_current(t, p_real_w, pf, vrms), rng)
    v_est, i_est = rms(v_adc) * 1000 * v_scale, rms(i_adc) * 1000 * i_scale
    p_est = real_power(v_adc, i_adc) * 1e6 * v_scale * i_scale      # mV x mV -> scaled
    return {"v_rms": v_est, "i_rms": i_est, "apparent_va": apparent_power(v_est, i_est),
            "real_w": p_est, "pf_est": power_factor(p_est, v_est, i_est),
            "i_true": p_real_w / (vrms * pf), "apparent_true": p_real_w / pf}
