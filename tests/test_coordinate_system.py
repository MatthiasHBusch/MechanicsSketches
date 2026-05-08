"""
Visual test for coordinate_system label offsets.

Verifies that offset_axN_x/y always act in the unrotated scene frame,
regardless of the coordinate system's angle_deg.

Usage:
    python -m MechanicsSketches.tests.test_coordinate_system
"""
import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..'))

from MechanicsSketches.base import create_sketch, add_to_sketch, make_text
from MechanicsSketches.elements import add_coordinate_system

OUTPUT_DIR = os.path.dirname(os.path.abspath(__file__))


def test_coordinate_system_offsets():
    sketch = create_sketch("Coordinate System Offsets")
    S = 30

    # Row 1: rotation only, no offsets — sanity check
    cy = 0
    for i, ang in enumerate([0, 45, 90, 180, 270]):
        cx = i * 250
        add_coordinate_system(sketch, cx=cx, cy=cy, angle_deg=ang, scale_factor=S)
        add_to_sketch(sketch, make_text(cx, cy - 150, f"angle={ang}°, no offsets",
                                        fontsize=14, ha="center", va="top"))

    # Row 2: identical positive offsets on all 3 labels
    # Expected: each label moved by the SAME (+20, +20) vector regardless of cs rotation.
    cy = -350
    for i, ang in enumerate([0, 45, 90, 180, 270]):
        cx = i * 250
        add_coordinate_system(sketch, cx=cx, cy=cy, angle_deg=ang, scale_factor=S,
                              offset_ax1_x=20, offset_ax1_y=20,
                              offset_ax2_x=20, offset_ax2_y=20,
                              offset_ax3_x=20, offset_ax3_y=20)
        add_to_sketch(sketch, make_text(cx, cy - 150, f"angle={ang}°, all offsets +20,+20",
                                        fontsize=12, ha="center", va="top"))

    # Row 3: per-axis offsets (ax1 only)
    cy = -700
    for i, ang in enumerate([0, 45, 90, 180, 270]):
        cx = i * 250
        add_coordinate_system(sketch, cx=cx, cy=cy, angle_deg=ang, scale_factor=S,
                              offset_ax1_x=30, offset_ax1_y=0)
        add_to_sketch(sketch, make_text(cx, cy - 150, f"angle={ang}°, ax1 +30 in x",
                                        fontsize=12, ha="center", va="top"))

    from MechanicsSketches.qt_renderer import render
    out = os.path.join(OUTPUT_DIR, "debug_coordinate_system_offsets_qt.pdf")
    render(sketch, filename=out)
    print(f"Written: {out}")


if __name__ == "__main__":
    test_coordinate_system_offsets()
