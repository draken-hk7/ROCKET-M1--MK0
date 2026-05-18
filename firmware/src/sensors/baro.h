#pragma once

#include <Arduino.h>

class Barometer {
 public:
  bool begin();
  float read_pressure_pa();
  float read_altitude_m();
  float read_temp_c();

 private:
  float baseline_pressure_pa_ = 101325.0f;
};
