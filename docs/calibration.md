# Calibration

Raw ADC readings are in millivolts at the ESP32 pin; real units need two scale factors. The firmware stores them in flash, so you calibrate once.

| Quantity | Formula | Serial command |
|---|---|---|
| Voltage scale (V per mV) | `reference volts / measured mV RMS` | `cv <multimeter reading>` |
| Current scale (A per mV) | `reference amps / measured mV RMS` (after noise-floor removal) | `ci <known amps>` |
| Current noise floor (mV) | RMS of the current channel with **no load** | `zero` |

Other commands: `show` (print stored values), `reset` (zero the energy counter). Open the Arduino Serial Monitor at 115200 baud, line ending "Newline".

## Procedure

1. **Voltage.** Measure the mains with a trusted multimeter while the meter runs. Type `cv 229.5` (your reading). The meter now maps its ADC-side RMS to that value. Adjust the ZMPT101B trim pot beforehand so the waveform uses a good part of the ADC range without clipping.
2. **Current noise floor.** With the clamp on the wire and the load **off**, type `zero`.
3. **Current scale.** Switch on a load of known current. A resistive load of 40–100 W is far better than a 5 W lamp, because low currents sit close to the ADC resolution floor (see [measurement_study.md](measurement_study.md)). Compute its current from a clamp meter or its rating, then type `ci 0.435` (your value).
4. Type `show` and note the values; they persist across reboots.

## Starting values

`config.h` sets the current scale from the CT type: `A/V = CT ratio / burden` for a current-output CT (SCT-013-000: 2000 / 100 Ω = **20 A/V**), or the rated amps-per-volt for a voltage-output CT (SCT-013-030: **30 A/V**). The voltage default is only a placeholder, so always calibrate it.

## Doing the same maths in Python

```python
from energy_meter import ct_amps_per_volt, voltage_scale

print(ct_amps_per_volt(ct_ratio=2000, burden_ohms=100))   # 20.0 A per volt
print(voltage_scale(229.5, 850.0))                         # volts per mV from one multimeter reading
```
