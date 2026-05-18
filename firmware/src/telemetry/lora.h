#pragma once

#include <Arduino.h>

struct TelemetryPacket {
  uint8_t packet_id;
  uint8_t flight_state;
  uint16_t altitude_dm;
  int16_t velocity_cms;
  int16_t accel_z_cms2;
  int16_t temp_dc;
  float latitude;
  float longitude;
  uint16_t battery_mv;
  uint32_t timestamp_ms;
  uint32_t loop_count;
  uint16_t checksum_crc16;
  uint16_t reserved;
};

uint16_t crc16_ccitt(const uint8_t* data, size_t length);

class LoraTelemetry {
 public:
  bool begin();
  void transmit(const TelemetryPacket& packet);
};
