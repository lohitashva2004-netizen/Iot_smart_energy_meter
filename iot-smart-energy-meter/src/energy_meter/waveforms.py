"""Synthetic mains waveforms and a model of the ESP32's analog front end.

Everything here is a MODEL used for tests and the resolution study. Noise and
gain defaults are assumptions, not measurements of the prototype.
"""

from __future__ import annotations

from dataclasses import dataclass

import numpy as np

VREF = 3.3
ADC_BITS = 12
LSB_MV = VREF / (2 ** ADC_BITS - 1) * 1000          # ~0.806 mV
BIAS_V = VREF / 2                                   # 1.65 V: 2 x 10 k divider + 10 uF coupling


def mains_voltage(t, vrms: float = 230.0, f: float = 50.0):
    return vrms * np.sqrt(2) * np.sin(2 * np.pi * f * np.asarray(t))


def load_current(t, p_real_w: float, pf: float = 1.0, vrms: float = 230.0, f: float = 50.0):
    """Sinusoidal load current lagging the voltage by acos(pf); Irms = P / (V pf)."""
    irms = p_real_w / (vrms * pf)
    phi = np.arccos(pf)
    return irms * np.sqrt(2) * np.sin(2 * np.pi * f * np.asarray(t) - phi)


def quantize(volts, bits: int = ADC_BITS, vref: float = VREF):
    """Clip to the ADC range and round to the nearest code (returns volts)."""
    levels = 2 ** bits - 1
    codes = np.round(np.clip(volts, 0, vref) / vref * levels)
    return codes / levels * vref


@dataclass
class Frontend:
    """Voltage channel (ZMPT101B) and current channel (CT + burden) feeding the ADC."""
    zmpt_volts_per_volt: float = 1.2 / 325.0        # about 1.2 V amplitude at 230 V RMS (pot-adjustable)
    ct_amps_per_volt: float = 20.0                  # SCT-013-000 with a 100 ohm burden: 2000 / 100
    noise_mv_rms: float = 2.0                       # assumed ADC + analog noise (mV RMS)

    def sample(self, v_mains, i_mains, rng: np.random.Generator):
        noise = lambda n: rng.normal(0, self.noise_mv_rms / 1000, n)
        v_adc = BIAS_V + v_mains * self.zmpt_volts_per_volt + noise(len(v_mains))
        i_adc = BIAS_V + i_mains / self.ct_amps_per_volt + noise(len(i_mains))
        return quantize(v_adc), quantize(i_adc)
