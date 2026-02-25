"""
Visual test for point-to-point dimension functions.

Compares add_dimension_arrow / add_dimension_thickness (center-based)
with add_dimension_arrow_pp / add_dimension_thickness_pp (point-based)
to verify they produce identical results.

Usage:
    python -m MechanicsSketches.tests.test_dimension_pp
    python -m MechanicsSketches.tests.test_dimension_pp --qt
"""
import os
import sys
import math

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..'))

from MechanicsSketches.base import create_sketch, make_text, make_line, add_to_sketch
from MechanicsSketches.elements import (
    add_beam, add_pinned_support, add_roller_support,
    add_dimension_arrow, add_dimension_arrow_pp,
    add_dimension_thickness, add_dimension_thickness_pp,
)

OUTPUT_DIR = os.path.dirname(os.path.abspath(__file__))


def test_dimension_arrow_pp(renderer='mpl'):
    """Compare center-based and point-based dimension arrows side by side."""
    sketch = create_sketch("Dimension Arrow PP Test")
    S = 1.0

    # --- Row 1: Horizontal ---
    y_row1 = 20

    # Center-based (blue reference line above)
    add_to_sketch(sketch, make_line(0, y_row1, 10, y_row1, 0.03, 9, edgecolor="blue"))
    add_dimension_arrow(sketch, cx=5, cy=y_row1 + 1, length=10, angle_deg=0,
                        scale_factor=S, annotation="$L$ (center)")

    # Point-based (red reference line above)
    add_to_sketch(sketch, make_line(0, y_row1 - 3, 10, y_row1 - 3, 0.03, 9, edgecolor="red"))
    add_dimension_arrow_pp(sketch, ax=0, ay=y_row1 - 2, bx=10, by=y_row1 - 2,
                           scale_factor=S, annotation="$L$ (pp)")

    add_to_sketch(sketch, make_text(5, y_row1 + 4, "Horizontal", fontsize=0.8, layer=10))

    # --- Row 2: Vertical ---
    x_col2 = 20

    add_to_sketch(sketch, make_line(x_col2, 0, x_col2, 10, 0.03, 9, edgecolor="blue"))
    add_dimension_arrow(sketch, cx=x_col2 + 1, cy=5, length=10, angle_deg=90,
                        scale_factor=S, annotation="$H$ (center)")

    add_to_sketch(sketch, make_line(x_col2 + 5, 0, x_col2 + 5, 10, 0.03, 9, edgecolor="red"))
    add_dimension_arrow_pp(sketch, ax=x_col2 + 6, ay=0, bx=x_col2 + 6, by=10,
                           scale_factor=S, annotation="$H$ (pp)")

    add_to_sketch(sketch, make_text(x_col2 + 3, 13, "Vertical", fontsize=0.8, layer=10))

    # --- Row 3: Angled (45°) ---
    y_row3 = -5

    add_dimension_arrow(sketch, cx=5, cy=y_row3, length=10, angle_deg=45,
                        scale_factor=S, annotation="$D$ (center)")

    d = 10 / 2
    ax, ay = 5 - d * math.cos(math.radians(45)), y_row3 - d * math.sin(math.radians(45))
    bx, by = 5 + d * math.cos(math.radians(45)), y_row3 + d * math.sin(math.radians(45))
    add_dimension_arrow_pp(sketch, ax=ax + 4, ay=ay + 4, bx=bx + 4, by=by + 4,
                           scale_factor=S, annotation="$D$ (pp)")

    add_to_sketch(sketch, make_text(5, y_row3 + 8, "Angled 45", fontsize=0.8, layer=10))

    # --- Row 4: Practical beam example ---
    y_row4 = -15
    beam_len = 15

    add_beam(sketch, 0, y_row4, beam_len, y_row4, scale_factor=S)
    add_pinned_support(sketch, 0, y_row4, scale_factor=S)
    add_roller_support(sketch, beam_len, y_row4, scale_factor=S)

    # Dimension below beam using pp
    add_dimension_arrow_pp(sketch, ax=0, ay=y_row4 - 2, bx=beam_len, by=y_row4 - 2,
                           scale_factor=S * 0.8, annotation="$\\ell$",
                           helper_line_1_length=1.5, helper_line_2_length=1.5)

    # Sub-dimensions
    add_dimension_arrow_pp(sketch, ax=0, ay=y_row4 - 5, bx=6, by=y_row4 - 5,
                           scale_factor=S * 0.8, annotation="$a$",
                           helper_line_1_length=4, helper_line_2_length=4)
    add_dimension_arrow_pp(sketch, ax=6, ay=y_row4 - 5, bx=beam_len, by=y_row4 - 5,
                           scale_factor=S * 0.8, annotation="$b$",
                           helper_line_1_length=4, helper_line_2_length=4)

    add_to_sketch(sketch, make_text(beam_len / 2, y_row4 + 3, "Beam with PP dimensions", fontsize=0.8, layer=10))

    filename = os.path.join(OUTPUT_DIR, f"debug_dimension_pp_{renderer}.pdf")

    if renderer == 'qt':
        from MechanicsSketches.qt_renderer import render
        render(sketch, filename=filename)
    else:
        from MechanicsSketches.renderer import mpl_render
        mpl_render(sketch, figsize=(14, 18), filename=filename, dpi=200)

    print(f"Saved: {filename}")


def test_thickness_pp(renderer='mpl'):
    """Compare center-based and point-based thickness dimensions."""
    sketch = create_sketch("Thickness PP Test")
    S = 1.0

    # Horizontal thickness
    add_dimension_thickness(sketch, cx=5, cy=5, thickness=4, angle_deg=0,
                            scale_factor=S, annotation="$t$ (center)")
    add_dimension_thickness_pp(sketch, ax=3, ay=2, bx=7, by=2,
                               scale_factor=S, annotation="$t$ (pp)")

    # Vertical thickness
    add_dimension_thickness(sketch, cx=18, cy=5, thickness=4, angle_deg=90,
                            scale_factor=S, annotation="$h$ (center)")
    add_dimension_thickness_pp(sketch, ax=22, ay=3, bx=22, by=7,
                               scale_factor=S, annotation="$h$ (pp)")

    # Angled thickness
    d = 2
    add_dimension_thickness_pp(sketch, ax=5 - d * math.cos(math.radians(30)),
                               ay=-5 - d * math.sin(math.radians(30)),
                               bx=5 + d * math.cos(math.radians(30)),
                               by=-5 + d * math.sin(math.radians(30)),
                               scale_factor=S, annotation="$d$ (pp, 30)")

    add_to_sketch(sketch, make_text(12, 9, "Thickness PP Test", fontsize=1.0, layer=10))

    filename = os.path.join(OUTPUT_DIR, f"debug_thickness_pp_{renderer}.pdf")

    if renderer == 'qt':
        from MechanicsSketches.qt_renderer import render
        render(sketch, filename=filename)
    else:
        from MechanicsSketches.renderer import mpl_render
        mpl_render(sketch, figsize=(14, 10), filename=filename, dpi=200)

    print(f"Saved: {filename}")


if __name__ == "__main__":
    renderer = 'qt' if '--qt' in sys.argv else 'mpl'
    print(f"Using renderer: {renderer}")
    print(f"Output directory: {OUTPUT_DIR}\n")

    test_dimension_arrow_pp(renderer)
    test_thickness_pp(renderer)

    print("\nDone! Check the PDF files in the tests/ directory.")
