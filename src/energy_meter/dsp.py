"""True-RMS and power maths: the same algorithm the firmware runs on the ESP32.

The ADC sees each AC signal riding on a DC bias (about 1.65 V). Per channel the
firmware (1) averages the window to find the bias, (2) subtracts it, (3) takes the
root of the mean square. Using the *mean-square* rather than peak-to-peak makes
the result valid for non-sinusoidal waveforms too.
"""

from __future__ import annotations

import numpy as np


def remove_dc(x) -> np.ndarray:
    """Subtract the window mean (the ADC bias)."""
    x = np.asarray(x, dtype=float)
    return x - x.mean()


def rms(x, remove_offset: bool = True) -> float:
    """True RMS of a sampled window."""
    x = np.asarray(x, dtype=float)
    if remove_offset:
        x = remove_dc(x)
    return float(np.sqrt(np.mean(x * x)))


def apparent_power(v_rms: float, i_rms: float) -> float:
    """S = Vrms x Irms (VA). This is what the report's P = V x I computes."""
    return v_rms * i_rms


def real_power(v_inst, i_inst) -> float:
    """P = mean(v(t) * i(t)) over whole cycles (W). Needs simultaneous v and i samples."""
    return float(np.mean(remove_dc(v_inst) * remove_dc(i_inst)))


def power_factor(p_real: float, v_rms: float, i_rms: float) -> float:
    s = apparent_power(v_rms, i_rms)
    return p_real / s if s > 0 else 0.0
