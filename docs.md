# MechanicsSketches Documentation

**MechanicsSketches** is a Python library for creating, editing, and rendering technical sketches for engineering mechanics. It provides a programmatic API for building sketches composed of primitives and pre-built mechanical components, a Qt-based renderer (with matplotlib fallback) supporting PDF/PNG/SVG output, and a graphical editor built with PyQt5.

---

## Table of Contents

1. [Installation & Requirements](#installation--requirements)
2. [Project Structure](#project-structure)
3. [Quick Start](#quick-start)
4. [Core Concepts](#core-concepts)
   - [Sketch Data Structure](#sketch-data-structure)
   - [Primitives](#primitives)
   - [Transformations](#transformations)
   - [Groups & Components](#groups--components)
5. [Module Reference](#module-reference)
   - [base.py](#basepy)
   - [elements.py](#elementspy)
   - [renderer.py (matplotlib)](#rendererpy)
   - [qt_renderer.py (default)](#qt_rendererpy)
   - [editor.py](#editorpy)
6. [API Reference](#api-reference)
   - [Sketch Management](#sketch-management)
   - [Primitives](#primitives-api)
   - [Transformations](#transformations-api)
   - [Mechanical Elements](#mechanical-elements-api)
7. [Examples](#examples)
8. [JSON Format](#json-format)

---

## Installation & Requirements

### Dependencies

- **Python 3.7+**
- **matplotlib** – For rendering sketches to images
- **PyQt5** – For the graphical editor (optional, only needed for `editor.py`)

### Installation

```bash
# Install dependencies
pip install matplotlib PyQt5

# Add MechanicsSketches to your Python path or install locally
```

### LaTeX Rendering (Optional)

For high-quality text rendering with LaTeX, ensure you have a LaTeX distribution installed (e.g., TeX Live, MiKTeX). The renderer uses `text.usetex: True` by default.

---

## Project Structure

```
MechanicsSketches/
├── __init__.py          # Package initialization, exports all public APIs
├── base.py              # Core primitives, transformations, sketch structure
├── elements.py          # Pre-built mechanical components (supports, forces, etc.)
├── qt_renderer.py       # Qt-based rendering engine (default, supports PDF/PNG/SVG)
├── renderer.py          # Matplotlib-based rendering engine (fallback)
├── editor.py            # PyQt5 graphical editor
├── MechanicsAgent/      # AI agent integration (experimental)
│   ├── __init__.py
│   └── agent.py
└── run_mechanics_agent.py
```

---

## Quick Start

### Creating a Simple Sketch Programmatically

```python
from MechanicsSketches import *
import os

# Create a new sketch
sketch = create_sketch("Simple Beam Example")

# Define scale factor (recommended: 20-40)
S = 30.0

# Add a beam from (0, 0) to (10*S, 0)
add_beam(sketch, ax=0, ay=0, bx=10*S, by=0, scale_factor=S)

# Add supports (angle_deg=0 means pointing upward)
add_pinned_support(sketch, cx=0, cy=0, angle_deg=0, scale_factor=S)
add_roller_support(sketch, cx=10*S, cy=0, angle_deg=0, scale_factor=S)

# Add a force (angle_deg=0 means pointing downward, 180 means upward)
add_force(sketch, cx=5*S, cy=0, angle_deg=0, scale_factor=S, annotation=r"$F$")

# Render and save (Qt renderer is default)
script_dir = os.path.dirname(os.path.abspath(__file__))
render(sketch, filename=os.path.join(script_dir, "beam_example.pdf"), dpi=300)
```

### Using the Graphical Editor

```bash
python -c "from MechanicsSketches.editor import *; import sys; from PyQt5.QtWidgets import QApplication; app = QApplication(sys.argv); win = MainWindow(); win.show(); app.exec_()"
```

---

## Core Concepts

### Sketch Data Structure

A sketch is a Python dictionary with the following structure:

```python
{
    "name": "Sketch Name",
    "objects": [...],       # List of primitives and groups
    "parameters": {...}     # Optional user-defined parameters
}
```

### Primitives

Primitives are the basic building blocks:

| Type      | Description                          | Key Properties                              |
|-----------|--------------------------------------|---------------------------------------------|
| `line`    | A line segment                       | `x: [x0, x1]`, `y: [y0, y1]`                |
| `circle`  | A circle                             | `x`, `y` (center), `r` (radius)             |
| `polygon` | A closed polygon                     | `points: [(x0,y0), (x1,y1), ...]`           |
| `arc`     | An arc segment                       | `x`, `y`, `width`, `height`, `theta1`, `theta2`, `angle` |
| `text`    | Text annotation (supports LaTeX)     | `x`, `y`, `text`, `fontsize`, `rotation`    |

All primitives share common properties:
- `lw` – Line width (default: 1.0)
- `l` – Layer/z-order (higher = on top)
- `edgecolor` – Edge color (default: "black")
- `facecolor` – Fill color (default: "white" or "none")

### Transformations

Three transformation functions operate on primitives or lists of primitives:

- **`translate(obj, dx, dy)`** – Move by offset (dx, dy)
- **`rotate(obj, cx, cy, angle_deg)`** – Rotate around center (cx, cy)
- **`scale(obj, cx, cy, factor, scale_linewidth=False)`** – Scale relative to center

Transformations return new objects (non-destructive).

### Groups & Components

Groups combine multiple primitives into a named collection:

```python
group = make_group(primitives, "Group Name")
```

**Components** are specialized groups with metadata for regeneration:
- `c_type` – Component type identifier (e.g., `"pinned_support"`)
- `c_params` – Parameters used to create the component

---

## Module Reference

### base.py

Core functionality for sketch creation and manipulation.

#### Sketch Management Functions

| Function | Description |
|----------|-------------|
| `create_sketch(name, parameters)` | Create a new empty sketch |
| `add_to_sketch(sketch, obj)` | Add a primitive or group to sketch |
| `make_group(objects, name)` | Create a named group from objects |
| `save_sketch(sketch, filename)` | Save sketch to JSON file |
| `load_sketch(filename)` | Load sketch from JSON file |

#### Primitive Factory Functions

| Function | Description |
|----------|-------------|
| `make_line(x0, y0, x1, y1, linewidth, layer, edgecolor)` | Create a line |
| `make_circle(x, y, r, linewidth, layer, facecolor, edgecolor)` | Create a circle |
| `make_arc(x, y, width, height, theta1, theta2, angle, linewidth, layer, edgecolor)` | Create an arc |
| `make_polygon(points, linewidth, layer, facecolor, edgecolor)` | Create a polygon |
| `make_rectangle(x0, y0, x1, y1, linewidth, layer, facecolor, edgecolor)` | Create a rectangle (polygon) |
| `make_text(x, y, text, fontsize, layer, color, ha, va, rotation, render_mode)` | Create text |

#### Transformation Functions

| Function | Description |
|----------|-------------|
| `translate(obj_or_list, dx, dy)` | Translate objects by (dx, dy) |
| `rotate(obj_or_list, cx, cy, angle_deg, ignore_text=False)` | Rotate around point (cx, cy) |
| `scale(obj_or_list, cx, cy, factor, scale_linewidth=False)` | Scale from center point |

---

### elements.py

Pre-built mechanical components for engineering diagrams.

#### Support Elements

| Function | German Name | Description | Orientation (angle_deg=0) |
|----------|-------------|-------------|---------------------------|
| `make_pinned_support(cx, cy, angle_deg, scale_factor)` | Festlager | Pinned support with triangle and hatching | Below beam, supporting upward |
| `add_pinned_support(sketch, ..., name="")` | | Add to sketch with group wrapper | |
| `make_roller_support(cx, cy, angle_deg, scale_factor)` | Loslager | Roller support with sliding gap | Below beam, supporting upward |
| `add_roller_support(sketch, ..., name="")` | | Add to sketch with group wrapper | |
| `make_fixed_support(cx, cy, angle_deg, scale_factor)` | Einspannung | Fixed/clamped support with wall hatching | Vertical wall, hatching left |
| `add_fixed_support(sketch, ..., name="")` | | Add to sketch with group wrapper | |
| `make_hinge(cx, cy, scale_factor)` | Gelenk | Hinge joint (simple circle) | N/A (no angle param) |
| `add_hinge(sketch, ..., name="")` | | Add to sketch with group wrapper | |

#### Structural Elements

| Function | German Name | Description |
|----------|-------------|-------------|
| `make_beam(ax, ay, bx, by, scale_factor)` | Balken | Rectangular beam between two points |
| `add_beam(sketch, ...)` | | Add to sketch with group wrapper |
| `make_truss(ax, ay, bx, by, scale_factor)` | Dehnstab | Truss member (line) between two points |
| `add_truss(sketch, ...)` | | Add to sketch with group wrapper |

#### Loads & Annotations

| Function | Description | Orientation (angle_deg=0) |
|----------|-------------|---------------------------|
| `make_arrow(cx, cy, length, angle_deg, scale_factor, annotation, fontsize_scale, offsetx, offsety, rotate_annotation)` | Generic arrow | Points rightward (+x) |
| `add_arrow(sketch, ..., name="")` | Add arrow to sketch | |
| `make_force(cx, cy, angle_deg, scale_factor, annotation, fontsize_scale, offsetx, offsety, rotate_annotation, tip_at_surface)` | Force arrow pointing toward the application point | Points downward (toward beam) |
| `add_force(sketch, ..., name="")` | Add force to sketch | |
| `make_force_pull(cx, cy, angle_deg, scale_factor, annotation, fontsize_scale, offsetx, offsety, rotate_annotation)` | Pulling force anchored at structure contact point | Arrowhead points away (e.g. downward) |
| `add_force_pull(sketch, ..., name="")` | Add pulling force to sketch | |
| `make_moment(cx, cy, angle_deg, scale_factor, annotation, fontsize_scale, offsetx, offsety, rotate_annotation)` | Curved moment arrow | Counterclockwise |
| `add_moment(sketch, ..., name="")` | Add moment to sketch | |
| `make_moment_arrow(cx, cy, angle_deg, scale_factor, annotation, fontsize_scale, offsetx, offsety, rotate_annotation)` | Straight arrow with double arrowhead (>>) | Points downward (same as force) |
| `add_moment_arrow(sketch, ..., name="")` | Add moment arrow to sketch | |
| `make_distributed_load(cx, cy, length, angle_deg, scale_factor, distribution, annotation, ..., show_distribution_line, tip_at_surface)` | Distributed load (multiple arrows + connecting line) | Downward, uniform |
| `add_distributed_load(sketch, ..., name="")` | Add distributed load to sketch | |
| `make_shear_distributed_load(cx, cy, length, angle_deg, scale_factor, distribution, annotation, ..., show_distribution_line, tip_at_surface)` | Shear distributed load (arrows parallel to surface) | Rightward, uniform |
| `add_shear_distributed_load(sketch, ..., name="")` | Add shear distributed load to sketch | |

#### Dimensions & Coordinate Systems

| Function | Description | Orientation (angle_deg=0) |
|----------|-------------|---------------------------|
| `make_coordinate_system(cx, cy, angle_deg, scale_factor, ax1, ax2, ax3, last_axis_out_of_image, fontsize_scale, rotate_annotation)` | x-y-z coordinate system | ax1→right, ax2→up |
| `add_coordinate_system(sketch, ..., name="")` | Add coordinate system to sketch | |
| `make_dimension_arrow(cx, cy, length, angle_deg, scale_factor, annotation, fontsize_scale, offsetx, offsety, rotate_annotation)` | Double-headed dimension arrow | Horizontal |
| `add_dimension_arrow(sketch, ..., name="")` | Add dimension to sketch | |
| `make_dimension_thickness(cx, cy, thickness, angle_deg, scale_factor, annotation, fontsize_scale, offsetx, offsety, rotate_annotation)` | Thickness dimension (inward arrows) | Horizontal |
| `add_dimension_thickness(sketch, ..., name="")` | Add thickness dimension to sketch | |
| `add_dimension_arrow_pp(sketch, ax, ay, bx, by, ...)` | Dimension arrow between two points (computes center, length, angle) | A→B direction |
| `add_dimension_thickness_pp(sketch, ax, ay, bx, by, ...)` | Thickness dimension between two points (computes center, distance, angle) | A→B direction |

#### Text

| Function | Description |
|----------|-------------|
| `add_text(sketch, x, y, text, fontsize=10, name="", rotation=0)` | Add text annotation to sketch |

---

### qt_renderer.py

**Default renderer** – Qt-based rendering engine supporting PDF, PNG, JPG, and SVG output.

#### Features

- **Automatic headless mode**: Sets `QT_QPA_PLATFORM=offscreen` when imported as a library
- **Vector output**: Native PDF and SVG export
- **Consistent rendering**: Same rendering engine as the editor GUI

#### Main Function

```python
def render(sketch, filename=None, dpi=300, margin=0.05):
    """
    Render a sketch dictionary to file without opening a GUI.
    
    Args:
        sketch: Sketch dictionary from create_sketch()
        filename: Output path. Format determined by extension:
                  - .pdf → Vector PDF
                  - .png/.jpg/.jpeg → Raster image
                  - .svg → Vector SVG
        dpi: Dots per inch for raster output (default 300)
        margin: Border margin as fraction of content size (default 0.05)
    
    Raises:
        ValueError: If filename is None
        RenderError: If rendering fails
    """
```

---

### renderer.py

Matplotlib-based rendering engine (fallback). Use `mpl_render()` to access this renderer.

#### Configuration

The renderer uses the following matplotlib settings:

```python
plt.rcParams.update({
    "text.usetex": True,
    "font.family": "serif",
    "font.serif": ["Computer Modern Roman"],
})
```

#### Main Function

```python
def mpl_render(sketch, figsize=(5,5), filename=None, dpi=300):
    """
    Renders a hierarchical sketch (objects + groups) using matplotlib.
    
    Args:
        sketch: The sketch dictionary to render
        figsize: Figure size in inches (width, height)
        filename: Output filename (PDF, PNG, SVG, etc.). If None, displays interactively.
        dpi: Resolution for raster output
    """
```

The renderer handles all primitive types:
- **Lines** → `ax.plot()`
- **Circles** → `plt.Circle` patch
- **Polygons** → `plt.Polygon` patch
- **Arcs** → `patches.Arc` patch
- **Text** → `ax.text()` with LaTeX support

Groups are recursively processed to render nested objects.

---

### editor.py

A full-featured graphical editor built with PyQt5.

#### Features

- **Interactive Canvas**: Pan, zoom, select, and move objects
- **Drawing Tools**: Line, circle, rectangle, text
- **Component Library**: Click to place pre-built mechanical elements
- **Object Tree**: Hierarchical view of sketch structure
- **Property Editor**: Modify object properties in real-time
- **File Operations**: New, Open (JSON), Save (JSON), Export (PDF/PNG)

#### Key Classes

| Class | Description |
|-------|-------------|
| `MainWindow` | Main application window with menus, toolbar, docks |
| `SketchScene` | QGraphicsScene handling drawing and interaction |
| `GLine`, `GCircle`, `GPolygon`, `GArc`, `GText`, `GGroup` | QGraphicsItem wrappers for primitives |
| `SketchItemMixin` | Shared behavior for graphics items (selection, sync) |

#### Editor Modes

```python
class EditorMode(Enum):
    SELECT = auto()         # Select and move objects
    DRAW_LINE = auto()      # Draw lines
    DRAW_CIRCLE = auto()    # Draw circles
    DRAW_RECT = auto()      # Draw rectangles
    DRAW_TEXT = auto()      # Place text
    PLACE_COMPONENT = auto() # Place library components
```

#### Launching the Editor

```python
from MechanicsSketches.editor import MainWindow
from PyQt5.QtWidgets import QApplication
import sys

app = QApplication(sys.argv)
window = MainWindow()
window.show()
sys.exit(app.exec_())
```

---

## API Reference

### Sketch Management

```python
# Create a new sketch
sketch = create_sketch(name="My Sketch", parameters={})

# Add objects
add_to_sketch(sketch, obj)

# Save and load
save_sketch(sketch, "sketch.json")
sketch = load_sketch("sketch.json")
```

### Primitives API

```python
# Line from (0,0) to (5,0)
line = make_line(0, 0, 5, 0, linewidth=1.0, layer=5, edgecolor="black")

# Circle at (2,3) with radius 1
circle = make_circle(2, 3, 1, linewidth=1.0, layer=5, facecolor="white", edgecolor="black")

# Rectangle from (0,0) to (4,2)
rect = make_rectangle(0, 0, 4, 2)

# Polygon with custom points
poly = make_polygon([(0,0), (1,2), (3,1)], facecolor="lightgray")

# Arc centered at (0,0)
arc = make_arc(0, 0, width=4, height=4, theta1=0, theta2=90)

# Text with LaTeX
text = make_text(0, 0, r"$F = ma$", fontsize=20, ha="center", va="center")

# Text with rotation
text = make_text(0, 0, "Label", fontsize=20, rotation=90)
```

### Transformations API

```python
# Translate by (dx, dy)
moved = translate(obj, 5, 3)

# Rotate 45° around (0, 0)
rotated = rotate(obj, 0, 0, 45)

# Scale by factor 2.0 from origin
scaled = scale(obj, 0, 0, 2.0)

# Chain transformations
result = translate(rotate(scale(obj, 0, 0, 0.5), 0, 0, 30), 10, 5)
```

### Mechanical Elements API

#### Supports

```python
# Pinned support at (0, 0), supporting from below (angle_deg=0 default)
add_pinned_support(sketch, cx=0, cy=0, angle_deg=0, scale_factor=S)

# Roller support at (10*S, 0), supporting from below
add_roller_support(sketch, cx=10*S, cy=0, angle_deg=0, scale_factor=S)

# Fixed support (wall) at (0, 0)
# angle_deg=0: vertical wall with hatching to the left
# angle_deg=90: horizontal wall with hatching below
add_fixed_support(sketch, cx=0, cy=0, angle_deg=0, scale_factor=S)

# Hinge connection at joint
add_hinge(sketch, cx=5*S, cy=0, scale_factor=S)
```

#### Structural Elements

```python
# Beam from point A to point B
add_beam(sketch, ax=0, ay=0, bx=10, by=0, scale_factor=1.0)

# Truss member (line) from A to B
add_truss(sketch, ax=0, ay=0, bx=5, by=3, scale_factor=1.0)
```

#### Forces & Moments

```python
# Force at (5*S, 0)
# angle_deg=0: pointing downward (toward beam, designed for horizontal beams)
# angle_deg=180: pointing upward
# angle_deg=90: pointing rightward
# angle_deg=-90: pointing leftward
add_force(sketch, cx=5*S, cy=0, angle_deg=0, scale_factor=S, 
          annotation=r"$F$", fontsize_scale=1.0, offsetx=0, offsety=0)

# Force with tip directly at (cx, cy) - no gap (for plate surfaces)
add_force(sketch, cx=5*S, cy=0, angle_deg=0, scale_factor=S,
          annotation=r"$F$", tip_at_surface=True)

# Pulling force (tension) anchored at the beam
# (cx, cy) is where the force attaches to the structure
# Arrowhead points AWAY from structure in the pull direction
# angle_deg=0: pulls downward, 90: pulls rightward, 180: pulls upward
add_force_pull(sketch, cx=10*S, cy=0, angle_deg=90, scale_factor=S,
               annotation=r"$F$")

# Moment at (3*S, 0) with label
# angle_deg=0: counterclockwise
add_moment(sketch, cx=3*S, cy=0, angle_deg=0, scale_factor=S,
           annotation=r"$M$", fontsize_scale=1.0)

# Moment arrow (double-headed straight arrow) at (7*S, 0)
# angle_deg=0: pointing rightward (+x)
# Useful for moment vectors in 3D free body diagrams
add_moment_arrow(sketch, cx=7*S, cy=0, angle_deg=0, scale_factor=S,
                 annotation=r"$M_x$", fontsize_scale=1.0)

# Distributed load (uniform, default distribution=lambda t: 0.5)
add_distributed_load(sketch, cx=5*S, cy=0, length=10*S,
                     scale_factor=S, annotation=r"$q_0$")

# Triangular distributed load (linear, growing left to right)
add_distributed_load(sketch, cx=5*S, cy=0, length=10*S,
                     scale_factor=S, distribution=lambda t: t,
                     annotation=r"$q(x)$")

# Sign-changing load (positive on left, negative on right)
# Negative values flip arrows to point away from structure
add_distributed_load(sketch, cx=5*S, cy=0, length=10*S,
                     scale_factor=S, distribution=lambda t: 0.5 - t)

# Shear distributed load (arrows parallel to surface, tangential)
# Positive f(t): arrows point rightward, negative: leftward
add_shear_distributed_load(sketch, cx=5*S, cy=0, length=10*S,
                           scale_factor=S, annotation=r"$\tau_0$")

# Triangular shear load
add_shear_distributed_load(sketch, cx=5*S, cy=0, length=10*S,
                           scale_factor=S, distribution=lambda t: t,
                           annotation=r"$\tau(x)$")

# Distributed load without connecting line
add_distributed_load(sketch, cx=5*S, cy=0, length=10*S,
                     scale_factor=S, show_distribution_line=False)

# Distributed load with tips at surface (no gap)
add_distributed_load(sketch, cx=5*S, cy=0, length=10*S,
                     scale_factor=S, tip_at_surface=True)

# Shear load without distribution line and vertical end lines
add_shear_distributed_load(sketch, cx=5*S, cy=0, length=10*S,
                           scale_factor=S, show_distribution_line=False)
```

#### Dimensions

```python
# Dimension arrow: centered at (cx, cy), spans 'length' units (in coord space, not scaled)
# angle_deg=0: horizontal, angle_deg=90: vertical (label above)
add_dimension_arrow(sketch, cx=2.5*S, cy=-S, length=5*S, angle_deg=0,
                    scale_factor=S*0.6, annotation=r"$L$", fontsize_scale=1.0)

# Thickness dimension (arrows pointing inward)
add_dimension_thickness(sketch, cx=0, cy=0, thickness=2*S, angle_deg=90,
                        scale_factor=S, annotation=r"$t$", fontsize_scale=1.0)

# Point-to-point dimension arrow (convenience: specify endpoints instead of center)
add_dimension_arrow_pp(sketch, ax=0, ay=-S, bx=5*S, by=-S,
                       scale_factor=S*0.6, annotation=r"$a$")

# Point-to-point thickness dimension
add_dimension_thickness_pp(sketch, ax=-S, ay=0, bx=S, by=0,
                           scale_factor=S, annotation=r"$d$")

# Coordinate system
# angle_deg=0: ax1 points right (+x), ax2 points up (+y)
# angle_deg=180: ax1 points left, ax2 points down (inverted)
# angle_deg=-90: ax1 points down, ax2 points right
# last_axis_out_of_image=True: dot (coming out), False: cross (going in)
add_coordinate_system(sketch, cx=-2*S, cy=-2*S, scale_factor=S,
                      ax1=r"$x$", ax2=r"$y$", ax3=r"$z$",
                      last_axis_out_of_image=True)
```

---

## Examples

### Example 1: Simply Supported Beam with Point Load

```python
from MechanicsSketches import *
import os

sketch = create_sketch("Simply Supported Beam")
S = 30.0  # Scale factor

# Beam
add_beam(sketch, ax=0, ay=0, bx=12*S, by=0, scale_factor=S)

# Supports (angle_deg=0 = upward)
add_pinned_support(sketch, cx=0, cy=0, angle_deg=0, scale_factor=S)
add_roller_support(sketch, cx=12*S, cy=0, angle_deg=0, scale_factor=S)

# Point load at midspan (angle_deg=0 = downward push force)
add_force(sketch, cx=6*S, cy=0, angle_deg=0, scale_factor=S, annotation=r"$P$")

# Dimensions
add_dimension_arrow(sketch, cx=3*S, cy=-S, length=6*S, scale_factor=S*0.6, annotation=r"$a$")
add_dimension_arrow(sketch, cx=9*S, cy=-S, length=6*S, scale_factor=S*0.6, annotation=r"$b$")

# Coordinate system (angle_deg=-90: z down, x right; for beam bending convention)
add_coordinate_system(sketch, cx=-2*S, cy=S, scale_factor=S*0.6,
                      ax1=r"$z$", ax2=r"$x$", ax3=r"$y$")

script_dir = os.path.dirname(os.path.abspath(__file__))
render(sketch, filename=os.path.join(script_dir, "simply_supported_beam.pdf"))
```

### Example 2: Cantilever Beam with Distributed Load

```python
from MechanicsSketches import *
import os

sketch = create_sketch("Cantilever Beam")
S = 30.0

# Fixed support on the left (angle_deg=0 = vertical wall with hatching left)
add_fixed_support(sketch, cx=0, cy=0, angle_deg=0, scale_factor=S)

# Beam
add_beam(sketch, ax=0, ay=0, bx=8*S, by=0, scale_factor=S)

# Multiple forces to simulate distributed load (angle_deg=0 = downward)
for i in range(1, 8):
    add_force(sketch, cx=i*S, cy=0, angle_deg=0, scale_factor=S*0.5)

# Moment at support
add_moment(sketch, cx=0, cy=0, angle_deg=0, scale_factor=S, annotation=r"$M_A$")

script_dir = os.path.dirname(os.path.abspath(__file__))
render(sketch, filename=os.path.join(script_dir, "cantilever.pdf"))
```

### Example 3: Truss Structure

```python
from MechanicsSketches import *
import os

sketch = create_sketch("Simple Truss")
S = 30.0

# Bottom chord (using make_line for thin truss members)
add_to_sketch(sketch, make_line(0, 0, 4*S, 0, linewidth=0.1*S))
add_to_sketch(sketch, make_line(4*S, 0, 8*S, 0, linewidth=0.1*S))

# Top chord
add_to_sketch(sketch, make_line(4*S, 3*S, 0, 0, linewidth=0.1*S))
add_to_sketch(sketch, make_line(4*S, 3*S, 8*S, 0, linewidth=0.1*S))

# Vertical
add_to_sketch(sketch, make_line(4*S, 0, 4*S, 3*S, linewidth=0.1*S))

# Joints
add_hinge(sketch, 0, 0, scale_factor=S)
add_hinge(sketch, 4*S, 0, scale_factor=S)
add_hinge(sketch, 8*S, 0, scale_factor=S)
add_hinge(sketch, 4*S, 3*S, scale_factor=S)

# Supports
add_pinned_support(sketch, cx=0, cy=0, angle_deg=0, scale_factor=S)
add_roller_support(sketch, cx=8*S, cy=0, angle_deg=0, scale_factor=S)

# Load at top (angle_deg=0 = downward force)
add_force(sketch, cx=4*S, cy=3*S, angle_deg=0, scale_factor=S, annotation=r"$F$")

script_dir = os.path.dirname(os.path.abspath(__file__))
render(sketch, filename=os.path.join(script_dir, "truss.pdf"))
```

---

## JSON Format

Sketches are stored as JSON with the following structure:

```json
{
    "name": "Sketch Name",
    "parameters": {},
    "objects": [
        {
            "type": "line",
            "x": [0.0, 5.0],
            "y": [0.0, 0.0],
            "lw": 1.0,
            "l": 5,
            "edgecolor": "black"
        },
        {
            "type": "circle",
            "x": 2.5,
            "y": 0.0,
            "r": 0.4,
            "lw": 1.0,
            "l": 7,
            "facecolor": "white",
            "edgecolor": "black"
        },
        {
            "type": "group",
            "name": "Festlager (0, 0, 0°)",
            "c_type": "pinned_support",
            "c_params": {
                "cx": 0.0,
                "cy": 0.0,
                "angle_deg": 0.0,
                "scale_factor": 1.0
            },
            "objects": [...]
        }
    ]
}
```

### Component Regeneration

Components store their creation parameters in `c_type` and `c_params`. The editor uses these to regenerate components when parameters change:

```python
COMPONENT_FACTORIES = {
    "pinned_support": make_pinned_support,
    "roller_support": make_roller_support,
    "fixed_support": make_fixed_support,
    "hinge": make_hinge,
    "beam": make_beam,
    "truss": make_truss,
    "force": make_force,
    "force_pull": make_force_pull,
    "moment": make_moment,
    "moment_arrow": make_moment_arrow,
    "distributed_load": make_distributed_load,
    "shear_distributed_load": make_shear_distributed_load,
    "coordinate_system": make_coordinate_system,
    "dimension_arrow": make_dimension_arrow,
    "dimension_thickness": make_dimension_thickness,
}
```

---

## License

This library is provided for educational and research purposes.

---

## Contributing

Contributions are welcome! Please ensure any new components follow the existing patterns:

1. Create a `make_*` function that returns a list of primitives
2. Create an `add_*` wrapper that adds the group to a sketch with `c_type` and `c_params`
3. Register the component in `COMPONENT_FACTORIES` if it should be editable in the GUI
