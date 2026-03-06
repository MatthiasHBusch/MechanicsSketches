"""
Best-practice sketches for MechanicsSketches.

These are carefully tuned "golden" examples that produce clear, well-proportioned
output with no overlaps. Use these as templates/prompts.

Each function documents WHY certain parameter choices were made.
"""
import os
import sys
import math

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
from MechanicsSketches import *

OUT = os.path.dirname(os.path.abspath(__file__))


# =============================================================================
# TEMPLATE 1: Simply Supported Beam with Point Load
# =============================================================================
# Key rules:
#   - S = 30 is the sweet spot for scale
#   - Dimensions at -2.5*S below beam (enough room for supports)
#   - Overall dimension at -4*S if you need two rows
#   - Coordinate system at bottom-left, offset -2.5*S from beam start
#   - Force fontsize_scale=1 works perfectly at S=30
#   - Dimension scale_factor = S*0.5 (smaller arrows), fontsize_scale=2.0
#     so labels match force label sizes (2.0 * S*0.5 = S)

def best_01_simply_supported_beam():
    sketch = create_sketch("Simply Supported Beam")
    S = 30.0
    L = 10  # beam length in S-units

    add_beam(sketch, ax=0, ay=0, bx=L*S, by=0, scale_factor=S)
    add_pinned_support(sketch, cx=0, cy=0, angle_deg=0, scale_factor=S)
    add_roller_support(sketch, cx=L*S, cy=0, angle_deg=0, scale_factor=S)
    add_force(sketch, cx=5*S, cy=0, angle_deg=0, scale_factor=S, annotation=r"$F$")

    # Dimension BELOW beam: use -2.8*S for first row, -4.5*S for second
    # fontsize_scale=2.0 compensates for smaller scale_factor to match force labels
    add_dimension_arrow_pp(sketch, ax=0, ay=-2.8*S, bx=5*S, by=-2.8*S,
                           scale_factor=S*0.5, annotation=r"$a$", fontsize_scale=2.0)
    add_dimension_arrow_pp(sketch, ax=5*S, ay=-2.8*S, bx=L*S, by=-2.8*S,
                           scale_factor=S*0.5, annotation=r"$b$", fontsize_scale=2.0)
    add_dimension_arrow_pp(sketch, ax=0, ay=-4.5*S, bx=L*S, by=-4.5*S,
                           scale_factor=S*0.5, annotation=r"$L$", fontsize_scale=2.0)

    # Coordinate system: bottom-left, fontsize_scale=2.0 for readable labels
    add_coordinate_system(sketch, cx=-2.5*S, cy=-4*S, scale_factor=S*0.5,
                          ax1=r"$x$", ax2=r"$z$", ax3=r"$y$",
                          last_axis_out_of_image=True, fontsize_scale=2.0)

    render(sketch, filename=os.path.join(OUT, "best_01_simply_supported.png"), dpi=200)
    print("  OK: best_01_simply_supported.png")


# =============================================================================
# TEMPLATE 2: Cantilever Beam
# =============================================================================
# Key rules for cantilever:
#   - Fixed support angle_deg=0 gives vertical wall, hatching LEFT
#   - Moment at S*0.7 (smaller than structure), fontsize_scale=1.4
#     so label matches force size (1.4 * 0.7*S ~ S)
#   - Use offsetx to push moment label right of the arc

def best_02_cantilever():
    sketch = create_sketch("Cantilever Beam")
    S = 30.0
    L = 8

    add_fixed_support(sketch, cx=0, cy=0, angle_deg=0, scale_factor=S)
    add_beam(sketch, ax=0, ay=0, bx=L*S, by=0, scale_factor=S)
    add_force(sketch, cx=L*S, cy=0, angle_deg=0, scale_factor=S, annotation=r"$P$")

    # Moment: S*0.7 keeps arc smaller than beam, fontsize_scale=1.4 for label parity
    # Default annotation position sits just above the arc — no offsetx needed
    add_moment(sketch, cx=0, cy=0, angle_deg=0, scale_factor=S*0.7,
               annotation=r"$M_A$", fontsize_scale=1.4)

    add_dimension_arrow_pp(sketch, ax=0, ay=-2.5*S, bx=L*S, by=-2.5*S,
                           scale_factor=S*0.5, annotation=r"$L$", fontsize_scale=2.0)

    render(sketch, filename=os.path.join(OUT, "best_02_cantilever.png"), dpi=200)
    print("  OK: best_02_cantilever.png")


