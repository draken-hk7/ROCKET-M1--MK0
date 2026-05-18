"""Aggregate educational plot generation for ROCKET M1- MK0."""

from __future__ import annotations

from pathlib import Path

try:
    from propulsion.cea_analysis import run as run_cea_proxy
    from propulsion.common import SAFETY_NOTICE, output_path
    from propulsion.nozzle_design import generate_normalized_bell_profile, write_nozzle_svg
except ImportError:  # pragma: no cover
    from cea_analysis import run as run_cea_proxy
    from common import SAFETY_NOTICE, output_path
    from nozzle_design import generate_normalized_bell_profile, write_nozzle_svg


def write_pdf_summary(path: Path) -> None:
    """Write a minimal PDF summary without external dependencies.

    Args:
        path: Destination PDF path.
    """

    path.parent.mkdir(parents=True, exist_ok=True)
    text_lines = [
        "ROCKET M1- MK0 Educational Performance Summary",
        "This PDF contains non-operational proxy results only.",
        "No fabrication, propellant, injector, or hot-fire data is included.",
        SAFETY_NOTICE,
    ]
    content = "BT /F1 14 Tf 72 740 Td " + " Tj 0 -24 Td ".join(
        f"({line.replace('(', '[').replace(')', ']')})" for line in text_lines
    ) + " Tj ET"
    objects = [
        "1 0 obj << /Type /Catalog /Pages 2 0 R >> endobj\n",
        "2 0 obj << /Type /Pages /Kids [3 0 R] /Count 1 >> endobj\n",
        "3 0 obj << /Type /Page /Parent 2 0 R /MediaBox [0 0 612 792] /Resources << /Font << /F1 4 0 R >> >> /Contents 5 0 R >> endobj\n",
        "4 0 obj << /Type /Font /Subtype /Type1 /BaseFont /Helvetica >> endobj\n",
        f"5 0 obj << /Length {len(content.encode('latin-1'))} >> stream\n{content}\nendstream endobj\n",
    ]
    pdf = "%PDF-1.4\n"
    offsets = [0]
    for obj in objects:
        offsets.append(len(pdf.encode("latin-1")))
        pdf += obj
    xref_offset = len(pdf.encode("latin-1"))
    pdf += f"xref\n0 {len(objects) + 1}\n0000000000 65535 f \n"
    for offset in offsets[1:]:
        pdf += f"{offset:010d} 00000 n \n"
    pdf += (
        f"trailer << /Size {len(objects) + 1} /Root 1 0 R >>\n"
        f"startxref\n{xref_offset}\n%%EOF\n"
    )
    path.write_bytes(pdf.encode("latin-1"))


def write_normalized_kn_svg(path: Path) -> None:
    """Write a normalized solid-grain burnback teaching plot.

    Args:
        path: Destination SVG path.
    """

    width = 720
    height = 260
    points = []
    for index in range(41):
        x = index / 40.0
        y = 0.55 + 0.28 * (1.0 - (2.0 * x - 1.0) ** 2)
        px = 48 + x * (width - 96)
        py = height - 48 - y * 150
        points.append(f"{px:.2f},{py:.2f}")
    lines = [
        f'<svg xmlns="http://www.w3.org/2000/svg" width="{width}" height="{height}" viewBox="0 0 {width} {height}">',
        "<style>text{font-family:Arial,sans-serif;fill:#1f2933;font-size:12px}.title{font-size:18px;font-weight:700}</style>",
        '<rect width="100%" height="100%" fill="#fbfcfd"/>',
        '<text class="title" x="24" y="30">Normalized Burnback Teaching Curve</text>',
        '<text x="24" y="50">Shape-only curve, not APCP grain sizing or burn-rate data</text>',
        f'<polyline points="{" ".join(points)}" fill="none" stroke="#31556f" stroke-width="3"/>',
        f'<text x="24" y="{height - 20}">{SAFETY_NOTICE}</text>',
        "</svg>",
    ]
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text("\n".join(lines) + "\n", encoding="utf-8")


def run() -> dict[str, Path]:
    """Generate aggregate educational plots and summary PDF.

    Returns:
        Mapping of artifact names to paths.
    """

    cea_artifacts = run_cea_proxy()
    plots_directory = output_path("plots").parent / "plots"
    plots_directory.mkdir(parents=True, exist_ok=True)
    nozzle_svg = plots_directory / "normalized_nozzle_profile.svg"
    kn_svg = plots_directory / "normalized_burnback_curve.svg"
    pdf_path = Path(__file__).resolve().parents[1] / "docs" / "performance_analysis.pdf"
    write_nozzle_svg(generate_normalized_bell_profile(), nozzle_svg)
    write_normalized_kn_svg(kn_svg)
    write_pdf_summary(pdf_path)
    return {
        "performance_csv": cea_artifacts["csv"],
        "nozzle_svg": nozzle_svg,
        "kn_svg": kn_svg,
        "pdf": pdf_path,
    }


if __name__ == "__main__":
    artifacts = run()
    for artifact_name, artifact_path in artifacts.items():
        print(f"{artifact_name}: {artifact_path}")
