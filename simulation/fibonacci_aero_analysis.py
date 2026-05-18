"""Fibonacci geometry comparison for airframe aerodynamics."""

from __future__ import annotations

import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from config import vehicle_params as vp
from simulation.aerodynamics import calculate_stability, drag_coefficient

OUTPUT_DIR = PROJECT_ROOT / "outputs"


def run() -> Path:
    """Generate Fibonacci aero comparison plot.

    Returns:
        Path to generated PNG.

    Units:
        Angles in degrees, span in millimeters.

    Aerospace Application:
        Compares sweep and span choices for passive stability and drag.
    """

    import matplotlib.pyplot as plt

    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    sweep_values_deg = [0.0, 21.0, vp.FIN_SWEEP_ANGLE_DEG, 45.0]
    cd_values = [drag_coefficient(vp.COAST_VELOCITY_MS, sweep) for sweep in sweep_values_deg]
    span_values_mm = [55.0, 89.0, 144.0]
    sm_values = [calculate_stability(span_mm=span).static_margin_calibers for span in span_values_mm]

    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(12, 4.8))
    ax1.plot(sweep_values_deg, cd_values, marker="o", color="tab:blue")
    ax1.axvline(vp.FIN_SWEEP_ANGLE_DEG, color="tab:green", linestyle="--", label="phi x 21 deg")
    ax1.set_xlabel("Fin sweep angle (deg)")
    ax1.set_ylabel("Estimated CD")
    ax1.set_title("Drag vs Fibonacci Sweep")
    ax1.grid(True, alpha=0.3)
    ax1.legend()

    ax2.plot(span_values_mm, sm_values, marker="s", color="tab:orange")
    ax2.axhline(1.0, color="tab:red", linestyle="--", label="minimum stable")
    ax2.set_xlabel("Fin span (mm)")
    ax2.set_ylabel("Static margin (calibers)")
    ax2.set_title("Static Margin vs Fibonacci Span")
    ax2.grid(True, alpha=0.3)
    ax2.legend()

    fig.tight_layout()
    path = OUTPUT_DIR / "fibonacci_aero_comparison.png"
    fig.savefig(path, dpi=180)
    plt.close(fig)
    print(f"Saved: {path}")
    return path


if __name__ == "__main__":
    run()
