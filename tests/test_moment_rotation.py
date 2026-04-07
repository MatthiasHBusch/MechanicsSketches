"""
Visual debug script for moment and arc rotation.

Creates a PDF with moments at various rotation angles to debug rotation issues.
Also creates standalone arc tests to isolate arc rotation behavior.

Usage (matplotlib renderer):
    python -m MechanicsSketches.tests.test_moment_rotation

Usage (Qt renderer, if available):
    python -m MechanicsSketches.tests.test_moment_rotation --qt
"""
import os
import sys
import math

# Allow running as a script from the repo root
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..'))

from MechanicsSketches.base import (
    create_sketch, make_arc, make_line, make_circle, make_polygon,
    scale, rotate, translate, add_to_sketch, make_group, make_text
)
from MechanicsSketches.elements import (
    make_moment, add_moment,
    make_force, add_force,
    add_beam, add_pinned_support,
)

OUTPUT_DIR = os.path.dirname(os.path.abspath(__file__))


def test_moments_grid(renderer='mpl'):
    """
    Draw a grid of moments at 0°, 45°, 90°, 135°, 180°, 270°
    with annotated labels showing the expected angle.
    A reference force is drawn at each position to compare rotation behavior.
    """
    sketch = create_sketch("Moment Rotation Debug")

    angles = [0, 45, 90, 135, 180, 270]
    spacing_x = 360
    spacing_y = 420

    for i, angle in enumerate(angles):
        col = i % 3
        row = i // 3

        cx = col * spacing_x
        cy = -row * spacing_y

        # Add moment with rotation
        add_moment(sketch, cx=cx, cy=cy, angle_deg=angle, scale_factor=30,
                   annotation=f"$M_{{{angle}}}$", fontsize_scale=1)

        # Add a reference force at same location with same rotation (offset below)
        add_force(sketch, cx=cx, cy=cy - 180, angle_deg=angle, scale_factor=30,
                  annotation=f"$F_{{{angle}}}$", fontsize_scale=1)

        # Label
        label = make_text(cx, cy + 150, f"angle = {angle}", fontsize=20, layer=10)
        add_to_sketch(sketch, label)

    filename = os.path.join(OUTPUT_DIR, f"debug_moment_rotation_{renderer}.pdf")

    if renderer == 'qt':
        from MechanicsSketches.qt_renderer import render
        render(sketch, filename=filename)
    else:
        from MechanicsSketches.renderer import mpl_render
        mpl_render(sketch, figsize=(18, 12), filename=filename, dpi=200)

    print(f"Saved: {filename}")


def test_arc_rotation_isolated(renderer='mpl'):
    """
    Draw arcs alone (without the moment arrow head) at various rotations
    to isolate whether the arc primitive rotates correctly.
    Also draw a reference line from center in the direction of theta1
    to verify alignment.
    """
    sketch = create_sketch("Arc Rotation Debug")

    angles = [0, 30, 60, 90, 120, 180]
    spacing = 300
    radius = 60.0

    for i, angle in enumerate(angles):
        col = i % 3
        row = i // 3
        cx = col * spacing
        cy = -row * spacing

        # Create an arc at the origin and rotate it
        arc = make_arc(0, 0, 2 * radius, 2 * radius, -35, 45, 0.0, linewidth=1.5, layer=8)
        arc = rotate(arc, 0, 0, angle)
        arc = translate(arc, cx, cy)
        add_to_sketch(sketch, arc)

        # Draw a reference line from center to the expected start point of the arc
        # theta1 after rotation = -35 + angle
        start_angle_rad = math.radians(-35 + angle)
        end_x = cx + radius * math.cos(start_angle_rad)
        end_y = cy + radius * math.sin(start_angle_rad)
        ref_line = make_line(cx, cy, end_x, end_y, linewidth=0.9, layer=9, edgecolor="red")
        add_to_sketch(sketch, ref_line)

        # Draw another reference line for theta2
        end_angle_rad = math.radians(45 + angle)
        end_x2 = cx + radius * math.cos(end_angle_rad)
        end_y2 = cy + radius * math.sin(end_angle_rad)
        ref_line2 = make_line(cx, cy, end_x2, end_y2, linewidth=0.9, layer=9, edgecolor="blue")
        add_to_sketch(sketch, ref_line2)

        # Small center mark
        add_to_sketch(sketch, make_circle(cx, cy, 4.5, linewidth=0.9, layer=10))

        # Label
        label = make_text(cx, cy + 105, f"rot = {angle}", fontsize=20, layer=10)
        add_to_sketch(sketch, label)

        # Expected theta info
        info = make_text(cx, cy - 105, f"$\\theta_1$={-35+angle} $\\theta_2$={45+angle}", fontsize=15, layer=10)
        add_to_sketch(sketch, info)

    filename = os.path.join(OUTPUT_DIR, f"debug_arc_rotation_{renderer}.pdf")

    if renderer == 'qt':
        from MechanicsSketches.qt_renderer import render
        render(sketch, filename=filename)
    else:
        from MechanicsSketches.renderer import mpl_render
        mpl_render(sketch, figsize=(14, 10), filename=filename, dpi=200)

    print(f"Saved: {filename}")


