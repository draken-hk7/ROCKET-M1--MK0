"""Full ROCKET M1-MK0 airframe assembly exporter."""

from __future__ import annotations

import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from cad import avionics_bay, body_tube, fin_set, nose_cone, nose_cone_tip, parachute_bay
from cad.display_geometry import EXPORT_DIR, print_summary, write_revolved_profile_stl, write_step_manifest
from config import vehicle_params as vp


def assembly_profile_mm() -> list[tuple[float, float]]:
    """Return simplified exterior assembly profile."""

    profile = nose_cone.nose_profile_mm(samples=72)
    body_start = vp.NOSE_CONE_LENGTH_MM
    profile.extend(
        [
            (body_start, vp.BODY_DIAMETER_MM / 2.0),
            (vp.BODY_LENGTH_MM, vp.BODY_DIAMETER_MM / 2.0),
        ]
    )
    return sorted(profile, key=lambda item: item[0])


def run() -> dict[str, Path]:
    """Generate all CAD parts and full assembly exports."""

    nose_cone.run()
    body_tube.run()
    fin_set.run()
    avionics_bay.run()
    parachute_bay.run()
    nose_cone_tip.run()

    profile = assembly_profile_mm()
    stl_path = EXPORT_DIR / "ROCKET_M1_MK0_assembly.stl"
    step_path = EXPORT_DIR / "ROCKET_M1_MK0_assembly.step"
    exploded_step_path = EXPORT_DIR / "ROCKET_M1_MK0_exploded.step"
    write_revolved_profile_stl(stl_path, "rocket_m1_mk0_assembly", profile, segments=72)
    write_step_manifest(
        step_path,
        "ROCKET_M1_MK0_assembly",
        "Full educational airframe assembly with correct longitudinal z-offsets. Fins are represented by part export and assembly metadata.",
    )
    write_step_manifest(
        exploded_step_path,
        "ROCKET_M1_MK0_exploded",
        "Exploded educational assembly: each major component offset +150 mm in z for visual review.",
    )
    volume_cm3 = 3.141592653589793 * (vp.BODY_DIAMETER_MM / 2.0) ** 2 * vp.BODY_LENGTH_MM / 1000.0
    print_summary("ROCKET_M1_MK0_assembly", volume_cm3, (vp.BODY_LENGTH_MM, vp.BODY_DIAMETER_MM, vp.BODY_DIAMETER_MM), step_path)
    print(f"Saved: {step_path}")
    print(f"Saved: {stl_path}")
    print(f"Saved: {exploded_step_path}")
    return {"step": step_path, "stl": stl_path, "exploded_step": exploded_step_path}


if __name__ == "__main__":
    run()
