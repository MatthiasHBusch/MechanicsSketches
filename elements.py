import math
from .base import (
    make_line, make_circle, make_rectangle, make_polygon, make_arc, make_text,
    scale, rotate, translate,
    add_to_sketch, make_group
)

# --- Festlager ----------------------------------------------------------------

def make_pinned_support(cx=0.0, cy=0.0, angle_deg=0.0, scale_factor=1.0):
    """Creates a pinned support (Festlager).

    At angle_deg=0, the support sits below the beam (triangle pointing up,
    hatching below). Designed for a horizontal beam.

    Args:
        cx, cy: Application point (top of the support triangle).
        angle_deg: Rotation in degrees. 0 = supporting from below.
        scale_factor: Uniform scale.
    """
    # 0. Geometry constants
    triangle_height = 1.5
    triangle_width = 2.0
    baseline_width = 2.5
    circle_radius = 0.4
    # hatching
    hatching_distance = 0.6
    hatching_length = 0.6
    # linewidth
    base_lw = 0.05

    # 1. Base shape
    primitives = []

    # Triangle
    primitives.append(make_line(0, 0, -triangle_width/2, -triangle_height, base_lw, 3))
    primitives.append(make_line(0, 0,  triangle_width/2, -triangle_height, base_lw, 3))

    # Circle at fix point
    primitives.append(make_circle(0, 0, circle_radius, base_lw, 7))

    # Baseline
    primitives.append(make_line(-baseline_width/2, -triangle_height, baseline_width/2, -triangle_height, base_lw, 3))

    # Hatching
    x = -baseline_width/2 + hatching_length
    while x <= baseline_width/2 + 1e-9:
        primitives.append(make_line(x, -triangle_height, x - hatching_length, -triangle_height - hatching_length, 0.5 * base_lw, 3))
        x += hatching_distance

    # 2. Transformations
    primitives = scale(primitives, 0, 0, scale_factor, scale_linewidth=True)
    primitives = rotate(primitives, 0, 0, angle_deg)
    primitives = translate(primitives, cx, cy)

    return primitives

def add_pinned_support(sketch, cx=0.0, cy=0.0, angle_deg=0.0, scale_factor=1.0, name=""):
    objects = make_pinned_support(cx=cx, cy=cy, angle_deg=angle_deg, scale_factor=scale_factor)
    if name == "":
        name = f"Festlager ({cx}, {cy}, {angle_deg}°)"
    group = make_group(objects, name)
    group["c_type"] = "pinned_support"
    group["c_params"] = {"cx": cx, "cy": cy, "angle_deg": angle_deg, "scale_factor": scale_factor}
    add_to_sketch(sketch, group)
    return group

# --- Loslager ----------------------------------------------------------------

def make_roller_support(cx=0.0, cy=0.0, angle_deg=0.0, scale_factor=1.0):
    """Creates a roller support (Loslager).

    At angle_deg=0, the support sits below the beam (triangle pointing up,
    hatching below, sliding gap between triangle and baseline).
    Designed for a horizontal beam.

    Args:
        cx, cy: Application point (top of the support triangle).
        angle_deg: Rotation in degrees. 0 = supporting from below.
        scale_factor: Uniform scale.
    """
    # 0. Geometry constants
    triangle_height = 1.5
    triangle_width = 2.0
    baseline_width = 2.5
    baseline_gap = 0.15
    circle_radius = 0.4
    # hatching
    hatching_distance = 0.6
    hatching_length = 0.6
    # linewidth
    base_lw = 0.05

    # 1. Base shape
    primitives = []

    # Triangle
    primitives.append(make_line(0, 0, -triangle_width/2, -triangle_height + baseline_gap, base_lw, 3))
    primitives.append(make_line(0, 0,  triangle_width/2, -triangle_height + baseline_gap, base_lw, 3))
    primitives.append(make_line(-triangle_width/2, -triangle_height + baseline_gap, triangle_width/2, -triangle_height + baseline_gap, base_lw, 3))

    # Circle at fix point
    primitives.append(make_circle(0, 0, circle_radius, base_lw, 7))

    # Baseline
    primitives.append(make_line(-baseline_width/2, -triangle_height, baseline_width/2, -triangle_height, base_lw, 3))

    # Hatching
    x = -baseline_width/2 + hatching_length
    while x <= baseline_width/2 + 1e-9:
        primitives.append(make_line(x, -triangle_height, x - hatching_length, -triangle_height - hatching_length, 0.5 * base_lw, 3))
        x += hatching_distance

    # 2. Transformations
    primitives = scale(primitives, 0, 0, scale_factor, scale_linewidth=True)
    primitives = rotate(primitives, 0, 0, angle_deg)
    primitives = translate(primitives, cx, cy)

    return primitives

def add_roller_support(sketch, cx=0.0, cy=0.0, angle_deg=0.0, scale_factor=1.0, name=""):
    objects = make_roller_support(cx=cx, cy=cy, angle_deg=angle_deg, scale_factor=scale_factor)
    if name == "":
        name = f"Loslager ({cx}, {cy}, {angle_deg}°)"
    group = make_group(objects, name)
    group["c_type"] = "roller_support"
    group["c_params"] = {"cx": cx, "cy": cy, "angle_deg": angle_deg, "scale_factor": scale_factor}
    add_to_sketch(sketch, group)
    return group

# --- Einspannung ----------------------------------------------------------------

def make_fixed_support(cx=0.0, cy=0.0, angle_deg=0.0, scale_factor=1.0):
    """Creates a fixed support / clamped wall (Einspannung).

    At angle_deg=0, this is a vertical wall with hatching to the left.
    Designed as the left end of a horizontal beam.

    Args:
        cx, cy: Point where the wall meets the beam.
        angle_deg: Rotation in degrees. 0 = vertical wall, hatching left.
        scale_factor: Uniform scale.
    """
    # 0. Geometry constants
    baseline_width = 2.5
    # hatching
    hatching_distance = 0.6
    hatching_length = 0.6
    # linewidth
    base_lw = 0.05
    primitives = []
    # Baseline
    primitives.append(make_line(0, -baseline_width/2, 0, baseline_width/2, base_lw, 3))

    # Hatching
    y = -baseline_width/2 + hatching_length
    while y <= baseline_width/2 + 1e-9:
        primitives.append(make_line(-hatching_length, y, 0, y - hatching_length, 0.5 * base_lw, 3))
        y += hatching_distance

    # 2. Transformations
    primitives = scale(primitives, 0, 0, scale_factor, scale_linewidth=True)
    primitives = rotate(primitives, 0, 0, angle_deg)
    primitives = translate(primitives, cx, cy)

    return primitives

def add_fixed_support(sketch, cx=0.0, cy=0.0, angle_deg=0.0, scale_factor=1.0, name=""):
    objects = make_fixed_support(cx=cx, cy=cy, angle_deg=angle_deg, scale_factor=scale_factor)
    if name == "":
        name = f"Einspannung ({cx}, {cy}, {angle_deg}°)"
    group = make_group(objects, name)
    group["c_type"] = "fixed_support"
    group["c_params"] = {"cx": cx, "cy": cy, "angle_deg": angle_deg, "scale_factor": scale_factor}
    add_to_sketch(sketch, group)
    return group

# --- Gelenk ----------------------------------------------------------------

def make_hinge(cx=0.0, cy=0.0, scale_factor=1.0):
    """Creates a hinge joint (Gelenk).

    A small circle at the given point, indicating an internal hinge.

    Args:
        cx, cy: Center of the hinge.
        scale_factor: Uniform scale.
    """
    # 0. Geometry constants
    circle_radius = 0.4
    base_lw = 0.05
    primitives = []

    # Circle
    primitives.append(make_circle(0, 0, circle_radius, base_lw, 7))
    primitives = scale(primitives, 0, 0, scale_factor, scale_linewidth=True)
    primitives = translate(primitives, cx, cy)

    return primitives