# =============================================================================
# TEMPLATE 3: Propped Cantilever with Multiple Loads
# =============================================================================
# Key rules for complex FBDs:
#   - Space forces at least 3*S apart so labels don't touch
#   - Moment scale_factor S*0.7 to keep it smaller than full-size forces
#   - fontsize_scale=1.4 on moments for label-size parity with forces
#   - Stack dimensions: first row at -2.8*S, overall at -4.5*S

def best_03_propped_cantilever():
    sketch = create_sketch("Propped Cantilever FBD")
    S = 30.0
    L = 12

    add_beam(sketch, ax=0, ay=0, bx=L*S, by=0, scale_factor=S)
    add_fixed_support(sketch, cx=0, cy=0, angle_deg=0, scale_factor=S)
    add_roller_support(sketch, cx=L*S, cy=0, angle_deg=0, scale_factor=S)

    # Forces spaced well apart (4*S each)
    add_force(sketch, cx=4*S, cy=0, angle_deg=0, scale_factor=S, annotation=r"$F_1$")
    add_force(sketch, cx=8*S, cy=0, angle_deg=0, scale_factor=S, annotation=r"$F_2$")

    # Moment at wall - smaller scale, fontsize boosted for label parity
    add_moment(sketch, cx=0, cy=0, angle_deg=0, scale_factor=S*0.7,
               annotation=r"$M_A$", fontsize_scale=1.4)

    # Segment dimensions (first row) - fontsize_scale=2.0 for label parity
    add_dimension_arrow_pp(sketch, ax=0, ay=-2.8*S, bx=4*S, by=-2.8*S,
                           scale_factor=S*0.5, annotation=r"$a$", fontsize_scale=2.0)
    add_dimension_arrow_pp(sketch, ax=4*S, ay=-2.8*S, bx=8*S, by=-2.8*S,
                           scale_factor=S*0.5, annotation=r"$b$", fontsize_scale=2.0)
    add_dimension_arrow_pp(sketch, ax=8*S, ay=-2.8*S, bx=L*S, by=-2.8*S,
                           scale_factor=S*0.5, annotation=r"$c$", fontsize_scale=2.0)

    # Overall dimension (second row)
    add_dimension_arrow_pp(sketch, ax=0, ay=-4.5*S, bx=L*S, by=-4.5*S,
                           scale_factor=S*0.5, annotation=r"$L$", fontsize_scale=2.0)

    add_coordinate_system(sketch, cx=-2.5*S, cy=-4*S, scale_factor=S*0.5,
                          ax1=r"$x$", ax2=r"$z$", ax3=r"$y$",
                          last_axis_out_of_image=True, fontsize_scale=2.0)

    render(sketch, filename=os.path.join(OUT, "best_03_propped_cantilever.png"), dpi=200)
    print("  OK: best_03_propped_cantilever.png")


# =============================================================================
# TEMPLATE 4: Truss Structure
# =============================================================================
# Key rules for trusses:
#   - Use add_truss (lines) not add_beam (rectangles)
#   - Truss scale_factor = S*0.08 gives clean thin lines
#   - Place hinges at ALL joints
#   - Force on top node: annotation shifted with offsety for clarity

