"""Aerodynamics, stability, trajectory, and OpenRocket export.

This module implements educational Barrowman-style calculations for a
non-propellant research airframe. It does not model motors, thrust, ignition,
combustion, or energetic events.
"""

from __future__ import annotations

import csv
import math
import sys
import xml.etree.ElementTree as ET
from dataclasses import dataclass
from pathlib import Path
from typing import Iterable

PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from config import vehicle_params as vp

OUTPUT_DIR = PROJECT_ROOT / "outputs"
SIM_DIR = PROJECT_ROOT / "simulation"


@dataclass(frozen=True)
class StabilityResult:
    """Static stability result.

    Args:
        cn_alpha_nose: Nose normal force derivative, dimensionless per radian.
        xcp_nose_mm: Nose center of pressure from nose tip in millimeters.
        cn_alpha_fins: Fin normal force derivative, dimensionless per radian.
        xcp_fins_mm: Fin center of pressure from nose tip in millimeters.
        xcp_total_mm: Combined center of pressure from nose tip in millimeters.
        xcm_mm: Center of mass from nose tip in millimeters.
        static_margin_calibers: Static margin in body calibers.
        cd_total: Total drag coefficient.

    Units:
        Lengths in millimeters, coefficients dimensionless.

    Aerospace Application:
        Verifies passive fin stability for a simulation-first airframe.
    """

    cn_alpha_nose: float
    xcp_nose_mm: float
    cn_alpha_fins: float
    xcp_fins_mm: float
    xcp_total_mm: float
    xcm_mm: float
    static_margin_calibers: float
    cd_total: float


@dataclass(frozen=True)
class CoastPoint:
    """Coast trajectory state.

    Args:
        time_s: Simulation time in seconds.
        altitude_m: Altitude above start in meters.
        velocity_ms: Vertical velocity in meters per second.
        mach: Mach number using a 343 m/s sea-level reference.

    Units:
        SI units.

    Aerospace Application:
        Supports simple coast-phase envelope checks without any thrust model.
    """

    time_s: float
    altitude_m: float
    velocity_ms: float
    mach: float


def nose_normal_force() -> tuple[float, float]:
    """Compute nose normal-force derivative and center of pressure.

    Returns:
        Tuple of CN_alpha and XCP in millimeters.

    Units:
        XCP in millimeters from nose tip.

    Aerospace Application:
        Barrowman approximation for ogive/von Karman nose shapes.
    """

    cn_alpha_nose = 2.0
    xcp_nose_mm = 0.466 * vp.NOSE_CONE_LENGTH_MM
    return cn_alpha_nose, xcp_nose_mm


def fin_area_m2(span_mm: float = vp.FIN_SPAN_MM) -> float:
    """Compute trapezoidal fin planform area.

    Args:
        span_mm: Fin span in millimeters.

    Returns:
        Planform area for one fin in square meters.

    Units:
        mm input, m^2 output.

    Aerospace Application:
        Used for normal-force, drag, and root-bending estimates.
    """

    if span_mm <= 0.0:
        raise ValueError("span_mm must be positive for fin area.")
    return 0.5 * (vp.FIN_ROOT_CHORD_MM + vp.FIN_TIP_CHORD_MM) * span_mm * 1e-6


