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
    S = 30

    # --- Row 1: Horizontal ---
    y_row1 = 600

    # Center-based (blue reference line above)
    add_to_sketch(sketch, make_line(0, y_row1, 300, y_row1, 0.9, 9, edgecolor="blue"))
    add_dimension_arrow(sketch, cx=150, cy=y_row1 + 30, length=300, angle_deg=0,
                        scale_factor=S, annotation="$L$ (center)")

    # Point-based (red reference line above)
    add_to_sketch(sketch, make_line(0, y_row1 - 90, 300, y_row1 - 90, 0.9, 9, edgecolor="red"))
    add_dimension_arrow_pp(sketch, ax=0, ay=y_row1 - 60, bx=300, by=y_row1 - 60,
                           scale_factor=S, annotation="$L$ (pp)")

    add_to_sketch(sketch, make_text(150, y_row1 + 120, "Horizontal", fontsize=20, layer=10))

    # --- Row 2: Vertical ---
    x_col2 = 600

    add_to_sketch(sketch, make_line(x_col2, 0, x_col2, 300, 0.9, 9, edgecolor="blue"))
    add_dimension_arrow(sketch, cx=x_col2 + 30, cy=150, length=300, angle_deg=90,
                        scale_factor=S, annotation="$H$ (center)")

    add_to_sketch(sketch, make_line(x_col2 + 150, 0, x_col2 + 150, 300, 0.9, 9, edgecolor="red"))
    add_dimension_arrow_pp(sketch, ax=x_col2 + 180, ay=0, bx=x_col2 + 180, by=300,
                           scale_factor=S, annotation="$H$ (pp)")

    add_to_sketch(sketch, make_text(x_col2 + 90, 390, "Vertical", fontsize=20, layer=10))

    # --- Row 3: Angled (45°) ---
    y_row3 = -150

    add_dimension_arrow(sketch, cx=150, cy=y_row3, length=300, angle_deg=45,
                        scale_factor=S, annotation="$D$ (center)")

    d = 300 / 2
    ax, ay = 150 - d * math.cos(math.radians(45)), y_row3 - d * math.sin(math.radians(45))
    bx, by = 150 + d * math.cos(math.radians(45)), y_row3 + d * math.sin(math.radians(45))
    add_dimension_arrow_pp(sketch, ax=ax + 120, ay=ay + 120, bx=bx + 120, by=by + 120,
                           scale_factor=S, annotation="$D$ (pp)")

    add_to_sketch(sketch, make_text(150, y_row3 + 240, "Angled 45", fontsize=20, layer=10))

    # --- Row 4: Practical beam example ---
    y_row4 = -450
    beam_len = 450

    add_beam(sketch, 0, y_row4, beam_len, y_row4, scale_factor=S)
    add_pinned_support(sketch, 0, y_row4, scale_factor=S)
    add_roller_support(sketch, beam_len, y_row4, scale_factor=S)

    # Dimension below beam using pp
    add_dimension_arrow_pp(sketch, ax=0, ay=y_row4 - 60, bx=beam_len, by=y_row4 - 60,
                           scale_factor=S * 0.8, annotation="$\\ell$",
                           helper_line_1_length=45, helper_line_2_length=45)

    # Sub-dimensions
    add_dimension_arrow_pp(sketch, ax=0, ay=y_row4 - 150, bx=180, by=y_row4 - 150,
                           scale_factor=S * 0.8, annotation="$a$",
                           helper_line_1_length=120, helper_line_2_length=120)
    add_dimension_arrow_pp(sketch, ax=180, ay=y_row4 - 150, bx=beam_len, by=y_row4 - 150,
                           scale_factor=S * 0.8, annotation="$b$",
                           helper_line_1_length=120, helper_line_2_length=120)

    add_to_sketch(sketch, make_text(beam_len / 2, y_row4 + 90, "Beam with PP dimensions", fontsize=20, layer=10))

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
    S = 30

    # Horizontal thickness
    add_dimension_thickness(sketch, cx=150, cy=150, thickness=120, angle_deg=0,
                            scale_factor=S, annotation="$t$ (center)")
    add_dimension_thickness_pp(sketch, ax=90, ay=60, bx=210, by=60,
                               scale_factor=S, annotation="$t$ (pp)")

    # Vertical thickness
    add_dimension_thickness(sketch, cx=540, cy=150, thickness=120, angle_deg=90,
                            scale_factor=S, annotation="$h$ (center)")
    add_dimension_thickness_pp(sketch, ax=660, ay=90, bx=660, by=210,
                               scale_factor=S, annotation="$h$ (pp)")

    # Angled thickness
    d = 60
    add_dimension_thickness_pp(sketch, ax=150 - d * math.cos(math.radians(30)),
                               ay=-150 - d * math.sin(math.radians(30)),
                               bx=150 + d * math.cos(math.radians(30)),
                               by=-150 + d * math.sin(math.radians(30)),
                               scale_factor=S, annotation="$d$ (pp, 30)")

    add_to_sketch(sketch, make_text(360, 270, "Thickness PP Test", fontsize=20, layer=10))

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
