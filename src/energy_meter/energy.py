"""Accumulating energy from power over real elapsed time."""

from __future__ import annotations


class EnergyAccumulator:
    """Integrates power over measured time slices (not an assumed fixed period).

    ``power_factor`` mirrors the report's simplification: with PF = 1 the
    accumulated figure is apparent energy (VAh) presented as kWh.
    """

    def __init__(self, power_factor: float = 1.0, wh: float = 0.0):
        if not 0 < power_factor <= 1:
            raise ValueError("power_factor must be in (0, 1]")
        self.power_factor = power_factor
        self.wh = wh

    def update(self, power_w: float, dt_s: float) -> float:
        if dt_s < 0:
            raise ValueError("dt must be non-negative")
        self.wh += power_w * self.power_factor * dt_s / 3600.0
        return self.wh

    @property
    def kwh(self) -> float:
        return self.wh / 1000.0

    def cost(self, tariff_per_kwh: float) -> float:
        return self.kwh * tariff_per_kwh

    def reset(self) -> None:
        self.wh = 0.0
