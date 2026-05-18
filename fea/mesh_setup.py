"""Generate a non-operational FEA training deck.

The deck is a tiny educational mesh with no pressure loads or material
allowables for real hardware. It exists to demonstrate file generation and CI.
"""

from __future__ import annotations

from pathlib import Path


PROJECT_ROOT = Path(__file__).resolve().parents[1]
FEA_DIR = PROJECT_ROOT / "fea"
SAFETY_NOTICE = "EDUCATIONAL TRAINING DECK ONLY - NOT VALID FOR STRUCTURAL QUALIFICATION."


def generate_training_bdf() -> str:
    """Create a minimal Nastran-style training deck.

    Returns:
        BDF text content.
    """

    return f"""$ ROCKET M1- MK0
$ {SAFETY_NOTICE}
$ Operational pressure loads, thermal loads, real material data, and safety
$ factors are intentionally omitted.
SOL 101
CEND
TITLE = ROCKET M1- MK0 DISPLAY MODEL TRAINING MESH
SUBCASE 1
  SPC = 1
BEGIN BULK
PARAM,POST,-1
MAT1,1,1.0,0.30,0.30
PSHELL,1,1,1.0
GRID,1,,0.0,0.0,0.0
GRID,2,,1.0,0.0,0.0
GRID,3,,1.0,1.0,0.0
GRID,4,,0.0,1.0,0.0
CQUAD4,1,1,1,2,3,4
SPC1,1,123456,1
ENDDATA
"""


def run() -> dict[str, Path]:
    """Write the training BDF file.

    Returns:
        Mapping of artifact names to generated paths.
    """

    FEA_DIR.mkdir(parents=True, exist_ok=True)
    bdf_path = FEA_DIR / "engine_structure.bdf"
    bdf_path.write_text(generate_training_bdf(), encoding="utf-8")
    return {"bdf": bdf_path}


if __name__ == "__main__":
    artifacts = run()
    for artifact_name, artifact_path in artifacts.items():
        print(f"{artifact_name}: {artifact_path}")
