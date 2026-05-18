#include "baro.h"

#include <Wire.h>

#include "../config/pins.h"

bool Barometer::begin() {
  Wire.begin(BARO_SDA, BARO_SCL);
  baseline_pressure_pa_ = 101325.0f;
  return true;
}

float Barometer::read_pressure_pa() {
  // Placeholder hardware abstraction: replace with BMP390 library call on target.
  return baseline_pressure_pa_;
}

float Barometer::read_altitude_m() {
  const float pressure_pa = read_pressure_pa();
  return 44330.0f * (1.0f - powf(pressure_pa / baseline_pressure_pa_, 0.1903f));
}

float Barometer::read_temp_c() {
  return 25.0f;
}
