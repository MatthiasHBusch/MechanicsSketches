# MechanicsSketches API Reference

Condensed reference for all public functions. For full documentation, see [docs.md](../../../docs.md).

---

## Sketch Management (`base.py`)

```python
create_sketch(name="", parameters={})
# Returns: dict with keys "name", "objects", "parameters"

add_to_sketch(sketch, obj)
# Adds a primitive or group to sketch["objects"]

make_group(objects, name="")
# Returns: group dict with type="group"

save_sketch(sketch, filename)
# Saves sketch to JSON file

load_sketch(filename)
# Returns: sketch dict from JSON file
```

---

## Primitives (`base.py`)

```python
make_line(x0, y0, x1, y1, linewidth=1.0, layer=5, edgecolor="black")
# Returns: line dict

make_circle(x, y, r, linewidth=1.0, layer=5, facecolor="white", edgecolor="black")
# Returns: circle dict

make_arc(x, y, width, height, theta1, theta2, angle=0, linewidth=1.0, layer=5, edgecolor="black")
# Returns: arc dict

make_polygon(points, linewidth=1.0, layer=5, facecolor="white", edgecolor="black")
# points: list of (x, y) tuples
# Returns: polygon dict

make_rectangle(x0, y0, x1, y1, linewidth=1.0, layer=5, facecolor="white", edgecolor="black")
# Returns: polygon dict (rectangle is a special case of polygon)

make_text(x, y, text, fontsize=20, layer=10, color="black", ha="center", va="center", rotation=0, render_mode="latex")
# Returns: text dict. Use render_mode="plain" to disable LaTeX.
```

---

## Transformations (`base.py`)

```python
translate(obj_or_list, dx, dy)
# Returns: new translated object(s)

rotate(obj_or_list, cx, cy, angle_deg, ignore_text=False)
# Returns: new rotated object(s). Rotates around (cx, cy).

scale(obj_or_list, cx, cy, factor, scale_linewidth=False)
# Returns: new scaled object(s). Scales from center (cx, cy).
```

All transformations are non-destructive (return new objects).

---

## Mechanical Elements (`elements.py`)

All `add_*` functions take `sketch` as first argument and call `add_to_sketch` internally.
All `make_*` functions return a list of primitives without adding to a sketch.

### Supports

```python
add_pinned_support(sketch, cx, cy, angle_deg=0, scale_factor=1.0, name="")
# Pinned support (Festlager). angle_deg=0 → triangle points upward.

add_roller_support(sketch, cx, cy, angle_deg=0, scale_factor=1.0, name="")
# Roller support (Loslager). angle_deg=0 → points upward with sliding gap.

add_fixed_support(sketch, cx, cy, angle_deg=0, scale_factor=1.0, length=1.0, abs_length=None, name="")
# Fixed/clamped support (Einspannung). angle_deg=0 → vertical wall, hatching left.
# length: relative size multiplier (default 1.0).
# abs_length: absolute wall length in scene units (overrides length, scale-independent).

add_hinge(sketch, cx, cy, scale_factor=1.0, name="")
# Hinge joint (Gelenk). Simple circle, no angle parameter.

add_sleeve_support(sketch, cx, cy, angle_deg=0, scale_factor=1.0, name="")
# Sliding sleeve support (Verschiebehülse) — transmits only a moment,
# allows translation in both directions. Rendered as a π-shape (vertical
# crossbar on the left, two horizontal legs pointing right toward the
# beam) plus a fixed wall behind it (parallel to the crossbar).
# (cx, cy) is the beam end; at angle_deg=0 the beam extends to the right.
```

### Structural Elements

```python
add_beam(sketch, ax, ay, bx, by, scale_factor=1.0, name="")
# Rectangular beam from (ax, ay) to (bx, by).

add_truss(sketch, ax, ay, bx, by, scale_factor=1.0, name="")
# Truss member (line) from (ax, ay) to (bx, by).
```

### Gears

