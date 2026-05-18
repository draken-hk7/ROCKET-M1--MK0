#include "gps.h"

#include "../config/pins.h"

bool Gps::begin() {
  Serial2.begin(9600, SERIAL_8N1, GPS_RX, GPS_TX);
  return true;
}

void Gps::poll() {
  while (Serial2.available() > 0) {
    (void)Serial2.read();
  }
}

float Gps::read_lat() { return 0.0f; }
float Gps::read_lon() { return 0.0f; }
float Gps::read_alt_m() { return 0.0f; }
uint8_t Gps::read_fix_quality() { return 0; }
