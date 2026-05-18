"""Legacy compatibility entrypoint for non-propellant performance plots."""

from __future__ import annotations

from simulation.aerodynamics import run as run_aero
from simulation.fibonacci_aero_analysis import run as run_fibonacci
from simulation.voronoi_fin_optimization import run as run_voronoi


def run() -> None:
    """Generate current airframe performance plots."""

    run_aero()
    run_fibonacci()
    run_voronoi()


if __name__ == "__main__":
    run()