def fin_normal_force(span_mm: float = vp.FIN_SPAN_MM, sweep_angle_deg: float = vp.FIN_SWEEP_ANGLE_DEG) -> tuple[float, float]:
    """Compute fin normal-force derivative and CP station.

    Args:
        span_mm: Fin semi-span in millimeters.
        sweep_angle_deg: Leading-edge sweep angle in degrees.

    Returns:
        Tuple of CN_alpha and XCP in millimeters from nose tip.

    Units:
        Lengths in millimeters, angle in degrees.

    Aerospace Application:
        Educational Barrowman fin model with a sweep effectiveness correction.
    """

    if span_mm <= 0.0:
        raise ValueError("span_mm must be positive for fin normal force.")
    taper_ratio = vp.FIN_TIP_CHORD_MM / vp.FIN_ROOT_CHORD_MM
    root_mm = vp.FIN_ROOT_CHORD_MM
    tip_mm = vp.FIN_TIP_CHORD_MM
    body_diameter_mm = vp.BODY_DIAMETER_MM
    denominator = 1.0 + math.sqrt(1.0 + (2.0 * taper_ratio / (root_mm + tip_mm)) ** 2)
    cn_alpha_raw = 4.0 * vp.FIN_COUNT * (span_mm / body_diameter_mm) ** 2 / denominator
    sweep_factor = math.cos(math.radians(sweep_angle_deg)) ** 2
    cn_alpha_fins = cn_alpha_raw * sweep_factor

    # Mean aerodynamic chord centroid with quarter-chord aerodynamic center.
    tip_le_offset_mm = span_mm * math.tan(math.radians(sweep_angle_deg))
    mac_mm = (2.0 / 3.0) * root_mm * (1.0 + taper_ratio + taper_ratio**2) / (1.0 + taper_ratio)
    mac_le_x_mm = tip_le_offset_mm * (1.0 + 2.0 * taper_ratio) / (3.0 * (1.0 + taper_ratio))
    xcp_from_fin_le_mm = mac_le_x_mm + 0.25 * mac_mm
    xcp_fins_mm = vp.FIN_LEADING_EDGE_X_MM + xcp_from_fin_le_mm
    return cn_alpha_fins, xcp_fins_mm


def center_of_mass_mm() -> float:
    """Compute vehicle center of mass from configured component masses.

    Returns:
        Center of mass in millimeters from the nose tip.

    Units:
        Millimeters.

    Aerospace Application:
        Provides the mass centroid for static margin calculation.
    """

    total_mass_g = sum(component.mass_g for component in vp.COMPONENT_MASSES)
    if total_mass_g <= 0.0:
        raise ValueError("Total vehicle mass must be positive.")
    return sum(component.mass_g * component.centroid_mm for component in vp.COMPONENT_MASSES) / total_mass_g


def drag_coefficient(
    velocity_ms: float = vp.COAST_VELOCITY_MS,
    sweep_angle_deg: float = vp.FIN_SWEEP_ANGLE_DEG,
    span_mm: float = vp.FIN_SPAN_MM,
) -> float:
    """Estimate total drag coefficient.

    Args:
        velocity_ms: Reference velocity in meters per second.
        sweep_angle_deg: Fin leading-edge sweep in degrees.
        span_mm: Fin span in millimeters.

    Returns:
        Estimated drag coefficient.

    Units:
        Velocity in m/s, angle in degrees, span in millimeters.

    Aerospace Application:
        Provides a subsonic external-aero estimate for coast simulation.
    """

    if velocity_ms <= 0.0:
        raise ValueError("velocity_ms must be positive for drag estimation.")
    length_m = vp.BODY_LENGTH_MM / 1000.0
    diameter_m = vp.BODY_DIAMETER_MM / 1000.0
    reynolds = vp.AIR_DENSITY_KG_M3 * velocity_ms * length_m / vp.AIR_DYNAMIC_VISCOSITY_PA_S
    cf = 0.074 / (reynolds**0.2)
    wetted_area_m2 = math.pi * diameter_m * length_m
    cd_body = cf * wetted_area_m2 / vp.REFERENCE_AREA_M2
    cd_base = 0.12
    sweep_drag_factor = 1.0 - 0.18 * math.sin(math.radians(sweep_angle_deg))
    cd_fins = 0.008 * vp.FIN_COUNT * fin_area_m2(span_mm) / vp.REFERENCE_AREA_M2 * sweep_drag_factor
    return cd_body + cd_base + cd_fins


