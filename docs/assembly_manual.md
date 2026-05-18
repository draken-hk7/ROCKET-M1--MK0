# ROCKET M1-MK0 Assembly Manual

This manual covers a non-propellant educational airframe and electronics
package. It does not include motor installation, launch operations, energetic
deployment, or hot-fire content.

## 1. Fin Attachment

1. Dry-fit all three fins into the body-tube slots.
2. Use a 120 degree alignment jig to verify equal spacing.
3. Lightly scuff bonding surfaces and remove dust with isopropyl alcohol.
4. Apply structural epoxy to the fin root tab and slot wall.
5. Hold alignment until the epoxy reaches handling strength.
6. Add small external fillets after the root bond cures.

Recommended fastener torque for M3 electronics screws: 0.4 N m maximum.

## 2. Electronics Installation

1. Wear ESD protection before handling ESP32, IMU, GPS, LoRa, or SD hardware.
2. Seat the ESP32 on four M3 standoffs.
3. Route SPI wiring away from the LoRa antenna keepout.
4. Secure batteries in the sled with insulated retention straps.
5. Confirm the arm switch defaults to unarmed.
6. Verify GPIO32/GPIO33 are simulation flags only.

## 3. Recovery Rigging

1. Attach the shock cord to fore and aft bulkhead eyebolts.
2. Route the cord without sharp bends or fiberglass contact points.
3. Pack the parachute loosely for bench-fit checks only.
4. Verify the vent pattern is unobstructed.

## 4. Pre-Flight Checklist

For this repository, use the checklist as a simulation and bench-readiness list:

1. CAD exports regenerated.
2. Aerodynamic and structural scripts complete.
3. Firmware builds in PlatformIO.
4. Battery voltage is within electronics limits.
5. SD card logs sample rows.
6. LoRa packets decode with valid CRC.
7. No energetic devices are connected.

## 5. Post-Run Inspection

1. Inspect fin roots for cracks.
2. Inspect the avionics sled for loose fasteners.
3. Export telemetry logs and confirm CRC validity.
4. Record any configuration changes in the revision history.