```python
add_gear_cut(sketch, cx, cy, r_i=12.0, r_a=45.0, b=30.0, tooth_fraction=0.15,
             angle_deg=0, scale_factor=1.0, name="")
# Cut gear (cross-section view). Three rectangles:
#   - Background: full radial extent (incl. tooth tips), layer 4 (behind shaft).
#   - Two body rectangles above/below the shaft, hatched at half lw, layer 6.
# r_i, r_a, b are in scene units. tooth_fraction sets tooth height / r_a.
# At angle_deg=0, the gear axis is horizontal (along x).

add_gear_side(sketch, cx, cy, r_i=12.0, r_a=45.0, n_teeth=24, tooth_fraction=0.15,
              angle_deg=0, scale_factor=1.0, name="")
# Side-view gear (looking along the rotation axis).
# Outer polygon for the tooth profile (50/50 tooth/gap, rectangular teeth)
# and inner circle for the shaft bore.
# r_i, r_a in scene units. tooth_fraction sets tooth height / r_a.
```

### Loads

```python
add_force(sketch, cx, cy, angle_deg=0, scale_factor=1.0,
          annotation="", fontsize_scale=1.0, fontsize=None, offsetx=0, offsety=0,
          rotate_annotation=False, tip_at_surface=False, name="")
# Force arrow. angle_deg=0 → points downward (toward beam).
# tip_at_surface=True: arrow tip exactly at (cx, cy), no gap.
# tip_at_surface=False (default): small gap between tip and (cx, cy).
# fontsize: absolute font size in points. Final rendered size regardless of scale_factor.

add_moment(sketch, cx, cy, angle_deg=0, scale_factor=1.0,
           annotation="", fontsize_scale=1.0, fontsize=None, offsetx=0, offsety=0,
           rotate_annotation=False, name="")
# Curved moment arrow. angle_deg=0 → counterclockwise.

add_moment_arrow(sketch, cx, cy, angle_deg=0, scale_factor=1.0,
                 annotation="", fontsize_scale=1.0, fontsize=None, offsetx=0, offsety=0,
                 rotate_annotation=False, tip_at_surface=False, name="")
# Straight moment arrow with double arrowhead (>>). angle_deg=0 → downward (same as force).
# Two stacked arrowheads at the tip distinguish it from a single-headed force arrow.
# tip_at_surface=True: arrow tip exactly at (cx, cy), no gap.
# tip_at_surface=False (default): small gap between tip and (cx, cy).

add_moment_arrow_pull(sketch, cx, cy, angle_deg=0, scale_factor=1.0,
                      annotation="", fontsize_scale=1.0, fontsize=None,
                      offsetx=0, offsety=0, rotate_annotation=False, name="")
# Pulling moment arrow (double arrowhead) anchored at the structural contact point.
# Unlike moment_arrow, (cx, cy) is the far end of the shaft (the structure side);
# the double arrowhead points AWAY from the structure in direction angle_deg.
# angle_deg=0 → pulls downward (same convention as force_pull).

add_distributed_load(sketch, cx, cy, length, angle_deg=0, scale_factor=1.0,
                     distribution=lambda t: 0.5, annotation="",
                     fontsize_scale=1.0, fontsize=None, offsetx=0, offsety=0,
                     rotate_annotation=False, show_distribution_line=True,
                     tip_at_surface=False, name="")
# Distributed load (multiple arrows + connecting line). n_arrows auto-computed.
# distribution: f(t) -> float, t ∈ [0,1]. Negative f(t) flips arrows.
# show_distribution_line=False: hides the connecting line.
# tip_at_surface=True: arrow tips exactly at the application line.
# Examples: lambda t: 0.5 (uniform), lambda t: t (triangular).

add_shear_distributed_load(sketch, cx, cy, length, angle_deg=0, scale_factor=1.0,
                           distribution=lambda t: 0.5, annotation="",
                           fontsize_scale=1.0, fontsize=None, offsetx=0, offsety=0,
                           rotate_annotation=False, show_distribution_line=True,
                           tip_at_surface=False, name="")
# Shear distributed load (arrows parallel to surface, tangential).
# Arrows have constant gap between tip and next tail, lengths from distribution.
# show_distribution_line=False: hides distribution line and vertical end lines.
# tip_at_surface=True: arrows exactly at the application line.
# distribution: f(t) -> float, t ∈ [0,1]. Positive → rightward, negative → leftward.
# Examples: lambda t: 0.5 (uniform), lambda t: t (triangular).

add_pressure(sketch, cx, cy, scale_factor=1.0, n=8, annotation="",
             fontsize_scale=1.0, fontsize=None, offsetx=0, offsety=0,
             rotate_annotation=False, angle_deg=0, inward=False, name="")
# Pressure symbol: n radial arrows around a central annotation.
# n: number of arrows arranged in a circle (default 8).
# inward=False (default): arrows point outward from the center (positive pressure convention).
# inward=True: arrows point toward the center (negative pressure / external compression).
# angle_deg: rotates the entire arrow ring.
```