def calculate_stability(span_mm: float = vp.FIN_SPAN_MM, sweep_angle_deg: float = vp.FIN_SWEEP_ANGLE_DEG) -> StabilityResult:
    """Calculate static stability and drag.

    Args:
        span_mm: Fin span in millimeters.
        sweep_angle_deg: Fin sweep in degrees.

    Returns:
        StabilityResult with CP, CM, static margin, and CD.

    Units:
        Millimeters and dimensionless coefficients.

    Aerospace Application:
        Main Barrowman stability check for the educational vehicle.
    """

    cn_alpha_nose, xcp_nose_mm = nose_normal_force()
    cn_alpha_fins, xcp_fins_mm = fin_normal_force(span_mm, sweep_angle_deg)
    xcp_total_mm = (
        cn_alpha_nose * xcp_nose_mm + cn_alpha_fins * xcp_fins_mm
    ) / (cn_alpha_nose + cn_alpha_fins)
    xcm_mm = center_of_mass_mm()
    static_margin = (xcp_total_mm - xcm_mm) / vp.BODY_DIAMETER_MM
    cd_total = drag_coefficient(vp.COAST_VELOCITY_MS, sweep_angle_deg, span_mm)
    return StabilityResult(
        cn_alpha_nose=cn_alpha_nose,
        xcp_nose_mm=xcp_nose_mm,
        cn_alpha_fins=cn_alpha_fins,
        xcp_fins_mm=xcp_fins_mm,
        xcp_total_mm=xcp_total_mm,
        xcm_mm=xcm_mm,
        static_margin_calibers=static_margin,
        cd_total=cd_total,
    )


def simulate_coast(cd_total: float, dt_s: float = 0.01) -> list[CoastPoint]:
    """Integrate coast-phase vertical motion using Euler integration.

    Args:
        cd_total: Drag coefficient.
        dt_s: Time step in seconds.

    Returns:
        List of coast trajectory points.

    Units:
        SI units throughout.

    Aerospace Application:
        Estimates coast altitude after a non-propellant initial velocity state.
    """

    if cd_total <= 0.0 or dt_s <= 0.0:
        raise ValueError("cd_total and dt_s must be positive for coast simulation.")
    mass_kg = vp.MASS_TOTAL_G / 1000.0
    altitude_m = 0.0
    velocity_ms = vp.COAST_VELOCITY_MS
    time_s = 0.0
    points: list[CoastPoint] = []
    for _ in range(6000):
        mach = abs(velocity_ms) / 343.0
        points.append(CoastPoint(time_s, altitude_m, velocity_ms, mach))
        drag_n = 0.5 * vp.AIR_DENSITY_KG_M3 * velocity_ms * abs(velocity_ms) * cd_total * vp.REFERENCE_AREA_M2
        acceleration_ms2 = -vp.GRAVITY_MS2 - drag_n / mass_kg
        velocity_ms += acceleration_ms2 * dt_s
        altitude_m += velocity_ms * dt_s
        time_s += dt_s
        if time_s > 0.2 and altitude_m <= 0.0:
            break
    return points


def write_csv(path: Path, rows: Iterable[dict[str, float]]) -> None:
    """Write trajectory or summary rows to CSV."""

    rows_list = list(rows)
    if not rows_list:
        raise ValueError("CSV rows must not be empty.")
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(rows_list[0].keys()))
        writer.writeheader()
        writer.writerows(rows_list)
    print(f"Saved: {path}")


def _save_plots(result: StabilityResult, trajectory: list[CoastPoint]) -> None:
    """Save aero plots and vector diagrams."""

    import matplotlib.pyplot as plt

    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    times = [point.time_s for point in trajectory]
    altitudes = [point.altitude_m for point in trajectory]
    velocities = [point.velocity_ms for point in trajectory]
    mach = [point.mach for point in trajectory]

    fig, ax = plt.subplots(figsize=(8, 4.5))
    ax.plot(times, altitudes, color="tab:blue")
    ax.set_xlabel("Time (s)")
    ax.set_ylabel("Altitude (m)")
    ax.set_title("Coast Altitude vs Time")
    ax.grid(True, alpha=0.3)
    path = OUTPUT_DIR / "altitude_vs_time.png"
    fig.tight_layout()
    fig.savefig(path, dpi=180)
    plt.close(fig)
    print(f"Saved: {path}")

    fig, ax1 = plt.subplots(figsize=(8, 4.5))
    ax1.plot(times, velocities, color="tab:orange", label="Velocity")
    ax1.set_xlabel("Time (s)")
    ax1.set_ylabel("Velocity (m/s)")
    ax2 = ax1.twinx()
    ax2.plot(times, mach, color="tab:green", label="Mach")
    ax2.set_ylabel("Mach")
    ax1.set_title("Velocity and Mach vs Time")
    ax1.grid(True, alpha=0.3)
    path = OUTPUT_DIR / "velocity_vs_mach.png"
    fig.tight_layout()
    fig.savefig(path, dpi=180)
    plt.close(fig)
    print(f"Saved: {path}")

    fig, ax = plt.subplots(figsize=(10, 2.5))
    ax.plot([0.0, vp.BODY_LENGTH_MM], [0.0, 0.0], color="black", linewidth=4)
    ax.scatter([result.xcm_mm], [0.0], color="tab:blue", s=90, label="XCM")
    ax.scatter([result.xcp_total_mm], [0.0], color="tab:red", s=90, label="XCP")
    ax.text(result.xcm_mm, 9.0, "CM", ha="center")
    ax.text(result.xcp_total_mm, 9.0, "CP", ha="center")
    ax.set_ylim(-20.0, 35.0)
    ax.set_xlabel("Station from nose tip (mm)")
    ax.set_yticks([])
    ax.set_title(f"Static Margin: {result.static_margin_calibers:.2f} calibers")
    ax.legend(loc="upper right")
    path = OUTPUT_DIR / "static_margin_diagram.png"
    fig.tight_layout()
    fig.savefig(path, dpi=180)
    plt.close(fig)
    print(f"Saved: {path}")

    write_cp_cm_svg(OUTPUT_DIR / "cp_cm_diagram.svg", result)


