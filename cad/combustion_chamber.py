"""Generate a non-pressure combustion chamber display model."""

from __future__ import annotations

from pathlib import Path

try:
    from cad.display_geometry import (
        EXPORT_DIR,
        SAFETY_NOTICE,
        export_optional_cadquery_cylinder,
        write_revolved_profile_stl,
        write_step_manifest,
        write_svg,
    )
except ImportError:  # pragma: no cover
    from display_geometry import (
        EXPORT_DIR,
        SAFETY_NOTICE,
        export_optional_cadquery_cylinder,
        write_revolved_profile_stl,
        write_step_manifest,
        write_svg,
    )


def display_chamber_profile_mm() -> list[tuple[float, float]]:
    """Return a solid exterior display chamber profile.

    Returns:
        List of x and radius pairs in display millimeters.
    """

    return [
        (0.0, 26.0),
        (5.0, 26.0),
        (8.0, 18.0),
        (78.0, 18.0),
        (82.0, 26.0),
        (88.0, 26.0),
    ]


def run() -> dict[str, Path]:
    """Generate non-operational chamber artifacts.

    Returns:
        Mapping of artifact names to generated paths.
    """

    step_path = EXPORT_DIR / "combustion_chamber_display.step"
    stl_path = EXPORT_DIR / "combustion_chamber_display.stl"
    svg_path = EXPORT_DIR / "combustion_chamber_display.svg"
    cadquery_done = export_optional_cadquery_cylinder(step_path, stl_path, 18.0, 88.0)
    if not cadquery_done:
        write_revolved_profile_stl(stl_path, "combustion_chamber_display", display_chamber_profile_mm())
        write_step_manifest(
            step_path,
            "combustion_chamber_display",
            "Solid exterior display envelope. No internal cavity, ports, weld prep, or pressure features.",
        )

    body = [
        '<text class="title" x="24" y="30">Combustion Chamber Display Envelope</text>',
        '<text x="24" y="52">Solid model, no pressure cavity or manufacturing tolerances</text>',
        '<rect x="90" y="92" width="420" height="72" rx="6" fill="#dce8f2" stroke="#31556f" stroke-width="2"/>',
        '<rect x="60" y="82" width="54" height="92" rx="4" fill="#edf3f8" stroke="#31556f" stroke-width="2"/>',
        '<rect x="486" y="82" width="54" height="92" rx="4" fill="#edf3f8" stroke="#31556f" stroke-width="2"/>',
        f'<text x="24" y="228">{SAFETY_NOTICE}</text>',
    ]
    write_svg(svg_path, 620, 260, body)
    return {"step": step_path, "stl": stl_path, "svg": svg_path}


if __name__ == "__main__":
    artifacts = run()
    for artifact_name, artifact_path in artifacts.items():
        print(f"{artifact_name}: {artifact_path}")
