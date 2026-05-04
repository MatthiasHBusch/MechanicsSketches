"""
Visual test for pressure element (n arrows in a circle around a central annotation).

Usage:
    python -m MechanicsSketches.tests.test_pressure
"""
import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..'))

from MechanicsSketches.base import create_sketch, add_to_sketch, make_text
from MechanicsSketches.elements import add_pressure

OUTPUT_DIR = os.path.dirname(os.path.abspath(__file__))


def test_pressure_variants():
    """Pressure symbol with various n values, inward/outward, and annotations."""
    sketch = create_sketch("Pressure Variants")
    S = 30
    spacing = 200

    # Row 1: different n values (inward)
    for i, n in enumerate([4, 6, 8, 12, 16]):
        cx = i * spacing
        cy = 0
        add_pressure(sketch, cx=cx, cy=cy, scale_factor=S, n=n,
                     annotation=r"$p$", fontsize=20)
        add_to_sketch(sketch, make_text(cx, cy - 100, f"n={n}",
                                        fontsize=20, ha="center", va="top"))

    # Row 2: outward arrows
    for i, n in enumerate([4, 6, 8, 12, 16]):
        cx = i * spacing
        cy = -spacing * 1.6
        add_pressure(sketch, cx=cx, cy=cy, scale_factor=S, n=n,
                     annotation=r"$p$", fontsize=20, inward=False)
        add_to_sketch(sketch, make_text(cx, cy - 100, f"n={n}, outward",
                                        fontsize=20, ha="center", va="top"))

    # Row 3: different annotations and rotations
    cases = [
        (r"$p_0$", 0),
        (r"$p_i$", 0),
        (r"$\sigma$", 0),
        (r"$p$", 22.5),
        (r"$p$", 45),
    ]
    for i, (anno, angle) in enumerate(cases):
        cx = i * spacing
        cy = -spacing * 3.2
        add_pressure(sketch, cx=cx, cy=cy, scale_factor=S, n=8,
                     annotation=anno, fontsize=20, angle_deg=angle)
        add_to_sketch(sketch, make_text(cx, cy - 100, f"angle={angle}°",
                                        fontsize=20, ha="center", va="top"))

    from MechanicsSketches.qt_renderer import render
    out = os.path.join(OUTPUT_DIR, "debug_pressure_qt.pdf")
    render(sketch, filename=out)
    print(f"Written: {out}")


if __name__ == "__main__":
    test_pressure_variants()
