#include "lora.h"

#include <LoRa.h>
#include <SPI.h>

#include "../config/pins.h"

uint16_t crc16_ccitt(const uint8_t* data, const size_t length) {
  uint16_t crc = 0xFFFF;
  for (size_t i = 0; i < length; ++i) {
    crc ^= static_cast<uint16_t>(data[i]) << 8;
    for (uint8_t bit = 0; bit < 8; ++bit) {
      if ((crc & 0x8000) != 0) {
        crc = static_cast<uint16_t>((crc << 1) ^ 0x1021);
      } else {
        crc = static_cast<uint16_t>(crc << 1);
      }
    }
  }
  return crc;
}

bool LoraTelemetry::begin() {
  LoRa.setPins(LORA_CS, LORA_RST, LORA_IRQ);
  return LoRa.begin(433E6);
}

void LoraTelemetry::transmit(const TelemetryPacket& packet) {
  LoRa.beginPacket();
  LoRa.write(reinterpret_cast<const uint8_t*>(&packet), sizeof(TelemetryPacket));
  LoRa.endPacket();
}