def write_cp_cm_svg(path: Path, result: StabilityResult) -> None:
    """Write clean vector CP/CM diagram."""

    width = 980
    height = 190
    margin = 52
    scale = (width - 2 * margin) / vp.BODY_LENGTH_MM

    def sx(station_mm: float) -> float:
        return margin + station_mm * scale

    body_y = 96
    nose = f"M {sx(0):.1f} {body_y:.1f} C {sx(45):.1f} 42, {sx(vp.NOSE_CONE_LENGTH_MM - 40):.1f} 42, {sx(vp.NOSE_CONE_LENGTH_MM):.1f} {body_y - 38:.1f}"
    body = (
        f"L {sx(vp.BODY_LENGTH_MM):.1f} {body_y - 38:.1f} "
        f"L {sx(vp.BODY_LENGTH_MM):.1f} {body_y + 38:.1f} "
        f"L {sx(vp.NOSE_CONE_LENGTH_MM):.1f} {body_y + 38:.1f} "
        f"C {sx(vp.NOSE_CONE_LENGTH_MM - 40):.1f} 150, {sx(45):.1f} 150, "
        f"{sx(0):.1f} {body_y:.1f} Z"
    )
    svg = f"""<svg xmlns="http://www.w3.org/2000/svg" width="{width}" height="{height}" viewBox="0 0 {width} {height}">
<style>text{{font-family:Arial,sans-serif;fill:#1f2933;font-size:13px}}.title{{font-size:18px;font-weight:700}}</style>
<rect width="100%" height="100%" fill="#fbfcfd"/>
<text class="title" x="24" y="30">ROCKET M1-MK0 CP / CM Diagram</text>
<path d="{nose} {body}" fill="#e5eef6" stroke="#31556f" stroke-width="2"/>
<line x1="{sx(result.xcm_mm):.1f}" y1="48" x2="{sx(result.xcm_mm):.1f}" y2="152" stroke="#2563eb" stroke-width="3"/>
<line x1="{sx(result.xcp_total_mm):.1f}" y1="48" x2="{sx(result.xcp_total_mm):.1f}" y2="152" stroke="#dc2626" stroke-width="3"/>
<text x="{sx(result.xcm_mm):.1f}" y="44" text-anchor="middle">CM {result.xcm_mm:.0f} mm</text>
<text x="{sx(result.xcp_total_mm):.1f}" y="170" text-anchor="middle">CP {result.xcp_total_mm:.0f} mm</text>
<text x="24" y="176">Static margin {result.static_margin_calibers:.2f} calibers. Non-propellant educational simulation.</text>
</svg>
"""
    path.write_text(svg, encoding="utf-8")
    print(f"Saved: {path}")


