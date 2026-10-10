/*
 * IoT Smart Energy Meter - ESP32 firmware
 *
 * Measures mains voltage (ZMPT101B) and current (SCT-013 clamp CT), computes true-RMS
 * values, power and accumulated energy, shows them on a 16x2 I2C LCD and streams them
 * to Blynk (V1 voltage, V2 current, V3 power, V4 energy in kWh).
 *
 * The meter keeps measuring and showing readings on the LCD when Wi-Fi or the cloud is
 * down; Blynk is retried in the background.
 *
 * Libraries (Library Manager): "Blynk" (Volodymyr Shymanskyy), "LiquidCrystal I2C".
 *
 * SAFETY: this device is wired to MAINS VOLTAGE. Build and test with the supply
 * disconnected, keep the high-voltage side enclosed, and never touch the circuit live.
 */

#include "secrets.h"            // must come BEFORE the Blynk header (template id / name / token)
#include "config.h"

#include <WiFi.h>
#include <BlynkSimpleEsp32.h>
#include <Wire.h>
#include <LiquidCrystal_I2C.h>
#include <Preferences.h>
#include <math.h>

LiquidCrystal_I2C lcd(LCD_ADDR, 16, 2);
Preferences prefs;

float voltsPerMv, ampsPerMv, currentFloorMv;
double energyWh = 0.0;
float lastVmv = 0, lastImv = 0;                     // last raw RMS windows (for calibration commands)
uint32_t lastReport = 0, lastSave = 0, lastBlynkTry = 0;

// ------------------------------------------------------------------ sampling
// One pass over a whole number of mains cycles: accumulate sum and sum of squares of
// both channels, then RMS = sqrt(E[x^2] - mean^2). Subtracting the mean removes the
// 1.65 V ADC bias, and using mean-square gives true RMS for non-sinusoidal loads too.
void sampleWindow(float &vRmsMv, float &iRmsMv) {
  double sv = 0, svv = 0, si = 0, sii = 0;
  uint32_t n = 0, t0 = micros();
  while (micros() - t0 < SAMPLE_WINDOW_US) {
    double v = analogReadMilliVolts(PIN_VOLTAGE);   // eFuse-calibrated reading in mV
    double i = analogReadMilliVolts(PIN_CURRENT);
    sv += v; svv += v * v; si += i; sii += i * i; n++;
  }
  if (n == 0) { vRmsMv = iRmsMv = 0; return; }
  double mv = sv / n, mi = si / n;
  double varV = svv / n - mv * mv, varI = sii / n - mi * mi;
  vRmsMv = varV > 0 ? sqrt(varV) : 0;
  iRmsMv = varI > 0 ? sqrt(varI) : 0;
}

// ------------------------------------------------------------------- display
void showLcd(float v, float i, float p, double wh) {
  char l1[17], l2[17], e[10];
  if (wh < 1000.0) snprintf(e, sizeof e, "%.2fWh", wh); else snprintf(e, sizeof e, "%.3fkWh", wh / 1000.0);
  snprintf(l1, sizeof l1, "V:%.1f I:%.3f", v, i);
  snprintf(l2, sizeof l2, "P:%.2f E:%s", p, e);
  lcd.setCursor(0, 0); lcd.print(l1); for (int k = strlen(l1); k < 16; k++) lcd.print(' ');
  lcd.setCursor(0, 1); lcd.print(l2); for (int k = strlen(l2); k < 16; k++) lcd.print(' ');
}

