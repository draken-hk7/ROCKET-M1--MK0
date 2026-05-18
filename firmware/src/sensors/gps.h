#pragma once

#include <Arduino.h>

class Gps {
 public:
  bool begin();
  void poll();
  float read_lat();
  float read_lon();
  float read_alt_m();
  uint8_t read_fix_quality();
};