def best_04_truss():
    sketch = create_sketch("Simple Truss")
    S = 30.0
    t = S * 0.08  # truss line thickness

    # Members
    add_truss(sketch, ax=0, ay=0, bx=4*S, by=0, scale_factor=t)
    add_truss(sketch, ax=4*S, ay=0, bx=8*S, by=0, scale_factor=t)
    add_truss(sketch, ax=0, ay=0, bx=4*S, by=3*S, scale_factor=t)
    add_truss(sketch, ax=4*S, ay=3*S, bx=8*S, by=0, scale_factor=t)
    add_truss(sketch, ax=4*S, ay=0, bx=4*S, by=3*S, scale_factor=t)

    # Joints at every node
    add_hinge(sketch, cx=0, cy=0, scale_factor=S)
    add_hinge(sketch, cx=4*S, cy=0, scale_factor=S)
    add_hinge(sketch, cx=8*S, cy=0, scale_factor=S)
    add_hinge(sketch, cx=4*S, cy=3*S, scale_factor=S)

    # Supports
    add_pinned_support(sketch, cx=0, cy=0, angle_deg=0, scale_factor=S)
    add_roller_support(sketch, cx=8*S, cy=0, angle_deg=0, scale_factor=S)

    # Load at top
    add_force(sketch, cx=4*S, cy=3*S, angle_deg=0, scale_factor=S, annotation=r"$F$")

    # Dimensions - fontsize_scale=2.0 for label parity
    add_dimension_arrow_pp(sketch, ax=0, ay=-2.8*S, bx=4*S, by=-2.8*S,
                           scale_factor=S*0.5, annotation=r"$a$", fontsize_scale=2.0)
    add_dimension_arrow_pp(sketch, ax=4*S, ay=-2.8*S, bx=8*S, by=-2.8*S,
                           scale_factor=S*0.5, annotation=r"$a$", fontsize_scale=2.0)

    render(sketch, filename=os.path.join(OUT, "best_04_truss.png"), dpi=200)
    print("  OK: best_04_truss.png")


# =============================================================================
# TEMPLATE 5: Frame Structure (L-shape)
# =============================================================================
# Key rules for frames:
#   - Use add_beam for both vertical and horizontal members
#   - Fixed support angle_deg=90 for horizontal ground
#   - Horizontal force: angle_deg=90 (rightward push)
#   - Place hinge at the corner joint

def best_05_frame():
    sketch = create_sketch("L-Frame")
    S = 30.0

    # Vertical column
    add_beam(sketch, ax=0, ay=0, bx=0, by=6*S, scale_factor=S)
    # Horizontal beam
    add_beam(sketch, ax=0, ay=6*S, bx=8*S, by=6*S, scale_factor=S)

    # Fixed support at base (horizontal ground)
    add_fixed_support(sketch, cx=0, cy=0, angle_deg=90, scale_factor=S)

    # Roller at far end
    add_roller_support(sketch, cx=8*S, cy=6*S, angle_deg=0, scale_factor=S)

    # Corner hinge
    add_hinge(sketch, cx=0, cy=6*S, scale_factor=S)

    # Horizontal force on column
    add_force(sketch, cx=0, cy=3*S, angle_deg=90, scale_factor=S, annotation=r"$H$")

    # Vertical force on beam
    add_force(sketch, cx=4*S, cy=6*S, angle_deg=0, scale_factor=S, annotation=r"$V$")

    render(sketch, filename=os.path.join(OUT, "best_05_frame.png"), dpi=200)
    print("  OK: best_05_frame.png")


# =============================================================================
# TEMPLATE 6: Distributed Load (simulated)
# =============================================================================
# Key rules for distributed loads:
#   - Use S*0.4 for small force arrows
#   - Place arrows at cy=0.4*S (beam top surface) so arrowheads
#     don't penetrate the beam body
#   - 6-8 arrows for a clean look
#   - Connect tops with a line
#   - Label using make_text at S*0.8 above the connecting line
#   - fontsize for make_text: scale_factor * fontsize_scale product
#     i.e. for S=30, fontsize ~ 30*1 = 30 in make_text

