"""Single source of truth for ROCKET M1-MK0 vehicle parameters.

All dimensions are SI-derived and exposed in millimeters for CAD workflows.
The vehicle is a simulation-first, non-propellant educational airframe.
"""

from __future__ import annotations

import math
from dataclasses import dataclass


# Airframe
BODY_DIAMETER_MM: float = 76.0
BODY_LENGTH_MM: float = 1200.0
WALL_THICKNESS_MM: float = 3.0
NOSE_CONE_LENGTH_MM: float = 228.0
NOSE_CONE_TYPE: str = "von_karman"

# Fins
FIN_COUNT: int = 3
FIN_ROOT_CHORD_MM: float = 120.0
FIN_TIP_CHORD_MM: float = 60.0
FIN_SPAN_MM: float = 89.0
FIN_SWEEP_ANGLE_DEG: float = 33.98
FIN_THICKNESS_MM: float = 4.0
FIN_MATERIAL: str = "G10 fiberglass"

# Masses
MASS_AIRFRAME_G: float = 320.0
MASS_AVIONICS_G: float = 180.0
MASS_NOSE_CONE_G: float = 95.0
MASS_RECOVERY_G: float = 210.0
MASS_PAYLOAD_G: float = 150.0
MASS_TOTAL_G: float = 955.0

# Flight performance simulation targets
TARGET_ALTITUDE_M: float = 300.0
COAST_VELOCITY_MS: float = 85.0
DRAG_COEFFICIENT_CD: float = 0.45

# Derived geometry and simulation constants
AVIONICS_BAY_LENGTH_MM: float = 144.0
PARACHUTE_BAY_LENGTH_MM: float = 200.0
FIN_BOLT_COUNT: int = 8
PARACHUTE_VENT_COUNT: int = 13
RAIL_BUTTON_POSITIONS_MM: tuple[float, float, float, float] = (21.0, 34.0, 55.0, 89.0)
BODY_RADIUS_MM: float = BODY_DIAMETER_MM / 2.0
INNER_DIAMETER_MM: float = BODY_DIAMETER_MM - 2.0 * WALL_THICKNESS_MM
REFERENCE_AREA_M2: float = math.pi * (BODY_DIAMETER_MM / 1000.0) ** 2 / 4.0
AIR_DENSITY_KG_M3: float = 1.225
AIR_DYNAMIC_VISCOSITY_PA_S: float = 1.81e-5
AIR_KINEMATIC_VISCOSITY_M2_S: float = 1.5e-5
GRAVITY_MS2: float = 9.80665

# Component centroid stations measured from the nose tip, in millimeters.
NOSE_CG_MM: float = 0.55 * NOSE_CONE_LENGTH_MM
AVIONICS_CG_MM: float = NOSE_CONE_LENGTH_MM + 0.5 * AVIONICS_BAY_LENGTH_MM
PAYLOAD_CG_MM: float = NOSE_CONE_LENGTH_MM + AVIONICS_BAY_LENGTH_MM + 75.0
RECOVERY_CG_MM: float = NOSE_CONE_LENGTH_MM + AVIONICS_BAY_LENGTH_MM + 0.5 * PARACHUTE_BAY_LENGTH_MM
AIRFRAME_CG_MM: float = BODY_LENGTH_MM * 0.55
FIN_LEADING_EDGE_X_MM: float = BODY_LENGTH_MM - FIN_ROOT_CHORD_MM - 30.0

# Material allowables used for educational structural estimates.
G10_ALLOWABLE_TENSILE_PA: float = 207e6
CARBON_FIBER_E_PA: float = 70e9
CARBON_FIBER_DENSITY_KG_M3: float = 1600.0
G10_DENSITY_KG_M3: float = 1850.0

# Fit policy for non-pressure educational CAD.
CLEARANCE_FIT_MM: float = 0.2
INTERFERENCE_FIT_MM: float = -0.05


@dataclass(frozen=True)
class ComponentMass:
    """Mass item with longitudinal centroid.

    Args:
        name: Component name.
        mass_g: Component mass in grams.
        centroid_mm: Centroid station from nose tip in millimeters.

    Units:
        mass_g in grams, centroid_mm in millimeters.

    Aerospace Application:
        Used by Barrowman stability analysis to estimate center of mass.
    """

    name: str
    mass_g: float
    centroid_mm: float


COMPONENT_MASSES: tuple[ComponentMass, ...] = (
    ComponentMass("nose_cone", MASS_NOSE_CONE_G, NOSE_CG_MM),
    ComponentMass("avionics", MASS_AVIONICS_G, AVIONICS_CG_MM),
    ComponentMass("recovery", MASS_RECOVERY_G, RECOVERY_CG_MM),
    ComponentMass("payload", MASS_PAYLOAD_G, PAYLOAD_CG_MM),
    ComponentMass("airframe", MASS_AIRFRAME_G, AIRFRAME_CG_MM),
)


FIBONACCI_DESIGN_NOTES: tuple[str, ...] = (
    "Body L/D ratio = 1200/76 = 15.8, between F(7)=13 and F(8)=21.",
    "Nose cone L/D ratio = 3.0 for von Karman profile.",
    "Fin span/root ratio = 89/144 = 0.618, approximately 1/phi.",
    "Fin can bolt count = 8 = F(6).",
    "Avionics bay length = 144 mm = F(12).",
    "Parachute vent count = 13 = F(7).",
)


def validate_vehicle_parameters() -> None:
    """Validate key configuration values.

    Raises:
        ValueError: If a parameter would make the simulation inconsistent.

    Units:
        Dimension checks use millimeters and grams.

    Aerospace Application:
        Guards CAD and stability scripts from silently using impossible
        vehicle geometry.
    """

    if BODY_DIAMETER_MM <= 0.0 or BODY_LENGTH_MM <= BODY_DIAMETER_MM:
        raise ValueError("Airframe dimensions must define a slender positive vehicle.")
    if FIN_COUNT < 3:
        raise ValueError("FIN_COUNT must be at least 3 for passive stability.")
    if FIN_SPAN_MM <= 0.0 or FIN_ROOT_CHORD_MM <= FIN_TIP_CHORD_MM:
        raise ValueError("Fin geometry must use positive span and tapered chord.")
    summed_mass_g = sum(component.mass_g for component in COMPONENT_MASSES)
    if abs(summed_mass_g - MASS_TOTAL_G) > 1e-6:
        raise ValueError("MASS_TOTAL_G must equal the component mass sum.")


if __name__ == "__main__":
    validate_vehicle_parameters()
    for note in FIBONACCI_DESIGN_NOTES:
        print(note)
