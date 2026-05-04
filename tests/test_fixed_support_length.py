"""
Visual test for fixed_support length parameter.

Usage:
    python -m MechanicsSketches.tests.test_fixed_support_length
"""
import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..'))

from MechanicsSketches.base import create_sketch, add_to_sketch, make_text
from MechanicsSketches.elements import add_fixed_support, add_beam

OUTPUT_DIR = os.path.dirname(os.path.abspath(__file__))


def test_fixed_support_lengths():
    """Fixed supports with varying length parameter."""
    sketch = create_sketch("Fixed Support Length Variants")
    S = 30
    beam_len = 200
    y_spacing = 120

    lengths = [0.5, 0.75, 1.0, 1.2, 1.5, 2.0]

    for i, length in enumerate(lengths):
        cy = -i * y_spacing
        add_fixed_support(sketch, cx=0, cy=cy, angle_deg=0, scale_factor=S, length=length)
        add_beam(sketch, ax=0, ay=cy, bx=beam_len, by=cy, scale_factor=S)
        add_to_sketch(sketch, make_text(
            beam_len + 20, cy, f"length={length}",
            fontsize=12, ha="left", va="center",
        ))

    # Also test rotated fixed supports with different lengths
    x_offset = beam_len + 200
    for i, length in enumerate([0.5, 1.0, 1.5]):
        cy = -i * y_spacing * 2
        add_fixed_support(sketch, cx=x_offset, cy=cy, angle_deg=90, scale_factor=S, length=length)
        add_beam(sketch, ax=x_offset, ay=cy, bx=x_offset + beam_len, by=cy, scale_factor=S)
        add_to_sketch(sketch, make_text(
            x_offset + beam_len + 20, cy, f"90°, length={length}",
            fontsize=12, ha="left", va="center",
        ))

    from MechanicsSketches.qt_renderer import render
    out = os.path.join(OUTPUT_DIR, "debug_fixed_support_length_qt.pdf")
    render(sketch, filename=out)
    print(f"Written: {out}")


def test_fixed_support_abs_length():
    """Fixed supports using abs_length (absolute size, scale-independent)."""
    sketch = create_sketch("Fixed Support abs_length")
    beam_len = 200
    y_spacing = 120

    # Same abs_length, different scale_factors → walls should appear identical
    abs_len = 100
    for i, sf in enumerate([20, 30, 40, 50]):
        cy = -i * y_spacing
        add_fixed_support(sketch, cx=0, cy=cy, scale_factor=sf, abs_length=abs_len)
        add_beam(sketch, ax=0, ay=cy, bx=beam_len, by=cy, scale_factor=sf)
        add_to_sketch(sketch, make_text(
            beam_len + 20, cy, f"abs_length={abs_len}, S={sf}",
            fontsize=12, ha="left", va="center",
        ))

    # Different abs_length values at fixed scale_factor
    x_offset = beam_len + 300
    S = 30
    for i, abs_len in enumerate([50, 100, 150, 200]):
        cy = -i * y_spacing
        add_fixed_support(sketch, cx=x_offset, cy=cy, scale_factor=S, abs_length=abs_len)
        add_beam(sketch, ax=x_offset, ay=cy, bx=x_offset + beam_len, by=cy, scale_factor=S)
        add_to_sketch(sketch, make_text(
            x_offset + beam_len + 20, cy, f"abs_length={abs_len}",
            fontsize=12, ha="left", va="center",
        ))

    from MechanicsSketches.qt_renderer import render
    out = os.path.join(OUTPUT_DIR, "debug_fixed_support_abs_length_qt.pdf")
    render(sketch, filename=out)
    print(f"Written: {out}")


if __name__ == "__main__":
    test_fixed_support_lengths()
    test_fixed_support_abs_length()
