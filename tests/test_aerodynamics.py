"""Tests for ROCKET M1-MK0 aerodynamics."""

from __future__ import annotations

from config.vehicle_params import FIN_ROOT_CHORD_MM, FIN_SPAN_MM, FIN_SWEEP_ANGLE_DEG
from simulation.aerodynamics import calculate_stability
from utils.nature_geometry import golden_ratio, phyllotaxis_pattern


def test_static_margin_positive() -> None:
    """Static margin must be stable."""

    assert calculate_stability().static_margin_calibers > 1.0


def test_static_margin_not_overstable() -> None:
    """Static margin should remain below the educational upper bound."""

    assert calculate_stability().static_margin_calibers < 5.0


def test_cd_reasonable() -> None:
    """Drag coefficient should be in a plausible subsonic range."""

    cd = calculate_stability().cd_total
    assert 0.3 < cd < 0.8


def test_fibonacci_sweep_angle() -> None:
    """Configured sweep should equal 21 degrees times phi."""

    assert abs(FIN_SWEEP_ANGLE_DEG - 21.0 * golden_ratio) < 0.01


def test_golden_ratio_fin_span() -> None:
    """Fin span/root ratio should be golden-ratio adjacent."""

    assert abs(FIN_SPAN_MM / FIN_ROOT_CHORD_MM - 1.0 / golden_ratio) < 0.13


def test_phyllotaxis_point_count() -> None:
    """Parachute vent count uses F(7)=13."""

    assert len(phyllotaxis_pattern(13, 1.0)) == 13
