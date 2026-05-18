"""Ogive tip cap CAD generator with Fibonacci spiral groove reference."""

from __future__ import annotations

import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from cad.display_geometry import EXPORT_DIR, bbox_from_profile_mm, print_summary, profile_volume_cm3, write_revolved_profile_stl, write_step_manifest
from cad.nose_cone import von_karman_radius_mm
from utils.nature_geometry import fibonacci_spiral_points


def tip_profile_mm() -> list[tuple[float, float]]:
    """Return the first 20 mm of the ogive profile."""

    return [(index, von_karman_radius_mm(index)) for index in [i * 20.0 / 24.0 for i in range(25)]]


def run() -> dict[str, Path]:
    """Generate nose tip STEP and STL files."""

    profile = tip_profile_mm()
    stl_path = EXPORT_DIR / "nose_tip.stl"
    step_path = EXPORT_DIR / "nose_tip.step"
    write_revolved_profile_stl(stl_path, "nose_tip_spiral_reference", profile, segments=48)
    groove = fibonacci_spiral_points(21, 0.6)
    write_step_manifest(
        step_path,
        "nose_tip",
        f"20 mm ogive tip cap with Fibonacci spiral groove reference; groove points={len(groove)}.",
    )
    print_summary("nose_tip", profile_volume_cm3(profile), bbox_from_profile_mm(profile), step_path)
    print(f"Saved: {step_path}")
    print(f"Saved: {stl_path}")
    return {"step": step_path, "stl": stl_path}


if __name__ == "__main__":
    run()