def test_moment_with_beam(renderer='mpl'):
    """
    A practical test: beam with moments at different orientations,
    mimicking a real use case where moments are applied to a structure.
    """
    sketch = create_sketch("Moment on Beam Debug")

    S = 30
    # Horizontal beam
    add_beam(sketch, 0, 0, 600, 0, scale_factor=S)
    add_pinned_support(sketch, 0, 0, scale_factor=S)
    add_pinned_support(sketch, 600, 0, scale_factor=S)

    # Moments at various positions with different rotations
    test_cases = [
        (150, 0, 0, "$M_0$"),
        (300, 0, 90, "$M_{90}$"),
        (450, 0, 180, "$M_{180}$"),
        (150, 0, -45, "$M_{-45}$"),
        (450, 0, 45, "$M_{45}$"),
    ]

    for cx, cy, angle, label in test_cases:
        add_moment(sketch, cx=cx, cy=cy + 90, angle_deg=angle,
                   scale_factor=S * 0.8, annotation=label, fontsize_scale=1)

    filename = os.path.join(OUTPUT_DIR, f"debug_moment_on_beam_{renderer}.pdf")

    if renderer == 'qt':
        from MechanicsSketches.qt_renderer import render
        render(sketch, filename=filename)
    else:
        from MechanicsSketches.renderer import mpl_render
        mpl_render(sketch, figsize=(14, 6), filename=filename, dpi=200)

    print(f"Saved: {filename}")


def test_arc_data_after_rotation():
    """
    Print the arc data dict after rotation to inspect the values.
    This helps verify that rotate() modifies the correct fields.
    """
    print("\n=== Arc Data After Rotation ===\n")

    radius = 2.0
    arc = make_arc(0, 0, 2 * radius, 2 * radius, -35, 45, 0.0, linewidth=0.05, layer=8)
    print(f"Original arc:  x={arc['x']}, y={arc['y']}, "
          f"theta1={arc['theta1']}, theta2={arc['theta2']}, angle={arc['angle']}, "
          f"w={arc['width']}, h={arc['height']}")

    for rot_angle in [0, 45, 90, 180]:
        rotated = rotate(arc, 0, 0, rot_angle)
        print(f"After rot {rot_angle:>3}°: x={rotated['x']:.3f}, y={rotated['y']:.3f}, "
              f"theta1={rotated['theta1']:.1f}, theta2={rotated['theta2']:.1f}, "
              f"angle={rotated['angle']:.1f}, w={rotated['width']}, h={rotated['height']}")

    print("\n  NOTE: rotate() adjusts theta1/theta2 but NOT the 'angle' property.")
    print("  For circular arcs (w==h), this is correct.")
    print("  For elliptical arcs, the 'angle' property should be updated instead.")
    print("  The Qt renderer (GArc.update_path) ignores 'angle' entirely.\n")


if __name__ == "__main__":
    renderer = 'qt' if '--qt' in sys.argv else 'mpl'
    print(f"Using renderer: {renderer}")
    print(f"Output directory: {OUTPUT_DIR}\n")

    # Data inspection (always runs)
    test_arc_data_after_rotation()

    # Visual tests
    test_moments_grid(renderer)
    test_arc_rotation_isolated(renderer)
    test_moment_with_beam(renderer)

    print("\nDone! Check the PDF files in the tests/ directory.")
