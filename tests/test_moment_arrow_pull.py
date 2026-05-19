"""
Visual test for moment_arrow_pull (double-headed pulling moment arrow).

Verifies that cx, cy is anchored at the structural attachment point (far
end of the shaft) and the double arrowhead points away from the structure
at the given angle. Compares side-by-side with force_pull and moment_arrow.

Usage:
    python -m MechanicsSketches.tests.test_moment_arrow_pull
"""
import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..'))

from MechanicsSketches.base import create_sketch, add_to_sketch, make_text
from MechanicsSketches.elements import (
    add_moment_arrow_pull, add_moment_arrow,
    add_force_pull, add_force,
    add_beam, add_pinned_support, add_roller_support,
)

OUTPUT_DIR = os.path.dirname(os.path.abspath(__file__))


def test_moment_arrow_pull_angles():
    """Grid of pulling moment arrows at various angles."""
    sketch = create_sketch("Moment Arrow Pull Variants")
    S = 30
    spacing = 360

    angles = [0, 45, 90, 135, 180, -90]
    for i, ang in enumerate(angles):
        col = i % 3
        row = i // 3
        cx = col * spacing
        cy = -row * spacing

        # The pulling moment arrow itself
        add_moment_arrow_pull(sketch, cx=cx, cy=cy, angle_deg=ang, scale_factor=S,
                              annotation=rf"$M_{{{ang}}}$", fontsize=18)

        # Marker at (cx, cy) — should be at the shaft's far end (structure side)
        add_to_sketch(sketch, make_text(cx, cy - 30, f"angle={ang}°",
                                        fontsize=14, ha="center", va="top"))


    from MechanicsSketches.qt_renderer import render
    out = os.path.join(OUTPUT_DIR, "debug_moment_arrow_pull_angles_qt.pdf")
    render(sketch, filename=out)
    print(f"Written: {out}")


def test_moment_arrow_pull_on_beam():
    """Pulling moments at the supports of a beam, alongside pulling forces."""
    sketch = create_sketch("Moment Arrow Pull on Beam")
    S = 30

    add_beam(sketch, 0, 0, 900, 0, scale_factor=S)
    add_pinned_support(sketch, 0, 0, scale_factor=S)
    add_roller_support(sketch, 900, 0, scale_factor=S)

    # Pulling moments at the supports — shaft anchored on the beam,
    # double arrowhead pointing away (downward at angle_deg=0).
    add_moment_arrow_pull(sketch, cx=150, cy=0, angle_deg=0, scale_factor=S,
                          annotation=r"$M_A$", fontsize=20)
    add_moment_arrow_pull(sketch, cx=750, cy=0, angle_deg=180, scale_factor=S,
                          annotation=r"$M_B$", fontsize=20)

    # Comparison: regular moment_arrow (tip at beam) and force_pull (tension)
    add_moment_arrow(sketch, cx=300, cy=0, angle_deg=0, scale_factor=S,
                     annotation=r"$M_x$", fontsize=20)
    add_force_pull(sketch, cx=450, cy=0, angle_deg=0, scale_factor=S,
                   annotation=r"$F_p$", fontsize=20)
    add_force(sketch, cx=600, cy=0, angle_deg=0, scale_factor=S,
              annotation=r"$F$", fontsize=20)

    add_to_sketch(sketch, make_text(450, -150,
                                     "Pull moments at A,B; regular moment $M_x$; pulling force $F_p$; regular force $F$",
                                     fontsize=14, ha="center", va="top"))

    from MechanicsSketches.qt_renderer import render
    out = os.path.join(OUTPUT_DIR, "debug_moment_arrow_pull_beam_qt.pdf")
    render(sketch, filename=out)
    print(f"Written: {out}")


if __name__ == "__main__":
    test_moment_arrow_pull_angles()
    test_moment_arrow_pull_on_beam()
