"""Educational thermodynamic proxy for ROCKET M1- MK0.

This is not NASA CEA and does not model real propellant chemistry. It creates a
traceable performance-index envelope for documentation and software testing
without producing operational engine design data.
"""

from __future__ import annotations

import math
from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Iterable, Literal

try:
    from propulsion.common import SAFETY_NOTICE, output_path, write_csv, write_json
except ImportError:  # pragma: no cover - supports direct script execution
    from common import SAFETY_NOTICE, output_path, write_csv, write_json


PropellantFamily = Literal["lox_ethanol_proxy", "h2o2_kerosene_proxy"]


@dataclass(frozen=True)
class PerformancePoint:
    """Single non-operational thermodynamic proxy point.

    Attributes:
        chamber_pressure_bar: Chamber pressure label in bar.
        mixture_ratio_o_f: Oxidizer-to-fuel mixture ratio label.
        propellant_family: Proxy propellant family name.
        isp_index: Dimensionless specific impulse quality index.
        c_star_index: Dimensionless characteristic velocity quality index.
        thrust_coefficient_index: Dimensionless thrust coefficient quality index.
        chamber_temperature_index: Dimensionless temperature severity index.
        note: Safety and validity note.
    """

    chamber_pressure_bar: float
    mixture_ratio_o_f: float
    propellant_family: PropellantFamily
    isp_index: float
    c_star_index: float
    thrust_coefficient_index: float
    chamber_temperature_index: float
    note: str


def _bounded(value: float, lower: float = 0.0, upper: float = 1.0) -> float:
    """Clamp a floating-point value.

    Args:
        value: Input value.
        lower: Lower bound.
        upper: Upper bound.

    Returns:
        Clamped value.
    """

    return max(lower, min(upper, value))


def _mixture_quality(mixture_ratio_o_f: float, optimum_o_f: float) -> float:
    """Compute a smooth dimensionless mixture quality curve.

    Args:
        mixture_ratio_o_f: Oxidizer-to-fuel mixture ratio label.
        optimum_o_f: Proxy optimum oxidizer-to-fuel ratio label.

    Returns:
        Dimensionless quality index between 0 and 1.
    """

    spread = 0.55
    exponent = -((mixture_ratio_o_f - optimum_o_f) ** 2) / (2.0 * spread**2)
    return _bounded(math.exp(exponent))


def _pressure_quality(chamber_pressure_bar: float) -> float:
    """Compute a dimensionless pressure quality index.

    Args:
        chamber_pressure_bar: Chamber pressure label in bar.

    Returns:
        Dimensionless quality index between 0 and 1.

    Raises:
        ValueError: If pressure label is outside the educational envelope.
    """

    if chamber_pressure_bar < 1.0 or chamber_pressure_bar > 50.0:
        raise ValueError(
            "chamber_pressure_bar must remain in the educational plotting "
            "range of 1 to 50 bar."
        )
    return _bounded(0.55 + 0.18 * math.log10(chamber_pressure_bar))


def estimate_proxy_point(
    chamber_pressure_bar: float,
    mixture_ratio_o_f: float,
    propellant_family: PropellantFamily,
) -> PerformancePoint:
    """Estimate a non-operational thermodynamic proxy point.

    Args:
        chamber_pressure_bar: Chamber pressure label in bar.
        mixture_ratio_o_f: Oxidizer-to-fuel mixture ratio label.
        propellant_family: Proxy propellant family.

    Returns:
        Dimensionless performance point.

    Raises:
        ValueError: If mixture ratio or propellant family is invalid.
    """

    if mixture_ratio_o_f <= 0.0:
        raise ValueError("mixture_ratio_o_f must be positive for envelope plotting.")

    if propellant_family == "lox_ethanol_proxy":
        optimum_o_f = 1.8
        thermal_bias = 0.82
    elif propellant_family == "h2o2_kerosene_proxy":
        optimum_o_f = 6.5
        thermal_bias = 0.72
    else:
        raise ValueError(f"Unsupported propellant_family: {propellant_family}")

    mixture_index = _mixture_quality(mixture_ratio_o_f, optimum_o_f)
    pressure_index = _pressure_quality(chamber_pressure_bar)
    isp_index = _bounded(0.30 + 0.52 * mixture_index + 0.12 * pressure_index)
    c_star_index = _bounded(0.25 + 0.60 * mixture_index)
    thrust_coefficient_index = _bounded(0.45 + 0.35 * pressure_index)
    chamber_temperature_index = _bounded(thermal_bias * (0.45 + 0.55 * mixture_index))

    return PerformancePoint(
        chamber_pressure_bar=round(chamber_pressure_bar, 3),
        mixture_ratio_o_f=round(mixture_ratio_o_f, 3),
        propellant_family=propellant_family,
        isp_index=round(isp_index, 5),
        c_star_index=round(c_star_index, 5),
        thrust_coefficient_index=round(thrust_coefficient_index, 5),
        chamber_temperature_index=round(chamber_temperature_index, 5),
        note=SAFETY_NOTICE,
    )


