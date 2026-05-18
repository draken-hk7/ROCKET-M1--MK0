"""Generate a non-operational nozzle display model."""

from __future__ import annotations

import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from cad.display_geometry import EXPORT_DIR, SAFETY_NOTICE, write_revolved_profile_stl, write_step_manifest, write_svg
from propulsion.nozzle_design import generate_normalized_bell_profile, run as run_nozzle_profile


def display_nozzle_profile_mm() -> list[tuple[float, float]]:
    """Create a scaled solid display profile from normalized data.

    Returns:
        Display x and radius pairs in millimeters.
    """

    points = generate_normalized_bell_profile(samples=72)
    x_min = min(point.x_over_rt for point in points)
    scale_mm = 10.0
    return [
        ((point.x_over_rt - x_min) * scale_mm, point.radius_over_rt * scale_mm)
        for point in points
    ]


def run() -> dict[str, Path]:
    """Generate non-operational nozzle artifacts.

    Returns:
        Mapping of artifact names to generated paths.
    """

    profile_artifacts = run_nozzle_profile()
    stl_path = EXPORT_DIR / "nozzle_display.stl"
    step_path = EXPORT_DIR / "nozzle_display.step"
    svg_path = EXPORT_DIR / "nozzle_display.svg"
    write_revolved_profile_stl(stl_path, "nozzle_display", display_nozzle_profile_mm())
    write_step_manifest(
        step_path,
        "nozzle_display",
        "Solid exterior display profile derived from normalized curve. No throat sizing or internal flow path.",
    )
    body = [
        '<text class="title" x="24" y="30">Nozzle Display Assembly</text>',
        '<text x="24" y="52">Normalized exterior silhouette, no absolute throat or exit dimensions</text>',
        '<path d="M 70 145 C 150 105, 230 104, 330 112 C 440 122, 560 74, 690 66 L 690 224 C 560 216, 440 168, 330 178 C 230 186, 150 185, 70 145 Z" fill="#dce8f2" stroke="#31556f" stroke-width="2"/>',
        f'<text x="24" y="276">{SAFETY_NOTICE}</text>',
    ]
    write_svg(svg_path, 760, 310, body)
    return {"stl": stl_path, "step": step_path, "svg": svg_path, "dxf": profile_artifacts["dxf"]}


if __name__ == "__main__":
    artifacts = run()
    for artifact_name, artifact_path in artifacts.items():
        print(f"{artifact_name}: {artifact_path}")
