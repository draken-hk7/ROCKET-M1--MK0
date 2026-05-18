# Non-Propellant Educational Test Plan

## Purpose

Demonstrate documentation, sensor logging, and software workflow validation
without propellants, pressure combustion, ignition, or hot-fire operations.

## Permitted Demonstrations

- inspect generated CSV, SVG, STL, and PDF artifacts
- run Python scripts in CI
- log room-temperature bench sensor data with the DAQ sketch
- review safety gates that block operational calculations

## Prohibited Uses

- propellant preparation or loading
- injector flow characterization for a rocket engine
- pressure testing of fabricated metal parts
- ignition or pyrotechnic devices
- hot-fire operations
- launch operations

## Acceptance Criteria

- all scripts complete without uncaught exceptions
- generated artifacts include non-operational safety notices
- CAD exports are display-only solids or manifests
- no document contains operational firing sequence data
