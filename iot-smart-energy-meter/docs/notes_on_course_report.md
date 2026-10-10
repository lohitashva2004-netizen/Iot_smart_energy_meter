# Notes on the submitted course report

This repository adds a tested reference model, a documented firmware and a measurement study around the project described in the MMIT mini-project report. A few observations from re-reading the report alongside its own photographs, kept here so the repo and the report can be read together.

| Topic | In the report | In this repo / evidence |
|---|---|---|
| **Energy unit on the LCD** | Energy is described in kWh. | The photograph of the running prototype shows `P:4.62 E:0.12`. At 4.62 W, 0.12 *Wh* accumulates in about 94 s, whereas 0.12 *kWh* would take about 26 hours. So the LCD figure is almost certainly Wh. The Blynk energy gauge reading "0" (range 0–10) matches kWh values of order 10⁻⁴. The firmware here shows Wh on the LCD and sends kWh to Blynk. |
| **Power = V × I** | "Power (W) = Voltage (RMS) × Current (RMS)". | Confirmed by the photo: 231.0 V × 0.020 A = 4.62 W exactly. This is *apparent* power; it equals real power only for a resistive load (PF = 1). |
| **Test load** | "AC incandescent lightbulb". | The bulb in the photographs looks like an LED lamp. LED drivers usually have a power factor below 1, so V × I overstates real power. The report's own future scope (power factor / real power) addresses this. |
| **How RMS is computed** | §3.4 mentions finding peak-to-peak values; the abstract says true RMS. | The firmware here computes true RMS from the mean-square of the sampled window, which is valid for non-sinusoidal loads too. |
| **Low-current accuracy** | 4.8 W "demonstrating sensitivity". | A 5 W load draws about 22 mA. With a 100 A-class CT the signal is about 1 mV RMS, close to one ADC step, so the reading is near the resolution floor ([measurement study](measurement_study.md)). Validate with a larger known load. |
| **Pins and CT variant** | Not specified ("a separate analog input pin"; "SCT-013"). | The firmware uses GPIO 34/35 and an SCT-013-000 with a 100 Ω burden as defaults (matching the circuit diagram's 100E). Change `config.h` if your build differs. |
| **"Secure connection" to Blynk** | Described as secure. | The standard Blynk header uses port 80; see [blynk_setup.md](blynk_setup.md). |
| **Persistent energy** | Accumulated in RAM. | This firmware also stores energy in flash every 10 minutes so a power cut does not reset it. |
