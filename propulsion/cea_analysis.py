"""Legacy compatibility entrypoint for non-propellant aero analysis.

The project no longer performs combustion or propellant chemistry calculations.
Run `simulation/aerodynamics.py` for the current airframe analysis.
"""

from __future__ import annotations

from simulation.aerodynamics import run


if __name__ == "__main__":
    run()
