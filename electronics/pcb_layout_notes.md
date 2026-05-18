# PCB Layout Notes

- Use a continuous ground plane on the bottom layer.
- Place BMP390 away from heat sources and board edges; provide a static port
  path in the avionics bay.
- Place ICM-42688 close to the vehicle centerline to reduce rotational
  acceleration coupling.
- Follow a Fibonacci spiral placement order for signal-critical modules:
  IMU near the origin, barometer at the next spiral point, SD card next, then
  LoRa and GPS interface.
- Keep LoRa antenna feed clear of copper and batteries by at least 15 mm.
- Decouple every module with 100 nF local ceramic capacitors plus one 10 uF
  bulk capacitor per rail segment.
- Route SPI as short, length-similar traces; avoid crossing the antenna keepout.
- Put the arm switch on a board edge and use a pull-down so the default state
  is unarmed.
- GPIO32/GPIO33 simulation flags must not connect to energetic hardware.
