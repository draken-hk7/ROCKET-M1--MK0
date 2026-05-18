/*
  ROCKET M1- MK0 generic educational DAQ sketch.
  Logs eight analog channels at approximately 1 kHz for bench demonstrations.
  Not validated for hazardous testing, pyrotechnics, hot-fire, or flight use.
*/

const int kChannelCount = 8;
const int kAnalogPins[kChannelCount] = {A0, A1, A2, A3, A4, A5, A6, A7};
const unsigned long kSamplePeriodMicros = 1000;

unsigned long nextSampleMicros = 0;

void setup() {
  Serial.begin(115200);
  while (!Serial) {
    ; // Wait for USB serial on boards that need it.
  }
  Serial.println("time_us,ch0,ch1,ch2,ch3,ch4,ch5,ch6,ch7");
  nextSampleMicros = micros();
}

void loop() {
  const unsigned long nowMicros = micros();
  if ((long)(nowMicros - nextSampleMicros) < 0) {
    return;
  }

  nextSampleMicros += kSamplePeriodMicros;
  Serial.print(nowMicros);
  for (int channel = 0; channel < kChannelCount; channel++) {
    Serial.print(",");
    Serial.print(analogRead(kAnalogPins[channel]));
  }
  Serial.println();
}
