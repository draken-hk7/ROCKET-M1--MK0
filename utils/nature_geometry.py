"""Biomimetic geometry utilities for ROCKET M1-MK0.

The functions are deterministic and simulation-oriented. They generate
Fibonacci, golden-ratio, Voronoi, catenary, logarithmic spiral, honeycomb, and
dragon-curve patterns used by CAD, electronics layout, renders, and tests.
"""

from __future__ import annotations

import math
import random
from pathlib import Path
from typing import Sequence


Point2D = tuple[float, float]
Segment2D = tuple[Point2D, Point2D]

# Golden ratio constants from the closed-form value phi = (1 + sqrt(5)) / 2.
golden_ratio: float = (1.0 + math.sqrt(5.0)) / 2.0
golden_angle_deg: float = 360.0 / (golden_ratio * golden_ratio)
golden_angle_rad: float = math.radians(golden_angle_deg)

PROJECT_ROOT = Path(__file__).resolve().parents[1]


def fibonacci_sequence(n: int) -> list[int]:
    """Return the first n Fibonacci numbers.

    Args:
        n: Number of Fibonacci terms to return.

    Returns:
        Sequence beginning with 0, 1.

    Units:
        Dimensionless integer sequence.

    Aerospace Application:
        Provides repeatable counts and station choices for vents, fasteners,
        sensors, and bay lengths.
    """

    if n < 0:
        raise ValueError("n must be non-negative for a Fibonacci sequence.")
    values: list[int] = []
    a, b = 0, 1
    for _ in range(n):
        values.append(a)
        a, b = b, a + b
    return values


def fibonacci_spiral_points(n_points: int, scale: float) -> list[Point2D]:
    """Generate points along a Fibonacci spiral.

    Args:
        n_points: Number of points to generate.
        scale: Radial scale factor in arbitrary layout units.

    Returns:
        Cartesian (x, y) points.

    Units:
        Output coordinates use the same arbitrary unit as scale.

    Aerospace Application:
        Used for sensor placement sketches, vent patterns, and visual renders.
    """

    if n_points < 0 or scale <= 0.0:
        raise ValueError("n_points must be non-negative and scale must be positive.")
    points: list[Point2D] = []
    for index in range(n_points):
        theta_rad = index * math.pi / 6.0
        radius = scale * (golden_ratio ** (theta_rad / (math.pi / 2.0))) / golden_ratio
        points.append((radius * math.cos(theta_rad), radius * math.sin(theta_rad)))
    return points


def phyllotaxis_pattern(n_points: int, scale: float) -> list[Point2D]:
    """Generate a sunflower-style phyllotaxis pattern.

    Args:
        n_points: Number of points in the pattern.
        scale: Radial growth scale in arbitrary layout units.

    Returns:
        Cartesian (x, y) points using the golden angle.

    Units:
        Output coordinates use the same arbitrary unit as scale.

    Aerospace Application:
        Used for parachute vent holes, fin-can bolt rings, and PCB placement.
    """

    if n_points < 0 or scale <= 0.0:
        raise ValueError("n_points must be non-negative and scale must be positive.")
    points: list[Point2D] = []
    for index in range(n_points):
        radius = scale * math.sqrt(index + 0.5)
        theta_rad = index * golden_angle_rad
        points.append((radius * math.cos(theta_rad), radius * math.sin(theta_rad)))
    return points


def _clip(value: float, lower: float, upper: float) -> float:
    """Clip a scalar to bounds."""

    return max(lower, min(upper, value))


def voronoi_lattice(width: float, height: float, n_seeds: int, seed: int = 42) -> list[Segment2D]:
    """Generate approximate Voronoi cell boundaries as line segments.

    Args:
        width: Domain width in layout units.
        height: Domain height in layout units.
        n_seeds: Number of Voronoi seeds.
        seed: Deterministic random seed.

    Returns:
        Boundary line segments as ((x1, y1), (x2, y2)).

    Units:
        Output coordinates use the same units as width and height.

    Aerospace Application:
        Creates weight-reduction lattice sketches for fins and nose bulkheads.
    """

    if width <= 0.0 or height <= 0.0 or n_seeds < 2:
        raise ValueError("Voronoi width/height must be positive and n_seeds >= 2.")
    rng = random.Random(seed)
    seeds = [(rng.random() * width, rng.random() * height) for _ in range(n_seeds)]
    segments: list[Segment2D] = []
    for i, seed_a in enumerate(seeds):
        for seed_b in seeds[i + 1:]:
            ax, ay = seed_a
            bx, by = seed_b
            mx, my = (ax + bx) / 2.0, (ay + by) / 2.0
            dx, dy = bx - ax, by - ay
            length = math.hypot(dx, dy)
            if length <= 1e-9:
                continue
            nx, ny = -dy / length, dx / length
            half = 0.16 * min(width, height)
            p1 = (_clip(mx - nx * half, 0.0, width), _clip(my - ny * half, 0.0, height))
            p2 = (_clip(mx + nx * half, 0.0, width), _clip(my + ny * half, 0.0, height))
            if math.hypot(p2[0] - p1[0], p2[1] - p1[1]) > 1e-6:
                segments.append((p1, p2))
    return segments


def catenary_curve(a: float, x_range: Sequence[float]) -> list[Point2D]:
    """Evaluate a catenary curve y = a*cosh(x/a).

    Args:
        a: Catenary scale parameter in layout units.
        x_range: X coordinates in layout units.

    Returns:
        Cartesian (x, y) curve points.

    Units:
        Output coordinates use the same units as a and x_range.

    Aerospace Application:
        Used for nose profile approximations and recovery shroud-line geometry.
    """

    if a <= 0.0:
        raise ValueError("Catenary parameter a must be positive.")
    return [(x, a * math.cosh(x / a)) for x in x_range]


