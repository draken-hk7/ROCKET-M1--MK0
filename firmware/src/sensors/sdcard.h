#pragma once

#include <Arduino.h>

class SdLogger {
 public:
  bool begin();
  void log_csv_header();
  void log_row(uint32_t timestamp_ms, uint8_t state, float altitude_m, float accel_z_ms2, float gps_alt_m);
};
