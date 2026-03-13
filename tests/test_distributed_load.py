"""
Visual test for distributed_load element.

Usage:
    python -m MechanicsSketches.tests.test_distributed_load --qt
    python -m MechanicsSketches.tests.test_distributed_load
"""
import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..'))

from MechanicsSketches.base import create_sketch, make_text, add_to_sketch
from MechanicsSketches.elements import (
    add_distributed_load, add_beam, add_pinned_support, add_roller_support,
    add_fixed_support,
)

OUTPUT_DIR = os.path.dirname(os.path.abspath(__file__))


def test_distributed_load_variants(renderer='mpl'):
    """Various distribution functions on a beam."""
    sketch = create_sketch("Distributed Load Variants")
    S = 1.0
    beam_len = 10
    y_spacing = 12

    cases = [
        (0, "Uniform (default)", None),
        (-y_spacing, "Uniform explicit", lambda t: 0.5),
        (-2 * y_spacing, "Triangular (t)", lambda t: t),
        (-3 * y_spacing, "Inv. triangular (1-t)", lambda t: 1 - t),
        (-4 * y_spacing, "Sign change (t-0.5)", lambda t: t - 0.5),
        (-5 * y_spacing, "Parabolic", lambda t: 4*t*(1-t)),
    ]

    for cy_off, label, dist in cases:
        add_beam(sketch, 0, cy_off, beam_len, cy_off, scale_factor=S)
        add_pinned_support(sketch, 0, cy_off, scale_factor=S)
        add_roller_support(sketch, beam_len, cy_off, scale_factor=S)

        add_distributed_load(sketch, cx=beam_len / 2, cy=cy_off,
                             length=beam_len, scale_factor=S,
                             distribution=dist, annotation=r"$q_0$",
                             fontsize_scale=S)

        add_to_sketch(sketch, make_text(-3, cy_off, label, fontsize=0.6, layer=10))

    filename = os.path.join(OUTPUT_DIR, f"debug_distributed_load_{renderer}.pdf")

    if renderer == 'qt':
        from MechanicsSketches.qt_renderer import render
        render(sketch, filename=filename)
    else:
        from MechanicsSketches.renderer import mpl_render
        mpl_render(sketch, figsize=(14, 30), filename=filename, dpi=200)

    print(f"Saved: {filename}")


def test_distributed_load_rotations(renderer='mpl'):
    """Distributed loads at various angles."""
    sketch = create_sketch("Distributed Load Rotations")
    S = 1.0

    angles = [0, 90, 180, 270]
    spacing = 15

    for i, angle in enumerate(angles):
        cx = (i % 2) * spacing
        cy = -(i // 2) * spacing

        add_distributed_load(sketch, cx=cx, cy=cy, length=6,
                             angle_deg=angle, scale_factor=S,
                             distribution=lambda t: t,
                             annotation=f"$q_{{{angle}}}$",
                             fontsize_scale=S)

        add_to_sketch(sketch, make_text(cx, cy + 6, f"angle={angle}",
                                         fontsize=0.6, layer=10))

    filename = os.path.join(OUTPUT_DIR, f"debug_distributed_load_rot_{renderer}.pdf")

    if renderer == 'qt':
        from MechanicsSketches.qt_renderer import render
        render(sketch, filename=filename)
    else:
        from MechanicsSketches.renderer import mpl_render
        mpl_render(sketch, figsize=(14, 14), filename=filename, dpi=200)

    print(f"Saved: {filename}")


if __name__ == "__main__":
    renderer = 'qt' if '--qt' in sys.argv else 'mpl'
    print(f"Using renderer: {renderer}")
    print(f"Output directory: {OUTPUT_DIR}\n")

    test_distributed_load_variants(renderer)
    test_distributed_load_rotations(renderer)

    print("\nDone! Check the PDF files in the tests/ directory.")
