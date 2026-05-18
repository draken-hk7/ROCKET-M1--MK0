"""Tests for biomimetic geometry utilities."""

from __future__ import annotations

import math

from utils.nature_geometry import (
    catenary_curve,
    fibonacci_sequence,
    golden_angle_deg,
    golden_ratio,
    phyllotaxis_pattern,
    voronoi_lattice,
)


def test_fibonacci_sequence_correctness() -> None:
    """Verify canonical Fibonacci sequence."""

    assert fibonacci_sequence(8) == [0, 1, 1, 2, 3, 5, 8, 13]


def test_golden_ratio_value() -> None:
    """Verify golden ratio value."""

    assert abs(golden_ratio - 1.6180339887) < 1e-9


def test_golden_angle_value() -> None:
    """Verify golden angle in degrees."""

    assert abs(golden_angle_deg - 137.5077) < 1e-3


def test_phyllotaxis_no_overlap() -> None:
    """Verify phyllotaxis points are separated."""

    points = phyllotaxis_pattern(13, 1.0)
    min_distance = min(
        math.hypot(ax - bx, ay - by)
        for index, (ax, ay) in enumerate(points)
        for bx, by in points[index + 1:]
    )
    assert min_distance > 0.5


def test_voronoi_covers_domain() -> None:
    """Verify Voronoi segments stay inside the requested domain."""

    segments = voronoi_lattice(10.0, 5.0, 13)
    assert segments
    for (x1, y1), (x2, y2) in segments:
        assert 0.0 <= x1 <= 10.0
        assert 0.0 <= x2 <= 10.0
        assert 0.0 <= y1 <= 5.0
        assert 0.0 <= y2 <= 5.0


def test_catenary_symmetry() -> None:
    """Verify catenary symmetry."""

    points = dict(catenary_curve(2.0, [-1.0, 0.0, 1.0]))
    assert abs(points[-1.0] - points[1.0]) < 1e-12
