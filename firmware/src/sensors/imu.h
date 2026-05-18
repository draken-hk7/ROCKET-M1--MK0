#pragma once

#include <Arduino.h>

struct Vector3 {
  float x;
  float y;
  float z;
};

class Imu {
 public:
  bool begin();
  Vector3 read_accel_ms2();
  Vector3 read_gyro_rads();
  bool detect_launch(float accel_z_ms2, uint32_t now_ms);

 private:
  uint32_t boost_start_ms_ = 0;
};
