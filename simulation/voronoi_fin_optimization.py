"""Voronoi fin lattice mass and stiffness trade study."""

from __future__ import annotations

import sys
from pathlib import Path


PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

OUTPUT_DIR = PROJECT_ROOT / "outputs"


def evaluate_lattice(cell_count: int) -> tuple[float, float]:
    """Estimate mass saving and stiffness retention for a fin lattice.

    Args:
        cell_count: Number of Voronoi cells.

    Returns:
        Tuple of mass saving percent and stiffness retention percent.

    Units:
        Percent values.

    Aerospace Application:
        Rule-of-mixtures screening for fin lightening cutouts.
    """

    if cell_count <= 0:
        raise ValueError("cell_count must be positive for lattice evaluation.")
    void_fraction = min(0.32, 0.08 + 0.0045 * cell_count)
    mass_saving_percent = 100.0 * void_fraction
    stiffness_retention_percent = 100.0 * (1.0 - 0.72 * void_fraction)
    return mass_saving_percent, stiffness_retention_percent


def run() -> Path:
    """Generate Voronoi optimization plot."""

    import matplotlib.pyplot as plt

    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    counts = [8, 13, 21, 34]
    results = [evaluate_lattice(count) for count in counts]
    mass_saving = [item[0] for item in results]
    stiffness = [item[1] for item in results]
    feasible = [(count, ms, sr) for count, ms, sr in zip(counts, mass_saving, stiffness) if sr > 85.0]
    optimal = max(feasible, key=lambda item: item[1])

    fig, ax = plt.subplots(figsize=(7.5, 5.0))
    ax.plot(mass_saving, stiffness, marker="o", color="tab:purple")
    for count, ms, sr in zip(counts, mass_saving, stiffness):
        ax.text(ms + 0.3, sr, f"{count} cells")
    ax.scatter([optimal[1]], [optimal[2]], color="tab:green", s=90, label="selected >85% stiffness")
    ax.axhline(85.0, color="tab:red", linestyle="--", label="minimum stiffness retention")
    ax.set_xlabel("Mass saving (%)")
    ax.set_ylabel("Stiffness retention (%)")
    ax.set_title("Voronoi Fin Optimization")
    ax.grid(True, alpha=0.3)
    ax.legend()
    path = OUTPUT_DIR / "voronoi_fin_optimization.png"
    fig.tight_layout()
    fig.savefig(path, dpi=180)
    plt.close(fig)
    print(f"Saved: {path}")
    return path


if __name__ == "__main__":
    run()