def export_openrocket(path: Path, result: StabilityResult) -> None:
    """Export a compact OpenRocket-compatible XML file."""

    rocket = ET.Element("openrocket", attrib={"version": "23.09"})
    document = ET.SubElement(rocket, "rocket")
    ET.SubElement(document, "name").text = "ROCKET M1-MK0"
    ET.SubElement(document, "designer").text = "Codex educational simulation"
    stage = ET.SubElement(document, "subcomponents")
    nose = ET.SubElement(stage, "nosecone")
    ET.SubElement(nose, "name").text = "Von Karman nose cone"
    ET.SubElement(nose, "length").text = f"{vp.NOSE_CONE_LENGTH_MM / 1000.0:.6f}"
    ET.SubElement(nose, "aftradius").text = f"{vp.BODY_DIAMETER_MM / 2000.0:.6f}"
    ET.SubElement(nose, "shape").text = vp.NOSE_CONE_TYPE
    body = ET.SubElement(stage, "bodytube")
    ET.SubElement(body, "name").text = "76 mm carbon/fiberglass body"
    ET.SubElement(body, "length").text = f"{(vp.BODY_LENGTH_MM - vp.NOSE_CONE_LENGTH_MM) / 1000.0:.6f}"
    ET.SubElement(body, "radius").text = f"{vp.BODY_DIAMETER_MM / 2000.0:.6f}"
    fins = ET.SubElement(stage, "trapezoidfinset")
    ET.SubElement(fins, "name").text = "Fibonacci sweep fin set"
    ET.SubElement(fins, "fincount").text = str(vp.FIN_COUNT)
    ET.SubElement(fins, "rootchord").text = f"{vp.FIN_ROOT_CHORD_MM / 1000.0:.6f}"
    ET.SubElement(fins, "tipchord").text = f"{vp.FIN_TIP_CHORD_MM / 1000.0:.6f}"
    ET.SubElement(fins, "height").text = f"{vp.FIN_SPAN_MM / 1000.0:.6f}"
    ET.SubElement(fins, "sweeplength").text = f"{vp.FIN_SPAN_MM * math.tan(math.radians(vp.FIN_SWEEP_ANGLE_DEG)) / 1000.0:.6f}"
    ET.SubElement(fins, "thickness").text = f"{vp.FIN_THICKNESS_MM / 1000.0:.6f}"
    analysis = ET.SubElement(document, "analysis")
    ET.SubElement(analysis, "centerOfMass").text = f"{result.xcm_mm / 1000.0:.6f}"
    ET.SubElement(analysis, "centerOfPressure").text = f"{result.xcp_total_mm / 1000.0:.6f}"
    ET.SubElement(analysis, "staticMarginCalibers").text = f"{result.static_margin_calibers:.4f}"
    tree = ET.ElementTree(rocket)
    path.parent.mkdir(parents=True, exist_ok=True)
    ET.indent(tree, space="  ")
    tree.write(path, encoding="utf-8", xml_declaration=True)
    print(f"Saved: {path}")


def run() -> StabilityResult:
    """Run the full aerodynamic analysis workflow."""

    vp.validate_vehicle_parameters()
    result = calculate_stability()
    print(f"Static Margin: {result.static_margin_calibers:.2f} calibers")
    if result.static_margin_calibers < 1.0:
        raise AssertionError("UNSTABLE - increase fin span or move mass forward")
    if result.static_margin_calibers > 4.0:
        print("Warning: Over-stable - may weathercock in crosswind")

    trajectory = simulate_coast(result.cd_total)
    write_csv(
        OUTPUT_DIR / "coast_trajectory.csv",
        [
            {
                "time_s": point.time_s,
                "altitude_m": point.altitude_m,
                "velocity_ms": point.velocity_ms,
                "mach": point.mach,
            }
            for point in trajectory
        ],
    )
    write_csv(
        OUTPUT_DIR / "aerodynamics_summary.csv",
        [
            {
                "xcp_total_mm": result.xcp_total_mm,
                "xcm_mm": result.xcm_mm,
                "static_margin_calibers": result.static_margin_calibers,
                "cd_total": result.cd_total,
                "apogee_m": max(point.altitude_m for point in trajectory),
            }
        ],
    )
    _save_plots(result, trajectory)
    export_openrocket(SIM_DIR / "ROCKET_M1_MK0.ork", result)
    return result


if __name__ == "__main__":
    run()
