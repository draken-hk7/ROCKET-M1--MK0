#pragma once

#include <Arduino.h>

class Battery {
 public:
  void begin();
  float read_voltage_v();
  float read_percent();
};
