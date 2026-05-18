"""Merge structural and electronics BOMs."""

from __future__ import annotations

import csv
from pathlib import Path


PROJECT_ROOT = Path(__file__).resolve().parents[1]
BOM_DIR = PROJECT_ROOT / "bom"
ELECTRONICS_BOM = PROJECT_ROOT / "electronics" / "bom_electronics.csv"


def read_csv(path: Path) -> list[dict[str, str]]:
    """Read CSV rows from a BOM file."""

    with path.open("r", encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle))


def normalize_rows() -> list[dict[str, str]]:
    """Normalize structural and electronics BOM rows."""

    rows: list[dict[str, str]] = []
    for row in read_csv(BOM_DIR / "bom_structural.csv"):
        rows.append(
            {
                "Category": "Structural",
                "Part": row["Part"],
                "Material_or_Package": row["Material"],
                "Description": row["Dimensions_mm"],
                "Qty": row["Qty"],
                "Supplier": row["Supplier"],
                "Price_INR": row["Price_INR"],
            }
        )
    for row in read_csv(ELECTRONICS_BOM):
        rows.append(
            {
                "Category": "Electronics",
                "Part": row["Component"],
                "Material_or_Package": row["Package"],
                "Description": row["Value"],
                "Qty": row["Quantity"],
                "Supplier": row["Supplier"],
                "Price_INR": row["Price_INR"],
            }
        )
    return rows


def run() -> dict[str, Path]:
    """Merge BOMs and write CSV/Markdown outputs."""

    BOM_DIR.mkdir(parents=True, exist_ok=True)
    rows = normalize_rows()
    total = sum(float(row["Price_INR"]) * int(row["Qty"]) for row in rows)
    csv_path = BOM_DIR / "FULL_BOM.csv"
    md_path = BOM_DIR / "FULL_BOM.md"
    with csv_path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(rows[0].keys()))
        writer.writeheader()
        writer.writerows(rows)
    lines = [
        "# ROCKET M1-MK0 Full BOM",
        "",
        "| Category | Part | Material/Package | Description | Qty | Supplier | Price INR |",
        "|---|---|---|---|---:|---|---:|",
    ]
    for row in rows:
        lines.append(
            f"| {row['Category']} | {row['Part']} | {row['Material_or_Package']} | "
            f"{row['Description']} | {row['Qty']} | {row['Supplier']} | {row['Price_INR']} |"
        )
    lines.extend(["", f"Total estimated build cost: INR {total:,.0f}"])
    md_path.write_text("\n".join(lines) + "\n", encoding="utf-8")
    print(f"Total estimated build cost: INR {total:,.0f}")
    print(f"Saved: {csv_path}")
    print(f"Saved: {md_path}")
    return {"csv": csv_path, "md": md_path}


if __name__ == "__main__":
    run()