// -------------------------------------------------------- serial calibration
// cv <volts>   calibrate voltage against a multimeter reading
// ci <amps>    calibrate current against a load of known current
// zero         record the zero-load noise floor of the current channel (clamp OFF any load)
// reset        zero the energy counter
// show         print the stored calibration
void handleSerial() {
  if (!Serial.available()) return;
  String line = Serial.readStringUntil('\n'); line.trim();
  if (line.startsWith("cv ") && lastVmv > 0) {
    voltsPerMv = line.substring(3).toFloat() / lastVmv; prefs.putFloat("vscale", voltsPerMv);
    Serial.printf("voltage scale = %.5f V/mV (saved)\n", voltsPerMv);
  } else if (line.startsWith("ci ")) {
    float eff = sqrtf(fmaxf(lastImv * lastImv - currentFloorMv * currentFloorMv, 0));
    if (eff > 0) { ampsPerMv = line.substring(3).toFloat() / eff; prefs.putFloat("iscale", ampsPerMv);
      Serial.printf("current scale = %.6f A/mV (saved)\n", ampsPerMv); }
  } else if (line == "zero") {
    currentFloorMv = lastImv; prefs.putFloat("ifloor", currentFloorMv);
    Serial.printf("current noise floor = %.3f mV (saved)\n", currentFloorMv);
  } else if (line == "reset") {
    energyWh = 0; prefs.putDouble("energyWh", 0); Serial.println("energy reset");
  } else if (line == "show") {
    Serial.printf("vscale=%.5f V/mV  iscale=%.6f A/mV  ifloor=%.3f mV  energy=%.4f Wh\n",
                  voltsPerMv, ampsPerMv, currentFloorMv, energyWh);
  } else {
    Serial.println("commands: cv <V> | ci <A> | zero | reset | show");
  }
}

// --------------------------------------------------------------------- setup
void setup() {
  Serial.begin(115200);
  analogReadResolution(12);
  analogSetPinAttenuation(PIN_VOLTAGE, ADC_11db);
  analogSetPinAttenuation(PIN_CURRENT, ADC_11db);

  prefs.begin("meter", false);
  voltsPerMv     = prefs.getFloat("vscale", DEFAULT_VOLTS_PER_MV);
  ampsPerMv      = prefs.getFloat("iscale", DEFAULT_AMPS_PER_MV);
  currentFloorMv = prefs.getFloat("ifloor", DEFAULT_CURRENT_NOISE_FLOOR_MV);
  energyWh       = prefs.getDouble("energyWh", 0.0);      // energy survives power cycles

  lcd.init(); lcd.backlight();
  lcd.setCursor(0, 0); lcd.print("IoT Energy Meter");
  lcd.setCursor(0, 1); lcd.print("Starting...");

  WiFi.mode(WIFI_STA);
  WiFi.begin(WIFI_SSID, WIFI_PASS);                      // non-blocking: metering starts regardless
  Blynk.config(BLYNK_AUTH_TOKEN);
  lastReport = millis();
}

// ---------------------------------------------------------------------- loop
void loop() {
  handleSerial();

  if (WiFi.status() == WL_CONNECTED) {
    if (!Blynk.connected() && millis() - lastBlynkTry > BLYNK_RETRY_MS) {
      lastBlynkTry = millis();
      Blynk.connect(3000);                               // bounded wait; never stalls metering for long
    }
    if (Blynk.connected()) Blynk.run();
  }

  uint32_t now = millis();
  if (now - lastReport < REPORT_INTERVAL_MS) return;
  float dtS = (now - lastReport) / 1000.0f;              // real elapsed time, not an assumed period
  lastReport = now;

  sampleWindow(lastVmv, lastImv);
  float vRms = lastVmv * voltsPerMv;
  float iEff = sqrtf(fmaxf(lastImv * lastImv - currentFloorMv * currentFloorMv, 0));
  float iRms = iEff * ampsPerMv;
  float power = vRms * iRms * ASSUMED_POWER_FACTOR;      // W (apparent power when PF is assumed to be 1)

  energyWh += (double)power * dtS / 3600.0;
  if (now - lastSave > ENERGY_SAVE_MS) { prefs.putDouble("energyWh", energyWh); lastSave = now; }

  showLcd(vRms, iRms, power, energyWh);

  if (Blynk.connected()) {
    Blynk.virtualWrite(V1, vRms);                        // Voltage gauge
    Blynk.virtualWrite(V2, iRms);                        // Current
    Blynk.virtualWrite(V3, power);                       // Power gauge
    Blynk.virtualWrite(V4, energyWh / 1000.0);           // Energy in kWh
  }
  Serial.printf("V=%.1f V  I=%.3f A  P=%.2f W  E=%.3f Wh  wifi=%d blynk=%d\n",
                vRms, iRms, power, energyWh, WiFi.status() == WL_CONNECTED, Blynk.connected());
}
