"""Generate a decorative injector face display artifact."""

from __future__ import annotations

import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from cad.display_geometry import EXPORT_DIR, SAFETY_NOTICE, write_step_manifest, write_svg
from propulsion.injector_design import generate_decorative_pattern, run as run_injector_pattern


def run() -> dict[str, Path]:
    """Generate decorative injector plate files.

    Returns:
        Mapping of artifact names to generated paths.
    """

    pattern_artifacts = run_injector_pattern()
    step_path = EXPORT_DIR / "injector_plate_display.step"
    svg_path = EXPORT_DIR / "injector_plate_display.svg"
    write_step_manifest(
        step_path,
        "injector_plate_display",
        "Decorative face marks only. No holes, no manifolds, no impingement geometry, no flow sizing.",
    )

    circles = []
    for mark in generate_decorative_pattern():
        x_px = 220 + mark.x_normalized * 110
        y_px = 140 + mark.y_normalized * 110
        circles.append(f'<circle cx="{x_px:.2f}" cy="{y_px:.2f}" r="3.8" fill="#31556f"/>')

    body = [
        '<text class="title" x="24" y="30">Decorative Injector Face</text>',
        '<text x="24" y="52">Display marks only, no through-holes or flow paths</text>',
        '<circle cx="220" cy="140" r="126" fill="#edf3f8" stroke="#31556f" stroke-width="2"/>',
        '<circle cx="220" cy="140" r="18" fill="none" stroke="#9aa6b2" stroke-width="2"/>',
        *circles,
        f'<text x="24" y="292">{SAFETY_NOTICE}</text>',
    ]
    write_svg(svg_path, 470, 325, body)
    return {"step": step_path, "svg": svg_path, "pattern_csv": pattern_artifacts["csv"]}


if __name__ == "__main__":
    artifacts = run()
    for artifact_name, artifact_path in artifacts.items():
        print(f"{artifact_name}: {artifact_path}")
