#include <Arduino.h>
#include <esp_task_wdt.h>

#include "config/pins.h"
#include "recovery/recovery.h"
#include "sensors/baro.h"
#include "sensors/battery.h"
#include "sensors/gps.h"
#include "sensors/imu.h"
#include "sensors/sdcard.h"
#include "telemetry/lora.h"

enum FlightState : uint8_t {
  IDLE = 0,
  ARMED = 1,
  BOOST_DETECT = 2,
  COAST = 3,
  APOGEE_DETECT = 4,
  DROGUE_DEPLOY = 5,
  MAIN_DEPLOY = 6,
  DESCENT = 7,
  LANDED = 8,
  SAFE = 9
};

static constexpr float PHI = 1.6180339887f;
static constexpr float PHI_SQ = PHI * PHI;

Barometer barometer;
Imu imu;
Gps gps;
SdLogger sd_logger;
Battery battery;
RecoveryLogic recovery;
LoraTelemetry radio;

FlightState state = IDLE;
uint32_t loop_count = 0;
float filtered_altitude_m = 0.0f;
float previous_altitude_m = 0.0f;
float velocity_ms = 0.0f;

float phi_filter(const float new_val, const float prev_val) {
  // Fibonacci complementary filter - phi-weighted sensor fusion.
  return (new_val / PHI_SQ) + (prev_val / PHI);
}

void update_led(const uint32_t now_ms) {
  if (state == IDLE) {
    digitalWrite(STATUS_LED, (now_ms / 500) % 2);
  } else if (state == ARMED) {
    digitalWrite(STATUS_LED, (now_ms / 100) % 2);
  } else if (state == SAFE) {
    const uint32_t phase = now_ms % 1000;
    digitalWrite(STATUS_LED, phase < 90 || (phase > 180 && phase < 270));
  } else {
    digitalWrite(STATUS_LED, HIGH);
  }
}

void transition_state(const FlightState next_state) {
  if (state != next_state) {
    state = next_state;
    Serial.printf("STATE,%u\n", static_cast<unsigned>(state));
  }
}

TelemetryPacket build_packet(const uint32_t now_ms, const Vector3 accel, const float temp_c) {
  TelemetryPacket packet{};
  packet.packet_id = 0x42;
  packet.flight_state = static_cast<uint8_t>(state);
  packet.altitude_dm = static_cast<uint16_t>(max(0.0f, filtered_altitude_m * 10.0f));
  packet.velocity_cms = static_cast<int16_t>(velocity_ms * 100.0f);
  packet.accel_z_cms2 = static_cast<int16_t>(accel.z * 100.0f);
  packet.temp_dc = static_cast<int16_t>(temp_c * 10.0f);
  packet.latitude = gps.read_lat();
  packet.longitude = gps.read_lon();
  packet.battery_mv = static_cast<uint16_t>(battery.read_voltage_v() * 1000.0f);
  packet.timestamp_ms = now_ms;
  packet.loop_count = loop_count;
  packet.reserved = 0;
  packet.checksum_crc16 = 0;
  packet.checksum_crc16 = crc16_ccitt(reinterpret_cast<uint8_t*>(&packet), 28);
  return packet;
}

void setup() {
  Serial.begin(115200);
  pinMode(STATUS_LED, OUTPUT);
  pinMode(ARM_SWITCH, INPUT);
  pinMode(DROGUE_SIM_FLAG, OUTPUT);
  pinMode(MAIN_SIM_FLAG, OUTPUT);
  digitalWrite(DROGUE_SIM_FLAG, LOW);
  digitalWrite(MAIN_SIM_FLAG, LOW);

  barometer.begin();
  imu.begin();
  gps.begin();
  battery.begin();
  sd_logger.begin();
  sd_logger.log_csv_header();
  radio.begin();

  esp_task_wdt_init(8, true);
  esp_task_wdt_add(nullptr);
  Serial.println("ROCKET_M1_MK0_FLIGHT_COMPUTER_READY");
}

void loop() {
  static uint32_t last_sensor_ms = 0;
  static uint32_t last_log_ms = 0;
  static uint32_t last_radio_ms = 0;
  const uint32_t now_ms = millis();
  esp_task_wdt_reset();
  update_led(now_ms);

  if (now_ms - last_sensor_ms >= 10) {
    last_sensor_ms = now_ms;
    gps.poll();
    const Vector3 accel = imu.read_accel_ms2();
    const float raw_altitude_m = barometer.read_altitude_m();
    filtered_altitude_m = phi_filter(raw_altitude_m, filtered_altitude_m);
    velocity_ms = (filtered_altitude_m - previous_altitude_m) / 0.01f;
    previous_altitude_m = filtered_altitude_m;

    if (state == IDLE && digitalRead(ARM_SWITCH) == HIGH) {
      transition_state(ARMED);
    }
    if (state == ARMED && imu.detect_launch(accel.z, now_ms)) {
      transition_state(BOOST_DETECT);
    }
    if (state == BOOST_DETECT && accel.z < 11.0f) {
      transition_state(COAST);
    }
    if ((state == COAST || state == BOOST_DETECT) && recovery.update_apogee(filtered_altitude_m)) {
      transition_state(APOGEE_DETECT);
      recovery.drogue_event(now_ms);
      transition_state(DROGUE_DEPLOY);
    }
    if ((state == DROGUE_DEPLOY || state == DESCENT) && recovery.main_event(filtered_altitude_m, now_ms)) {
      transition_state(MAIN_DEPLOY);
    }
    if (state == MAIN_DEPLOY && filtered_altitude_m < 3.0f && fabsf(velocity_ms) < 0.5f) {
      transition_state(LANDED);
    }
    if (state == LANDED && digitalRead(ARM_SWITCH) == LOW) {
      transition_state(SAFE);
    }
  }

  if (now_ms - last_log_ms >= 500) {
    last_log_ms = now_ms;
    const Vector3 accel = imu.read_accel_ms2();
    sd_logger.log_row(now_ms, static_cast<uint8_t>(state), filtered_altitude_m, accel.z, gps.read_alt_m());
  }

  const uint32_t radio_period_ms = (state == IDLE || state == SAFE) ? 5000 : 500;
  if (now_ms - last_radio_ms >= radio_period_ms) {
    last_radio_ms = now_ms;
    const Vector3 accel = imu.read_accel_ms2();
    const TelemetryPacket packet = build_packet(now_ms, accel, barometer.read_temp_c());
    radio.transmit(packet);
  }

  loop_count++;
}
