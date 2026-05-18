# ROCKET M1- MK0 Educational Design Report

## Scope

ROCKET M1- MK0 is a non-operational educational repository for propulsion
software workflow practice. It demonstrates how a professional project might
organize analysis, CAD automation, FEA/CFD templates, documentation, CI, and
generated artifacts.

It is not a buildable rocket engine package. Fabrication-critical calculations
and test procedures are intentionally omitted.

## Configuration

- Engine class: educational display and simulation proxy
- Propulsion modes discussed: liquid bipropellant proxy and solid burnback
  teaching curve
- Geometry mode: normalized contours and solid display envelopes
- CAD mode: display model only, no pressure cavity or fluid passages
- Unit system: SI in code and generated data

## Thermodynamic Analysis

`propulsion/cea_analysis.py` generates dimensionless performance indices for
software validation and plotting. The model is a smooth proxy and is not NASA
CEA, Cantera, RocketPy, or any real chemical equilibrium calculation.

Omitted by design:

- species mole fractions
- chamber temperature in kelvin
- dimensional specific impulse
- mass flow
- injector pressure drop
- throat area

## Nozzle Geometry

`propulsion/nozzle_design.py` generates a normalized bell-like contour as
`x_over_rt` and `radius_over_rt`. This is useful for documentation and CAD
automation practice. It does not include absolute throat diameter, exit
diameter, contour tolerances, or a method-of-characteristics net.

## Chamber and Injector

`propulsion/chamber_sizing.py` creates a display envelope summary and blocks
pressure-vessel calculations. `propulsion/injector_design.py` creates a
decorative face pattern and blocks orifice sizing.

## CAD

The `cad/` scripts generate display artifacts:

- solid exterior chamber silhouette
- solid exterior nozzle silhouette
- decorative injector face
- cooling-jacket illustration
- full display assembly

These files are not manufacturing releases and must not be used for pressure
hardware.

## FEA and CFD

The FEA deck and OpenFOAM case are templates for file-structure practice. They
do not contain validated material models, loads, boundary conditions, thermal
profiles, mesh convergence, turbulence validation, or acceptance criteria.

## Manufacturing

The BOM and drawings are for display models only. Critical notes such as
surface finish, pressure-rated tolerances, weld preparations, and thread
specifications are intentionally not provided for operational parts.

## Test and Instrumentation

The test directory provides a non-propellant educational test plan and a generic
DAQ sketch. Hot-fire, ignition, propellant handling, and valve sequencing are
outside this repository.
