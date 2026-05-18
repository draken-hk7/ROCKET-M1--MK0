"""Normalized nozzle contour generator for educational documentation.

The module generates a dimensionless bell-nozzle-like curve for diagrams and
software workflows. It does not calculate throat area, expansion ratio from a
mission point, mass flow, or any pressure-coupled manufacturing dimensions.
"""

from __future__ import annotations

import math
from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Iterable

try:
    from propulsion.common import (
        SAFETY_NOTICE,
        block_operational_calculation,
        output_path,
        write_csv,
        write_json,
    )
except ImportError:  # pragma: no cover
    from common import SAFETY_NOTICE, block_operational_calculation, output_path, write_csv, write_json


@dataclass(frozen=True)
class NormalizedNozzlePoint:
    """A single point on a normalized nozzle contour.

    Attributes:
        station_index: Ordered station index.
        x_over_rt: Axial coordinate normalized by throat radius.
        radius_over_rt: Local radius normalized by throat radius.
        region: Contour region label.
        note: Safety and validity note.
    """

    station_index: int
    x_over_rt: float
    radius_over_rt: float
    region: str
    note: str


def refuse_absolute_nozzle_sizing(thrust_n: float, chamber_pressure_pa: float) -> None:
    """Reject absolute nozzle sizing requests.

    Args:
        thrust_n: Requested thrust in newtons.
        chamber_pressure_pa: Requested chamber pressure in pascals.

    Raises:
        NonOperationalDesignError: Always raised via the shared safety gate.
    """

    _ = thrust_n, chamber_pressure_pa
    block_operational_calculation("Absolute nozzle throat and exit sizing")


