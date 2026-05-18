#pragma once

#include <Arduino.h>

class RecoveryLogic {
 public:
  bool update_apogee(float altitude_m);
  bool drogue_event(uint32_t timestamp_ms);
  bool main_event(float altitude_agl_m, uint32_t timestamp_ms);

 private:
  float previous_altitude_m_ = 0.0f;
  uint8_t descent_count_ = 0;
  bool drogue_sent_ = false;
  bool main_sent_ = false;
};
