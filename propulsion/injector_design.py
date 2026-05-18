"""Injector documentation generator with operational sizing blocked.

The generated pattern is a decorative, normalized face layout for CAD and
drawing practice. It is not an injector design and contains no through-hole or
flow-sizing data.
"""

from __future__ import annotations

import math
from dataclasses import asdict, dataclass
from pathlib import Path

try:
    from propulsion.common import SAFETY_NOTICE, block_operational_calculation, output_path, write_csv, write_json
except ImportError:  # pragma: no cover
    from common import SAFETY_NOTICE, block_operational_calculation, output_path, write_csv, write_json


@dataclass(frozen=True)
class DecorativeInjectorMark:
    """Decorative injector face mark.

    Attributes:
        mark_id: Stable mark identifier.
        x_normalized: Normalized x coordinate on the display face.
        y_normalized: Normalized y coordinate on the display face.
        ring_label: Decorative ring label.
        note: Safety and validity note.
    """

    mark_id: str
    x_normalized: float
    y_normalized: float
    ring_label: str
    note: str


def bernoulli_orifice_sizing_blocked(
    mass_flow_kg_s: float,
    density_kg_m3: float,
    pressure_drop_pa: float,
) -> None:
    """Reject injector orifice sizing.

    Args:
        mass_flow_kg_s: Requested mass flow in kilograms per second.
        density_kg_m3: Fluid density in kilograms per cubic meter.
        pressure_drop_pa: Injector pressure drop in pascals.

    Raises:
        NonOperationalDesignError: Always raised via the shared safety gate.
    """

    _ = mass_flow_kg_s, density_kg_m3, pressure_drop_pa
    block_operational_calculation("Injector orifice sizing")


def generate_decorative_pattern() -> list[DecorativeInjectorMark]:
    """Generate a normalized decorative injector face pattern.

    Returns:
        List of decorative face marks.
    """

    marks: list[DecorativeInjectorMark] = []
    ring_specs = [("inner_display_ring", 0.28, 8), ("outer_display_ring", 0.58, 16)]
    for ring_label, radius, count in ring_specs:
        for index in range(count):
            angle_rad = 2.0 * math.pi * index / count
            marks.append(
                DecorativeInjectorMark(
                    mark_id=f"{ring_label}_{index:02d}",
                    x_normalized=round(radius * math.cos(angle_rad), 6),
                    y_normalized=round(radius * math.sin(angle_rad), 6),
                    ring_label=ring_label,
                    note=SAFETY_NOTICE,
                )
            )
    marks.append(
        DecorativeInjectorMark(
            mark_id="center_display_mark",
            x_normalized=0.0,
            y_normalized=0.0,
            ring_label="center_display_mark",
            note=SAFETY_NOTICE,
        )
    )
    return marks


def run(output_directory: Path | None = None) -> dict[str, Path]:
    """Write decorative injector pattern outputs.

    Args:
        output_directory: Optional output directory override.

    Returns:
        Mapping of artifact names to paths.
    """

    target_directory = output_directory or output_path("injector").parent / "injector"
    target_directory.mkdir(parents=True, exist_ok=True)
    marks = generate_decorative_pattern()
    csv_path = target_directory / "decorative_injector_pattern.csv"
    json_path = target_directory / "injector_metadata.json"
    write_csv(
        csv_path,
        [asdict(mark) for mark in marks],
        ["mark_id", "x_normalized", "y_normalized", "ring_label", "note"],
    )
    write_json(
        json_path,
        {
            "artifact": "decorative_injector_face_pattern",
            "safety_notice": SAFETY_NOTICE,
            "not_included": [
                "orifice count for flow",
                "orifice diameter",
                "impingement angle",
                "pressure drop",
                "atomization performance",
                "valve timing",
            ],
        },
    )
    return {"csv": csv_path, "json": json_path}


if __name__ == "__main__":
    artifacts = run()
    for artifact_name, artifact_path in artifacts.items():
        print(f"{artifact_name}: {artifact_path}")
