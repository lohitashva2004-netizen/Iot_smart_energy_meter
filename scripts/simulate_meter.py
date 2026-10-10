"""Simulate the meter running: prints what the LCD would show every 2 s.

    python scripts/simulate_meter.py --load-w 4.8 --pf 1.0 --minutes 2
"""

import argparse

import numpy as np

from energy_meter.energy import EnergyAccumulator
from energy_meter.simulate import calibrate_frontend, measure
from energy_meter.waveforms import Frontend


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--load-w", type=float, default=4.8, help="true real power of the load")
    ap.add_argument("--pf", type=float, default=1.0)
    ap.add_argument("--minutes", type=float, default=2.0)
    ap.add_argument("--noise-mv", type=float, default=2.0, help="assumed ADC noise (mV RMS)")
    ap.add_argument("--seed", type=int, default=1)
    a = ap.parse_args()
    rng = np.random.default_rng(a.seed)
    fe = Frontend(noise_mv_rms=a.noise_mv)
    vs, is_ = calibrate_frontend(fe, rng)
    energy = EnergyAccumulator()
    for k in range(int(a.minutes * 30)):
        r = measure(a.load_w, a.pf, fe, vs, is_, rng)
        energy.update(r["apparent_va"], 2.0)             # firmware integrates V x I, as in the report
        if k % 5 == 0:
            print(f"t={2 * k:4d}s | V:{r['v_rms']:.1f} I:{r['i_rms']:.3f} | P:{r['apparent_va']:.2f} E:{energy.wh:.2f}Wh"
                  f"   (true P {a.load_w:.2f} W, real-power estimate {r['real_w']:.2f} W)")
    print(f"accumulated: {energy.wh:.3f} Wh = {energy.kwh:.6f} kWh")


if __name__ == "__main__":
    main()
