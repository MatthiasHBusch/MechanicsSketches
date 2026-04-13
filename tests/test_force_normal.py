"""
Visual test for force_normal (in/out of plane force arrow).

Usage:
    python -m MechanicsSketches.tests.test_force_normal
"""
import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..'))

from MechanicsSketches.base import create_sketch, add_to_sketch, make_text
from MechanicsSketches.elements import (
    add_force_normal, add_force, add_beam,
    add_pinned_support, add_roller_support,
)

OUTPUT_DIR = os.path.dirname(os.path.abspath(__file__))


def test_force_normal_variants():
    """Out-of-plane and into-plane forces, with and without annotation."""
    sketch = create_sketch("Force Normal Variants")
    S = 30
    spacing = 80

    cases = [
        (0, 0, False, "",       "out, no label"),
        (1, 0, True,  "",       "in, no label"),
        (2, 0, False, r"$F_z$", "out, with label"),
        (3, 0, True,  r"$F_z$", "in, with label"),
    ]

    for col, _, inward, anno, label in cases:
        cx = col * spacing * 2
        cy = 0
        add_force_normal(sketch, cx=cx, cy=cy, scale_factor=S,
                         inward=inward, annotation=anno)
        add_to_sketch(sketch, make_text(
            cx, cy - S * 0.6, label,
            fontsize=10, ha="center", va="top",
        ))

    # Comparison row: regular force next to normal force on a beam
    cy_beam = -spacing * 2
    add_beam(sketch, ax=0, ay=cy_beam, bx=8 * S, by=cy_beam, scale_factor=S)
    add_pinned_support(sketch, cx=0, cy=cy_beam, scale_factor=S)
    add_roller_support(sketch, cx=8 * S, cy=cy_beam, scale_factor=S)
    add_force(sketch, cx=2 * S, cy=cy_beam, scale_factor=S, annotation=r"$F$")
    add_force_normal(sketch, cx=4 * S, cy=cy_beam, scale_factor=S,
                     inward=False, annotation=r"$F_z^{out}$")
    add_force_normal(sketch, cx=6 * S, cy=cy_beam, scale_factor=S,
                     inward=True, annotation=r"$F_z^{in}$")

    # Different scale factors row
    cy_scale = -spacing * 4
    for i, sf in enumerate([S * 0.5, S, S * 1.5, S * 2.0]):
        cx = i * spacing * 2
        add_force_normal(sketch, cx=cx, cy=cy_scale, scale_factor=sf,
                         inward=(i % 2 == 1), annotation=r"$F$")

    from MechanicsSketches.qt_renderer import render
    out = os.path.join(OUTPUT_DIR, "debug_force_normal_qt.pdf")
    render(sketch, filename=out)
    print(f"Written: {out}")


if __name__ == "__main__":
    test_force_normal_variants()
