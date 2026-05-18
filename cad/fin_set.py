"""Trapezoidal Fibonacci-sweep fin CAD generator."""

from __future__ import annotations

import math
import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from cad.display_geometry import (
    EXPORT_DIR,
    polygon_area_mm2,
    print_summary,
    write_extruded_polygon_stl,
    write_step_manifest,
    write_svg,
)
from config import vehicle_params as vp
from utils.nature_geometry import dragon_curve_fins, golden_ratio, voronoi_lattice


def fin_polygon_mm() -> list[tuple[float, float]]:
    """Return trapezoidal fin polygon in chord/span coordinates."""

    sweep_offset_mm = vp.FIN_SPAN_MM * math.tan(math.radians(vp.FIN_SWEEP_ANGLE_DEG))
    return [
        (0.0, 0.0),
        (vp.FIN_ROOT_CHORD_MM, 0.0),
        (sweep_offset_mm + vp.FIN_TIP_CHORD_MM, vp.FIN_SPAN_MM),
        (sweep_offset_mm, vp.FIN_SPAN_MM),
    ]


def write_voronoi_svg(path: Path) -> None:
    """Write SVG showing fin Voronoi lattice cutout pattern."""

    width = 640
    height = 420
    scale = 3.0
    polygon = fin_polygon_mm()
    points = " ".join(f"{80 + x * scale:.1f},{330 - y * scale:.1f}" for x, y in polygon)
    segments = []
    for (x1, y1), (x2, y2) in voronoi_lattice(vp.FIN_ROOT_CHORD_MM, vp.FIN_SPAN_MM, 21):
        segments.append(
            f'<line x1="{80 + x1 * scale:.1f}" y1="{330 - y1 * scale:.1f}" '
            f'x2="{80 + x2 * scale:.1f}" y2="{330 - y2 * scale:.1f}" stroke="#4b8f74" stroke-width="2"/>'
        )
    dragon = dragon_curve_fins(10)
    if dragon:
        min_x = min(x for x, _ in dragon)
        min_y = min(y for _, y in dragon)
        dragon_points = " ".join(f"{430 + (x - min_x) * 5:.1f},{110 + (y - min_y) * 5:.1f}" for x, y in dragon)
        segments.append(f'<polyline points="{dragon_points}" fill="none" stroke="#8a5cf6" stroke-width="2"/>')
    body = [
        '<text class="title" x="24" y="30">Fin Voronoi Pattern</text>',
        '<text x="24" y="52">Educational lattice sketch; 2 mm skins retained around edges</text>',
        f'<polygon points="{points}" fill="#e5eef6" stroke="#31556f" stroke-width="3"/>',
        *segments,
        (
            f'<text x="24" y="390">Leading edge sweep {vp.FIN_SWEEP_ANGLE_DEG:.2f} deg; '
            f"rounded-tip radius = thickness x phi = {vp.FIN_THICKNESS_MM * golden_ratio:.2f} mm</text>"
        ),
    ]
    write_svg(path, width, height, body)
    print(f"Saved: {path}")


def run() -> dict[str, Path]:
    """Generate fin STEP, STL, and Voronoi SVG files."""

    polygon = fin_polygon_mm()
    stl_path = EXPORT_DIR / "fin.stl"
    step_path = EXPORT_DIR / "fin.step"
    svg_path = EXPORT_DIR / "fin_voronoi_pattern.svg"
    write_extruded_polygon_stl(stl_path, "fibonacci_sweep_fin", polygon, vp.FIN_THICKNESS_MM)
    write_voronoi_svg(svg_path)
    area_mm2 = polygon_area_mm2(polygon)
    volume_cm3 = area_mm2 * vp.FIN_THICKNESS_MM / 1000.0
    bbox_x = max(x for x, _ in polygon) - min(x for x, _ in polygon)
    bbox_y = max(y for _, y in polygon) - min(y for _, y in polygon)
    write_step_manifest(
        step_path,
        "fin",
        (
            "Trapezoidal G10 fin with Fibonacci-derived sweep. GD&T notes: root tab "
            "controls body-slot insertion; leading edge and tip radius are reference "
            "surfaces for aerodynamic simulation only; Voronoi void fraction target 18 percent."
        ),
    )
    print_summary("fin", volume_cm3, (bbox_x, bbox_y, vp.FIN_THICKNESS_MM), step_path)
    print(f"Saved: {step_path}")
    print(f"Saved: {stl_path}")
    return {"step": step_path, "stl": stl_path, "svg": svg_path}


if __name__ == "__main__":
    run()
