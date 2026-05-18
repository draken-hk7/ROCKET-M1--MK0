"""Generate ESP32 avionics wiring diagram."""

from __future__ import annotations

import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from utils.nature_geometry import phyllotaxis_pattern

ELECTRONICS_DIR = PROJECT_ROOT / "electronics"


def run() -> dict[str, Path]:
    """Generate wiring diagram SVG and PNG."""

    import matplotlib.pyplot as plt
    from matplotlib.patches import FancyArrowPatch, Rectangle

    ELECTRONICS_DIR.mkdir(parents=True, exist_ok=True)
    peripherals = ["BMP390", "ICM-42688", "GPS M9N", "RFM96W", "SD Card", "Battery", "Arm Switch", "LED"]
    points = phyllotaxis_pattern(len(peripherals), 1.1)
    fig, ax = plt.subplots(figsize=(9, 7))
    ax.add_patch(Rectangle((-0.45, -0.25), 0.9, 0.5, facecolor="#e5eef6", edgecolor="#31556f", linewidth=2))
    ax.text(0, 0, "ESP32", ha="center", va="center", fontsize=13, weight="bold")
    colors = ["blue", "yellow", "green", "yellow", "yellow", "red", "black", "purple"]
    for label, (x, y), color in zip(peripherals, points, colors):
        ax.add_patch(Rectangle((x - 0.34, y - 0.16), 0.68, 0.32, facecolor="#ffffff", edgecolor="#31556f"))
        ax.text(x, y, label, ha="center", va="center", fontsize=9)
        ax.add_patch(FancyArrowPatch((0.45 if x > 0 else -0.45, 0), (x - 0.34 if x > 0 else x + 0.34, y), arrowstyle="-", color=color, linewidth=2))
    ax.set_title("ROCKET M1-MK0 Fibonacci Avionics Wiring")
    ax.set_aspect("equal")
    ax.axis("off")
    svg_path = ELECTRONICS_DIR / "wiring_diagram.svg"
    png_path = ELECTRONICS_DIR / "wiring_diagram.png"
    fig.savefig(svg_path, bbox_inches="tight")
    fig.savefig(png_path, dpi=180, bbox_inches="tight")
    plt.close(fig)
    print(f"Saved: {svg_path}")
    print(f"Saved: {png_path}")
    return {"svg": svg_path, "png": png_path}


if __name__ == "__main__":
    run()
