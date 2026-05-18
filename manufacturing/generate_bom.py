"""Generate a display-model bill of materials."""

from __future__ import annotations

import csv
import json
from dataclasses import asdict, dataclass
from pathlib import Path


PROJECT_ROOT = Path(__file__).resolve().parents[1]
MANUFACTURING_DIR = PROJECT_ROOT / "manufacturing"
SAFETY_NOTICE = "BOM is for non-pressure display and documentation artifacts only."


@dataclass(frozen=True)
class BomItem:
    """Bill-of-materials item.

    Attributes:
        part_name: Part name.
        part_number: Project part number.
        quantity: Quantity per display assembly.
        material: Non-flight material.
        stock_size: Suggested display stock size.
        process: Display-model process.
        supplier_options: Supplier examples.
        estimated_cost_usd: Estimated display-model cost in USD.
        estimated_cost_inr: Estimated display-model cost in INR.
        lead_time_days: Estimated lead time in days.
        note: Safety note.
    """

    part_name: str
    part_number: str
    quantity: int
    material: str
    stock_size: str
    process: str
    supplier_options: str
    estimated_cost_usd: float
    estimated_cost_inr: float
    lead_time_days: int
    note: str


def generate_bom() -> list[BomItem]:
    """Generate the display-model BOM.

    Returns:
        List of BOM items.
    """

    return [
        BomItem("Display chamber body", "RM1-DISP-001", 1, "Aluminum or plastic", "round bar display blank", "3D print or visual-turning demo", "local maker shop", 18.0, 1500.0, 7, SAFETY_NOTICE),
        BomItem("Display nozzle body", "RM1-DISP-002", 1, "Aluminum or plastic", "round bar display blank", "3D print or visual-turning demo", "local maker shop", 16.0, 1330.0, 7, SAFETY_NOTICE),
        BomItem("Decorative injector face", "RM1-DISP-003", 1, "Acrylic or aluminum", "flat display plate", "laser marking or engraving", "local maker shop", 10.0, 830.0, 5, SAFETY_NOTICE),
        BomItem("Fastener mockups", "RM1-DISP-004", 8, "Commercial screws", "M3 display screws", "cosmetic assembly only", "McMaster-Carr or local hardware", 6.0, 500.0, 5, SAFETY_NOTICE),
    ]


def run() -> dict[str, Path]:
    """Write BOM JSON and CSV files.

    Returns:
        Mapping of artifact names to generated paths.
    """

    MANUFACTURING_DIR.mkdir(parents=True, exist_ok=True)
    items = generate_bom()
    rows = [asdict(item) for item in items]
    json_path = MANUFACTURING_DIR / "bom.json"
    csv_path = MANUFACTURING_DIR / "bom.csv"
    json_path.write_text(json.dumps({"safety_notice": SAFETY_NOTICE, "items": rows}, indent=2) + "\n", encoding="utf-8")
    with csv_path.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(rows[0].keys()))
        writer.writeheader()
        writer.writerows(rows)
    return {"json": json_path, "csv": csv_path}


if __name__ == "__main__":
    artifacts = run()
    for artifact_name, artifact_path in artifacts.items():
        print(f"{artifact_name}: {artifact_path}")