def best_06_distributed_load():
    sketch = create_sketch("Distributed Load")
    S = 30.0
    L = 10
    Sf = S * 0.4  # smaller force arrows
    beam_top = 0.4 * S  # top surface of beam

    add_beam(sketch, ax=0, ay=0, bx=L*S, by=0, scale_factor=S)
    add_pinned_support(sketch, cx=0, cy=0, angle_deg=0, scale_factor=S)
    add_roller_support(sketch, cx=L*S, cy=0, angle_deg=0, scale_factor=S)

    # Distributed load arrows - placed at beam top surface so arrowheads stay above beam
    n = 7
    x_positions = [i * L * S / (n + 1) for i in range(1, n + 1)]
    for x in x_positions:
        add_force(sketch, cx=x, cy=beam_top, angle_deg=0, scale_factor=Sf)

    # Connecting line at arrow tops
    # Arrow top in local coords: dy_c + arrow_length = 0.5 + 3.0 = 3.5, scaled by Sf
    arrow_top_y = beam_top + 3.5 * Sf
    add_to_sketch(sketch, make_line(
        x_positions[0], arrow_top_y,
        x_positions[-1], arrow_top_y,
        0.05 * S, 8
    ))

    # Label above the line (use make_text with fontsize matching force labels)
    add_to_sketch(sketch, make_text(
        L * S / 2, arrow_top_y + 0.8 * S,
        r"$q_0$", fontsize=S * 1, layer=10
    ))

    render(sketch, filename=os.path.join(OUT, "best_06_distributed_load.png"), dpi=200)
    print("  OK: best_06_distributed_load.png")


# =============================================================================
# TEMPLATE 7: Beam with Moment (avoiding overlap)
# =============================================================================
# Key rules for moments on beams:
#   - Use scale_factor S*0.7 for moments (smaller than full S)
#   - fontsize_scale=1.4 so label matches force labels (1.4 * 0.7 ~ 1.0)
#   - Use offsetx to push the label AWAY from the beam body
#   - For CCW moment (angle_deg=0), label naturally sits above beam
#   - For CW moment (angle_deg=180), label naturally sits below beam
#     Use offsety to adjust vertical position if needed

def best_07_beam_with_moments():
    sketch = create_sketch("Beam with Moments")
    S = 30.0
    L = 12

    add_beam(sketch, ax=0, ay=0, bx=L*S, by=0, scale_factor=S)
    add_pinned_support(sketch, cx=0, cy=0, angle_deg=0, scale_factor=S)
    add_roller_support(sketch, cx=L*S, cy=0, angle_deg=0, scale_factor=S)

    # CCW moment at 3*S - label sits above arc by default
    add_moment(sketch, cx=3*S, cy=0, angle_deg=0, scale_factor=S*0.7,
               annotation=r"$M_1$", fontsize_scale=1.4)

    # CW moment at 9*S - label sits below arc by default (180° flips)
    add_moment(sketch, cx=9*S, cy=0, angle_deg=180, scale_factor=S*0.7,
               annotation=r"$M_2$", fontsize_scale=1.4)

    render(sketch, filename=os.path.join(OUT, "best_07_moments.png"), dpi=200)
    print("  OK: best_07_moments.png")


# =============================================================================
# TEMPLATE 8: Inclined Beam
# =============================================================================
# Key rules for inclined beams:
#   - Use angle_deg=0 for supports (horizontal ground) to avoid
#     support geometry overlapping the beam body
#   - Forces remain vertical (angle_deg=0 = downward)
#   - Dimensions: place below lowest point, use proper LaTeX

def best_08_inclined_beam():
    sketch = create_sketch("Inclined Beam")
    S = 30.0
    angle = 25  # degrees
    L = 8

    bx = L * S * math.cos(math.radians(angle))
    by = L * S * math.sin(math.radians(angle))

    add_beam(sketch, ax=0, ay=0, bx=bx, by=by, scale_factor=S)

    # Supports on horizontal ground (angle_deg=0 avoids overlap with inclined beam)
    add_pinned_support(sketch, cx=0, cy=0, angle_deg=0, scale_factor=S)
    add_roller_support(sketch, cx=bx, cy=by, angle_deg=0, scale_factor=S)

    # Vertical force at midpoint
    add_force(sketch, cx=bx/2, cy=by/2, angle_deg=0, scale_factor=S, annotation=r"$F$")

    # Horizontal dimension below everything
    add_dimension_arrow_pp(sketch, ax=0, ay=-3*S, bx=bx, by=-3*S,
                           scale_factor=S*0.5, annotation=r"$L \cos\alpha$",
                           fontsize_scale=2.0)

    render(sketch, filename=os.path.join(OUT, "best_08_inclined.png"), dpi=200)
    print("  OK: best_08_inclined.png")


