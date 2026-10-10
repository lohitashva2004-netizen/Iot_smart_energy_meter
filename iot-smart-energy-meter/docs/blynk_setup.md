# Blynk setup

The firmware sends four values with `Blynk.virtualWrite`:

| Virtual pin | Quantity | Unit | Widget in the project's dashboard | Range used |
|---|---|---|---|---|
| V1 | Voltage | V | Gauge | 0–500 |
| V2 | Current | A | Gauge | 0–30 |
| V3 | Power | W | Gauge | 0–50 |
| V4 | Energy | kWh | Gauge / value display | 0–10 |

![Blynk dashboard](images/blynk_dashboard.jpg)

## Steps

1. In the Blynk Console create a **Template** (hardware: ESP32, connection: Wi-Fi) and add four **datastreams** on V1–V4 (type: Double). Give them the units and ranges above.
2. Add widgets: gauges for voltage and power, value displays for current and energy, and a **SuperChart** on V3 for the power history.
3. Create a **Device** from the template and copy the template ID, template name and **auth token**.
4. Copy `firmware/smart_energy_meter/secrets.example.h` to `secrets.h` and paste the Wi-Fi details and the three Blynk values. `secrets.h` is git-ignored.
5. Flash the sketch (libraries: *Blynk*, *LiquidCrystal I2C*; board: ESP32 Dev Module).

## Tips

- **Decimals.** Gauges default to whole numbers, so a 0.02 A current or an energy of 0.0001 kWh shows as "0". Set the datastream to show 2–4 decimals (the project's screenshot shows these values rounded to integers).
- **Energy units.** V4 is in **kWh**. The LCD shows energy in **Wh** below 1 kWh (e.g. `E:0.12Wh`), because kWh figures for small loads would read 0.000.
- **Security.** `BlynkSimpleEsp32.h` connects on the default port 80. For an encrypted link use the library's SSL variant and review Blynk's current guidance. Never commit the auth token.
- The meter keeps measuring and displaying locally if Wi-Fi or Blynk is unreachable; it retries Blynk every 15 s.
