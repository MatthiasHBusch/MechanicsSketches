import math
from .base import (
    make_line, make_circle, make_rectangle, make_polygon, make_arc, make_text,
    scale, rotate, translate,
    add_to_sketch, make_group
)

# --- Festlager ----------------------------------------------------------------

def make_pinned_support(cx=0.0, cy=0.0, angle_deg=0.0, scale_factor=1.0):
    """
    Creates a pinned support (Festlager).
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
    """
    Creates a roller support (Loslager).
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
    """Creates a fixed support (Einspannung)."""
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
    """Creates a hinge (Gelenk)."""
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
    """Creates a beam."""
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
    """Creates a truss (Dehnstab)."""
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
    """Creates an arrow."""
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

def make_force(cx=0.0, cy=0.0, angle_deg=0.0, scale_factor=1.0, annotation="", fontsize_scale=1, offsetx=0.0, offsety=0.0, rotate_annotation=0):
    """Creates a force arrow."""
    arrow_length = 3.0
    arrow_head_length = 0.7
    arrow_head_width = 0.5
    dy_c = 0.5
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

def add_force(sketch, cx=0.0, cy=0.0, angle_deg=0.0, scale_factor=1.0, name="", annotation="", fontsize_scale=1, offsetx=0.0, offsety=0.0, rotate_annotation=0):
    objects = make_force(cx=cx, cy=cy, angle_deg=angle_deg, scale_factor=scale_factor, annotation=annotation, fontsize_scale=fontsize_scale, offsetx=offsetx, offsety=offsety, rotate_annotation=rotate_annotation)
    if name == "":
        name = f"Kraft ({cx}, {cy}, {angle_deg}°, {scale_factor})"
    group = make_group(objects, name)
    group["c_type"] = "force"
    group["c_params"] = {"cx": cx, "cy": cy, "angle_deg": angle_deg, "scale_factor": scale_factor, "annotation": annotation, "fontsize_scale": fontsize_scale, "offsetx": offsetx, "offsety": offsety, "rotate_annotation": rotate_annotation}
    add_to_sketch(sketch, group)
    return group

def make_moment(cx=0.0, cy=0.0, angle_deg=0.0, scale_factor=1.0, annotation="", fontsize_scale=1, offsetx=0.0, offsety=0.0, rotate_annotation=0):
    """Creates a moment."""
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
        text = make_text(3, 0, annotation, fontsize_scale, 10)
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

# --- Dimensions & Coordinate System -------------------------------------------

def make_coordinate_system(cx=0.0, cy=0.0, angle_deg=0.0, scale_factor=1.0, ax1="$x$", ax2="$y$", ax3="$z$", last_axis_out_of_image=True, fontsize_scale=1, rotate_annotation=0, offset_ax1_x=0.0, offset_ax1_y=0.0, offset_ax2_x=0.0, offset_ax2_y=0.0, offset_ax3_x=0.0, offset_ax3_y=0.0):
    """Creates a coordinate system."""
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
    
    primitives.append(make_text(0.5 + offset_ax3_x, 0.5 + offset_ax3_y, ax3, fontsize_scale, 10, rotation=rotate_annotation))
        
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
    """Creates a dimension arrow."""
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
    """Creates a thickness dimension."""
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

def add_text(sketch, x, y, text, fontsize=10, name="", rotation=0):
    """Adds a text to the sketch."""
    obj = make_text(x, y, text, fontsize, rotation=rotation)
    if name == "":
        name = f"Text ({x}, {y}, '{text}')"
    # Text is usually just a primitive, but to keep consistent with group structure if desired
    # But usually text is just GText. 
    # Let's wrap it in group if we want consistency? No, user asks specifically for predefined objects.
    # Text is kinda primitive. Let's leave it as primitive in editor, or wrap it?
    # Existing editor treats text as primitive.
    add_to_sketch(sketch, obj)
