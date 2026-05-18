"""Educational structural analysis for the ROCKET M1-MK0 airframe."""

from __future__ import annotations

import math
import sys
from dataclasses import dataclass
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from config import vehicle_params as vp
from simulation.aerodynamics import fin_area_m2, fin_normal_force

OUTPUT_DIR = PROJECT_ROOT / "outputs"
FEA_DIR = PROJECT_ROOT / "fea"


@dataclass(frozen=True)
class StructuralResult:
    """Structural calculation output.

    Args:
        max_q_pa: Maximum dynamic pressure in pascals.
        fin_bending_stress_pa: Estimated fin-root bending stress in pascals.
        fin_safety_factor: G10 tensile allowable divided by bending stress.
        hoop_stress_pa: Educational ejection-event hoop stress in pascals.
        impact_force_n: Landing impact force in newtons.
        first_bending_mode_hz: Approximate first bending frequency in hertz.

    Units:
        SI units.

    Aerospace Application:
        Summarizes non-flight-qualification structural estimates.
    """

    max_q_pa: float
    fin_bending_stress_pa: float
    fin_safety_factor: float
    hoop_stress_pa: float
    impact_force_n: float
    first_bending_mode_hz: float


def calculate_structural_response() -> StructuralResult:
    """Compute educational structural estimates.

    Returns:
        StructuralResult with stresses and safety factors.

    Units:
        SI units.

    Aerospace Application:
        Provides FEA pre-sizing values for a non-propellant simulation vehicle.
    """

    max_q_pa = 0.5 * vp.AIR_DENSITY_KG_M3 * vp.COAST_VELOCITY_MS**2
    cn_alpha_all_fins, xcp_fins_mm = fin_normal_force()
    cn_alpha_fin_single = cn_alpha_all_fins / vp.FIN_COUNT
    area_m2 = fin_area_m2()
    xcp_fin_from_root_m = max(0.01, (xcp_fins_mm - vp.FIN_LEADING_EDGE_X_MM) / 1000.0)
    bending_moment_nm = max_q_pa * cn_alpha_fin_single * area_m2 * xcp_fin_from_root_m
    chord_m = vp.FIN_ROOT_CHORD_MM / 1000.0
    thickness_m = vp.FIN_THICKNESS_MM / 1000.0
    inertia_m4 = chord_m * thickness_m**3 / 12.0
    c_m = thickness_m / 2.0
    fin_bending_stress_pa = bending_moment_nm * c_m / inertia_m4
    fin_safety_factor = vp.G10_ALLOWABLE_TENSILE_PA / fin_bending_stress_pa

    ejection_pressure_pa = 5.0e5
    radius_m = vp.BODY_DIAMETER_MM / 2000.0
    wall_m = vp.WALL_THICKNESS_MM / 1000.0
    hoop_stress_pa = ejection_pressure_pa * radius_m / wall_m

    mass_kg = vp.MASS_TOTAL_G / 1000.0
    landing_velocity_ms = 5.0
    crush_distance_m = 0.05
    impact_force_n = mass_kg * landing_velocity_ms**2 / (2.0 * crush_distance_m)

    length_m = vp.BODY_LENGTH_MM / 1000.0
    outer_radius_m = vp.BODY_DIAMETER_MM / 2000.0
    inner_radius_m = outer_radius_m - vp.WALL_THICKNESS_MM / 1000.0
    second_moment_m4 = math.pi * (outer_radius_m**4 - inner_radius_m**4) / 4.0
    area_m2 = math.pi * (outer_radius_m**2 - inner_radius_m**2)
    first_bending_mode_hz = (
        1.875**2
        / (2.0 * math.pi * length_m**2)
        * math.sqrt(vp.CARBON_FIBER_E_PA * second_moment_m4 / (vp.CARBON_FIBER_DENSITY_KG_M3 * area_m2))
    )

    return StructuralResult(
        max_q_pa=max_q_pa,
        fin_bending_stress_pa=fin_bending_stress_pa,
        fin_safety_factor=fin_safety_factor,
        hoop_stress_pa=hoop_stress_pa,
        impact_force_n=impact_force_n,
        first_bending_mode_hz=first_bending_mode_hz,
    )


def write_calculix_inp(path: Path) -> None:
    """Write a CalculiX shell-element training model."""

    path.parent.mkdir(parents=True, exist_ok=True)
    content = """*HEADING
ROCKET M1-MK0 EDUCATIONAL AIRFRAME FEA
Simulation-first shell model. No pressure-vessel or energetic-device qualification.
*NODE
1, 0.0, 0.0, 0.0
2, 1.2, 0.0, 0.0
3, 1.2, 0.076, 0.0
4, 0.0, 0.076, 0.0
5, 1.05, 0.076, 0.0
6, 1.17, 0.165, 0.0
7, 1.17, 0.076, 0.004
*ELEMENT, TYPE=S4R, ELSET=BODY_TUBE
1, 1, 2, 3, 4
*ELEMENT, TYPE=S4R, ELSET=FINS
2, 5, 6, 7, 3
*MATERIAL, NAME=G10_FIBERGLASS
*ELASTIC
24000000000., 0.14
*DENSITY
1850.
*MATERIAL, NAME=CARBON_FIBER_TUBE
*ELASTIC
70000000000., 0.30
*DENSITY
1600.
*SHELL SECTION, ELSET=BODY_TUBE, MATERIAL=CARBON_FIBER_TUBE
0.003
*SHELL SECTION, ELSET=FINS, MATERIAL=G10_FIBERGLASS
0.004
*BOUNDARY
1, 1, 6, 0.
4, 1, 6, 0.
*DLOAD
2, P, 4425.
*STEP
*STATIC
*NODE PRINT, NSET=NALL
U
*EL PRINT, ELSET=FINS
S
*END STEP
"""
    path.write_text(content, encoding="utf-8")
    print(f"Saved: {path}")


def write_report(path: Path, result: StructuralResult) -> None:
    """Write structural report text."""

    path.parent.mkdir(parents=True, exist_ok=True)
    content = f"""ROCKET M1-MK0 Structural Analysis Report
========================================

Scope:
  Simulation-first, non-propellant educational airframe estimates.
  FEA/hand-calculation values are not fabrication or flight qualification data.

Fin root bending:
  q = 0.5 * rho * V^2 = {result.max_q_pa:.1f} Pa
  sigma_bending = M*c/I = {result.fin_bending_stress_pa / 1e6:.2f} MPa
  G10 allowable = {vp.G10_ALLOWABLE_TENSILE_PA / 1e6:.1f} MPa
  Safety factor = {result.fin_safety_factor:.2f}

Body tube hoop stress:
  P_ejection = 5.0 bar simulation parameter only - not a fabrication spec
  sigma_hoop = P*r/t = {result.hoop_stress_pa / 1e6:.2f} MPa

Landing impact:
  F = m*v^2/(2*s) = {result.impact_force_n:.1f} N
  Distributed across fin tips and nose for educational load mapping.

Vibration:
  f1 = (1.875^2)/(2*pi*L^2)*sqrt(EI/rhoA)
  First bending mode estimate = {result.first_bending_mode_hz:.1f} Hz
"""
    path.write_text(content, encoding="utf-8")
    print(f"Saved: {path}")


def run() -> StructuralResult:
    """Run structural analysis and write FEA/report outputs."""

    result = calculate_structural_response()
    write_calculix_inp(FEA_DIR / "rocket_airframe.inp")
    write_report(OUTPUT_DIR / "structural_report.txt", result)
    return result


if __name__ == "__main__":
    run()
