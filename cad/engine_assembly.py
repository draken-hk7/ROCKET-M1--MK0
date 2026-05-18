"""Generate the full non-operational engine display assembly."""

from __future__ import annotations

import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from cad.combustion_chamber import run as run_chamber
from cad.cooling_jacket import run as run_cooling
from cad.display_geometry import EXPORT_DIR, SAFETY_NOTICE, write_revolved_profile_stl, write_step_manifest, write_svg
from cad.injector_plate import run as run_injector
from cad.nozzle_assembly import run as run_nozzle


def assembly_profile_mm() -> list[tuple[float, float]]:
    """Return a solid exterior assembly profile.

    Returns:
        Display x and radius pairs in millimeters.
    """

    return [
        (0.0, 26.0),
        (8.0, 26.0),
        (12.0, 18.0),
        (92.0, 18.0),
        (102.0, 14.0),
        (114.0, 10.0),
        (132.0, 13.0),
        (156.0, 18.0),
        (170.0, 22.0),
    ]


def run() -> dict[str, Path]:
    """Generate full display assembly artifacts.

    Returns:
        Mapping of artifact names to generated paths.
    """

    run_chamber()
    run_nozzle()
    run_injector()
    run_cooling()

    stl_path = EXPORT_DIR / "thrust_chamber.stl"
    step_path = EXPORT_DIR / "thrust_chamber.step"
    full_stl_path = EXPORT_DIR / "thrust_chamber_full.stl"
    full_step_path = EXPORT_DIR / "thrust_chamber_full.step"
    svg_path = EXPORT_DIR / "engine_assembly_display.svg"

    write_revolved_profile_stl(stl_path, "thrust_chamber_display", assembly_profile_mm())
    write_revolved_profile_stl(full_stl_path, "thrust_chamber_full_display", assembly_profile_mm())
    write_step_manifest(
        step_path,
        "thrust_chamber_display",
        "Full solid display assembly. No internal passages, injector features, or pressure-rated geometry.",
    )
    write_step_manifest(
        full_step_path,
        "thrust_chamber_full_display",
        "Alias of display assembly manifest for requested file naming compatibility.",
    )

    body = [
        '<text class="title" x="24" y="30">ROCKET M1- MK0 Display Assembly</text>',
        '<text x="24" y="52">Solid exterior display model, no operational interfaces</text>',
        '<path d="M 70 140 L 104 104 L 430 104 C 488 112, 548 88, 670 70 L 670 210 C 548 192, 488 168, 430 176 L 104 176 Z" fill="#dce8f2" stroke="#31556f" stroke-width="2"/>',
        '<line x1="104" y1="92" x2="104" y2="188" stroke="#31556f" stroke-width="2"/>',
        '<line x1="430" y1="96" x2="430" y2="184" stroke="#31556f" stroke-width="2"/>',
        '<text x="78" y="228">Injector display</text>',
        '<text x="236" y="94">Chamber display</text>',
        '<text x="520" y="70">Nozzle display</text>',
        f'<text x="24" y="292">{SAFETY_NOTICE}</text>',
    ]
    write_svg(svg_path, 740, 325, body)

    return {
        "step": step_path,
        "stl": stl_path,
        "full_step": full_step_path,
        "full_stl": full_stl_path,
        "svg": svg_path,
    }


if __name__ == "__main__":
    artifacts = run()
    for artifact_name, artifact_path in artifacts.items():
        print(f"{artifact_name}: {artifact_path}")
