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


def write_extruded_polygon_stl(
    path: Path,
    name: str,
    polygon_xy_mm: Sequence[tuple[float, float]],
    thickness_mm: float,
) -> None:
    """Write an ASCII STL by extruding a 2D polygon.

    Args:
        path: Destination STL path.
        name: STL solid name.
        polygon_xy_mm: Ordered polygon vertices in display millimeters.
        thickness_mm: Extrusion thickness in millimeters.

    Raises:
        ValueError: If fewer than three vertices or non-positive thickness.
    """

    if len(polygon_xy_mm) < 3:
        raise ValueError("polygon_xy_mm must include at least three vertices.")
    if thickness_mm <= 0.0:
        raise ValueError("thickness_mm must be positive.")

    ensure_directory(path.parent)
    z0 = -thickness_mm / 2.0
    z1 = thickness_mm / 2.0
    lower = [(x, y, z0) for x, y in polygon_xy_mm]
    upper = [(x, y, z1) for x, y in polygon_xy_mm]
    lines = [f"solid {name}", f"  // {SAFETY_NOTICE}"]

    for index in range(1, len(polygon_xy_mm) - 1):
        lines.extend(_facet_lines([upper[0], upper[index], upper[index + 1]]))
        lines.extend(_facet_lines([lower[0], lower[index + 1], lower[index]]))

    count = len(polygon_xy_mm)
    for index in range(count):
        next_index = (index + 1) % count
        lines.extend(_facet_lines([lower[index], lower[next_index], upper[next_index]]))
        lines.extend(_facet_lines([lower[index], upper[next_index], upper[index]]))

    lines.append(f"endsolid {name}")
    path.write_text("\n".join(lines) + "\n", encoding="utf-8")


def polygon_area_mm2(polygon_xy_mm: Sequence[tuple[float, float]]) -> float:
    """Calculate polygon area by the shoelace formula."""

    area = 0.0
    for index, (x0, y0) in enumerate(polygon_xy_mm):
        x1, y1 = polygon_xy_mm[(index + 1) % len(polygon_xy_mm)]
        area += x0 * y1 - x1 * y0
    return abs(area) / 2.0


def profile_volume_cm3(profile_mm: Sequence[tuple[float, float]]) -> float:
    """Estimate revolved profile volume in cubic centimeters."""

    volume_mm3 = 0.0
    for (x0, r0), (x1, r1) in zip(profile_mm, profile_mm[1:]):
        length = abs(x1 - x0)
        volume_mm3 += (3.141592653589793 * length / 3.0) * (r0 * r0 + r0 * r1 + r1 * r1)
    return volume_mm3 / 1000.0


def bbox_from_profile_mm(profile_mm: Sequence[tuple[float, float]]) -> tuple[float, float, float]:
    """Return bounding box for a revolved profile."""

    min_x = min(x for x, _ in profile_mm)
    max_x = max(x for x, _ in profile_mm)
    max_r = max(r for _, r in profile_mm)
    return (max_x - min_x, 2.0 * max_r, 2.0 * max_r)


def print_summary(part_name: str, volume_cm3: float, bbox_mm: tuple[float, float, float], export_path: Path) -> None:
    """Print a standard CAD summary table row."""

    print("part name | volume_cm3 | bbox_mm | export_path")
    print(
        f"{part_name} | {volume_cm3:.2f} | "
        f"{bbox_mm[0]:.1f} x {bbox_mm[1]:.1f} x {bbox_mm[2]:.1f} | {export_path}"
    )


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