def add_hinge(sketch, cx=0.0, cy=0.0, scale_factor=1.0, name=""):
    objects = make_hinge(cx=cx, cy=cy, scale_factor=scale_factor)
    if name == "":
        name = f"Gelenk ({cx}, {cy}, {scale_factor})"
    group = make_group(objects, name)
    group["c_type"] = "hinge"
    group["c_params"] = {"cx": cx, "cy": cy, "scale_factor": scale_factor}
    add_to_sketch(sketch, group)
    return group

# --- Beam & Truss -------------------------------------------------------------

def make_beam(ax, ay, bx, by, scale_factor=1.0):
    """Creates a beam (Balken) as a filled rectangle between two points.

    Args:
        ax, ay: Start point.
        bx, by: End point.
        scale_factor: Controls the beam thickness (not length).
    """
    start_x = ax
    start_y = ay
    length = ((bx - ax) ** 2 + (by - ay) ** 2) ** 0.5
    angle_deg = math.degrees(math.atan2(by - ay, bx - ax))

    x0, y0 = 0.0, -0.4 * scale_factor
    x1, y1 = length, 0.4 * scale_factor
    primitives = [make_rectangle(x0, y0, x1, y1, 0.05 * scale_factor, 5)]

    primitives = rotate(primitives, 0, 0, angle_deg)
    primitives = translate(primitives, start_x, start_y)

    return primitives

def add_beam(sketch, ax, ay, bx, by, scale_factor=1.0, name=""):
    objects = make_beam(ax, ay, bx, by, scale_factor)
    if name == "":
        name = f"Balken ({ax}, {ay}, {bx}, {by}, {scale_factor})"
    group = make_group(objects, name)
    group["c_type"] = "beam"
    group["c_params"] = {"ax": ax, "ay": ay, "bx": bx, "by": by, "scale_factor": scale_factor}
    add_to_sketch(sketch, group)
    return group

def make_truss(ax, ay, bx, by, scale_factor=1.0):
    """Creates a truss member (Dehnstab) as a thick line between two points.

    Args:
        ax, ay: Start point.
        bx, by: End point.
        scale_factor: Controls the line thickness.
    """
    primitives = [make_line(ax, ay, bx, by, 1.0 * scale_factor, 5)]
    return primitives

def add_truss(sketch, ax, ay, bx, by, scale_factor=1.0, name=""):
    objects = make_truss(ax, ay, bx, by, scale_factor)
    if name == "":
        name = f"Dehnstab ({ax}, {ay}, {bx}, {by}, {scale_factor})"
    group = make_group(objects, name)
    group["c_type"] = "truss"
    group["c_params"] = {"ax": ax, "ay": ay, "bx": bx, "by": by, "scale_factor": scale_factor}
    add_to_sketch(sketch, group)
    return group

# --- Forces & Moments ---------------------------------------------------------

def make_arrow(cx=0.0, cy=0.0, length=1.0, angle_deg=0.0, scale_factor=1.0, annotation="", fontsize_scale=1.0, offsetx=0.0, offsety=0.0, rotate_annotation=0):
    """Creates a generic arrow.

    At angle_deg=0, the arrow points to the right (+x).

    Args:
        cx, cy: Tail of the arrow.
        length: Arrow length in coordinate units (divided by scale_factor internally).
        angle_deg: Direction in degrees. 0 = right, 90 = up.
        scale_factor: Uniform scale.
        annotation: Label text (LaTeX supported).
    """
    arrow_head_length = 0.5
    arrow_head_width = 0.35
    length = length/scale_factor
    base_lw = 0.05
    primitives = []

    primitives.append(make_line(0, 0, length, 0, base_lw, 5))
    primitives.append(make_polygon([[length, -arrow_head_width/2], [length + arrow_head_length, 0], [length, arrow_head_width/2]], base_lw, 5, facecolor="black"))

    primitives = scale(primitives, 0, 0, scale_factor, scale_linewidth=True)
    primitives = rotate(primitives, 0, 0, angle_deg)
    primitives = translate(primitives, cx, cy)
    if annotation != "":
        text = make_text(length + 2 * arrow_head_length, -arrow_head_width, annotation, fontsize_scale, 10)
        text = scale(text, 0, 0, scale_factor, scale_linewidth=True)
        text = rotate(text, 0, 0, angle_deg)
        text = translate(text, cx + offsetx, cy + offsety)
        # rotate annotation around its center to the desired angle
        text = rotate(text, text["x"], text["y"], rotate_annotation - angle_deg)
        primitives.append(text)

    return primitives

def add_arrow(sketch, cx=0.0, cy=0.0, length=1.0, angle_deg=0.0, scale_factor=1.0, name="", annotation="", fontsize_scale=1, offsetx=0.0, offsety=0.0, rotate_annotation=0):
    objects = make_arrow(cx=cx, cy=cy, length=length, angle_deg=angle_deg, scale_factor=scale_factor, annotation=annotation, fontsize_scale=fontsize_scale, offsetx=offsetx, offsety=offsety, rotate_annotation=rotate_annotation)
    if name == "":
        name = f"Pfeil ({cx}, {cy}, {length}, {angle_deg}°)"
    group = make_group(objects, name)
    group["c_type"] = "arrow"
    group["c_params"] = {"cx": cx, "cy": cy, "length": length, "angle_deg": angle_deg, "scale_factor": scale_factor, "annotation": annotation, "fontsize_scale": fontsize_scale, "offsetx": offsetx, "offsety": offsety, "rotate_annotation": rotate_annotation}
    add_to_sketch(sketch, group)
    return group

def make_force(cx=0.0, cy=0.0, angle_deg=0.0, scale_factor=1.0, annotation="", fontsize_scale=1, offsetx=0.0, offsety=0.0, rotate_annotation=0, tip_at_surface=False):
    """Creates a force arrow pointing toward the application point.

    At angle_deg=0, the force points downward (arrow tip near the beam,
    shaft extending upward). Designed for a horizontal beam.

    Args:
        cx, cy: Application point (where the force acts).
        angle_deg: Rotation in degrees. 0 = downward, 90 = rightward,
                   180 = upward, -90/270 = leftward.
        scale_factor: Uniform scale.
        annotation: Label text (LaTeX supported).
        tip_at_surface: If True, the arrow tip is exactly at (cx, cy).
                    If False (default), there is a small gap between the
                    tip and the application point (suitable for beams).
    """
    arrow_length = 3.0
    arrow_head_length = 0.7
    arrow_head_width = 0.5
    dy_c = 0.0 if tip_at_surface else 0.5
    base_lw = 0.05
    primitives = []

    primitives.append(make_line(0, dy_c + arrow_head_length, 0, dy_c + arrow_length, base_lw, 8))
    primitives.append(make_polygon([[0, dy_c], [-arrow_head_width/2, dy_c + arrow_head_length], [arrow_head_width/2, dy_c + arrow_head_length]], base_lw, 8))
    primitives = scale(primitives, 0, 0, scale_factor, scale_linewidth=True)
    primitives = rotate(primitives, 0, 0, angle_deg)
    primitives = translate(primitives, cx, cy)

    if annotation != "":
        text = make_text(0, 2 * dy_c + arrow_length, annotation, fontsize_scale, 10)
        text = scale(text, 0, 0, scale_factor, scale_linewidth=True)
        text = rotate(text, 0, 0, angle_deg)
        text = translate(text, cx + offsetx, cy + offsety)
        text = rotate(text, text["x"], text["y"], rotate_annotation - angle_deg)
        primitives.append(text)

    return primitives

