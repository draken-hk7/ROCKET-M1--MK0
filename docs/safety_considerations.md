# Safety Considerations

ROCKET M1-MK0 is a simulation-first, non-propellant educational airframe.

## Regulatory

- Consult DGCA India model aircraft/model rocketry guidance before any outdoor
  operation.
- If telemetry transmitters are used, comply with local radio-frequency rules.
- Obtain site permission for any outdoor testing, even without propulsion.
- This repository does not authorize launch, propulsion, or energetic recovery.

## Mechanical

- Fiberglass and G10 dust require eye protection, gloves, respiratory PPE, and
  wet-sanding or dust extraction.
- Fin edges can be sharp after cutting; deburr and radius all exposed edges.
- Use conservative handling loads around suspended airframes and test stands.

## Electrical

- Use protected cells, proper chargers, fuses where practical, and insulated
  battery retention.
- Keep the arm switch off during bench wiring.
- GPIO simulation flags must not be connected to pyrotechnic, ignition, or
  energetic deployment hardware.

## Recovery

- Treat shock cords and parachute lines as snap-back hazards during bench tests.
- Keep personnel clear of spring-loaded or compressed packing demonstrations.

## Simulation Disclaimer

All FEA, CFD, CAD, telemetry, and stability outputs are educational estimates.
They are not certification, flight qualification, or fabrication release data.
