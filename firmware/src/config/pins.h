#pragma once

// ROCKET M1-MK0 ESP32 pin mapping.
// All recovery outputs are simulation flags only, not energetic outputs.

static constexpr int GPS_RX = 16;
static constexpr int GPS_TX = 17;
static constexpr int SPI_SCK = 14;
static constexpr int SPI_MISO = 12;
static constexpr int SPI_MOSI = 13;
static constexpr int LORA_CS = 18;
static constexpr int LORA_RST = 19;
static constexpr int LORA_IRQ = 26;
static constexpr int SD_CS = 5;
static constexpr int IMU_CS = 15;
static constexpr int BARO_SDA = 21;
static constexpr int BARO_SCL = 22;
static constexpr int BATTERY_ADC = 34;
static constexpr int STATUS_LED = 2;
static constexpr int ARM_SWITCH = 35;

static constexpr int DROGUE_SIM_FLAG = 32;
static constexpr int MAIN_SIM_FLAG = 33;