def add_force(sketch, cx=0.0, cy=0.0, angle_deg=0.0, scale_factor=1.0, name="", annotation="", fontsize_scale=1, offsetx=0.0, offsety=0.0, rotate_annotation=0, tip_at_surface=False):
    objects = make_force(cx=cx, cy=cy, angle_deg=angle_deg, scale_factor=scale_factor, annotation=annotation, fontsize_scale=fontsize_scale, offsetx=offsetx, offsety=offsety, rotate_annotation=rotate_annotation, tip_at_surface=tip_at_surface)
    if name == "":
        name = f"Kraft ({cx}, {cy}, {angle_deg}°, {scale_factor})"
    group = make_group(objects, name)
    group["c_type"] = "force"
    group["c_params"] = {"cx": cx, "cy": cy, "angle_deg": angle_deg, "scale_factor": scale_factor, "annotation": annotation, "fontsize_scale": fontsize_scale, "offsetx": offsetx, "offsety": offsety, "rotate_annotation": rotate_annotation, "tip_at_surface": tip_at_surface}
    add_to_sketch(sketch, group)
    return group

def make_force_pull(cx=0.0, cy=0.0, angle_deg=0.0, scale_factor=1.0, annotation="", fontsize_scale=1, offsetx=0.0, offsety=0.0, rotate_annotation=0):
    """Creates a pulling force arrow anchored at the structural contact point.

    Unlike make_force (where cx/cy is near the arrowhead), here cx/cy is
    the point on the structure where the force is applied (the far end of
    the arrow shaft).  The arrowhead points AWAY from the structure in the
    direction given by angle_deg.

    Use this for tension / pulling forces where it is natural to specify
    the attachment point on the beam rather than the arrow tip.

    At angle_deg=0, the force pulls downward (same convention as make_force).

    Args:
        cx, cy: Point on the structure where the force is applied.
        angle_deg: Direction of the pull. 0 = downward, 90 = rightward,
                   180 = upward, -90/270 = leftward.
        scale_factor: Uniform scale.
        annotation: Label text (LaTeX supported).
    """
    # Geometry constants (must match make_force)
    dy_c = 0.5
    arrow_length = 3.0
    total_h = dy_c + arrow_length  # 3.5

    theta = math.radians(angle_deg)
    sin_t = math.sin(theta)
    cos_t = math.cos(theta)

    # Shift internal origin so the far end of the shaft lands at (cx, cy).
    # In make_force local coords the far end is at (0, total_h) before scaling.
    # After scale + rotate + translate to (cx_int, cy_int):
    #   far_end = (cx_int - total_h*sf*sin(θ),  cy_int + total_h*sf*cos(θ))
    # We want far_end == (cx, cy):
    shift_x =  total_h * scale_factor * sin_t
    shift_y = -total_h * scale_factor * cos_t
    cx_int = cx + shift_x
    cy_int = cy + shift_y

    # Generate force arrow without annotation (we reposition it ourselves)
    primitives = make_force(cx_int, cy_int, angle_deg, scale_factor)

    if annotation != "":
        # Place annotation near the arrowhead (tip), which is far from the
        # structure.  In local coords the tip sits at y = dy_c, the label
        # should sit a bit beyond that (negative y in pull frame).
        label_h = total_h + 0.25          # slightly past the arrowhead
        text = make_text(0, -label_h, annotation, fontsize_scale, 10)
        text = scale(text, 0, 0, scale_factor, scale_linewidth=True)
        text = rotate(text, 0, 0, angle_deg)
        text = translate(text, cx + offsetx, cy + offsety)
        text = rotate(text, text["x"], text["y"], rotate_annotation - angle_deg)
        primitives.append(text)

    return primitives

def add_force_pull(sketch, cx=0.0, cy=0.0, angle_deg=0.0, scale_factor=1.0, name="", annotation="", fontsize_scale=1, offsetx=0.0, offsety=0.0, rotate_annotation=0):
    objects = make_force_pull(cx=cx, cy=cy, angle_deg=angle_deg, scale_factor=scale_factor, annotation=annotation, fontsize_scale=fontsize_scale, offsetx=offsetx, offsety=offsety, rotate_annotation=rotate_annotation)
    if name == "":
        name = f"Zugkraft ({cx}, {cy}, {angle_deg}°, {scale_factor})"
    group = make_group(objects, name)
    group["c_type"] = "force_pull"
    group["c_params"] = {"cx": cx, "cy": cy, "angle_deg": angle_deg, "scale_factor": scale_factor, "annotation": annotation, "fontsize_scale": fontsize_scale, "offsetx": offsetx, "offsety": offsety, "rotate_annotation": rotate_annotation}
    add_to_sketch(sketch, group)
    return group

def make_moment(cx=0.0, cy=0.0, angle_deg=0.0, scale_factor=1.0, annotation="", fontsize_scale=1, offsetx=0.0, offsety=0.0, rotate_annotation=0):
    """Creates a moment (curved arrow).

    At angle_deg=0, the moment is counterclockwise.

    Args:
        cx, cy: Center of the moment.
        angle_deg: Rotation in degrees.
        scale_factor: Uniform scale.
        annotation: Label text (LaTeX supported).
    """
    arrow_head_length = 0.7
    arrow_head_width = 0.5
    radius = 2.0
    base_lw = 0.05
    primitives = []

    primitives.append(make_arc(0, 0, 2 * radius, 2 * radius, -35, 45, 0.0, base_lw, 8))
    arrow_head = make_polygon([[0, 0], [-arrow_head_width/2, arrow_head_length], [arrow_head_width/2, arrow_head_length]], base_lw, 9)
    arrow_head = rotate(arrow_head, 0, 0, -35)
    arrow_head = translate(arrow_head, radius/math.sqrt(2) * 1.02, -radius/math.sqrt(2) * 1.02)
    primitives.append(arrow_head)
    
    primitives = scale(primitives, 0, 0, scale_factor, scale_linewidth=True)
    primitives = rotate(primitives, 0, 0, angle_deg)
    primitives = translate(primitives, cx, cy)
    
    if annotation != "":
        text = make_text(0.5, radius + 0.5, annotation, fontsize_scale, 10)
        text = scale(text, 0, 0, scale_factor, scale_linewidth=True)
        text = rotate(text, 0, 0, angle_deg)
        text = translate(text, cx + offsetx, cy + offsety)
        text = rotate(text, text["x"], text["y"], rotate_annotation - angle_deg)
        primitives.append(text)

    return primitives

def add_moment(sketch, cx=0.0, cy=0.0, angle_deg=0.0, scale_factor=1.0, name="", annotation="", fontsize_scale=1, offsetx=0.0, offsety=0.0, rotate_annotation=0):
    objects = make_moment(cx=cx, cy=cy, angle_deg=angle_deg, scale_factor=scale_factor, annotation=annotation, fontsize_scale=fontsize_scale, offsetx=offsetx, offsety=offsety, rotate_annotation=rotate_annotation)
    if name == "":
        name = f"Moment ({cx}, {cy}, {angle_deg}°, {scale_factor})"
    group = make_group(objects, name)
    group["c_type"] = "moment"
    group["c_params"] = {"cx": cx, "cy": cy, "angle_deg": angle_deg, "scale_factor": scale_factor, "annotation": annotation, "fontsize_scale": fontsize_scale, "offsetx": offsetx, "offsety": offsety, "rotate_annotation": rotate_annotation}
    add_to_sketch(sketch, group)
    return group

