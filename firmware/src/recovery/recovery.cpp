#include "recovery.h"

#include "../config/pins.h"

bool RecoveryLogic::update_apogee(const float altitude_m) {
  const float delta_m = altitude_m - previous_altitude_m_;
  previous_altitude_m_ = altitude_m;
  if (delta_m < -0.5f) {
    descent_count_++;
  } else {
    descent_count_ = 0;
  }
  return descent_count_ >= 3;
}

bool RecoveryLogic::drogue_event(const uint32_t timestamp_ms) {
  if (drogue_sent_) {
    return false;
  }
  drogue_sent_ = true;
  digitalWrite(DROGUE_SIM_FLAG, HIGH);  // Simulation flag only. No pyro output.
  Serial.printf("DROGUE_DEPLOY_SIM,%lu\n", static_cast<unsigned long>(timestamp_ms));
  return true;
}

bool RecoveryLogic::main_event(const float altitude_agl_m, const uint32_t timestamp_ms) {
  if (main_sent_ || altitude_agl_m >= 150.0f) {
    return false;
  }
  main_sent_ = true;
  digitalWrite(MAIN_SIM_FLAG, HIGH);  // Simulation flag only. No pyro output.
  Serial.printf("MAIN_DEPLOY_SIM,%lu\n", static_cast<unsigned long>(timestamp_ms));
  return true;
}
