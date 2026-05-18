# ROCKET M1-MK0 Text Schematic

All outputs are for sensing, logging, and simulation flags only. No energetic
deployment circuits are present.

| SIGNAL | FROM_PIN | TO_PIN | WIRE_COLOR | NOTES |
|---|---:|---:|---|---|
| 3V3 | ESP32 3V3 | BMP390 VIN, ICM-42688 VIN, RFM96W VIN, SD VIN | red | regulated 3.3 V rail |
| GND | ESP32 GND | all module grounds | black | star return to avionics sled ground node |
| I2C_SDA | GPIO21 | BMP390 SDA | blue | 4.7 k pull-up to 3.3 V |
| I2C_SCL | GPIO22 | BMP390 SCL | blue | 4.7 k pull-up to 3.3 V |
| SPI_SCK | GPIO14 | IMU SCK, LoRa SCK, SD SCK | yellow | shared SPI clock |
| SPI_MISO | GPIO12 | IMU MISO, LoRa MISO, SD MISO | yellow | shared SPI MISO |
| SPI_MOSI | GPIO13 | IMU MOSI, LoRa MOSI, SD MOSI | yellow | shared SPI MOSI |
| IMU_CS | GPIO15 | ICM-42688 CS | yellow | active low |
| LORA_CS | GPIO18 | RFM96W NSS | yellow | active low |
| LORA_RST | GPIO19 | RFM96W RESET | gray | reset line |
| LORA_IRQ | GPIO26 | RFM96W DIO0 | violet | packet interrupt |
| SD_CS | GPIO5 | SD card CS | yellow | active low |
| GPS_RX | GPIO16 | GPS TX | green | UART2 9600 baud |
| GPS_TX | GPIO17 | GPS RX | green | UART2 9600 baud |
| BATTERY_ADC | GPIO34 | voltage divider midpoint | orange | high impedance ADC input |
| ARM_SWITCH | GPIO35 | arm switch output | white | simulation arming input |
| STATUS_LED | GPIO2 | LED anode through 330R | purple | status indication |
