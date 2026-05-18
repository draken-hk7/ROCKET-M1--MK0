#include "imu.h"

#include <SPI.h>

#include "../config/pins.h"

bool Imu::begin() {
  pinMode(IMU_CS, OUTPUT);
  digitalWrite(IMU_CS, HIGH);
  return true;
}

Vector3 Imu::read_accel_ms2() {
  return {0.0f, 0.0f, 9.80665f};
}

Vector3 Imu::read_gyro_rads() {
  return {0.0f, 0.0f, 0.0f};
}

bool Imu::detect_launch(const float accel_z_ms2, const uint32_t now_ms) {
  const float threshold_ms2 = 2.5f * 9.80665f;
  if (accel_z_ms2 > threshold_ms2) {
    if (boost_start_ms_ == 0) {
      boost_start_ms_ = now_ms;
    }
    return (now_ms - boost_start_ms_) > 150;
  }
  boost_start_ms_ = 0;
  return false;
}
