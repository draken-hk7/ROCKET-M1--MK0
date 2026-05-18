"""Generate a cooling-jacket illustration, not an operational channel design."""

from __future__ import annotations

from pathlib import Path

try:
    from cad.display_geometry import EXPORT_DIR, SAFETY_NOTICE, write_step_manifest, write_svg
except ImportError:  # pragma: no cover
    from display_geometry import EXPORT_DIR, SAFETY_NOTICE, write_step_manifest, write_svg


def run() -> dict[str, Path]:
    """Generate cooling-jacket display artifacts.

    Returns:
        Mapping of artifact names to generated paths.
    """

    step_path = EXPORT_DIR / "cooling_jacket_display.step"
    svg_path = EXPORT_DIR / "cooling_jacket_display.svg"
    write_step_manifest(
        step_path,
        "cooling_jacket_display",
        "Illustrative external ribs only. No channel width, channel height, pressure drop, or coolant routing.",
    )

    rib_lines = []
    for index in range(13):
        x_px = 96 + index * 32
        rib_lines.append(f'<path d="M {x_px} 90 C {x_px + 18} 114, {x_px - 18} 142, {x_px} 166" fill="none" stroke="#31556f" stroke-width="2"/>')
    body = [
        '<text class="title" x="24" y="30">Cooling Jacket Illustration</text>',
        '<text x="24" y="52">External rib motif only, no regenerative cooling design data</text>',
        '<rect x="78" y="92" width="420" height="74" rx="8" fill="#edf3f8" stroke="#9aa6b2" stroke-width="2"/>',
        *rib_lines,
        f'<text x="24" y="232">{SAFETY_NOTICE}</text>',
    ]
    write_svg(svg_path, 580, 265, body)
    return {"step": step_path, "svg": svg_path}


if __name__ == "__main__":
    artifacts = run()
    for artifact_name, artifact_path in artifacts.items():
        print(f"{artifact_name}: {artifact_path}")
