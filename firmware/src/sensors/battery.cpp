#include "battery.h"

#include "../config/pins.h"

void Battery::begin() {
  pinMode(BATTERY_ADC, INPUT);
}

float Battery::read_voltage_v() {
  const int raw = analogRead(BATTERY_ADC);
  const float adc_v = (static_cast<float>(raw) / 4095.0f) * 3.3f;
  return adc_v * 2.0f;
}

float Battery::read_percent() {
  const float voltage_v = read_voltage_v();
  const float pct = (voltage_v - 6.0f) / (8.4f - 6.0f) * 100.0f;
  return constrain(pct, 0.0f, 100.0f);
}
