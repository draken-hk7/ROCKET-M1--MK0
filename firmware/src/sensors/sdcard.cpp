#include "sdcard.h"

#include <SD.h>
#include <SPI.h>

#include "../config/pins.h"

bool SdLogger::begin() {
  return SD.begin(SD_CS);
}

void SdLogger::log_csv_header() {
  File file = SD.open("/flight.csv", FILE_APPEND);
  if (file) {
    file.println("timestamp_ms,state,altitude_m,accel_z_ms2,gps_alt_m");
    file.close();
  }
}

void SdLogger::log_row(const uint32_t timestamp_ms, const uint8_t state, const float altitude_m, const float accel_z_ms2, const float gps_alt_m) {
  File file = SD.open("/flight.csv", FILE_APPEND);
  if (file) {
    file.printf("%lu,%u,%.2f,%.3f,%.2f\n", static_cast<unsigned long>(timestamp_ms), state, altitude_m, accel_z_ms2, gps_alt_m);
    file.close();
  }
}
