"""
Visual debug script for moment_arrow (double-headed straight arrow).

Creates a PDF with moment arrows at various rotation angles alongside
forces and curved moments for visual comparison.

Usage (Qt renderer):
    python -m MechanicsSketches.tests.test_moment_arrow --qt

Usage (matplotlib renderer):
    python -m MechanicsSketches.tests.test_moment_arrow
"""
import os
import sys

# Allow running as a script from the repo root
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..'))

from MechanicsSketches.base import (
    create_sketch, make_text, add_to_sketch
)
from MechanicsSketches.elements import (
    make_moment_arrow, add_moment_arrow,
    add_moment, add_force,
    add_beam, add_pinned_support, add_roller_support,
)

OUTPUT_DIR = os.path.dirname(os.path.abspath(__file__))


def test_moment_arrow_grid(renderer='mpl'):
    """
    Draw a grid of moment arrows at 0°, 45°, 90°, 135°, 180°, 270°
    alongside a force and curved moment at each angle for comparison.
    """
    sketch = create_sketch("Moment Arrow Rotation Debug")

    angles = [0, 45, 90, 135, 180, 270]
    spacing_x = 18
    spacing_y = 14

    for i, angle in enumerate(angles):
        col = i % 3
        row = i // 3

        cx = col * spacing_x
        cy = -row * spacing_y

        # Moment arrow (new element)
        add_moment_arrow(sketch, cx=cx, cy=cy, angle_deg=angle, scale_factor=1.0,
                         annotation=f"$M_{{{angle}}}$", fontsize_scale=1.0)

        # Reference force at same angle (offset to the right)
        add_force(sketch, cx=cx + 5, cy=cy, angle_deg=angle, scale_factor=1.0,
                  annotation=f"$F_{{{angle}}}$", fontsize_scale=1.0)

        # Reference curved moment (offset further right)
        add_moment(sketch, cx=cx + 10, cy=cy, angle_deg=angle, scale_factor=1.0,
                   annotation=f"$M_c$", fontsize_scale=1.0)

        # Label
        label = make_text(cx + 5, cy + 6, f"angle = {angle}", fontsize=0.8, layer=10)
        add_to_sketch(sketch, label)

    filename = os.path.join(OUTPUT_DIR, f"debug_moment_arrow_{renderer}.pdf")

    if renderer == 'qt':
        from MechanicsSketches.qt_renderer import render
        render(sketch, filename=filename)
    else:
        from MechanicsSketches.renderer import mpl_render
        mpl_render(sketch, figsize=(22, 14), filename=filename, dpi=200)

    print(f"Saved: {filename}")


def test_moment_arrow_on_beam(renderer='mpl'):
    """
    Practical test: beam with moment arrows at different positions,
    showing how double-headed arrows look on a real structure.
    """
    sketch = create_sketch("Moment Arrow on Beam")

    S = 1.0
    add_beam(sketch, 0, 0, 30, 0, scale_factor=S)
    add_pinned_support(sketch, 0, 0, scale_factor=S)
    add_roller_support(sketch, 30, 0, scale_factor=S)

    # Moment arrows at various positions
    add_moment_arrow(sketch, cx=7, cy=0, angle_deg=90, scale_factor=S,
                     annotation="$M_1$", fontsize_scale=1.0)
    add_moment_arrow(sketch, cx=15, cy=0, angle_deg=0, scale_factor=S,
                     annotation="$M_x$", fontsize_scale=1.0)
    add_moment_arrow(sketch, cx=22, cy=0, angle_deg=-90, scale_factor=S,
                     annotation="$M_2$", fontsize_scale=1.0)

    # Reference: curved moment for comparison
    add_moment(sketch, cx=10, cy=3, angle_deg=0, scale_factor=S * 0.7,
               annotation="$M_c$", fontsize_scale=0.8)

    filename = os.path.join(OUTPUT_DIR, f"debug_moment_arrow_beam_{renderer}.pdf")

    if renderer == 'qt':
        from MechanicsSketches.qt_renderer import render
        render(sketch, filename=filename)
    else:
        from MechanicsSketches.renderer import mpl_render
        mpl_render(sketch, figsize=(16, 8), filename=filename, dpi=200)

    print(f"Saved: {filename}")


if __name__ == "__main__":
    renderer = 'qt' if '--qt' in sys.argv else 'mpl'
    print(f"Using renderer: {renderer}")
    print(f"Output directory: {OUTPUT_DIR}\n")

    test_moment_arrow_grid(renderer)
    test_moment_arrow_on_beam(renderer)

    print("\nDone! Check the PDF files in the tests/ directory.")
