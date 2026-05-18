"""Parachute bay CAD generator with phyllotaxis vent pattern."""

from __future__ import annotations

import math
import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from cad.display_geometry import EXPORT_DIR, print_summary, write_revolved_profile_stl, write_step_manifest, write_svg
from config import vehicle_params as vp
from utils.nature_geometry import phyllotaxis_pattern


def bay_profile_mm() -> list[tuple[float, float]]:
    """Return parachute bay exterior profile."""

    radius = vp.BODY_DIAMETER_MM / 2.0
    return [(0.0, radius), (vp.PARACHUTE_BAY_LENGTH_MM, radius)]


def write_vent_svg(path: Path) -> None:
    """Write phyllotaxis vent pattern drawing."""

    points = phyllotaxis_pattern(vp.PARACHUTE_VENT_COUNT, 8.0)
    circles = [f'<circle cx="{180 + x:.1f}" cy="{180 + y:.1f}" r="4.5" fill="#31556f"/>' for x, y in points]
    body = [
        '<text class="title" x="24" y="30">Parachute Bay Vent Pattern</text>',
        '<text x="24" y="52">13-hole phyllotaxis equalization pattern, simulation reference only</text>',
        '<circle cx="180" cy="180" r="88" fill="#e5eef6" stroke="#31556f" stroke-width="2"/>',
        *circles,
    ]
    write_svg(path, 380, 340, body)
    print(f"Saved: {path}")


def run() -> dict[str, Path]:
    """Generate parachute bay STEP and STL files."""

    profile = bay_profile_mm()
    stl_path = EXPORT_DIR / "parachute_bay.stl"
    step_path = EXPORT_DIR / "parachute_bay.step"
    svg_path = EXPORT_DIR / "parachute_vent_pattern.svg"
    write_revolved_profile_stl(stl_path, "parachute_bay", profile, segments=64)
    write_vent_svg(svg_path)
    volume_cm3 = math.pi * (vp.BODY_DIAMETER_MM / 2.0) ** 2 * vp.PARACHUTE_BAY_LENGTH_MM / 1000.0
    write_step_manifest(
        step_path,
        "parachute_bay",
        (
            "Parachute bay with 13 phyllotaxis vent references and ejection-cap fit notes. "
            "Friction cap interference is documented for simulation packaging only; no energetic ejection design."
        ),
    )
    print_summary("parachute_bay", volume_cm3, (vp.PARACHUTE_BAY_LENGTH_MM, vp.BODY_DIAMETER_MM, vp.BODY_DIAMETER_MM), step_path)
    print(f"Saved: {step_path}")
    print(f"Saved: {stl_path}")
    return {"step": step_path, "stl": stl_path, "svg": svg_path}


if __name__ == "__main__":
    run()
