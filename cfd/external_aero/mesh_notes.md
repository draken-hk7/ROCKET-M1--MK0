# External Aero Mesh Notes

This OpenFOAM case is for incompressible, subsonic external aerodynamics around
the non-propellant ROCKET M1-MK0 airframe.

- Solver: `simpleFoam`
- Reference velocity: 85 m/s
- Reynolds number: approximately 2.4e6 to 4.4e6 depending on reference length
- Geometry inputs: use `cad/exports/ROCKET_M1_MK0_assembly.stl`,
  `cad/exports/fin.stl`, and `cad/exports/nose_cone.stl`
- Use `surfaceFeatureExtract` before snappyHexMesh.
- Recommended snappyHexMesh refinement:
  - nose cone: 2 levels
  - fin leading edges: 3 levels
  - fin trailing edges: 2 levels
  - wake region: 2 levels downstream to 6 body diameters
- Voronoi fin cutouts increase edge complexity. Use `featureEdgeMesh` and
  inspect non-orthogonality before solving.

No combustion, internal nozzle flow, or pressure-vessel physics are modeled.
