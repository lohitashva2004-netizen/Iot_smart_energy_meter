import pytest
from energy_meter.calibration import ct_amps_per_volt, current_scale, subtract_noise_floor, voltage_scale


def test_sct013_000_with_100_ohm_burden():
    # 100 A : 50 mA -> ratio 2000 ; 100 ohm burden -> 20 A per volt
    assert ct_amps_per_volt(ct_ratio=2000, burden_ohms=100) == pytest.approx(20.0)


def test_voltage_output_ct_passes_through():
    assert ct_amps_per_volt(amps_per_volt=30.0) == 30.0       # SCT-013-030: 30 A : 1 V


def test_ct_requires_enough_information():
    with pytest.raises(ValueError):
        ct_amps_per_volt(ct_ratio=2000)


def test_voltage_scale_from_multimeter_reading():
    # multimeter says 229.5 V while the ADC side measures 850 mV RMS
    k = voltage_scale(229.5, 850.0)
    assert k * 850.0 == pytest.approx(229.5)


def test_current_scale_roundtrip():
    assert current_scale(0.4348, 21.85) * 21.85 == pytest.approx(0.4348)


@pytest.mark.parametrize("fn", [voltage_scale, current_scale])
def test_scale_rejects_zero_signal(fn):
    with pytest.raises(ValueError):
        fn(1.0, 0.0)


def test_noise_floor_subtraction_is_quadrature():
    assert subtract_noise_floor(5.0, 3.0) == pytest.approx(4.0)
    assert subtract_noise_floor(2.0, 3.0) == 0.0