def generate_normalized_bell_profile(
    area_ratio: float = 3.0,
    length_fraction: float = 0.8,
    divergence_half_angle_deg: float = 15.0,
    samples: int = 96,
) -> list[NormalizedNozzlePoint]:
    """Generate a normalized educational bell contour.

    Args:
        area_ratio: Display-only exit-to-throat area ratio label.
        length_fraction: Display-only bell length fraction.
        divergence_half_angle_deg: Display-only divergence angle cap in degrees.
        samples: Number of contour samples.

    Returns:
        Ordered normalized nozzle contour points.

    Raises:
        ValueError: If inputs are outside educational plotting limits.
    """

    if area_ratio <= 1.0 or area_ratio > 8.0:
        raise ValueError("area_ratio must be between 1 and 8 for normalized plotting.")
    if not 0.5 <= length_fraction <= 1.0:
        raise ValueError("length_fraction must be between 0.5 and 1.0 for normalized plotting.")
    if divergence_half_angle_deg <= 0.0 or divergence_half_angle_deg > 15.0:
        raise ValueError("divergence_half_angle_deg must be in the educational range 0 to 15.")
    if samples < 24:
        raise ValueError("samples must be at least 24 for a smooth educational contour.")

    exit_radius_over_rt = math.sqrt(area_ratio)
    tangent_length = (exit_radius_over_rt - 1.0) / math.tan(math.radians(divergence_half_angle_deg))
    bell_length_over_rt = max(2.0, length_fraction * tangent_length)
    converging_length_over_rt = 1.6

    points: list[NormalizedNozzlePoint] = []
    converging_samples = max(8, samples // 4)
    diverging_samples = samples - converging_samples

    for index in range(converging_samples):
        u = index / (converging_samples - 1)
        x_over_rt = -converging_length_over_rt * (1.0 - u)
        radius_over_rt = 1.0 + 0.95 * (1.0 - u) ** 1.7
        points.append(
            NormalizedNozzlePoint(
                station_index=len(points),
                x_over_rt=round(x_over_rt, 6),
                radius_over_rt=round(radius_over_rt, 6),
                region="converging_display",
                note=SAFETY_NOTICE,
            )
        )

    for index in range(1, diverging_samples + 1):
        u = index / diverging_samples
        x_over_rt = bell_length_over_rt * u
        smooth = 3.0 * u**2 - 2.0 * u**3
        radius_over_rt = 1.0 + (exit_radius_over_rt - 1.0) * smooth
        points.append(
            NormalizedNozzlePoint(
                station_index=len(points),
                x_over_rt=round(x_over_rt, 6),
                radius_over_rt=round(radius_over_rt, 6),
                region="bell_display",
                note=SAFETY_NOTICE,
            )
        )

    return points


def write_nozzle_svg(points: Iterable[NormalizedNozzlePoint], path: Path) -> None:
    """Write a normalized cross-section SVG.

    Args:
        points: Normalized contour points.
        path: Destination SVG path.
    """

    points_list = list(points)
    min_x = min(point.x_over_rt for point in points_list)
    max_x = max(point.x_over_rt for point in points_list)
    max_r = max(point.radius_over_rt for point in points_list)
    width = 780
    height = 280
    pad = 42

    def sx(x_over_rt: float) -> float:
        return pad + (x_over_rt - min_x) / (max_x - min_x) * (width - 2 * pad)

    def sy(radius_over_rt: float) -> float:
        return height / 2 - radius_over_rt / max_r * (height / 2 - pad)

    top = " ".join(f"{sx(p.x_over_rt):.2f},{sy(p.radius_over_rt):.2f}" for p in points_list)
    bottom = " ".join(f"{sx(p.x_over_rt):.2f},{height - sy(p.radius_over_rt):.2f}" for p in reversed(points_list))
    center_y = height / 2
    lines = [
        f'<svg xmlns="http://www.w3.org/2000/svg" width="{width}" height="{height}" viewBox="0 0 {width} {height}">',
        "<style>text{font-family:Arial,sans-serif;fill:#1f2933;font-size:12px}.title{font-size:18px;font-weight:700}</style>",
        '<rect width="100%" height="100%" fill="#fbfcfd"/>',
        '<text class="title" x="24" y="30">Normalized Nozzle Display Profile</text>',
        '<text x="24" y="50">No absolute dimensions, throat area, or pressure-coupled sizing</text>',
        f'<line x1="{pad}" y1="{center_y}" x2="{width - pad}" y2="{center_y}" stroke="#9aa6b2" stroke-dasharray="4 4"/>',
        f'<polygon points="{top} {bottom}" fill="#dce8f2" stroke="#31556f" stroke-width="2"/>',
        f'<text x="24" y="{height - 22}">{SAFETY_NOTICE}</text>',
        "</svg>",
    ]
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text("\n".join(lines) + "\n", encoding="utf-8")


def write_nozzle_dxf(points: Iterable[NormalizedNozzlePoint], path: Path) -> None:
    """Write a DXF polyline of the normalized profile.

    Args:
        points: Normalized contour points.
        path: Destination DXF path.
    """

    path.parent.mkdir(parents=True, exist_ok=True)
    dxf_lines = [
        "0",
        "SECTION",
        "2",
        "HEADER",
        "9",
        "$INSUNITS",
        "70",
        "0",
        "0",
        "ENDSEC",
        "0",
        "SECTION",
        "2",
        "ENTITIES",
        "999",
        "NORMALIZED TRAINING PROFILE - NOT FOR CNC OR MANUFACTURING",
    ]
    for point in points:
        dxf_lines.extend(
            [
                "0",
                "POINT",
                "8",
                "NORMALIZED_PROFILE",
                "10",
                f"{point.x_over_rt:.6f}",
                "20",
                f"{point.radius_over_rt:.6f}",
                "30",
                "0.0",
            ]
        )
    dxf_lines.extend(["0", "ENDSEC", "0", "EOF"])
    path.write_text("\n".join(dxf_lines) + "\n", encoding="utf-8")


def run(output_directory: Path | None = None) -> dict[str, Path]:
    """Generate normalized nozzle outputs.

    Args:
        output_directory: Optional output directory override.

    Returns:
        Mapping of artifact names to paths.
    """

    target_directory = output_directory or output_path("nozzle").parent / "nozzle"
    target_directory.mkdir(parents=True, exist_ok=True)
    profile = generate_normalized_bell_profile()
    csv_path = target_directory / "normalized_nozzle_profile.csv"
    svg_path = target_directory / "normalized_nozzle_profile.svg"
    json_path = target_directory / "nozzle_metadata.json"
    dxf_path = Path(__file__).resolve().parents[1] / "cad" / "exports" / "nozzle.dxf"

    write_csv(
        csv_path,
        [asdict(point) for point in profile],
        ["station_index", "x_over_rt", "radius_over_rt", "region", "note"],
    )
    write_nozzle_svg(profile, svg_path)
    write_nozzle_dxf(profile, dxf_path)
    write_json(
        json_path,
        {
            "artifact": "normalized_nozzle_display_profile",
            "safety_notice": SAFETY_NOTICE,
            "not_included": [
                "throat area",
                "exit diameter",
                "mass flow",
                "wall contour tolerances",
                "MOC characteristic net",
                "CNC-ready dimensions",
            ],
        },
    )
    return {"csv": csv_path, "svg": svg_path, "json": json_path, "dxf": dxf_path}


if __name__ == "__main__":
    artifacts = run()
    for artifact_name, artifact_path in artifacts.items():
        print(f"{artifact_name}: {artifact_path}")
