# ROCKET M1-MK0 Engineering Specification

## 1. Purpose & Scope

ROCKET M1-MK0 is a simulation-first, non-propellant educational aerospace
research airframe. It integrates biomimetic geometry, structural estimates,
external aerodynamics, avionics, telemetry, and CAD automation.

## 2. Vehicle Description

```text
 nose tip                         avionics      recovery          fin can
   /\                               bay           bay               fins
  /  \____ cylindrical airframe ____[===]_________[===]___________/|\
  \  /                                                     3 fins at 120 deg
   \/
```

## 3. Performance Requirements

| Parameter | Value |
|---|---:|
| Body diameter | 76 mm |
| Body length | 1200 mm |
| Target altitude for simulation | 300 m |
| Coast velocity initial condition | 85 m/s |
| Minimum static margin | 1.0 caliber |
| Preferred static margin range | 1.0 to 5.0 calibers |

## 4. Mass Budget

| Component | Mass |
|---|---:|
| Airframe | 320 g |
| Avionics | 180 g |
| Nose cone | 95 g |
| Recovery | 210 g |
| Payload | 150 g |
| Total | 955 g |

## 5. Stability Analysis Summary

`simulation/aerodynamics.py` computes Barrowman-style CP, CM, static margin,
drag coefficient, coast trajectory, and OpenRocket XML export.

## 6. Structural Analysis Summary

`simulation/structural_analysis.py` estimates fin-root bending stress, body
tube hoop stress from a benign recovery-volume simulation parameter, landing
impact load, and first bending frequency.

## 7. Fibonacci Design Rationale

- Fin sweep angle: 21 degrees multiplied by phi gives 33.98 degrees.
- Fin span: 89 mm, a Fibonacci number, gives span/root near the golden ratio.
- Phyllotaxis parachute vents: 13 vents follow the golden angle.
- Voronoi lattice fins: nature-like cellular cutouts reduce educational model
  mass while retaining stiffness in screening calculations.
- Phi-weighted sensor fusion: firmware filter uses `new/phi^2 + history/phi`.
- Golden ratio dashboard: ground station uses 61.8/38.2 layout columns.
- Avionics bay: 144 mm length follows Fibonacci F(12).

## 8. Coordinate Reference Frame

The x-axis runs from nose tip toward aft. The y-axis is lateral, and the z-axis
is vertical in CAD sections. CP and CM stations are measured from the nose tip.

## 9. Interface Control Document

| Interface | Control |
|---|---|
| Nose shoulder to body tube | 0.2 mm educational clearance reference |
| Avionics bay to body tube | coupler OD below body ID by clearance reference |
| Fin root to body tube | three 120 degree slots, tab alignment controlled |
| Rail buttons | Fibonacci aft stations 21, 34, 55, 89 mm |
| Electronics | ESP32-centered wiring, SPI/I2C/UART separation |

## 10. Revision History

| Revision | Date | Description |
|---|---|---|
| A | 2026-05-18 | Complete simulation-first biomimetic airframe baseline |
