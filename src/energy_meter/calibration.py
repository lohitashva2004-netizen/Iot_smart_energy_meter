"""Turning ADC-side numbers into real units, and calibrating them against references."""

from __future__ import annotations


def ct_amps_per_volt(ct_ratio: float | None = None, burden_ohms: float | None = None,
                     amps_per_volt: float | None = None) -> float:
    """Primary amps per volt of burden voltage.

    Current-output CT (e.g. SCT-013-000: 100 A : 50 mA -> ratio 2000):
        I_secondary = I_primary / ratio ;  V_burden = I_secondary x R_burden
        => amps_per_volt = ratio / R_burden
    Voltage-output CT (e.g. SCT-013-030: 30 A : 1 V): pass amps_per_volt directly.
    """
    if amps_per_volt is not None:
        return float(amps_per_volt)
    if ct_ratio is None or burden_ohms is None:
        raise ValueError("give ct_ratio and burden_ohms, or amps_per_volt")
    return ct_ratio / burden_ohms


def voltage_scale(reference_volts: float, measured_mv_rms: float) -> float:
    """Volts of mains per mV of ADC-side RMS, from one multimeter reading."""
    if measured_mv_rms <= 0:
        raise ValueError("measured RMS must be positive")
    return reference_volts / measured_mv_rms


def current_scale(reference_amps: float, measured_mv_rms: float) -> float:
    """Amps per mV of ADC-side RMS, from a load of known current."""
    if measured_mv_rms <= 0:
        raise ValueError("measured RMS must be positive")
    return reference_amps / measured_mv_rms


def subtract_noise_floor(measured_rms: float, noise_floor_rms: float) -> float:
    """Remove a zero-load noise floor in quadrature (independent noise adds in power)."""
    d = measured_rms ** 2 - noise_floor_rms ** 2
    return d ** 0.5 if d > 0 else 0.0