def make_moment_arrow(cx=0.0, cy=0.0, angle_deg=0.0, scale_factor=1.0, annotation="", fontsize_scale=1, offsetx=0.0, offsety=0.0, rotate_annotation=0):
    """Creates a moment arrow (straight arrow with double arrowhead).

    A straight arrow with two arrowheads stacked at the tip (>>),
    representing a moment as a vector.  The double arrowhead at the tip
    distinguishes it visually from a single-headed force arrow.

    At angle_deg=0, the arrow points downward toward the application
    point (same convention as make_force).  The shaft extends upward
    with the double arrowhead near (cx, cy).

    The layout and label positioning follow the same conventions as
    make_force: the arrow is offset by dy_c from the application point,
    and the annotation is placed at the far end of the shaft.

    Args:
        cx, cy: Application point (where the moment acts).
        angle_deg: Rotation in degrees. 0 = downward, 90 = rightward,
                   180 = upward, -90/270 = leftward.
        scale_factor: Uniform scale.
        annotation: Label text (LaTeX supported).
        fontsize_scale: Scale factor for the annotation font size.
        offsetx, offsety: Extra offset for the annotation position.
        rotate_annotation: Rotation for the annotation text in degrees.
    """
    arrow_length = 3.0
    arrow_head_length = 0.7
    arrow_head_width = 0.5
    dy_c = 0.5
    base_lw = 0.05
    primitives = []

    # Shaft line (from behind second arrowhead to far end)
    primitives.append(make_line(0, dy_c + 2 * arrow_head_length, 0, dy_c + arrow_length, base_lw, 8))

    # First arrowhead (tip, closest to application point)
    primitives.append(make_polygon(
        [[0, dy_c], [-arrow_head_width/2, dy_c + arrow_head_length], [arrow_head_width/2, dy_c + arrow_head_length]],
        base_lw, 8))

    # Second arrowhead (stacked behind the first)
    primitives.append(make_polygon(
        [[0, dy_c + arrow_head_length], [-arrow_head_width/2, dy_c + 2 * arrow_head_length], [arrow_head_width/2, dy_c + 2 * arrow_head_length]],
        base_lw, 8))

    primitives = scale(primitives, 0, 0, scale_factor, scale_linewidth=True)
    primitives = rotate(primitives, 0, 0, angle_deg)
    primitives = translate(primitives, cx, cy)

    if annotation != "":
        text = make_text(0, 2 * dy_c + arrow_length, annotation, fontsize_scale, 10)
        text = scale(text, 0, 0, scale_factor, scale_linewidth=True)
        text = rotate(text, 0, 0, angle_deg)
        text = translate(text, cx + offsetx, cy + offsety)
        text = rotate(text, text["x"], text["y"], rotate_annotation - angle_deg)
        primitives.append(text)

    return primitives

def add_moment_arrow(sketch, cx=0.0, cy=0.0, angle_deg=0.0, scale_factor=1.0, name="", annotation="", fontsize_scale=1, offsetx=0.0, offsety=0.0, rotate_annotation=0):
    objects = make_moment_arrow(cx=cx, cy=cy, angle_deg=angle_deg, scale_factor=scale_factor, annotation=annotation, fontsize_scale=fontsize_scale, offsetx=offsetx, offsety=offsety, rotate_annotation=rotate_annotation)
    if name == "":
        name = f"Momentenpfeil ({cx}, {cy}, {angle_deg}°, {scale_factor})"
    group = make_group(objects, name)
    group["c_type"] = "moment_arrow"
    group["c_params"] = {"cx": cx, "cy": cy, "angle_deg": angle_deg, "scale_factor": scale_factor, "annotation": annotation, "fontsize_scale": fontsize_scale, "offsetx": offsetx, "offsety": offsety, "rotate_annotation": rotate_annotation}
    add_to_sketch(sketch, group)
    return group

def _default_distribution(t):
    return 0.5

def make_distributed_load(cx=0.0, cy=0.0, length=5.0, angle_deg=0.0, scale_factor=1.0,
                           distribution=None, annotation="", fontsize_scale=1,
                           offsetx=0.0, offsety=0.0, rotate_annotation=0,
                           show_distribution_line=True, tip_at_surface=False):
    """Creates a distributed load (multiple arrows with connecting line).

    A set of evenly spaced force arrows along a span, connected by a line
    at their far ends.  The distribution function controls individual arrow
    lengths and can produce uniform, triangular, or arbitrary load profiles.

    At angle_deg=0, arrows point downward toward (cx, cy), same as make_force.

    Args:
        cx, cy: Center of the load span (application line on the structure).
        length: Total span in coordinate units (divided by scale_factor
                internally, so length is in the same space as beam endpoints).
        angle_deg: Rotation in degrees. 0 = downward, 90 = rightward.
        scale_factor: Uniform scale.
        distribution: Callable f(t) -> float, where t ∈ [0, 1] is the
                      position along the span (0 = left/start, 1 = right/end).
                      Arrow length at t = 2 × |f(t)| × base_arrow_length.
                      Positive f(t): arrow points toward the structure
                      (like make_force).  Negative f(t): arrow flips,
                      originating at the structure surface and pointing away.
                      Default: lambda t: 0.5 (uniform load).
        annotation: Label text (LaTeX supported), placed above the highest
                    point of the connecting line.
        fontsize_scale: Scale factor for the annotation font size.
        offsetx, offsety: Extra offset for the annotation position.
        rotate_annotation: Rotation for the annotation text in degrees.
        show_distribution_line: If True (default), draw the connecting line
                    showing the distribution shape.
        tip_at_surface: If True, arrow tips are exactly at the application
                    line. If False (default), there is a small gap.
    """
    if distribution is None:
        distribution = _default_distribution

    span = length / scale_factor
    arrow_head_length = 0.7 * 0.7    # 30% smaller than force arrowheads
    arrow_head_width = 0.5 * 0.7     # 30% smaller than force arrowheads
    dy_c = 0.0 if tip_at_surface else 0.5
    base_arrow_length = 2.1          # 30% shorter than force arrows
    base_lw = 0.05

    n_arrows = max(2, round(span))
    primitives = []

    # --- Arrows ---------------------------------------------------------------
    for i in range(n_arrows):
        t = i / (n_arrows - 1) if n_arrows > 1 else 0.5
        x_pos = -span / 2 + t * span
        f_val = distribution(t)
        arrow_len = 2 * abs(f_val) * base_arrow_length

        # Skip arrows too short to fit an arrowhead
        if arrow_len < arrow_head_length * 1.05:
            continue

        if f_val >= 0:
            # Positive: tip near beam (pointing toward structure), shaft up
            tip_y = dy_c
            shaft_bottom = dy_c + arrow_head_length
            shaft_top = dy_c + arrow_len

            primitives.append(make_line(x_pos, shaft_bottom, x_pos, shaft_top, base_lw, 8))
            primitives.append(make_polygon(
                [[x_pos, tip_y],
                 [x_pos - arrow_head_width / 2, shaft_bottom],
                 [x_pos + arrow_head_width / 2, shaft_bottom]],
                base_lw, 8))
        else:
            # Negative: arrow flipped, tip points AWAY from beam (upward)
            # Shaft from beam surface to arrowhead base, head at connecting line
            line_y = dy_c + arrow_len   # connecting line is always positive
            head_base_y = line_y - arrow_head_length

            primitives.append(make_line(x_pos, dy_c, x_pos, head_base_y, base_lw, 8))
            primitives.append(make_polygon(
                [[x_pos, line_y],
                 [x_pos - arrow_head_width / 2, head_base_y],
                 [x_pos + arrow_head_width / 2, head_base_y]],
                base_lw, 8))

    # --- Connecting line (polyline, always on positive side) ------------------
    n_line_pts = max(n_arrows, 120)
    line_points_x = []
    line_points_y = []
    for j in range(n_line_pts):
        t = j / (n_line_pts - 1) if n_line_pts > 1 else 0.5
        x_pos = -span / 2 + t * span
        f_val = distribution(t)
        arrow_len = 2 * abs(f_val) * base_arrow_length
        # Line always on the positive (far-from-beam) side
        y_pos = dy_c + arrow_len

        line_points_x.append(x_pos)
        line_points_y.append(y_pos)

    if show_distribution_line:
        for j in range(len(line_points_x) - 1):
            primitives.append(make_line(
                line_points_x[j], line_points_y[j],
                line_points_x[j + 1], line_points_y[j + 1],
                base_lw, 8))

    # --- Transforms -----------------------------------------------------------
    primitives = scale(primitives, 0, 0, scale_factor, scale_linewidth=True)
    primitives = rotate(primitives, 0, 0, angle_deg)
    primitives = translate(primitives, cx, cy)

    # --- Annotation -----------------------------------------------------------
    if annotation != "":
        # Place label above the highest point of the connecting line
        max_y = max(line_points_y)
        text = make_text(0, max_y + dy_c, annotation, fontsize_scale, 10)
        text = scale(text, 0, 0, scale_factor, scale_linewidth=True)
        text = rotate(text, 0, 0, angle_deg)
        text = translate(text, cx + offsetx, cy + offsety)
        text = rotate(text, text["x"], text["y"], rotate_annotation - angle_deg)
        primitives.append(text)

    return primitives

