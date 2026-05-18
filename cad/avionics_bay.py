"""Avionics bay CAD generator with Fibonacci bay length."""

from __future__ import annotations

import math
import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from cad.display_geometry import EXPORT_DIR, print_summary, write_revolved_profile_stl, write_step_manifest
from config import vehicle_params as vp
from utils.nature_geometry import hexagonal_tessellation


def avionics_profile_mm() -> list[tuple[float, float]]:
    """Return avionics coupler exterior profile."""

    radius = vp.INNER_DIAMETER_MM / 2.0 - vp.CLEARANCE_FIT_MM / 2.0
    return [(0.0, radius), (vp.AVIONICS_BAY_LENGTH_MM, radius)]


def run() -> dict[str, Path]:
    """Generate avionics bay STEP and STL files."""

    profile = avionics_profile_mm()
    stl_path = EXPORT_DIR / "avionics_bay.stl"
    step_path = EXPORT_DIR / "avionics_bay.step"
    write_revolved_profile_stl(stl_path, "avionics_bay_coupler", profile, segments=64)
    radius = profile[0][1]
    volume_cm3 = math.pi * radius**2 * vp.AVIONICS_BAY_LENGTH_MM / 1000.0
    hole_centers = hexagonal_tessellation(4, 6, 5.0)
    write_step_manifest(
        step_path,
        "avionics_bay",
        (
            "144 mm Fibonacci avionics bay. Includes sled layout for two 18650 bays, ESP32, "
            "LoRa antenna routing, four M3 standoffs, and fore/aft bulkhead eyebolt references. "
            f"Hexagonal lightening-hole centers={len(hole_centers)}."
        ),
    )
    print_summary("avionics_bay", volume_cm3, (vp.AVIONICS_BAY_LENGTH_MM, 2 * radius, 2 * radius), step_path)
    print(f"Saved: {step_path}")
    print(f"Saved: {stl_path}")
    return {"step": step_path, "stl": stl_path}


if __name__ == "__main__":
    run()