def fibonacci_angle_sweep(base_angle_deg: float) -> float:
    """Scale a fin sweep angle by the golden ratio.

    Args:
        base_angle_deg: Base sweep angle in degrees.

    Returns:
        Golden-ratio-scaled sweep angle in degrees.

    Units:
        Degrees.

    Aerospace Application:
        Defines the canonical leading-edge sweep used by the fin planform.
    """

    if base_angle_deg <= 0.0:
        raise ValueError("base_angle_deg must be positive.")
    return base_angle_deg * golden_ratio


def logarithmic_spiral(a: float, b: float, theta_range: Sequence[float]) -> list[Point2D]:
    """Generate a logarithmic spiral r = a*exp(b*theta).

    Args:
        a: Initial radius in layout units.
        b: Exponential growth coefficient.
        theta_range: Angular stations in radians.

    Returns:
        Cartesian (x, y) points.

    Units:
        Coordinates use the same arbitrary layout unit as a.

    Aerospace Application:
        Used for fin planform sketches, nose rib patterns, and visual renders.
    """

    if a <= 0.0:
        raise ValueError("Logarithmic spiral parameter a must be positive.")
    points: list[Point2D] = []
    for theta_rad in theta_range:
        radius = a * math.exp(b * theta_rad)
        points.append((radius * math.cos(theta_rad), radius * math.sin(theta_rad)))
    return points


def hexagonal_tessellation(rows: int, cols: int, cell_size: float) -> list[Point2D]:
    """Generate honeycomb cell-center coordinates.

    Args:
        rows: Number of honeycomb rows.
        cols: Number of honeycomb columns.
        cell_size: Center spacing scale in layout units.

    Returns:
        Cell-center coordinates.

    Units:
        Coordinates use the same unit as cell_size.

    Aerospace Application:
        Places lightening holes and structural ribs in avionics and recovery bays.
    """

    if rows < 0 or cols < 0 or cell_size <= 0.0:
        raise ValueError("rows/cols must be non-negative and cell_size positive.")
    points: list[Point2D] = []
    dx = math.sqrt(3.0) * cell_size
    dy = 1.5 * cell_size
    for row in range(rows):
        for col in range(cols):
            x = col * dx + (0.5 * dx if row % 2 else 0.0)
            y = row * dy
            points.append((x, y))
    return points


def dragon_curve_fins(iterations: int) -> list[Point2D]:
    """Generate a dragon-curve polyline for decorative fin SVG rendering.

    Args:
        iterations: Number of fractal fold iterations.

    Returns:
        Dragon curve polyline points.

    Units:
        Dimensionless SVG layout units.

    Aerospace Application:
        Decorative fin-edge motif only; not used for structural CAD.
    """

    if iterations < 0 or iterations > 16:
        raise ValueError("iterations must be between 0 and 16 for a bounded SVG curve.")
    turns: list[int] = []
    for _ in range(iterations):
        turns = turns + [1] + [-turn for turn in reversed(turns)]
    heading = 0
    x, y = 0.0, 0.0
    points: list[Point2D] = [(x, y)]
    for turn in turns:
        heading = (heading + turn) % 4
        if heading == 0:
            x += 1.0
        elif heading == 1:
            y += 1.0
        elif heading == 2:
            x -= 1.0
        else:
            y -= 1.0
        points.append((x, y))
    return points


def _save_demo_plot(path: Path) -> None:
    """Save a combined biomimetic geometry reference plot.

    Args:
        path: Destination PNG path.

    Units:
        Pixel raster output.

    Aerospace Application:
        Documents all reusable nature-derived patterns in one QA artifact.
    """

    import matplotlib.pyplot as plt

    path.parent.mkdir(parents=True, exist_ok=True)
    figure, axes = plt.subplots(2, 3, figsize=(13, 8))
    panels = axes.ravel()

    spiral = fibonacci_spiral_points(24, 0.08)
    panels[0].plot([p[0] for p in spiral], [p[1] for p in spiral], marker="o")
    panels[0].set_title("Fibonacci Spiral")

    phyllo = phyllotaxis_pattern(89, 0.08)
    panels[1].scatter([p[0] for p in phyllo], [p[1] for p in phyllo], s=14)
    panels[1].set_title("Phyllotaxis")

    for (x1, y1), (x2, y2) in voronoi_lattice(1.0, 1.0, 13):
        panels[2].plot([x1, x2], [y1, y2], color="tab:green", linewidth=1)
    panels[2].set_title("Voronoi Lattice")

    xs = [value / 20.0 for value in range(-40, 41)]
    cat = catenary_curve(1.0, xs)
    panels[3].plot([p[0] for p in cat], [p[1] for p in cat])
    panels[3].set_title("Catenary")

    log = logarithmic_spiral(0.04, 0.17, [index * 0.18 for index in range(70)])
    panels[4].plot([p[0] for p in log], [p[1] for p in log])
    panels[4].set_title("Logarithmic Spiral")

    honey = hexagonal_tessellation(6, 7, 0.1)
    panels[5].scatter([p[0] for p in honey], [p[1] for p in honey], marker="h", s=70)
    panels[5].set_title("Hexagonal Tessellation")

    for panel in panels:
        panel.set_aspect("equal", adjustable="box")
        panel.grid(True, alpha=0.25)
    figure.tight_layout()
    figure.savefig(path, dpi=180)
    plt.close(figure)
    print(f"Saved: {path}")


if __name__ == "__main__":
    _save_demo_plot(PROJECT_ROOT / "outputs" / "nature_geometry_demo.png")
