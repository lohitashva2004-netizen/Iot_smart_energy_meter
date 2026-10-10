// Hardware and measurement configuration. Edit to match YOUR build.
#pragma once

// ------------------------------------------------------------------ pins
// ADC1 pins only: ADC2 is unusable while Wi-Fi is on. Both are input-only GPIOs.
constexpr uint8_t PIN_VOLTAGE = 34;   // ZMPT101B output (biased to ~1.65 V)
constexpr uint8_t PIN_CURRENT = 35;   // SCT-013 conditioning circuit output (biased to ~1.65 V)
constexpr uint8_t LCD_ADDR    = 0x27; // try 0x3F if the display stays blank
// I2C: SDA = GPIO21, SCL = GPIO22 (ESP32 defaults)

// ----------------------------------------------------------------- timing
constexpr uint32_t SAMPLE_WINDOW_US   = 200000UL;   // 10 cycles at 50 Hz (use 166667 for 10 cycles at 60 Hz)
constexpr uint32_t REPORT_INTERVAL_MS = 2000;       // LCD + Blynk refresh
constexpr uint32_t BLYNK_RETRY_MS     = 15000;      // reconnect attempts while offline
constexpr uint32_t ENERGY_SAVE_MS     = 600000UL;   // persist energy every 10 min (limits flash wear)

// ------------------------------------------------------------ calibration
// Mains volts per millivolt of ADC-side RMS. A placeholder: CALIBRATE with the serial
// command `cv <multimeter reading>` (see docs/calibration.md). The result is stored in flash.
constexpr float DEFAULT_VOLTS_PER_MV = 0.25f;

// Primary amps per volt of burden voltage:
//   SCT-013-000 (100 A : 50 mA) with 100 ohm burden -> 2000 / 100 = 20 A/V
//   SCT-013-005 (5 A : 1 V)                          ->  5 A/V
//   SCT-013-030 (30 A : 1 V)                         -> 30 A/V
constexpr float CT_AMPS_PER_VOLT = 20.0f;
constexpr float DEFAULT_AMPS_PER_MV = CT_AMPS_PER_VOLT / 1000.0f;

// Zero-load RMS of the current channel (mV). Measured with `zero` and subtracted in quadrature.
constexpr float DEFAULT_CURRENT_NOISE_FLOOR_MV = 0.0f;

// The original design assumes a resistive load (PF = 1), so P = V x I (apparent power).
constexpr float ASSUMED_POWER_FACTOR = 1.0f;