def add_distributed_load(sketch, cx=0.0, cy=0.0, length=5.0, angle_deg=0.0, scale_factor=1.0,
                          distribution=None, annotation="", fontsize_scale=1,
                          offsetx=0.0, offsety=0.0, rotate_annotation=0,
                          show_distribution_line=True, tip_at_surface=False, name=""):
    objects = make_distributed_load(cx=cx, cy=cy, length=length, angle_deg=angle_deg,
                                    scale_factor=scale_factor, distribution=distribution,
                                    annotation=annotation, fontsize_scale=fontsize_scale,
                                    offsetx=offsetx, offsety=offsety, rotate_annotation=rotate_annotation,
                                    show_distribution_line=show_distribution_line,
                                    tip_at_surface=tip_at_surface)
    if name == "":
        name = f"Streckenlast ({cx}, {cy}, {length}, {angle_deg}°)"
    group = make_group(objects, name)
    group["c_type"] = "distributed_load"
    group["c_params"] = {"cx": cx, "cy": cy, "length": length, "angle_deg": angle_deg,
                         "scale_factor": scale_factor, "annotation": annotation,
                         "fontsize_scale": fontsize_scale, "offsetx": offsetx, "offsety": offsety,
                         "rotate_annotation": rotate_annotation, "show_distribution_line": show_distribution_line,
                         "tip_at_surface": tip_at_surface}
    add_to_sketch(sketch, group)
    return group

def _solve_shear_arrow_positions(span, n_arrows, distribution, gap):
    """Solve for arrow positions with constant gap between consecutive arrows.

    Uses iterative fixed-point method to find positions where:
    - Arrow lengths are proportional to |distribution(t)| at their centers
    - Gap between one arrow's tip and next arrow's tail is constant
    - Arrows fill the entire span from -span/2 to +span/2

    Returns:
        List of (x_position, arrow_length, f_value) tuples
    """
    if n_arrows < 1:
        return []
    if n_arrows == 1:
        t = 0.5
        f_val = distribution(t)
        # Single arrow fills span minus small margins
        arrow_len = span * 0.8
        return [(0.0, arrow_len, f_val)]

    # Initial guess: uniform t positions
    t_values = [(i + 0.5) / n_arrows for i in range(n_arrows)]

    for iteration in range(30):
        # Sample distribution at current positions (use small window average for stability)
        f_values = []
        for t in t_values:
            # Average over small window for stability
            samples = [distribution(max(0, min(1, t + dt)))
                      for dt in [-0.02, -0.01, 0, 0.01, 0.02]]
            f_values.append(sum(samples) / len(samples))

        abs_f_values = [abs(f) for f in f_values]

        # Total space available for arrows = span - gaps
        total_arrow_space = span - (n_arrows - 1) * gap

        # Handle case where all f values are near zero
        sum_abs_f = sum(abs_f_values)
        if sum_abs_f < 1e-10:
            # Minimal arrows when distribution is zero
            arrow_lengths = [arrow_head_length * 1.5] * n_arrows
            k = 1.0
        else:
            # Scale factor to make arrows fit the available space
            k = total_arrow_space / sum_abs_f
            arrow_lengths = [k * abs_f for abs_f in abs_f_values]

        # Ensure minimum arrow length
        arrow_head_length = 0.7 * 0.7
        min_len = arrow_head_length * 1.2
        arrow_lengths = [max(min_len, a) for a in arrow_lengths]

        # Recalculate k after applying minimum
        actual_total = sum(arrow_lengths)
        if actual_total + (n_arrows - 1) * gap > span:
            # Need to shrink - reduce gap or arrow lengths proportionally
            scale = (span - (n_arrows - 1) * gap * 0.5) / actual_total
            arrow_lengths = [a * scale for a in arrow_lengths]

        # Calculate positions sequentially
        x_positions = []
        x = -span / 2 + arrow_lengths[0] / 2
        x_positions.append(x)

        for i in range(1, n_arrows):
            x = x_positions[i-1] + arrow_lengths[i-1] / 2 + gap + arrow_lengths[i] / 2
            x_positions.append(x)

        # Check if we overshoot the right boundary
        last_tip = x_positions[-1] + arrow_lengths[-1] / 2
        if last_tip > span / 2 + 0.01:
            # Compress everything proportionally
            overshoot = last_tip - span / 2
            total_with_gaps = sum(arrow_lengths) + (n_arrows - 1) * gap
            compress = (total_with_gaps - overshoot) / total_with_gaps
            arrow_lengths = [a * compress for a in arrow_lengths]
            # Recalculate positions
            x_positions = []
            x = -span / 2 + arrow_lengths[0] / 2
            x_positions.append(x)
            for i in range(1, n_arrows):
                x = x_positions[i-1] + arrow_lengths[i-1] / 2 + gap * compress + arrow_lengths[i] / 2
                x_positions.append(x)

        # Update t values from positions
        new_t_values = [(x + span / 2) / span for x in x_positions]
        new_t_values = [max(0, min(1, t)) for t in new_t_values]

        # Check convergence
        max_diff = max(abs(new_t_values[i] - t_values[i]) for i in range(n_arrows))
        t_values = new_t_values

        if max_diff < 1e-6:
            break

    # Get final f values at converged positions
    final_f_values = [distribution(t) for t in t_values]

    return list(zip(x_positions, arrow_lengths, final_f_values))