### Dimensions

```python
add_dimension_arrow(sketch, cx, cy, length, angle_deg=0, scale_factor=1.0,
                    annotation="", fontsize_scale=1.0, fontsize=None, offsetx=0, offsety=0,
                    rotate_annotation=False, name="")
# Double-headed dimension arrow centered at (cx, cy).
# length is in coordinate space (not scaled). angle_deg=0 → horizontal.
# fontsize: absolute font size in points. Final rendered size regardless of scale_factor.

add_dimension_thickness(sketch, cx, cy, thickness, angle_deg=0, scale_factor=1.0,
                        annotation="", fontsize_scale=1.0, fontsize=None, offsetx=0, offsety=0,
                        rotate_annotation=False, name="")
# Thickness dimension with inward-pointing arrows. angle_deg=0 → horizontal.

add_dimension_arrow_pp(sketch, ax, ay, bx, by, scale_factor=1.0,
                       annotation="", fontsize_scale=1.0, fontsize=None, offsetx=0, offsety=0,
                       rotate_annotation=False, name="")
# Convenience wrapper: dimension arrow from point A to point B.

add_dimension_thickness_pp(sketch, ax, ay, bx, by, scale_factor=1.0,
                           annotation="", fontsize_scale=1.0, fontsize=None, offsetx=0, offsety=0,
                           rotate_annotation=False, name="")
# Convenience wrapper: thickness dimension from point A to point B.
```

### Coordinate Systems

```python
add_coordinate_system(sketch, cx, cy, angle_deg=0, scale_factor=1.0,
                      ax1="$x$", ax2="$y$", ax3="$z$",
                      last_axis_out_of_image=True,
                      fontsize_scale=1.0, fontsize=None, rotate_annotation=False, name="")
# angle_deg=0 → ax1 points right, ax2 points up.
# last_axis_out_of_image=True → dot (⊙), False → cross (⊗).
# fontsize: absolute font size in points. Final rendered size regardless of scale_factor.
```

### Text

```python
add_text(sketch, x, y, text, fontsize=10, name="", rotation=0)
# Adds a text annotation at (x, y).
```

---

## Rendering

```python
# Qt renderer (default, recommended)
from MechanicsSketches.qt_renderer import render
render(sketch, filename="output.pdf", dpi=300, margin=0.05)
# Formats: .pdf, .png, .jpg, .svg

# Matplotlib renderer (fallback)
from MechanicsSketches.renderer import mpl_render
mpl_render(sketch, figsize=(5, 5), filename="output.pdf", dpi=300)
```

---

## JSON Sketch Format

```json
{
    "name": "Sketch Name",
    "parameters": {},
    "objects": [
        {"type": "line", "x": [0, 5], "y": [0, 0], "lw": 1.0, "l": 5, "edgecolor": "black"},
        {"type": "group", "name": "Support", "c_type": "pinned_support",
         "c_params": {"cx": 0, "cy": 0, "angle_deg": 0, "scale_factor": 30},
         "objects": [...]}
    ]
}
```
