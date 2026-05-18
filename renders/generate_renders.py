"""Generate ROCKET M1-MK0 visual reference renders."""

from __future__ import annotations

import math
import shutil
import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from config import vehicle_params as vp
from simulation.aerodynamics import calculate_stability
from utils.nature_geometry import logarithmic_spiral, phyllotaxis_pattern, voronoi_lattice

RENDER_DIR = PROJECT_ROOT / "renders"


def run() -> dict[str, Path]:
    """Generate all render assets."""

    import matplotlib.pyplot as plt

    RENDER_DIR.mkdir(parents=True, exist_ok=True)
    result = calculate_stability()

    side_svg = RENDER_DIR / "rocket_side_profile.svg"
    width = 1100
    height = 260
    margin = 44
    scale = (width - 2 * margin) / vp.BODY_LENGTH_MM

    def sx(x_mm: float) -> float:
        return margin + x_mm * scale

    spiral = logarithmic_spiral(2.0, 0.13, [i * 0.22 for i in range(42)])
    spiral_points = " ".join(f"{sx(58 + x * 7):.1f},{130 - y * 7:.1f}" for x, y in spiral)
    nose_path = (
        f"M {sx(0):.1f} 130 C {sx(70):.1f} 72, {sx(170):.1f} 72, "
        f"{sx(vp.NOSE_CONE_LENGTH_MM):.1f} 92 L {sx(vp.BODY_LENGTH_MM):.1f} 92 "
        f"L {sx(vp.BODY_LENGTH_MM):.1f} 168 L {sx(vp.NOSE_CONE_LENGTH_MM):.1f} 168 "
        f"C {sx(170):.1f} 188, {sx(70):.1f} 188, {sx(0):.1f} 130 Z"
    )
    fin_tip_le_mm = vp.FIN_LEADING_EDGE_X_MM + vp.FIN_SPAN_MM * math.tan(math.radians(vp.FIN_SWEEP_ANGLE_DEG))
    fin_points = " ".join(
        [
            f"{sx(vp.FIN_LEADING_EDGE_X_MM):.1f},168",
            f"{sx(vp.FIN_LEADING_EDGE_X_MM + vp.FIN_ROOT_CHORD_MM):.1f},168",
            f"{sx(fin_tip_le_mm + vp.FIN_TIP_CHORD_MM):.1f},235",
            f"{sx(fin_tip_le_mm):.1f},235",
        ]
    )
    cm_line = (
        f'<line x1="{sx(result.xcm_mm):.1f}" y1="65" x2="{sx(result.xcm_mm):.1f}" y2="190" '
        'stroke="#2563eb" stroke-width="3"/>'
    )
    cp_line = (
        f'<line x1="{sx(result.xcp_total_mm):.1f}" y1="65" x2="{sx(result.xcp_total_mm):.1f}" y2="190" '
        'stroke="#dc2626" stroke-width="3"/>'
    )
    side_svg.write_text(
        f"""<svg xmlns="http://www.w3.org/2000/svg" width="{width}" height="{height}" viewBox="0 0 {width} {height}">
<style>text{{font-family:Arial,sans-serif;fill:#1f2933;font-size:13px}}.title{{font-size:20px;font-weight:700}}</style>
<rect width="100%" height="100%" fill="#fbfcfd"/>
<text class="title" x="24" y="34">ROCKET M1-MK0 Side Profile</text>
<path d="{nose_path}" fill="#e5eef6" stroke="#31556f" stroke-width="2"/>
<polygon points="{fin_points}" fill="#cfe0ef" stroke="#31556f" stroke-width="2"/>
<polyline points="{spiral_points}" fill="none" stroke="#22a06b" stroke-width="2"/>
{cm_line}<text x="{sx(result.xcm_mm):.1f}" y="60" text-anchor="middle">CG</text>
{cp_line}<text x="{sx(result.xcp_total_mm):.1f}" y="210" text-anchor="middle">CP</text>
<text x="650" y="52">Fin sweep {vp.FIN_SWEEP_ANGLE_DEG:.2f} deg</text>
<text x="24" y="244">Golden-ratio proportions annotated for educational CAD and simulation.</text>
</svg>
""",
        encoding="utf-8",
    )
    print(f"Saved: {side_svg}")

    fig, ax = plt.subplots(figsize=(10, 4))
    ax.plot([0, vp.BODY_LENGTH_MM], [0, 0], linewidth=10, color="#31556f")
    ax.scatter([p[0] * 25 + 120 for p in phyllotaxis_pattern(13, 2.0)], [p[1] * 25 for p in phyllotaxis_pattern(13, 2.0)], color="#22a06b", label="phyllotaxis")
    for (x1, y1), (x2, y2) in voronoi_lattice(120, 89, 21):
        ax.plot([vp.FIN_LEADING_EDGE_X_MM + x1, vp.FIN_LEADING_EDGE_X_MM + x2], [-70 - y1 * 0.45, -70 - y2 * 0.45], color="#8a5cf6", linewidth=1)
    ax.text(90, 40, "golden spiral nose")
    ax.text(vp.FIN_LEADING_EDGE_X_MM, -135, "Voronoi fin lattice")
    ax.set_title("Fibonacci Anatomy")
    ax.set_aspect("equal", adjustable="box")
    ax.axis("off")
    anatomy = RENDER_DIR / "fibonacci_anatomy.png"
    fig.savefig(anatomy, dpi=180, bbox_inches="tight")
    plt.close(fig)
    print(f"Saved: {anatomy}")

    fin_detail = RENDER_DIR / "fin_voronoi_detail.svg"
    source_fin_svg = PROJECT_ROOT / "cad" / "exports" / "fin_voronoi_pattern.svg"
    if source_fin_svg.exists():
        shutil.copyfile(source_fin_svg, fin_detail)
    else:
        fin_detail.write_text("<svg xmlns=\"http://www.w3.org/2000/svg\"/>", encoding="utf-8")
    print(f"Saved: {fin_detail}")

    from utils.nature_geometry import _save_demo_plot

    reference = RENDER_DIR / "nature_geometry_reference.png"
    _save_demo_plot(reference)
    return {
        "side_svg": side_svg,
        "anatomy_png": anatomy,
        "fin_detail_svg": fin_detail,
        "nature_reference_png": reference,
    }


if __name__ == "__main__":
    run()