def generate_envelope(
    propellant_family: PropellantFamily = "lox_ethanol_proxy",
) -> list[PerformancePoint]:
    """Generate a non-operational performance envelope.

    Args:
        propellant_family: Proxy propellant family to plot.

    Returns:
        List of dimensionless performance points.
    """

    pressure_values_bar = [10.0, 12.5, 15.0, 17.5, 20.0]
    if propellant_family == "lox_ethanol_proxy":
        mixture_values = [1.2, 1.5, 1.8, 2.1, 2.4]
    else:
        mixture_values = [5.0, 5.75, 6.5, 7.25, 8.0]

    return [
        estimate_proxy_point(pressure_bar, mixture_ratio, propellant_family)
        for pressure_bar in pressure_values_bar
        for mixture_ratio in mixture_values
    ]


def _color_for_index(index: float) -> str:
    """Convert a dimensionless index to an SVG color.

    Args:
        index: Dimensionless index between 0 and 1.

    Returns:
        Hex RGB color string.
    """

    red = int(245 - 120 * index)
    green = int(245 - 60 * (1.0 - index))
    blue = int(245 - 185 * index)
    return f"#{red:02x}{green:02x}{blue:02x}"


def write_envelope_svg(points: Iterable[PerformancePoint], path: Path) -> None:
    """Write an SVG heatmap of the performance index envelope.

    Args:
        points: Performance points to plot.
        path: Destination SVG path.
    """

    points_list = list(points)
    pressures = sorted({point.chamber_pressure_bar for point in points_list})
    mixtures = sorted({point.mixture_ratio_o_f for point in points_list})
    cell = 58
    margin_left = 94
    margin_top = 72
    width = margin_left + cell * len(mixtures) + 40
    height = margin_top + cell * len(pressures) + 72
    by_key = {
        (point.chamber_pressure_bar, point.mixture_ratio_o_f): point
        for point in points_list
    }

    lines = [
        f'<svg xmlns="http://www.w3.org/2000/svg" width="{width}" height="{height}" viewBox="0 0 {width} {height}">',
        "<style>text{font-family:Arial,sans-serif;font-size:12px;fill:#1f2933}.title{font-size:18px;font-weight:700}.small{font-size:10px}</style>",
        '<rect width="100%" height="100%" fill="#fbfcfd"/>',
        '<text class="title" x="24" y="30">Educational Performance Index Envelope</text>',
        '<text x="24" y="50">Dimensionless proxy values, not NASA CEA or flight data</text>',
    ]

    for col, mixture in enumerate(mixtures):
        x = margin_left + col * cell + cell / 2
        lines.append(f'<text text-anchor="middle" x="{x:.1f}" y="66">O/F {mixture:g}</text>')

    for row, pressure in enumerate(pressures):
        y = margin_top + row * cell
        lines.append(f'<text text-anchor="end" x="86" y="{y + 34:.1f}">{pressure:g} bar</text>')
        for col, mixture in enumerate(mixtures):
            x = margin_left + col * cell
            point = by_key[(pressure, mixture)]
            color = _color_for_index(point.isp_index)
            lines.append(f'<rect x="{x}" y="{y}" width="{cell - 4}" height="{cell - 4}" rx="4" fill="{color}" stroke="#c9d1d9"/>')
            lines.append(f'<text text-anchor="middle" x="{x + cell / 2 - 2:.1f}" y="{y + 33:.1f}">{point.isp_index:.2f}</text>')

    lines.append(f'<text class="small" x="24" y="{height - 26}">{SAFETY_NOTICE}</text>')
    lines.append("</svg>")
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text("\n".join(lines) + "\n", encoding="utf-8")


def run(output_directory: Path | None = None) -> dict[str, Path]:
    """Generate educational thermodynamic outputs.

    Args:
        output_directory: Optional output directory override.

    Returns:
        Mapping of artifact names to paths.
    """

    target_directory = output_directory or output_path("performance").parent / "performance"
    target_directory.mkdir(parents=True, exist_ok=True)
    points = generate_envelope("lox_ethanol_proxy") + generate_envelope("h2o2_kerosene_proxy")
    rows = [asdict(point) for point in points]
    csv_path = target_directory / "performance_envelope.csv"
    json_path = target_directory / "performance_metadata.json"
    svg_path = target_directory / "performance_envelope.svg"

    write_csv(
        csv_path,
        rows,
        [
            "chamber_pressure_bar",
            "mixture_ratio_o_f",
            "propellant_family",
            "isp_index",
            "c_star_index",
            "thrust_coefficient_index",
            "chamber_temperature_index",
            "note",
        ],
    )
    write_json(
        json_path,
        {
            "artifact": "educational_thermodynamic_proxy",
            "safety_notice": SAFETY_NOTICE,
            "not_included": [
                "real NASA CEA equilibrium chemistry",
                "species mole fractions",
                "dimensional Isp",
                "mass flow",
                "throat area",
                "propellant feed sizing",
            ],
            "constants_source": "No physical combustion constants are used in this proxy model.",
        },
    )
    write_envelope_svg(generate_envelope("lox_ethanol_proxy"), svg_path)
    return {"csv": csv_path, "json": json_path, "svg": svg_path}


if __name__ == "__main__":
    artifacts = run()
    for artifact_name, artifact_path in artifacts.items():
        print(f"{artifact_name}: {artifact_path}")
