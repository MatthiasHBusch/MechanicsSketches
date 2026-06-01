"""
Visual test for sleeve_support (Verschiebehülse / sliding sleeve).

Standalone variants at different angles plus practical examples on beams.

Usage:
    python -m MechanicsSketches.tests.test_sleeve_support
"""
import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..'))

from MechanicsSketches.base import create_sketch, add_to_sketch, make_text
from MechanicsSketches.elements import (
    add_sleeve_support, add_beam, add_pinned_support, add_roller_support,
    add_fixed_support, add_force,
)

OUTPUT_DIR = os.path.dirname(os.path.abspath(__file__))


def test_sleeve_support():
    sketch = create_sketch("Sleeve Support Variants")
    S = 30
    spacing_x = 280

    # Row 1: standalone sleeve supports at the four cardinal angles.
    # At angle=0 the support is on the LEFT of (cx, cy) (beam would extend right).
    cy = 0
    for i, ang in enumerate([0, 90, 180, 270]):
        cx = i * spacing_x
        add_sleeve_support(sketch, cx=cx, cy=cy, angle_deg=ang, scale_factor=S)
        add_to_sketch(sketch, make_text(cx, cy - 80, f"angle={ang}°",
                                        fontsize=16, ha="center", va="top"))

    # Row 2: horizontal beam, sleeve as LEFT support (angle=0), roller on the right.
    cy = -260
    beam_len = 360
    add_sleeve_support(sketch, cx=0, cy=cy, scale_factor=S)
    add_beam(sketch, ax=0, ay=cy, bx=beam_len, by=cy, scale_factor=S)
    add_roller_support(sketch, cx=beam_len, cy=cy, scale_factor=S)
    add_force(sketch, cx=beam_len / 2, cy=cy, scale_factor=S, annotation=r"$F$")
    add_to_sketch(sketch, make_text(beam_len / 2, cy - 100,
                                    "sleeve (left) + roller (right) + central force",
                                    fontsize=14, ha="center", va="top"))

    # Row 3: horizontal beam, sleeve as RIGHT support (angle=180), pinned on the left.
    cy = -500
    add_pinned_support(sketch, cx=0, cy=cy, scale_factor=S)
    add_beam(sketch, ax=0, ay=cy, bx=beam_len, by=cy, scale_factor=S)
    add_sleeve_support(sketch, cx=beam_len, cy=cy, angle_deg=180, scale_factor=S)
    add_to_sketch(sketch, make_text(beam_len / 2, cy - 100,
                                    "pinned (left) + sleeve (right, angle=180°)",
                                    fontsize=14, ha="center", va="top"))

    # Row 4: vertical beam, sleeve at the BOTTOM (angle=270), fixed support on top.
    cy = -780
    beam_len_v = 280
    add_sleeve_support(sketch, cx=0, cy=cy, angle_deg=270, scale_factor=S)
    add_beam(sketch, ax=0, ay=cy, bx=0, by=cy + beam_len_v, scale_factor=S)
    add_fixed_support(sketch, cx=0, cy=cy + beam_len_v, angle_deg=-90, scale_factor=S)
    add_to_sketch(sketch, make_text(140, cy + beam_len_v / 2,
                                    "vertical beam:\nfixed top, sleeve bottom (angle=270°)",
                                    fontsize=14, ha="left", va="center"))

    # Row 5: sleeve directly compared to fixed_support side by side
    cy = -1140
    cx = 0
    add_fixed_support(sketch, cx=cx, cy=cy, scale_factor=S)
    add_beam(sketch, ax=cx, ay=cy, bx=cx + 220, by=cy, scale_factor=S)
    add_to_sketch(sketch, make_text(cx + 110, cy - 100, "fixed_support",
                                    fontsize=14, ha="center", va="top"))

    cx = 400
    add_sleeve_support(sketch, cx=cx, cy=cy, scale_factor=S)
    add_beam(sketch, ax=cx, ay=cy, bx=cx + 220, by=cy, scale_factor=S)
    add_to_sketch(sketch, make_text(cx + 110, cy - 100, "sleeve_support",
                                    fontsize=14, ha="center", va="top"))

    from MechanicsSketches.qt_renderer import render
    out = os.path.join(OUTPUT_DIR, "debug_sleeve_support_qt.pdf")
    render(sketch, filename=out)
    print(f"Written: {out}")


if __name__ == "__main__":
    test_sleeve_support()