def make_shear_distributed_load(cx=0.0, cy=0.0, length=5.0, angle_deg=0.0, scale_factor=1.0,
                                 distribution=None, annotation="", fontsize_scale=1,
                                 offsetx=0.0, offsety=0.0, rotate_annotation=0,
                                 show_distribution_line=True, tip_at_surface=False):
    """Creates a shear distributed load (arrows parallel to surface).

    A set of evenly spaced arrows pointing along the span, placed slightly
    outside the beam surface.  The distribution function controls individual
    arrow lengths and can produce uniform, triangular, or arbitrary profiles.
    A connecting line above the arrows shows the distribution shape, with
    vertical end lines at the span boundaries.

    At angle_deg=0, the span is horizontal and arrows point left/right.

    Args:
        cx, cy: Center of the load span (application line on the structure).
        length: Total span in coordinate units (divided by scale_factor
                internally, so length is in the same space as beam endpoints).
        angle_deg: Rotation in degrees. 0 = horizontal span.
        scale_factor: Uniform scale.
        distribution: Callable f(t) -> float, where t ∈ [0, 1] is the
                      position along the span (0 = left/start, 1 = right/end).
                      Arrow length at t proportional to |f(t)|.
                      Positive f(t): arrow points in +x direction (rightward
                      at angle_deg=0).  Negative f(t): arrow points in -x
                      direction (leftward).
                      Default: lambda t: 0.5 (uniform load pointing right).
        annotation: Label text (LaTeX supported), placed above the load.
        fontsize_scale: Scale factor for the annotation font size.
        offsetx, offsety: Extra offset for the annotation position.
        rotate_annotation: Rotation for the annotation text in degrees.
        show_distribution_line: If True (default), draw the distribution line
                    and vertical end lines.
        tip_at_surface: If True, arrows are exactly at the application
                    line. If False (default), there is a small gap.
    """
    if distribution is None:
        distribution = _default_distribution

    span = length / scale_factor
    arrow_head_length = 0.7 * 0.7    # 30% smaller than force arrowheads
    arrow_head_width = 0.5 * 0.7     # 30% smaller than force arrowheads
    dy_c = 0.0 if tip_at_surface else 0.5  # offset from beam surface
    dist_line_height = 2.1           # height of distribution line above dy_c
    base_lw = 0.05

    # Arrow density: arrows per unit length (in scaled coordinates)
    arrows_per_unit = 0.7
    n_arrows = max(2, round(span * arrows_per_unit))

    # Gap between arrows (constant spacing between tip and next tail)
    arrow_gap = 0.15

    primitives = []

    # --- Solve for arrow positions --------------------------------------------
    arrow_data = _solve_shear_arrow_positions(span, n_arrows, distribution, arrow_gap)

    # --- Draw arrows ----------------------------------------------------------
    for x_pos, arrow_len, f_val in arrow_data:
        # Skip arrows too short to fit an arrowhead
        if arrow_len < arrow_head_length * 1.1:
            continue

        if f_val >= 0:
            # Positive: arrow points in +x direction (rightward)
            tail_x = x_pos - arrow_len / 2
            tip_x = x_pos + arrow_len / 2

            # Clamp to span boundaries
            if tip_x > span / 2:
                tip_x = span / 2
            if tail_x < -span / 2:
                tail_x = -span / 2

            actual_len = tip_x - tail_x
            if actual_len < arrow_head_length * 1.1:
                continue

            shaft_end_x = tip_x - arrow_head_length

            primitives.append(make_line(tail_x, dy_c, shaft_end_x, dy_c, base_lw, 8))
            primitives.append(make_polygon(
                [[tip_x, dy_c],
                 [tip_x - arrow_head_length, dy_c - arrow_head_width / 2],
                 [tip_x - arrow_head_length, dy_c + arrow_head_width / 2]],
                base_lw, 8))
        else:
            # Negative: arrow points in -x direction (leftward)
            tail_x = x_pos + arrow_len / 2
            tip_x = x_pos - arrow_len / 2

            # Clamp to span boundaries
            if tip_x < -span / 2:
                tip_x = -span / 2
            if tail_x > span / 2:
                tail_x = span / 2

            actual_len = tail_x - tip_x
            if actual_len < arrow_head_length * 1.1:
                continue

            shaft_end_x = tip_x + arrow_head_length

            primitives.append(make_line(tail_x, dy_c, shaft_end_x, dy_c, base_lw, 8))
            primitives.append(make_polygon(
                [[tip_x, dy_c],
                 [tip_x + arrow_head_length, dy_c - arrow_head_width / 2],
                 [tip_x + arrow_head_length, dy_c + arrow_head_width / 2]],
                base_lw, 8))

    # --- Distribution line (polyline showing the distribution shape) ----------
    n_line_pts = max(n_arrows, 120)
    line_points_x = []
    line_points_y = []
    for j in range(n_line_pts):
        t = j / (n_line_pts - 1) if n_line_pts > 1 else 0.5
        x_pos = -span / 2 + t * span
        f_val = distribution(t)
        # Line height varies with |f(t)|
        y_pos = dy_c + dist_line_height * abs(f_val) * 2

        line_points_x.append(x_pos)
        line_points_y.append(y_pos)

    if show_distribution_line:
        for j in range(len(line_points_x) - 1):
            primitives.append(make_line(
                line_points_x[j], line_points_y[j],
                line_points_x[j + 1], line_points_y[j + 1],
                base_lw, 8))

        # --- Vertical end lines -----------------------------------------------
        # Left vertical line: from distribution line down to arrow level
        left_y_top = line_points_y[0]
        primitives.append(make_line(-span / 2, dy_c, -span / 2, left_y_top, base_lw, 8))

        # Right vertical line
        right_y_top = line_points_y[-1]
        primitives.append(make_line(span / 2, dy_c, span / 2, right_y_top, base_lw, 8))

    # --- Transforms -----------------------------------------------------------
    primitives = scale(primitives, 0, 0, scale_factor, scale_linewidth=True)
    primitives = rotate(primitives, 0, 0, angle_deg)
    primitives = translate(primitives, cx, cy)

    # --- Annotation -----------------------------------------------------------
    if annotation != "":
        if show_distribution_line:
            # Place label above the highest point of the distribution line
            max_y = max(line_points_y)
            text_y = max_y + dy_c
        else:
            # Place label closer when no distribution line is drawn
            text_y = dy_c + 0.8
        text = make_text(0, text_y, annotation, fontsize_scale, 10)
        text = scale(text, 0, 0, scale_factor, scale_linewidth=True)
        text = rotate(text, 0, 0, angle_deg)
        text = translate(text, cx + offsetx, cy + offsety)
        text = rotate(text, text["x"], text["y"], rotate_annotation - angle_deg)
        primitives.append(text)

    return primitives

def add_shear_distributed_load(sketch, cx=0.0, cy=0.0, length=5.0, angle_deg=0.0, scale_factor=1.0,
                                distribution=None, annotation="", fontsize_scale=1,
                                offsetx=0.0, offsety=0.0, rotate_annotation=0,
                                show_distribution_line=True, tip_at_surface=False, name=""):
    objects = make_shear_distributed_load(cx=cx, cy=cy, length=length, angle_deg=angle_deg,
                                          scale_factor=scale_factor, distribution=distribution,
                                          annotation=annotation, fontsize_scale=fontsize_scale,
                                          offsetx=offsetx, offsety=offsety, rotate_annotation=rotate_annotation,
                                          show_distribution_line=show_distribution_line,
                                          tip_at_surface=tip_at_surface)
    if name == "":
        name = f"Schubstreckenlast ({cx}, {cy}, {length}, {angle_deg}°)"
    group = make_group(objects, name)
    group["c_type"] = "shear_distributed_load"
    group["c_params"] = {"cx": cx, "cy": cy, "length": length, "angle_deg": angle_deg,
                         "scale_factor": scale_factor, "annotation": annotation,
                         "fontsize_scale": fontsize_scale, "offsetx": offsetx, "offsety": offsety,
                         "rotate_annotation": rotate_annotation, "show_distribution_line": show_distribution_line,
                         "tip_at_surface": tip_at_surface}
    add_to_sketch(sketch, group)
    return group

# --- Dimensions & Coordinate System -------------------------------------------

def make_coordinate_system(cx=0.0, cy=0.0, angle_deg=0.0, scale_factor=1.0, ax1="$x$", ax2="$y$", ax3="$z$", last_axis_out_of_image=True, fontsize_scale=1, rotate_annotation=0, offset_ax1_x=0.0, offset_ax1_y=0.0, offset_ax2_x=0.0, offset_ax2_y=0.0, offset_ax3_x=0.0, offset_ax3_y=0.0):
    """Creates a coordinate system with two in-plane axes and an optional third axis.

    At angle_deg=0, ax1 points right (+x) and ax2 points up (+y).

    Args:
        cx, cy: Origin of the coordinate system.
        angle_deg: Rotation of the entire system.
        ax1, ax2, ax3: Axis labels (LaTeX supported). Set ax3="" to hide.
        last_axis_out_of_image: True = dot (out of plane), False = cross (into plane).
        scale_factor: Uniform scale.
    """
    arrow_length = 3.0
    # linewidth
    base_lw = 0.05
    
    primitives = []
    primitives.extend(make_arrow(0, 0, arrow_length, 0, annotation=ax1, offsetx=offset_ax1_x, offsety=offset_ax1_y, fontsize_scale=fontsize_scale, rotate_annotation=rotate_annotation))
    primitives.extend(make_arrow(0, 0, arrow_length, 90, annotation=ax2, offsetx=offset_ax2_x, offsety=offset_ax2_y, fontsize_scale=fontsize_scale, rotate_annotation=rotate_annotation))
    if ax3 != "":
        primitives.append(make_circle(0, 0, 0.2, linewidth=base_lw, layer=5))  # z-Axis
        if not last_axis_out_of_image:
            c=0.2/math.sqrt(2)
            primitives.append(make_line(-c, -c, c, c, linewidth=base_lw))
            primitives.append(make_line(-c, c, c, -c, linewidth=base_lw))
        else:
            primitives.append(make_circle(0, 0, 0.08, linewidth=base_lw, layer=6, facecolor="black"))
    
    # Adapt ax3 label distance from origin to fontsize — prevents overlap at larger scales
    ax3_base = 0.5 * max(1.0, fontsize_scale)
    primitives.append(make_text(ax3_base + offset_ax3_x, ax3_base + offset_ax3_y, ax3, fontsize_scale, 10, rotation=rotate_annotation))
        
    primitives = scale(primitives, 0, 0, scale_factor, scale_linewidth=True)
    primitives = rotate(primitives, 0, 0, angle_deg, ignore_text=True)
    primitives = translate(primitives, cx, cy)

    return primitives

