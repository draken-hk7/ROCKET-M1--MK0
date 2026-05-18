# ROCKET M1- MK0

Educational mini rocket engine design workspace with non-operational analysis,
normalized geometry, display-model CAD generation, safety documentation, and
GitHub Actions validation.

## Safety Boundary

This repository does not contain a buildable rocket engine design. It
intentionally omits or blocks fabrication-critical details such as propellant
processing, injector orifice sizing, wall thickness sizing, ignition timing,
pressure-rated manufacturing drawings, and hot-fire procedures.

Use this project for classroom-level propulsion math, documentation practice,
CAD automation demonstrations, and software workflow validation only.

## What Is Included

- Educational thermodynamic proxy calculations, not NASA CEA results.
- Normalized nozzle contour generation with no absolute throat area.
- Non-pressure display CAD scripts with graceful fallback when CadQuery is not
  installed.
- FEA and CFD template files that are not flight or test qualified.
- Manufacturing and BOM artifacts for display models only.
- Safety notes and regulatory orientation for lawful, supervised work.

## Quick Start

```powershell
python propulsion/cea_analysis.py
python propulsion/nozzle_design.py
python propulsion/chamber_sizing.py
python propulsion/injector_design.py
python propulsion/performance_plots.py
python cad/combustion_chamber.py
python cad/nozzle_assembly.py
python cad/injector_plate.py
python cad/cooling_jacket.py
python cad/engine_assembly.py
python fea/mesh_setup.py
python manufacturing/generate_bom.py
```

Outputs are written to `outputs/`, `cad/exports/`, `manufacturing/`, `fea/`,
and `docs/`.

## Repository Map

```text
ROCKET M1- MK0/
├── README.md
├── LICENSE
├── .github/workflows/ci.yml
├── docs/
├── propulsion/
├── cad/
├── fea/
├── cfd/nozzle_flow/
├── manufacturing/
└── test/
```

## Engineering Standards

- Python 3.11+
- SI units in code and generated data
- Typed functions with Google-style docstrings
- Explicit safety gates for operational calculations
- No ITAR-controlled, classified, or fabrication-enabling content

## License

MIT License. See `LICENSE`.
