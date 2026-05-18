"""Combustion chamber documentation generator.

This module creates a safe display-envelope summary and explicitly blocks
pressure vessel sizing calculations that could enable operational hardware.
"""

from __future__ import annotations

from dataclasses import asdict, dataclass
from pathlib import Path

try:
    from propulsion.common import SAFETY_NOTICE, block_operational_calculation, output_path, write_json
except ImportError:  # pragma: no cover
    from common import SAFETY_NOTICE, block_operational_calculation, output_path, write_json


@dataclass(frozen=True)
class DisplayChamberEnvelope:
    """Non-pressure display chamber envelope.

    Attributes:
        display_length_mm: Exterior display length in millimeters.
        display_outer_diameter_mm: Exterior display diameter in millimeters.
        display_flange_diameter_mm: Decorative flange diameter in millimeters.
        intended_use: Intended non-operational use.
        note: Safety and validity note.
    """

    display_length_mm: float
    display_outer_diameter_mm: float
    display_flange_diameter_mm: float
    intended_use: str
    note: str


def barlow_wall_thickness_blocked(pressure_pa: float, radius_m: float) -> None:
    """Reject pressure vessel wall thickness sizing.

    Args:
        pressure_pa: Internal pressure in pascals.
        radius_m: Internal radius in meters.

    Raises:
        NonOperationalDesignError: Always raised via the shared safety gate.
    """

    _ = pressure_pa, radius_m
    block_operational_calculation("Pressure vessel wall thickness sizing")


def l_star_chamber_sizing_blocked(thrust_n: float, chamber_pressure_pa: float) -> None:
    """Reject L-star chamber sizing for an operational combustor.

    Args:
        thrust_n: Requested thrust in newtons.
        chamber_pressure_pa: Requested chamber pressure in pascals.

    Raises:
        NonOperationalDesignError: Always raised via the shared safety gate.
    """

    _ = thrust_n, chamber_pressure_pa
    block_operational_calculation("Operational L-star combustion chamber sizing")


def generate_display_envelope() -> DisplayChamberEnvelope:
    """Generate a benign display chamber envelope.

    Returns:
        Display-only chamber dimensions.
    """

    return DisplayChamberEnvelope(
        display_length_mm=84.0,
        display_outer_diameter_mm=36.0,
        display_flange_diameter_mm=52.0,
        intended_use="solid display model and documentation scale reference",
        note=SAFETY_NOTICE,
    )


def run(output_directory: Path | None = None) -> dict[str, Path]:
    """Write chamber documentation outputs.

    Args:
        output_directory: Optional output directory override.

    Returns:
        Mapping of artifact names to paths.
    """

    target_directory = output_directory or output_path("chamber").parent / "chamber"
    target_directory.mkdir(parents=True, exist_ok=True)
    envelope = generate_display_envelope()
    json_path = target_directory / "chamber_display_envelope.json"
    write_json(
        json_path,
        {
            "artifact": "display_chamber_envelope",
            "display_envelope": asdict(envelope),
            "materials_discussed_only": [
                "316L stainless steel",
                "Inconel 625",
            ],
            "not_included": [
                "internal chamber volume",
                "wall thickness",
                "burst pressure",
                "weld sizing",
                "regenerative cooling pressure drop",
                "pressure-rated tolerances",
            ],
            "safety_notice": SAFETY_NOTICE,
        },
    )
    return {"json": json_path}


if __name__ == "__main__":
    artifacts = run()
    for artifact_name, artifact_path in artifacts.items():
        print(f"{artifact_name}: {artifact_path}")