def add_coordinate_system(sketch, cx=0.0, cy=0.0, angle_deg=0.0, scale_factor=1.0, ax1="$x$", ax2="$y$", ax3="$z$", last_axis_out_of_image=True, fontsize_scale=1, name="", rotate_annotation=0, offset_ax1_x=0.0, offset_ax1_y=0.0, offset_ax2_x=0.0, offset_ax2_y=0.0, offset_ax3_x=0.0, offset_ax3_y=0.0):
    objects = make_coordinate_system(cx=cx, cy=cy, angle_deg=angle_deg, scale_factor=scale_factor, ax1=ax1, ax2=ax2, ax3=ax3, last_axis_out_of_image=last_axis_out_of_image, fontsize_scale=fontsize_scale, rotate_annotation=rotate_annotation, offset_ax1_x=offset_ax1_x, offset_ax1_y=offset_ax1_y, offset_ax2_x=offset_ax2_x, offset_ax2_y=offset_ax2_y, offset_ax3_x=offset_ax3_x, offset_ax3_y=offset_ax3_y)
    if name == "":
        name = f"Koordinatensystem ({cx}, {cy}, {angle_deg}°)"
    group = make_group(objects, name)
    group["c_type"] = "coordinate_system"
    group["c_params"] = {"cx": cx, "cy": cy, "angle_deg": angle_deg, "scale_factor": scale_factor, "ax1": ax1, "ax2": ax2, "ax3": ax3, "last_axis_out_of_image": last_axis_out_of_image, "fontsize_scale": fontsize_scale, "rotate_annotation": rotate_annotation, "offset_ax1_x": offset_ax1_x, "offset_ax1_y": offset_ax1_y, "offset_ax2_x": offset_ax2_x, "offset_ax2_y": offset_ax2_y, "offset_ax3_x": offset_ax3_x, "offset_ax3_y": offset_ax3_y}
    add_to_sketch(sketch, group)
    return group

def make_dimension_arrow(cx=0.0, cy=0.0, length=1.0, angle_deg=0.0, scale_factor=1.0, annotation="", fontsize_scale=1, offsetx=0.0, offsety=0.0, rotate_annotation=0, helper_line_1_length=0.0, helper_line_2_length=0.0):
    """Creates a double-headed dimension arrow.

    Positioned by its center (cx, cy). At angle_deg=0, the dimension is
    horizontal with the arrow line and annotation above the center point.
    To place a dimension below a beam, use angle_deg=180 (flips text and
    arrow to sit below). Helper lines extend in the opposite direction
    of the text (i.e., downward when text is above, upward when text is below).

    Also available as add_dimension_arrow_pp() which takes two endpoints
    instead of center + length + angle.

    Args:
        cx, cy: Center of the dimension span.
        length: Total span in coordinate units (divided by scale_factor internally).
        angle_deg: Rotation in degrees. 0 = horizontal, text above.
                   180 = horizontal, text below. 90 = vertical, text to the left.
        scale_factor: Uniform scale.
        annotation: Label text (LaTeX supported), placed above the arrow line.
        helper_line_1_length: Length of perpendicular helper line at the left/start end.
            Extends opposite to the text direction (downward when text is above).
        helper_line_2_length: Length of perpendicular helper line at the right/end end.
    """
    length = length/scale_factor
    arrow_head_length = 0.5
    arrow_length = length - 2 * arrow_head_length*1.12
    arrow_head_width = 0.35
    dy_c = 0.5 + arrow_head_width/2
    base_lw = 0.05
    primitives = []

    primitives.append(make_line(-arrow_length/2, dy_c, arrow_length/2, dy_c, base_lw, 8))
    head1 = make_polygon([[-arrow_head_length, dy_c], [0, dy_c - arrow_head_width/2], [0, dy_c + arrow_head_width/2]], base_lw, 8, facecolor="black")
    head2 = make_polygon([[arrow_head_length, dy_c], [0, dy_c - arrow_head_width/2], [0, dy_c + arrow_head_width/2]], base_lw, 8, facecolor="black")
    head1 = translate(head1, -arrow_length/2, 0)
    head2 = translate(head2, arrow_length/2, 0)
    primitives.append(head1)
    primitives.append(head2)

    if helper_line_1_length != 0.0:
        primitives.append(make_line(-length/2, dy_c + arrow_head_width, -length/2, -helper_line_1_length/scale_factor, base_lw/2, 8))
    if helper_line_2_length != 0.0:
        primitives.append(make_line(length/2, dy_c + arrow_head_width, length/2, -helper_line_2_length/scale_factor, base_lw/2, 8))

    primitives = scale(primitives, 0, 0, scale_factor, scale_linewidth=True)
    primitives = rotate(primitives, 0, 0, angle_deg)
    primitives = translate(primitives, cx, cy)
    
    if annotation != "":
        text = make_text(0, 2 * dy_c, annotation, fontsize_scale, 10)
        text = scale(text, 0, 0, scale_factor, scale_linewidth=True)
        text = rotate(text, 0, 0, angle_deg)
        text = translate(text, cx + offsetx, cy + offsety)
        text = rotate(text, text["x"], text["y"], rotate_annotation - angle_deg)
        primitives.append(text)

    return primitives

def add_dimension_arrow(sketch, cx=0.0, cy=0.0, length=1.0, angle_deg=0.0, scale_factor=1.0, name="", annotation="", fontsize_scale=1, offsetx=0.0, offsety=0.0, rotate_annotation=0, helper_line_1_length=0.0, helper_line_2_length=0.0):
    objects = make_dimension_arrow(cx=cx, cy=cy, length=length, angle_deg=angle_deg, scale_factor=scale_factor, annotation=annotation, fontsize_scale=fontsize_scale, offsetx=offsetx, offsety=offsety, rotate_annotation=rotate_annotation, helper_line_1_length=helper_line_1_length, helper_line_2_length=helper_line_2_length)
    if name == "":
        name = f"Bemaßungspfeil ({cx}, {cy}, {length}, {angle_deg}°, {scale_factor})"
    group = make_group(objects, name)
    group["c_type"] = "dimension_arrow"
    group["c_params"] = {"cx": cx, "cy": cy, "length": length, "angle_deg": angle_deg, "scale_factor": scale_factor, "annotation": annotation, "fontsize_scale": fontsize_scale, "offsetx": offsetx, "offsety": offsety, "rotate_annotation": rotate_annotation, "helper_line_1_length": helper_line_1_length, "helper_line_2_length": helper_line_2_length}
    add_to_sketch(sketch, group)
    return group