# =============================================================================
# TEMPLATE 9: Two-Span Continuous Beam with Hinge
# =============================================================================
# Key rules for multi-span beams:
#   - Separate beam segments at hinge locations
#   - Hinge at the joint point
#   - Segment dimensions on first row, overall on second

def best_09_two_span():
    sketch = create_sketch("Two-Span Beam with Hinge")
    S = 30.0

    # Two beam segments
    add_beam(sketch, ax=0, ay=0, bx=6*S, by=0, scale_factor=S)
    add_beam(sketch, ax=6*S, ay=0, bx=14*S, by=0, scale_factor=S)

    # Three supports
    add_pinned_support(sketch, cx=0, cy=0, angle_deg=0, scale_factor=S)
    add_roller_support(sketch, cx=6*S, cy=0, angle_deg=0, scale_factor=S)
    add_roller_support(sketch, cx=14*S, cy=0, angle_deg=0, scale_factor=S)

    # Hinge between spans
    add_hinge(sketch, cx=10*S, cy=0, scale_factor=S)

    # Forces well-spaced
    add_force(sketch, cx=3*S, cy=0, angle_deg=0, scale_factor=S, annotation=r"$F_1$")
    add_force(sketch, cx=12*S, cy=0, angle_deg=0, scale_factor=S, annotation=r"$F_2$")

    # Dimensions - fontsize_scale=2.0 for label parity
    add_dimension_arrow_pp(sketch, ax=0, ay=-2.8*S, bx=6*S, by=-2.8*S,
                           scale_factor=S*0.5, annotation=r"$a$", fontsize_scale=2.0)
    add_dimension_arrow_pp(sketch, ax=6*S, ay=-2.8*S, bx=14*S, by=-2.8*S,
                           scale_factor=S*0.5, annotation=r"$b$", fontsize_scale=2.0)
    add_dimension_arrow_pp(sketch, ax=0, ay=-4.5*S, bx=14*S, by=-4.5*S,
                           scale_factor=S*0.5, annotation=r"$L$", fontsize_scale=2.0)

    render(sketch, filename=os.path.join(OUT, "best_09_two_span.png"), dpi=200)
    print("  OK: best_09_two_span.png")


# =============================================================================
# TEMPLATE 10: Vertical Beam (Column) with Horizontal Loads
# =============================================================================

def best_10_vertical_column():
    sketch = create_sketch("Vertical Column")
    S = 30.0
    H = 8

    add_beam(sketch, ax=0, ay=0, bx=0, by=H*S, scale_factor=S)
    add_fixed_support(sketch, cx=0, cy=0, angle_deg=90, scale_factor=S)

    # Horizontal force at top (rightward = angle_deg=90)
    add_force(sketch, cx=0, cy=H*S, angle_deg=90, scale_factor=S, annotation=r"$H$")

    # Vertical dimension to the right - fontsize_scale=2.0 for label parity
    add_dimension_arrow(sketch, cx=3*S, cy=H*S/2, length=H*S,
                        angle_deg=90, scale_factor=S*0.5, annotation=r"$h$",
                        fontsize_scale=2.0)

    render(sketch, filename=os.path.join(OUT, "best_10_column.png"), dpi=200)
    print("  OK: best_10_column.png")


# =============================================================================
# Run all best-practice examples
# =============================================================================
if __name__ == "__main__":
    tests = [
        best_01_simply_supported_beam,
        best_02_cantilever,
        best_03_propped_cantilever,
        best_04_truss,
        best_05_frame,
        best_06_distributed_load,
        best_07_beam_with_moments,
        best_08_inclined_beam,
        best_09_two_span,
        best_10_vertical_column,
    ]

    print(f"Generating {len(tests)} best-practice examples...\n")
    for test in tests:
        try:
            test()
        except Exception as e:
            print(f"  FAIL: {test.__name__}: {e}")
            import traceback
            traceback.print_exc()

    print(f"\nDone! Check {OUT}/ for outputs.")
