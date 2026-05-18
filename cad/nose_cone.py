"""Parametric von Karman nose cone CAD generator."""

from __future__ import annotations

import math
import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from cad.display_geometry import (
    EXPORT_DIR,
    bbox_from_profile_mm,
    print_summary,
    profile_volume_cm3,
    write_revolved_profile_stl,
    write_step_manifest,
)
from config import vehicle_params as vp
from utils.nature_geometry import hexagonal_tessellation, logarithmic_spiral


def von_karman_radius_mm(x_mm: float) -> float:
    """Compute von Karman ogive radius at station x.

    Args:
        x_mm: Nose station from tip in millimeters.

    Returns:
        Radius in millimeters.

    Units:
        Millimeters.

    Aerospace Application:
        Low-drag transonic nose profile for simulation CAD.
    """

    if x_mm < 0.0 or x_mm > vp.NOSE_CONE_LENGTH_MM:
        raise ValueError("x_mm must lie inside the nose cone length.")
    theta = math.acos(1.0 - 2.0 * x_mm / vp.NOSE_CONE_LENGTH_MM)
    radius = (vp.BODY_DIAMETER_MM / 2.0) * math.sqrt((theta - 0.5 * math.sin(2.0 * theta)) / math.pi)
    return radius


def nose_profile_mm(samples: int = 96) -> list[tuple[float, float]]:
    """Generate the exterior nose cone revolved profile."""

    if samples < 16:
        raise ValueError("samples must be at least 16 for nose profile generation.")
    profile = []
    for index in range(samples):
        x_mm = vp.NOSE_CONE_LENGTH_MM * index / (samples - 1)
        profile.append((x_mm, von_karman_radius_mm(x_mm)))
    shoulder_radius = vp.BODY_DIAMETER_MM / 2.0 - vp.CLEARANCE_FIT_MM / 2.0
    profile.extend(
        [
            (vp.NOSE_CONE_LENGTH_MM + 18.0, shoulder_radius),
            (vp.NOSE_CONE_LENGTH_MM + 38.0, shoulder_radius),
        ]
    )
    return profile


def run() -> dict[str, Path]:
    """Generate nose cone STEP and STL files."""

    profile = nose_profile_mm()
    stl_path = EXPORT_DIR / "nose_cone.stl"
    step_path = EXPORT_DIR / "nose_cone.step"
    write_revolved_profile_stl(stl_path, "nose_cone_von_karman", profile)
    ribs = logarithmic_spiral(2.0, 0.08, [i * 0.2 for i in range(48)])
    bulkhead_holes = hexagonal_tessellation(4, 5, 4.0)
    write_step_manifest(
        step_path,
        "nose_cone",
        (
            "Von Karman ogive educational CAD. GD&T notes: shoulder OD uses +0.2 mm "
            "clearance fit to body ID; tip and shoulder are reference datums only. "
            f"Internal rib sketch points={len(ribs)}, honeycomb bulkhead centers={len(bulkhead_holes)}."
        ),
    )
    print_summary("nose_cone", profile_volume_cm3(profile), bbox_from_profile_mm(profile), step_path)
    print(f"Saved: {step_path}")
    print(f"Saved: {stl_path}")
    return {"step": step_path, "stl": stl_path}


if __name__ == "__main__":
    run()