def make_dimension_thickness(cx=0.0, cy=0.0, thickness=1.0, angle_deg=0.0, scale_factor=1.0, annotation="", fontsize_scale=1, offsetx=0.0, offsety=0.0, rotate_annotation=0):
    """Creates a thickness dimension with inward-pointing arrows.

    Positioned by its center (cx, cy). At angle_deg=0, the dimension is
    horizontal with arrows pointing inward to indicate the measured distance.
    The annotation is placed to the right of the arrows. Use angle_deg=180
    to place the annotation to the left, or angle_deg=90 for a vertical
    thickness with annotation above.

    Also available as add_dimension_thickness_pp() which takes two endpoints
    instead of center + thickness + angle.

    Args:
        cx, cy: Center of the thickness.
        thickness: Distance being measured in coordinate units (divided by scale_factor internally).
        angle_deg: Rotation in degrees. 0 = horizontal, 90 = vertical.
        scale_factor: Uniform scale.
        annotation: Label text (LaTeX supported), placed to the right of the arrows.
    """
    thickness = thickness/scale_factor
    arrow_length = 2 * 1.5 + thickness
    arrow_head_length = 0.5
    arrow_head_width = 0.35
    base_lw = 0.05
    primitives = []

    primitives.append(make_line(-arrow_length/2, 0, arrow_length/2, 0, base_lw, 8))
    head1 = make_polygon([[-arrow_head_length, 0], [0, -arrow_head_width/2], [0, arrow_head_width/2]], base_lw, 8, facecolor="black")
    head2 = make_polygon([[arrow_head_length, 0], [0, -arrow_head_width/2], [0, arrow_head_width/2]], base_lw, 8, facecolor="black")
    head1 = translate(head1, thickness/2 + arrow_head_length*1.1, 0)
    head2 = translate(head2, -thickness/2 - arrow_head_length*1.1, 0)
    primitives.append(head1)
    primitives.append(head2)

    primitives = scale(primitives, 0, 0, scale_factor, scale_linewidth=True)
    primitives = rotate(primitives, 0, 0, angle_deg)
    primitives = translate(primitives, cx, cy)
    
    if annotation != "":
        text = make_text(arrow_length/2 + 0.5, 0, annotation, fontsize_scale, 10)
        text = scale(text, 0, 0, scale_factor, scale_linewidth=True)
        text = rotate(text, 0, 0, angle_deg)
        text = translate(text, cx + offsetx, cy + offsety)
        text = rotate(text, text["x"], text["y"], rotate_annotation - angle_deg)
        primitives.append(text)

    return primitives

def add_dimension_thickness(sketch, cx=0.0, cy=0.0, thickness=1.0, angle_deg=0.0, scale_factor=1.0, name="", annotation="", fontsize_scale=1, offsetx=0.0, offsety=0.0, rotate_annotation=0):
    objects = make_dimension_thickness(cx=cx, cy=cy, thickness=thickness, angle_deg=angle_deg, scale_factor=scale_factor, annotation=annotation, fontsize_scale=fontsize_scale, offsetx=offsetx, offsety=offsety, rotate_annotation=rotate_annotation)
    if name == "":
        name = f"Bemaßungsdicke ({cx}, {cy}, {thickness}, {angle_deg}°, {scale_factor})"
    group = make_group(objects, name)
    group["c_type"] = "dimension_thickness"
    group["c_params"] = {"cx": cx, "cy": cy, "thickness": thickness, "angle_deg": angle_deg, "scale_factor": scale_factor, "annotation": annotation, "fontsize_scale": fontsize_scale, "offsetx": offsetx, "offsety": offsety, "rotate_annotation": rotate_annotation}
    add_to_sketch(sketch, group)
    return group

def add_dimension_arrow_pp(sketch, ax, ay, bx, by, scale_factor=1.0, name="", annotation="", fontsize_scale=1, offsetx=0.0, offsety=0.0, rotate_annotation=0, helper_line_1_length=0.0, helper_line_2_length=0.0):
    """Add a dimension arrow between two points A and B.
    
    Convenience wrapper around make_dimension_arrow that computes center,
    length, and angle from the two endpoints.
    """
    cx = (ax + bx) / 2
    cy = (ay + by) / 2
    length = math.sqrt((bx - ax) ** 2 + (by - ay) ** 2)
    angle_deg = math.degrees(math.atan2(by - ay, bx - ax))
    objects = make_dimension_arrow(cx=cx, cy=cy, length=length, angle_deg=angle_deg, scale_factor=scale_factor, annotation=annotation, fontsize_scale=fontsize_scale, offsetx=offsetx, offsety=offsety, rotate_annotation=rotate_annotation, helper_line_1_length=helper_line_1_length, helper_line_2_length=helper_line_2_length)
    if name == "":
        name = f"Bemaßungspfeil PP ({ax}, {ay}) -> ({bx}, {by})"
    group = make_group(objects, name)
    group["c_type"] = "dimension_arrow"
    group["c_params"] = {"cx": cx, "cy": cy, "length": length, "angle_deg": angle_deg, "scale_factor": scale_factor, "annotation": annotation, "fontsize_scale": fontsize_scale, "offsetx": offsetx, "offsety": offsety, "rotate_annotation": rotate_annotation, "helper_line_1_length": helper_line_1_length, "helper_line_2_length": helper_line_2_length}
    add_to_sketch(sketch, group)
    return group

def add_dimension_thickness_pp(sketch, ax, ay, bx, by, scale_factor=1.0, name="", annotation="", fontsize_scale=1, offsetx=0.0, offsety=0.0, rotate_annotation=0):
    """Add a thickness dimension between two points A and B.
    
    Convenience wrapper around make_dimension_thickness that computes center,
    thickness (distance), and angle from the two endpoints.
    """
    cx = (ax + bx) / 2
    cy = (ay + by) / 2
    thickness = math.sqrt((bx - ax) ** 2 + (by - ay) ** 2)
    angle_deg = math.degrees(math.atan2(by - ay, bx - ax))
    objects = make_dimension_thickness(cx=cx, cy=cy, thickness=thickness, angle_deg=angle_deg, scale_factor=scale_factor, annotation=annotation, fontsize_scale=fontsize_scale, offsetx=offsetx, offsety=offsety, rotate_annotation=rotate_annotation)
    if name == "":
        name = f"Bemaßungsdicke PP ({ax}, {ay}) -> ({bx}, {by})"
    group = make_group(objects, name)
    group["c_type"] = "dimension_thickness"
    group["c_params"] = {"cx": cx, "cy": cy, "thickness": thickness, "angle_deg": angle_deg, "scale_factor": scale_factor, "annotation": annotation, "fontsize_scale": fontsize_scale, "offsetx": offsetx, "offsety": offsety, "rotate_annotation": rotate_annotation}
    add_to_sketch(sketch, group)
    return group

def add_text(sketch, x, y, text, fontsize=10, name="", rotation=0, scale_factor=None):
    """Adds a text to the sketch.

    Args:
        x, y: Position of the text.
        text: Text string (LaTeX supported, e.g. r"$F$").
        fontsize: Text size. Interpretation depends on scale_factor:
            - Without scale_factor: raw scene units (75 = large, 30 = medium, 10 = small).
            - With scale_factor: behaves like fontsize_scale in force/moment/dimension,
              i.e. fontsize=1.0 with scale_factor=30 gives the same size as force labels.
        scale_factor: Optional. When provided, the text is scaled like other components
            (fontsize is multiplied by scale_factor). Recommended for consistent sizing.
        rotation: Rotation angle in degrees.
    """
    if scale_factor is not None:
        obj = make_text(0, 0, text, fontsize, rotation=rotation)
        obj = scale(obj, 0, 0, scale_factor)
        obj = translate(obj, x, y)
    else:
        obj = make_text(x, y, text, fontsize, rotation=rotation)
    if name == "":
        name = f"Text ({x}, {y}, '{text}')"
    # Text is usually just a primitive, but to keep consistent with group structure if desired
    # But usually text is just GText. 
    # Let's wrap it in group if we want consistency? No, user asks specifically for predefined objects.
    # Text is kinda primitive. Let's leave it as primitive in editor, or wrap it?
    # Existing editor treats text as primitive.
    add_to_sketch(sketch, obj)
