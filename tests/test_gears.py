"""
Visual test for gear elements (cut and side view).

Usage:
    python -m MechanicsSketches.tests.test_gears
"""
import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..'))

from MechanicsSketches.base import create_sketch, add_to_sketch, make_text
from MechanicsSketches.elements import (
    add_gear_cut, add_gear_side, add_beam, add_truss,
    add_pinned_support, add_roller_support,
)

OUTPUT_DIR = os.path.dirname(os.path.abspath(__file__))


def test_gears():
    """Cut gears and side-view gears with various parameters."""
    sketch = create_sketch("Gear Variants")
    S = 30

    # Row 1: cut gears with varying tooth_fraction
    cy = 0
    for i, tf in enumerate([0.10, 0.15, 0.20, 0.30]):
        cx = i * 200
        add_gear_cut(sketch, cx=cx, cy=cy, r_i=15, r_a=60, b=40,
                     tooth_fraction=tf, scale_factor=S)
        add_to_sketch(sketch, make_text(cx, cy - 100, f"tooth_fraction={tf}",
                                        fontsize=20, ha="center", va="top"))

    # Row 2: cut gears with varying r_a / r_i / b
    cy = -250
    cases = [
        (10, 50, 30, "r_i=10, r_a=50, b=30"),
        (15, 60, 50, "r_i=15, r_a=60, b=50"),
        (20, 70, 30, "r_i=20, r_a=70, b=30"),
        (25, 80, 60, "r_i=25, r_a=80, b=60"),
    ]
    for i, (r_i, r_a, b, label) in enumerate(cases):
        cx = i * 200
        add_gear_cut(sketch, cx=cx, cy=cy, r_i=r_i, r_a=r_a, b=b, scale_factor=S)
        add_to_sketch(sketch, make_text(cx, cy - 110, label,
                                        fontsize=14, ha="center", va="top"))

    # Row 3: cut gear on a shaft (beam)
    cy = -500
    shaft_y = cy
    add_beam(sketch, ax=-300, ay=shaft_y, bx=300, by=shaft_y, scale_factor=S)
    add_pinned_support(sketch, cx=-300, cy=shaft_y, scale_factor=S)
    add_roller_support(sketch, cx=300, cy=shaft_y, scale_factor=S)
    add_gear_cut(sketch, cx=-100, cy=shaft_y, r_i=15, r_a=60, b=40, scale_factor=S)
    add_gear_cut(sketch, cx=100, cy=shaft_y, r_i=15, r_a=80, b=50, scale_factor=S)
    add_to_sketch(sketch, make_text(0, cy - 120, "Cut gears on shaft (background behind beam, body hatched)",
                                    fontsize=14, ha="center", va="top"))

    # Row 4: side-view gears with varying n_teeth
    cy = -800
    for i, n in enumerate([6, 10, 16, 24]):
        cx = i * 200
        add_gear_side(sketch, cx=cx, cy=cy, r_i=12, r_a=60, n_teeth=n, scale_factor=S)
        add_to_sketch(sketch, make_text(cx, cy - 100, f"n_teeth={n}",
                                        fontsize=20, ha="center", va="top"))

    # Row 5: side-view gears with varying tooth_fraction
    cy = -1050
    for i, tf in enumerate([0.05, 0.15, 0.25, 0.4]):
        cx = i * 200
        add_gear_side(sketch, cx=cx, cy=cy, r_i=12, r_a=60, n_teeth=14,
                      tooth_fraction=tf, scale_factor=S)
        add_to_sketch(sketch, make_text(cx, cy - 100, f"tooth_fraction={tf}",
                                        fontsize=20, ha="center", va="top"))

    # Row 6: rotation
    cy = -1300
    for i, ang in enumerate([0, 30, 45, 90]):
        cx = i * 200
        add_gear_cut(sketch, cx=cx, cy=cy, r_i=15, r_a=55, b=30,
                     angle_deg=ang, scale_factor=S)
        add_to_sketch(sketch, make_text(cx, cy - 100, f"cut, angle={ang}°",
                                        fontsize=20, ha="center", va="top"))

    from MechanicsSketches.qt_renderer import render
    out = os.path.join(OUTPUT_DIR, "debug_gears_qt.pdf")
    render(sketch, filename=out)
    print(f"Written: {out}")


if __name__ == "__main__":
    test_gears()
