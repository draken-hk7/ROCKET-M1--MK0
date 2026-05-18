"""Shared utilities for the ROCKET M1- MK0 educational toolchain.

The modules in this package generate non-operational educational artifacts.
They are intentionally unsuitable for fabricating, pressure testing, or firing
rocket hardware.
"""

from __future__ import annotations

import csv
import json
from pathlib import Path
from typing import Iterable, Mapping, Sequence


PROJECT_ROOT = Path(__file__).resolve().parents[1]
OUTPUT_ROOT = PROJECT_ROOT / "outputs"

SAFETY_NOTICE = (
    "Educational non-operational artifact. Not for fabrication, pressure "
    "testing, propellant use, ignition, launch, or hot-fire operations."
)


class NonOperationalDesignError(RuntimeError):
    """Raised when a requested calculation would enable operational hardware."""


def ensure_directory(path: Path) -> Path:
    """Create a directory if needed.

    Args:
        path: Directory path to create.

    Returns:
        The same directory path.
    """

    path.mkdir(parents=True, exist_ok=True)
    return path


def output_path(*parts: str) -> Path:
    """Build an output path under the project-level outputs directory.

    Args:
        *parts: Path components below the outputs directory.

    Returns:
        Absolute path under outputs.
    """

    path = OUTPUT_ROOT.joinpath(*parts)
    ensure_directory(path.parent)
    return path


def write_json(path: Path, payload: Mapping[str, object]) -> None:
    """Write a mapping as formatted JSON.

    Args:
        path: Destination file path.
        payload: JSON-serializable mapping.
    """

    ensure_directory(path.parent)
    path.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def write_csv(
    path: Path,
    rows: Iterable[Mapping[str, object]],
    fieldnames: Sequence[str],
) -> None:
    """Write rows to CSV with a stable header.

    Args:
        path: Destination file path.
        rows: Iterable of row mappings.
        fieldnames: Ordered CSV field names.
    """

    ensure_directory(path.parent)
    with path.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=fieldnames)
        writer.writeheader()
        for row in rows:
            writer.writerow(row)


def block_operational_calculation(name: str) -> None:
    """Raise for calculations that would enable buildable propulsion hardware.

    Args:
        name: Human-readable calculation name.

    Raises:
        NonOperationalDesignError: Always raised with engineering context.
    """

    raise NonOperationalDesignError(
        f"{name} is intentionally omitted because it can produce fabrication "
        "or test parameters for operational rocket hardware."
    )
