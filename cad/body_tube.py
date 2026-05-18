"""Parametric airframe body tube CAD generator."""

from __future__ import annotations

import math
import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from cad.display_geometry import EXPORT_DIR, print_summary, write_revolved_profile_stl, write_step_manifest
from config import vehicle_params as vp


def body_profile_mm() -> list[tuple[float, float]]:
    """Generate an exterior body tube profile."""

    radius = vp.BODY_DIAMETER_MM / 2.0
    return [(0.0, radius), (vp.BODY_LENGTH_MM, radius)]


def run() -> dict[str, Path]:
    """Generate body tube STEP and STL files."""

    profile = body_profile_mm()
    stl_path = EXPORT_DIR / "body_tube.stl"
    step_path = EXPORT_DIR / "body_tube.step"
    write_revolved_profile_stl(stl_path, "body_tube_shell_reference", profile, segments=72)
    volume_cm3 = math.pi * (
        (vp.BODY_DIAMETER_MM / 2.0) ** 2 - (vp.INNER_DIAMETER_MM / 2.0) ** 2
    ) * vp.BODY_LENGTH_MM / 1000.0
    write_step_manifest(
        step_path,
        "body_tube",
        (
            "Cylindrical shell educational CAD. GD&T notes: rail-button bosses at "
            f"{list(vp.RAIL_BUTTON_POSITIONS_MM)} mm from aft; three fin slots at 120 deg; "
            "forward coupler socket and aft fin-can socket use non-pressure clearance references."
        ),
    )
    print_summary("body_tube", volume_cm3, (vp.BODY_LENGTH_MM, vp.BODY_DIAMETER_MM, vp.BODY_DIAMETER_MM), step_path)
    print(f"Saved: {step_path}")
    print(f"Saved: {stl_path}")
    return {"step": step_path, "stl": stl_path}


if __name__ == "__main__":
    run()
