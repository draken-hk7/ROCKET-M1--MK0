"""Display-only geometry helpers for CAD automation scripts.

The functions in this file create simple non-pressure visualization artifacts.
They are not substitutes for CAD, stress analysis, drawing release, or
manufacturing review by qualified professionals.
"""

from __future__ import annotations

import math
from pathlib import Path
from typing import Iterable, Sequence


PROJECT_ROOT = Path(__file__).resolve().parents[1]
EXPORT_DIR = PROJECT_ROOT / "cad" / "exports"
SAFETY_NOTICE = (
    "DISPLAY MODEL ONLY - NOT FOR FABRICATION, PRESSURE TESTING, "
    "PROPELLANT USE, IGNITION, LAUNCH, OR HOT FIRE."
)


def ensure_directory(path: Path) -> Path:
    """Create a directory if it does not exist.

    Args:
        path: Directory path.

    Returns:
        The same directory path.
    """

    path.mkdir(parents=True, exist_ok=True)
    return path


def write_step_manifest(path: Path, title: str, body: str) -> None:
    """Write a neutral STEP-style manifest, not a manufacturable solid.

    Args:
        path: Destination path with a STEP extension.
        title: Artifact title.
        body: Human-readable artifact description.
    """

    ensure_directory(path.parent)
    content = f"""ISO-10303-21;
HEADER;
FILE_DESCRIPTION(('ROCKET M1- MK0 non-operational display manifest'),'2;1');
FILE_NAME('{title}','2026-05-18T00:00:00',('Codex'),('ROCKET M1- MK0'),'educational','educational','not released');
FILE_SCHEMA(('CONFIG_CONTROL_DESIGN'));
ENDSEC;
DATA;
/* {SAFETY_NOTICE} */
/* {body} */
ENDSEC;
END-ISO-10303-21;
"""
    path.write_text(content, encoding="utf-8")


def _facet_lines(vertices: Sequence[tuple[float, float, float]]) -> list[str]:
    """Format one ASCII STL triangular facet.

    Args:
        vertices: Three vertices as x, y, z tuples in display millimeters.

    Returns:
        STL facet lines.
    """

    lines = ["  facet normal 0 0 0", "    outer loop"]
    for x_mm, y_mm, z_mm in vertices:
        lines.append(f"      vertex {x_mm:.6f} {y_mm:.6f} {z_mm:.6f}")
    lines.extend(["    endloop", "  endfacet"])
    return lines


def write_revolved_profile_stl(
    path: Path,
    name: str,
    profile_mm: Sequence[tuple[float, float]],
    segments: int = 40,
) -> None:
    """Write an ASCII STL from a display profile of radius versus station.

    Args:
        path: Destination STL path.
        name: STL solid name.
        profile_mm: Sequence of x and radius pairs in display millimeters.
        segments: Number of revolution segments.

    Raises:
        ValueError: If profile or segment count is invalid.
    """

    if len(profile_mm) < 2:
        raise ValueError("profile_mm must contain at least two points.")
    if segments < 8:
        raise ValueError("segments must be at least 8 for display STL generation.")

    ensure_directory(path.parent)
    lines = [f"solid {name}", f"  // {SAFETY_NOTICE}"]
    for left, right in zip(profile_mm, profile_mm[1:]):
        x0_mm, r0_mm = left
        x1_mm, r1_mm = right
        for segment in range(segments):
            a0 = 2.0 * math.pi * segment / segments
            a1 = 2.0 * math.pi * (segment + 1) / segments
            p00 = (x0_mm, r0_mm * math.cos(a0), r0_mm * math.sin(a0))
            p01 = (x0_mm, r0_mm * math.cos(a1), r0_mm * math.sin(a1))
            p10 = (x1_mm, r1_mm * math.cos(a0), r1_mm * math.sin(a0))
            p11 = (x1_mm, r1_mm * math.cos(a1), r1_mm * math.sin(a1))
            lines.extend(_facet_lines([p00, p10, p11]))
            lines.extend(_facet_lines([p00, p11, p01]))
    lines.append(f"endsolid {name}")
    path.write_text("\n".join(lines) + "\n", encoding="utf-8")


def write_svg(path: Path, width: int, height: int, body: Iterable[str]) -> None:
    """Write a simple SVG document.

    Args:
        path: Destination SVG path.
        width: SVG width in pixels.
        height: SVG height in pixels.
        body: SVG body lines.
    """

    ensure_directory(path.parent)
    lines = [
        f'<svg xmlns="http://www.w3.org/2000/svg" width="{width}" height="{height}" viewBox="0 0 {width} {height}">',
        "<style>text{font-family:Arial,sans-serif;fill:#1f2933;font-size:12px}.title{font-size:18px;font-weight:700}</style>",
        '<rect width="100%" height="100%" fill="#fbfcfd"/>',
        *body,
        "</svg>",
    ]
    path.write_text("\n".join(lines) + "\n", encoding="utf-8")


def export_optional_cadquery_cylinder(
    step_path: Path,
    stl_path: Path,
    radius_mm: float,
    length_mm: float,
) -> bool:
    """Export a solid display cylinder when CadQuery is available.

    Args:
        step_path: STEP destination path.
        stl_path: STL destination path.
        radius_mm: Display cylinder radius in millimeters.
        length_mm: Display cylinder length in millimeters.

    Returns:
        True if CadQuery export succeeded, otherwise False.
    """

    try:
        import cadquery as cq  # type: ignore
        from cadquery import exporters  # type: ignore
    except Exception:
        return False

    ensure_directory(step_path.parent)
    model = cq.Workplane("XY").circle(radius_mm).extrude(length_mm)
    exporters.export(model, str(step_path))
    exporters.export(model, str(stl_path))
    return True
