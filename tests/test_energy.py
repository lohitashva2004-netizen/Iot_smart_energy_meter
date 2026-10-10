import pytest
from energy_meter.energy import EnergyAccumulator


def test_one_kilowatt_for_one_hour_is_one_kwh():
    e = EnergyAccumulator()
    for _ in range(3600):
        e.update(1000, 1.0)
    assert e.kwh == pytest.approx(1.0) and e.wh == pytest.approx(1000.0)


def test_uses_real_elapsed_time_not_a_fixed_period():
    a, b = EnergyAccumulator(), EnergyAccumulator()
    a.update(100, 7.3)
    for _ in range(73):
        b.update(100, 0.1)
    assert a.wh == pytest.approx(b.wh)


def test_bulb_example_matches_the_prototype_lcd_order_of_magnitude():
    e = EnergyAccumulator()
    e.update(4.62, 94)                    # ~94 s at 4.62 W
    assert e.wh == pytest.approx(0.12, abs=0.005)   # the LCD's "E:0.12" is watt-hours, not kWh
    assert e.kwh < 0.001


def test_cost_and_reset():
    e = EnergyAccumulator(wh=2500)
    assert e.cost(8.0) == pytest.approx(20.0)
    e.reset()
    assert e.wh == 0


def test_power_factor_scales_energy():
    e = EnergyAccumulator(power_factor=0.5)
    e.update(100, 3600)
    assert e.wh == pytest.approx(50.0)


@pytest.mark.parametrize("bad", [0, -0.1, 1.5])
def test_invalid_power_factor_rejected(bad):
    with pytest.raises(ValueError):
        EnergyAccumulator(power_factor=bad)


def test_negative_dt_rejected():
    with pytest.raises(ValueError):
        EnergyAccumulator().update(10, -1)
