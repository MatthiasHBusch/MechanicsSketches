import sys
import json
import math
from enum import Enum, auto
from functools import partial

from io import BytesIO
try:
    import matplotlib.pyplot as plt
    HAS_MATPLOTLIB = True
except ImportError:
    HAS_MATPLOTLIB = False

from PyQt5.QtWidgets import (QApplication, QMainWindow, QGraphicsScene, QGraphicsView, 
                               QGraphicsItem, QGraphicsLineItem, QGraphicsEllipseItem, 
                               QGraphicsPolygonItem, QGraphicsTextItem, QGraphicsItemGroup,
                               QTreeWidget, QTreeWidgetItem, QDockWidget, QVBoxLayout, 
                               QWidget, QFileDialog, QFormLayout, QLineEdit, QToolBar,
                               QColorDialog, QDoubleSpinBox, QGraphicsPathItem, QTreeWidgetItemIterator,
                               QAbstractItemView, QAction, QMenu, QListWidget, QListWidgetItem, QInputDialog,
                               QGraphicsPixmapItem, QStyle, QComboBox)
from PyQt5.QtCore import Qt, QRectF, QPointF, QSizeF, QByteArray
from PyQt5.QtGui import QPen, QBrush, QColor, QPainter, QPolygonF, QPainterPath, QIcon, QPixmap, QImage, QFont, QTransform
from PyQt5.QtSvg import QGraphicsSvgItem, QSvgRenderer

try:
    import MechanicsSketches.base as ms_base
    import MechanicsSketches.elements as ms_elements
except ImportError:
    try:
        from . import base as ms_base
        from . import elements as ms_elements
    except ImportError:
        import base as ms_base
        import elements as ms_elements

# --- Scale Factor System ------------------------------------------------------
#
# Three independent scale factors to match matplotlib rendering:
#   1. GEOMETRY_SCALE = 1.0 (reference - sketch coordinates used directly)
#   2. FONTSIZE_SCALE - converts fontsize (points) to sketch units
#   3. LINEWIDTH_SCALE - converts linewidth (points) to pixels for cosmetic pens
#
# In matplotlib:
#   - fontsize and linewidth are in POINTS (1 pt = 1/72 inch)
#   - geometry coordinates are in DATA UNITS
#   - The relationship depends on figure size and data range
#
# Reference calculation (for figsize=(10,8) with data spanning ~100 units):
#   - Plot area ≈ 8 inches wide (after margins) = 576 points
#   - 100 data units = 576 points → 1 point ≈ 0.17 data units
#   - fontsize=20 → 20 * 0.17 ≈ 3.4 data units height
#   - linewidth=1 → 1 * 0.17 ≈ 0.17 data units (but we use pixels for cosmetic)
#
# For cosmetic pens (linewidth in pixels):
#   - Screen DPI ≈ 96, so 1 point = 96/72 ≈ 1.33 pixels
#   - At default view, we want linewidth=1 to appear as ~1-2 pixels

GEOMETRY_SCALE = 1.0  # Reference - do not change

# Fontsize: converts matplotlib fontsize (points) to sketch units
# Formula: sketch_units = fontsize_points * FONTSIZE_SCALE
# Derived from typical matplotlib figure: 1 point ≈ 0.17 sketch units
FONTSIZE_SCALE = 1.0  # Tune this to match matplotlib text size

# Linewidth: converts matplotlib linewidth (points) to sketch units
# This makes linewidth scale with zoom (like geometry), matching matplotlib
# Formula: sketch_units = linewidth_points * LINEWIDTH_SCALE
# Using same scale as fontsize for consistency
LINEWIDTH_SCALE = 1.0  # ≈1/3 of fontsize scale for thinner lines

def calculate_sketch_bounds(sketch):
    """Calculate the bounding box of all objects in a sketch.
    Returns (min_x, min_y, max_x, max_y) or None if empty."""
    
    min_x = min_y = float('inf')
    max_x = max_y = float('-inf')
    found_any = False
    
    def process_objects(objects):
        nonlocal min_x, min_y, max_x, max_y, found_any
        for obj in objects:
            obj_type = obj.get("type")
            
            if obj_type == "group" or "objects" in obj:
                process_objects(obj.get("objects", []))
            elif obj_type == "line":
                xs, ys = obj.get("x", [0, 0]), obj.get("y", [0, 0])
                min_x = min(min_x, min(xs))
                max_x = max(max_x, max(xs))
                min_y = min(min_y, min(ys))
                max_y = max(max_y, max(ys))
                found_any = True
            elif obj_type == "circle":
                cx, cy, r = obj.get("x", 0), obj.get("y", 0), obj.get("r", 1)
                min_x = min(min_x, cx - r)
                max_x = max(max_x, cx + r)
                min_y = min(min_y, cy - r)
                max_y = max(max_y, cy + r)
                found_any = True
            elif obj_type == "polygon":
                for px, py in obj.get("points", []):
                    min_x = min(min_x, px)
                    max_x = max(max_x, px)
                    min_y = min(min_y, py)
                    max_y = max(max_y, py)
                    found_any = True
            elif obj_type == "arc":
                cx, cy = obj.get("x", 0), obj.get("y", 0)
                w, h = obj.get("width", 1), obj.get("height", 1)
                min_x = min(min_x, cx - w/2)
                max_x = max(max_x, cx + w/2)
                min_y = min(min_y, cy - h/2)
                max_y = max(max_y, cy + h/2)
                found_any = True
            elif obj_type == "text":
                # Text bounds are approximate (depends on fontsize)
                tx, ty = obj.get("x", 0), obj.get("y", 0)
                fs = obj.get("fontsize", 20) * FONTSIZE_SCALE
                min_x = min(min_x, tx - fs)
                max_x = max(max_x, tx + fs)
                min_y = min(min_y, ty - fs)
                max_y = max(max_y, ty + fs)
                found_any = True
    
    process_objects(sketch.get("objects", []))
    
    if not found_any:
        return None
    
    return (min_x, min_y, max_x, max_y)

def calculate_auto_zoom(sketch, view_width, view_height, margin_factor=0.1):
    """Calculate optimal zoom level to fit sketch in view with margins.
    
    Args:
        sketch: The sketch dictionary
        view_width: View widget width in pixels
        view_height: View widget height in pixels
        margin_factor: Extra margin as fraction of view size (default 10%)
    
    Returns:
        Optimal zoom factor, or default if sketch is empty
    """
    bounds = calculate_sketch_bounds(sketch)
    
    if bounds is None:
        return 5.0  # Default for empty sketch
    
    min_x, min_y, max_x, max_y = bounds
    sketch_width = max_x - min_x
    sketch_height = max_y - min_y
    
    # Avoid division by zero for flat sketches
    if sketch_width < 0.01:
        sketch_width = 1.0
    if sketch_height < 0.01:
        sketch_height = 1.0
    
    # Add margins
    usable_width = view_width * (1 - 2 * margin_factor)
    usable_height = view_height * (1 - 2 * margin_factor)
    
    # Calculate zoom to fit
    zoom_x = usable_width / sketch_width
    zoom_y = usable_height / sketch_height
    
    # Use the smaller zoom to ensure everything fits
    optimal_zoom = min(zoom_x, zoom_y)
    
    # Clamp to reasonable range
    return max(0.1, min(50.0, optimal_zoom))

# --- Constants & Enums --------------------------------------------------------

class EditorMode(Enum):
    SELECT = auto()
    DRAW_LINE = auto()
    DRAW_CIRCLE = auto()
    DRAW_RECT = auto()
    DRAW_TEXT = auto()
    PLACE_COMPONENT = auto()

# Registry for regeneration
COMPONENT_FACTORIES = {
    "pinned_support": ms_elements.make_pinned_support,
    "roller_support": ms_elements.make_roller_support,
    "fixed_support": ms_elements.make_fixed_support,
    "hinge": ms_elements.make_hinge,
    "beam": ms_elements.make_beam,
    "truss": ms_elements.make_truss,
    "arrow": ms_elements.make_arrow,
    "force": ms_elements.make_force,
    "moment": ms_elements.make_moment,
    "coordinate_system": ms_elements.make_coordinate_system,
    "dimension_arrow": ms_elements.make_dimension_arrow,
    "dimension_thickness": ms_elements.make_dimension_thickness,
}

# Helper for regeneration
def regenerate_component(obj):
    if "c_type" not in obj or "c_params" not in obj:
        return False
        
    c_type = obj.get("c_type")
    factory = COMPONENT_FACTORIES.get(c_type)
    if not factory:
        return False
        
    try:
        new_primitives = factory(**obj["c_params"])
        obj["objects"] = new_primitives
        return True
    except Exception as e:
        print(f"Error regenerating component {c_type}: {e}")
        return False

# --- Python Code Generation ---------------------------------------------------

# Maps c_type to the add_* function name for export
COMPONENT_ADD_FUNCTIONS = {
    "pinned_support": "add_pinned_support",
    "roller_support": "add_roller_support",
    "fixed_support": "add_fixed_support",
    "hinge": "add_hinge",
    "beam": "add_beam",
    "truss": "add_truss",
    "arrow": "add_arrow",
    "force": "add_force",
    "moment": "add_moment",
    "coordinate_system": "add_coordinate_system",
    "dimension_arrow": "add_dimension_arrow",
    "dimension_thickness": "add_dimension_thickness",
}

def _format_value(value):
    """Format a Python value for code generation."""
    if isinstance(value, str):
        # Escape backslashes and quotes for string literals
        escaped = value.replace('\\', '\\\\').replace('"', '\\"')
        return f'"{escaped}"'
    elif isinstance(value, bool):
        return "True" if value else "False"
    elif isinstance(value, (int, float)):
        return repr(value)
    elif isinstance(value, list):
        return "[" + ", ".join(_format_value(v) for v in value) + "]"
    elif isinstance(value, tuple):
        return "(" + ", ".join(_format_value(v) for v in value) + ")"
    else:
        return repr(value)

def _generate_python_for_primitive(obj):
    """Generate Python code for a primitive object."""
    obj_type = obj.get("type")
    
    if obj_type == "line":
        x0, x1 = obj["x"]
        y0, y1 = obj["y"]
        lw = obj.get("lw", 1.0)
        layer = obj.get("l", 5)
        edgecolor = obj.get("edgecolor", "black")
        linestyle = obj.get("linestyle", "solid")
        
        # Determine if we need to include linestyle
        include_linestyle = False
        if isinstance(linestyle, (tuple, list)):
            # Always include custom patterns
            include_linestyle = True
        elif linestyle != "solid":
            # Include predefined styles if not default
            include_linestyle = True
        
        if include_linestyle:
            return f'add_to_sketch(sketch, make_line({x0}, {y0}, {x1}, {y1}, linewidth={lw}, layer={layer}, edgecolor={_format_value(edgecolor)}, linestyle={_format_value(linestyle)}))'
        else:
            return f'add_to_sketch(sketch, make_line({x0}, {y0}, {x1}, {y1}, linewidth={lw}, layer={layer}, edgecolor={_format_value(edgecolor)}))'
    
    elif obj_type == "circle":
        x, y, r = obj["x"], obj["y"], obj["r"]
        lw = obj.get("lw", 1.0)
        layer = obj.get("l", 5)
        facecolor = obj.get("facecolor", "white")
        edgecolor = obj.get("edgecolor", "black")
        return f'add_to_sketch(sketch, make_circle({x}, {y}, {r}, linewidth={lw}, layer={layer}, facecolor={_format_value(facecolor)}, edgecolor={_format_value(edgecolor)}))'
    
    elif obj_type == "polygon":
        points = obj["points"]
        lw = obj.get("lw", 1.0)
        layer = obj.get("l", 5)
        facecolor = obj.get("facecolor", "white")
        edgecolor = obj.get("edgecolor", "black")
        return f'add_to_sketch(sketch, make_polygon({_format_value(points)}, linewidth={lw}, layer={layer}, facecolor={_format_value(facecolor)}, edgecolor={_format_value(edgecolor)}))'
    
    elif obj_type == "arc":
        x, y = obj["x"], obj["y"]
        width, height = obj["width"], obj["height"]
        theta1, theta2 = obj["theta1"], obj["theta2"]
        angle = obj.get("angle", 0.0)
        lw = obj.get("lw", 1.0)
        layer = obj.get("l", 5)
        edgecolor = obj.get("edgecolor", "black")
        return f'add_to_sketch(sketch, make_arc({x}, {y}, {width}, {height}, {theta1}, {theta2}, angle={angle}, linewidth={lw}, layer={layer}, edgecolor={_format_value(edgecolor)}))'
    
    elif obj_type == "text":
        x, y = obj["x"], obj["y"]
        text = obj["text"]
        fontsize = obj.get("fontsize", 20)
        layer = obj.get("l", 10)
        color = obj.get("color", "black")
        ha = obj.get("ha", "center")
        va = obj.get("va", "center")
        rotation = obj.get("rotation", 0.0)
        return f'add_to_sketch(sketch, make_text({x}, {y}, {_format_value(text)}, fontsize={fontsize}, layer={layer}, color={_format_value(color)}, ha={_format_value(ha)}, va={_format_value(va)}, rotation={rotation}))'
    
    return f"# Unknown primitive type: {obj_type}"

def _generate_python_for_component(obj):
    """Generate Python code for a component (group with c_type)."""
    c_type = obj.get("c_type")
    c_params = obj.get("c_params", {})
    
    func_name = COMPONENT_ADD_FUNCTIONS.get(c_type)
    if not func_name:
        return f"# Unknown component type: {c_type}"
    
    # Format parameters
    params_str = ", ".join(f"{k}={_format_value(v)}" for k, v in c_params.items())
    return f"{func_name}(sketch, {params_str})"

def _generate_python_for_object(obj, indent=0):
    """Generate Python code for any object (primitive, component, or group)."""
    prefix = "    " * indent
    
    obj_type = obj.get("type")
    
    # Component (has c_type)
    if "c_type" in obj:
        return prefix + _generate_python_for_component(obj)
    
    # Regular group (no c_type)
    if obj_type == "group":
        lines = [prefix + f"# Group: {obj.get('name', 'unnamed')}"]
        for child in obj.get("objects", []):
            lines.append(_generate_python_for_object(child, indent))
        return "\n".join(lines)
    
    # Primitive
    return prefix + _generate_python_for_primitive(obj)

def generate_python_script(sketch, output_pdf_name=None):
    """Generate a complete Python script that recreates the sketch and renders to PDF."""
    sketch_name = sketch.get("name", "Sketch")
    if output_pdf_name is None:
        # Sanitize name for filename
        output_pdf_name = sketch_name.replace(" ", "_").lower() + ".pdf"
    
    lines = [
        "from MechanicsSketches import *",
        "import os",
        "",
        f"# Create sketch",
        f"sketch = create_sketch({_format_value(sketch_name)})",
        "",
        "# Objects",
    ]
    
    for obj in sketch.get("objects", []):
        lines.append(_generate_python_for_object(obj))
    
    lines.extend([
        "",
        "# Render to PDF (same folder as script)",
        "script_dir = os.path.dirname(os.path.abspath(__file__))",
        f"output_path = os.path.join(script_dir, {_format_value(output_pdf_name)})",
        "render(sketch, figsize=(10, 8), filename=output_path, dpi=300)",
        f"print(f'Saved to {{output_path}}')",
    ])
    
    return "\n".join(lines)



class SketchItemMixin:
    """Mixin to link QGraphicsItem with the sketch dictionary object."""
    def __init__(self, data_obj):
        self.data_obj = data_obj
        self.setFlag(QGraphicsItem.ItemIsSelectable, True)
        self.setFlag(QGraphicsItem.ItemIsMovable, True)
        self.setFlag(QGraphicsItem.ItemSendsGeometryChanges, True)
        self.update_style()
        self.setZValue(data_obj.get("l", 0))

    def itemChange(self, change, value):
        return super().itemChange(change, value)
    
    def update_style(self):
        pass

    def sync_to_data(self):
        """Updates self.data_obj from current item state."""
        pass
    
    def draw_selection_highlight(self, painter):
        """Draw a thin cosmetic selection rectangle if item is selected."""
        # Only draw if item is selectable (not a child in a group)
        if not (self.flags() & QGraphicsItem.ItemIsSelectable):
            return
        if self.isSelected():
            rect = self.boundingRect()
            pen = QPen(QColor(0, 120, 215))  # Windows selection blue
            pen.setCosmetic(True)  # Fixed pixel width regardless of zoom
            pen.setWidthF(1.0)  # 1 pixel wide
            pen.setStyle(Qt.DashLine)
            painter.setPen(pen)
            painter.setBrush(QBrush(Qt.NoBrush))
            painter.drawRect(rect)

class GLine(SketchItemMixin, QGraphicsLineItem):
    def __init__(self, data_obj):
        QGraphicsLineItem.__init__(self)
        super().__init__(data_obj)
        self.setLine(data_obj["x"][0], data_obj["y"][0], data_obj["x"][1], data_obj["y"][1])
        self.update_style()

    def update_style(self):
        pen = QPen(QColor(self.data_obj.get("edgecolor", "black")))
        # Non-cosmetic pen: linewidth scales with zoom (matching matplotlib)
        pen.setWidthF(self.data_obj.get("lw", 1.0) * LINEWIDTH_SCALE)
        
        # Handle linestyle - can be string or tuple for custom patterns
        linestyle = self.data_obj.get("linestyle", "solid")
        
        if isinstance(linestyle, (tuple, list)):
            # Custom dash pattern - Qt accepts Python list directly
            # Pattern values are in units of pen width
            dash_pattern = [float(value) for value in linestyle]
            pen.setDashPattern(dash_pattern)
        else:
            # Predefined string style
            linestyle_map = {
                "solid": Qt.SolidLine,
                "dashed": Qt.DashLine,
                "dotted": Qt.DotLine,
                "dashdot": Qt.DashDotLine
            }
            qt_linestyle = linestyle_map.get(linestyle, Qt.SolidLine)
            pen.setStyle(qt_linestyle)
        
        self.setPen(pen)

    def mouseReleaseEvent(self, event):
        super().mouseReleaseEvent(event)
        self.sync_to_data()

    def sync_to_data(self):
        p = self.pos()
        l = self.line()
        self.data_obj["x"] = [l.x1() + p.x(), l.x2() + p.x()]
        self.data_obj["y"] = [l.y1() + p.y(), l.y2() + p.y()]
        self.setPos(0, 0)
        self.setLine(self.data_obj["x"][0], self.data_obj["y"][0], self.data_obj["x"][1], self.data_obj["y"][1])

    def paint(self, painter, option, widget=None):
        # Disable default Qt selection highlight
        option.state &= ~QStyle.State_Selected
        super().paint(painter, option, widget)
        self.draw_selection_highlight(painter)

class GCircle(SketchItemMixin, QGraphicsEllipseItem):
    def __init__(self, data_obj):
        QGraphicsEllipseItem.__init__(self)
        super().__init__(data_obj)
        r = data_obj["r"]
        self.setRect(data_obj["x"] - r, data_obj["y"] - r, 2*r, 2*r)
        self.update_style()

    def update_style(self):
        pen = QPen(QColor(self.data_obj.get("edgecolor", "black")))
        # Non-cosmetic pen: linewidth scales with zoom (matching matplotlib)
        pen.setWidthF(self.data_obj.get("lw", 1.0) * LINEWIDTH_SCALE)
        self.setPen(pen)
        fc = self.data_obj.get("facecolor", "none")
        if fc != "none":
            self.setBrush(QBrush(QColor(fc)))
        else:
            self.setBrush(QBrush(Qt.NoBrush))

    def mouseReleaseEvent(self, event):
        super().mouseReleaseEvent(event)
        self.sync_to_data()

    def sync_to_data(self):
        p = self.pos()
        rect = self.rect()
        r = rect.width() / 2
        cx = rect.x() + r + p.x()
        cy = rect.y() + r + p.y()
        self.data_obj["x"] = cx
        self.data_obj["y"] = cy
        self.setPos(0, 0)
        self.setRect(cx - r, cy - r, 2*r, 2*r)

    def paint(self, painter, option, widget=None):
        option.state &= ~QStyle.State_Selected
        super().paint(painter, option, widget)
        self.draw_selection_highlight(painter)

class GPolygon(SketchItemMixin, QGraphicsPolygonItem):
    def __init__(self, data_obj):
        QGraphicsPolygonItem.__init__(self)
        super().__init__(data_obj)
        self.setPolygon(QPolygonF([QPointF(x, y) for x, y in data_obj["points"]]))
        self.update_style()

    def update_style(self):
        pen = QPen(QColor(self.data_obj.get("edgecolor", "black")))
        # Non-cosmetic pen: linewidth scales with zoom (matching matplotlib)
        pen.setWidthF(self.data_obj.get("lw", 1.0) * LINEWIDTH_SCALE)
        self.setPen(pen)
        fc = self.data_obj.get("facecolor", "none")
        if fc != "none":
            self.setBrush(QBrush(QColor(fc)))
        else:
            self.setBrush(QBrush(Qt.NoBrush))
    
    def mouseReleaseEvent(self, event):
        super().mouseReleaseEvent(event)
        self.sync_to_data()

    def sync_to_data(self):
        p = self.pos()
        poly = self.polygon()
        new_points = []
        for pt in poly:
            new_points.append((pt.x() + p.x(), pt.y() + p.y()))
        self.data_obj["points"] = new_points
        self.setPos(0, 0)
        self.setPolygon(QPolygonF([QPointF(x, y) for x, y in new_points]))

    def paint(self, painter, option, widget=None):
        option.state &= ~QStyle.State_Selected
        super().paint(painter, option, widget)
        self.draw_selection_highlight(painter)

class GArc(SketchItemMixin, QGraphicsPathItem):
    def __init__(self, data_obj):
        QGraphicsPathItem.__init__(self)
        super().__init__(data_obj)
        self.update_path()
        self.update_style()

    def update_path(self):
        path = QPainterPath()
        x, y = self.data_obj["x"], self.data_obj["y"]
        w, h = self.data_obj["width"], self.data_obj["height"]
        theta1, theta2 = self.data_obj["theta1"], self.data_obj["theta2"]
        rect = QRectF(x - w/2, y - h/2, w, h)
        path.arcMoveTo(rect, theta1)
        path.arcTo(rect, theta1, theta2 - theta1)
        self.setPath(path)

    def update_style(self):
        pen = QPen(QColor(self.data_obj.get("edgecolor", "black")))
        # Non-cosmetic pen: linewidth scales with zoom (matching matplotlib)
        pen.setWidthF(self.data_obj.get("lw", 1.0) * LINEWIDTH_SCALE)
        self.setPen(pen)
        self.setBrush(QBrush(Qt.NoBrush))

    def mouseReleaseEvent(self, event):
        super().mouseReleaseEvent(event)
        self.sync_to_data()

    def sync_to_data(self):
        p = self.pos()
        self.data_obj["x"] += p.x()
        self.data_obj["y"] += p.y()
        self.setPos(0, 0)
        self.update_path()

    def paint(self, painter, option, widget=None):
        option.state &= ~QStyle.State_Selected
        super().paint(painter, option, widget)
        self.draw_selection_highlight(painter)

def render_mpl_svg(text, fontsize, color="black", use_latex=True):
    """Render text using matplotlib to SVG, return SVG data and size for vector rendering."""
    if not HAS_MATPLOTLIB:
        return None
    
    try:
        from PyQt5.QtSvg import QSvgRenderer
        from PyQt5.QtCore import QByteArray
        
        # Configure matplotlib
        import matplotlib
        old_usetex = matplotlib.rcParams.get('text.usetex', False)
        matplotlib.rcParams['text.usetex'] = use_latex
        
        fig = plt.figure(facecolor="none", edgecolor="none")
        fig.text(0, 0, text, color=color, fontsize=fontsize)
        
        buf = BytesIO()
        fig.savefig(buf, format='svg', transparent=True, bbox_inches='tight', pad_inches=0.02)
        plt.close(fig)
        
        # Restore setting
        matplotlib.rcParams['text.usetex'] = old_usetex
        
        buf.seek(0)
        svg_data = buf.getvalue()
        
        # Get SVG size
        renderer = QSvgRenderer(QByteArray(svg_data))
        if not renderer.isValid():
            return None
        
        svg_size = renderer.defaultSize()
        
        # Return SVG bytes, width, height
        return svg_data, svg_size.width(), svg_size.height()
    except Exception as e:
        print(f"matplotlib SVG render error: {e}")
        return None


def render_typst(text, fontsize, color="black"):
    """Render text using Typst subprocess, return SVG data and size for vector rendering."""
    import subprocess
    import tempfile
    import os
    from PyQt5.QtSvg import QSvgRenderer
    from PyQt5.QtCore import QByteArray
    
    try:
        # Create temp .typ file
        typ_content = f'#set page(width: auto, height: auto, margin: 2pt)\n#set text(size: {fontsize}pt, fill: rgb("{color}"))\n{text}'
        
        with tempfile.NamedTemporaryFile(mode='w', suffix='.typ', delete=False, encoding='utf-8') as f:
            f.write(typ_content)
            typ_path = f.name
        
        svg_path = typ_path.replace('.typ', '.svg')
        
        # Run typst
        result = subprocess.run(['typst', 'compile', '--format', 'svg', typ_path, svg_path], 
                                capture_output=True, text=True, timeout=10)
        
        if result.returncode != 0:
            print(f"Typst error: {result.stderr}")
            os.unlink(typ_path)
            return None
        
        # Load SVG
        with open(svg_path, 'rb') as f:
            svg_data = f.read()
        
        # Cleanup
        os.unlink(typ_path)
        os.unlink(svg_path)
        
        # Get SVG size
        renderer = QSvgRenderer(QByteArray(svg_data))
        if not renderer.isValid():
            return None
        
        svg_size = renderer.defaultSize()
        
        # Return SVG bytes, width, height
        return svg_data, svg_size.width(), svg_size.height()
    except FileNotFoundError:
        print("Typst not found - install with: cargo install typst-cli")
        return None
    except Exception as e:
        print(f"Typst render error: {e}")
        return None


# Font priority for Qt native text rendering
MATH_FONTS = ["CMU Serif", "Computer Modern", "Latin Modern Roman", "STIX Two Text", "Times New Roman"]
_cached_math_font = None

def get_math_font():
    """Get the best available math font, with caching."""
    global _cached_math_font
    if _cached_math_font is not None:
        return _cached_math_font
    
    from PyQt5.QtGui import QFontDatabase
    db = QFontDatabase()
    available = db.families()
    
    for font_name in MATH_FONTS:
        if font_name in available:
            _cached_math_font = font_name
            return font_name
    
    _cached_math_font = ""  # Empty string = use default
    return ""


# GText uses FONTSIZE_SCALE defined at top of file

class GText(SketchItemMixin, QGraphicsItemGroup):
    def __init__(self, data_obj):
        QGraphicsItemGroup.__init__(self)
        self.data_obj = data_obj 
        
        self.setFlag(QGraphicsItem.ItemIsSelectable, True)
        self.setFlag(QGraphicsItem.ItemIsMovable, True)
        self.setFlag(QGraphicsItem.ItemSendsGeometryChanges, True)
        self.setZValue(data_obj.get("l", 0))

        self.rebuild_content()
        
    def rebuild_content(self):
        # Clear existing children
        for child in self.childItems():
            self.removeFromGroup(child)
            if self.scene():
                self.scene().removeItem(child)

        text = self.data_obj.get("text", "")
        color = self.data_obj.get("color", "black")
        fontsize = float(max(0.1, self.data_obj.get("fontsize", 20)))
        
        ha = self.data_obj.get("ha", "center")
        va = self.data_obj.get("va", "center")
        angle = self.data_obj.get("rotation", 0.0)
        
        # Get render mode: from data, or bake in global default on first render
        render_mode = self.data_obj.get("render_mode")
        if render_mode is None and self.scene():
            # Bake in the current global default so it doesn't change later
            render_mode = self.scene().defaults.get("text_render_mode", "auto")
            self.data_obj["render_mode"] = render_mode
        if render_mode is None:
            render_mode = "auto"
        
        # Handle "auto" mode - resolves to actual mode
        if render_mode == "auto":
            render_mode = "mpl_latex" if "$" in text else "qt"
        
        item = None
        scale_factor = 1.0
        w, h = 0, 0
        
        # Target height in sketch units
        target_height = fontsize * FONTSIZE_SCALE
        
        # Dispatch to appropriate renderer
        if render_mode == "mpl_latex":
            result = render_mpl_svg(text, fontsize, color, use_latex=True)
            if result:
                svg_data, svg_w, svg_h = result
                # Create SVG item from bytes
                renderer = QSvgRenderer(QByteArray(svg_data))
                item = QGraphicsSvgItem()
                item.setSharedRenderer(renderer)
                # Store renderer to prevent garbage collection
                item._svg_renderer = renderer
                
                actual_h = svg_h
                scale_factor = target_height / actual_h if actual_h > 0 else 1.0
                item.setTransform(item.transform().scale(scale_factor, -scale_factor))
                w, h = svg_w * scale_factor, svg_h * scale_factor
        
        elif render_mode == "mpl_mathtext":
            result = render_mpl_svg(text, fontsize, color, use_latex=False)
            if result:
                svg_data, svg_w, svg_h = result
                renderer = QSvgRenderer(QByteArray(svg_data))
                item = QGraphicsSvgItem()
                item.setSharedRenderer(renderer)
                item._svg_renderer = renderer
                
                actual_h = svg_h
                scale_factor = target_height / actual_h if actual_h > 0 else 1.0
                item.setTransform(item.transform().scale(scale_factor, -scale_factor))
                w, h = svg_w * scale_factor, svg_h * scale_factor
        
        elif render_mode == "typst":
            result = render_typst(text, fontsize, color)
            if result:
                svg_data, svg_w, svg_h = result
                renderer = QSvgRenderer(QByteArray(svg_data))
                item = QGraphicsSvgItem()
                item.setSharedRenderer(renderer)
                item._svg_renderer = renderer
                
                actual_h = svg_h
                scale_factor = target_height / actual_h if actual_h > 0 else 1.0
                item.setTransform(item.transform().scale(scale_factor, -scale_factor))
                w, h = svg_w * scale_factor, svg_h * scale_factor
        
        # Qt native or fallback
        if not item:
            item = QGraphicsTextItem(text)
            f = item.font()
            
            # Use math font if available
            math_font = get_math_font()
            if math_font:
                f.setFamily(math_font)
            
            # Render at high resolution for quality
            render_px = 200
            f.setPixelSize(render_px)
            f.setStyleStrategy(QFont.PreferAntialias)
            item.setFont(f)
            
            rect = item.boundingRect()
            actual_px = rect.height()
            scale_factor = target_height / actual_px if actual_px > 0 else 1.0
            item.setTransform(item.transform().scale(scale_factor, -scale_factor))
            w, h = rect.width() * scale_factor, rect.height() * scale_factor

        if item:
            # Alignment Logic
            x_shift = 0
            y_shift = 0
            
            # Horizontal
            if ha == 'center': x_shift = -w / 2
            elif ha == 'right': x_shift = -w
            
            # Vertical (Y-flipped coordinates)
            if va == 'center': y_shift = h / 2
            elif va == 'bottom': y_shift = h
            elif va == 'baseline': y_shift = 0
            
            item.setPos(x_shift, y_shift)
            item.setFlag(QGraphicsItem.ItemIsSelectable, False)
            self.addToGroup(item)

        # Move Group to data pos and rotation
        self.setPos(self.data_obj.get("x", 0), self.data_obj.get("y", 0))
        self.setRotation(angle)


    def update_style(self):
        self.rebuild_content()
        # Also sync data pos if needed? No, update_style usually called on property change.
        # If x/y changed, setPos will be handled by rebuild_content currently.
        # But wait: GGroup logic separates pos.
        # self.rebuild_content() already calls self.setPos(x,y).

    def mouseReleaseEvent(self, event):
        super().mouseReleaseEvent(event)
        self.sync_to_data()

    def sync_to_data(self):
        d = self.pos()
        self.data_obj["x"] = d.x()
        self.data_obj["y"] = d.y()

    def paint(self, painter, option, widget=None):
        # Disable default Qt selection highlight
        option.state &= ~QStyle.State_Selected
        super().paint(painter, option, widget)
        if self.isSelected():
            rect = self.boundingRect()
            pen = QPen(QColor(0, 120, 215))
            pen.setCosmetic(True)
            pen.setWidthF(1.0)
            pen.setStyle(Qt.DashLine)
            painter.setPen(pen)
            painter.setBrush(QBrush(Qt.NoBrush))
            painter.drawRect(rect)

class GGroup(QGraphicsItem):
    """
    A logical group that tracks child items but adds them directly to the scene,
    preserving their individual/global z-values for correct layer ordering.
    """
    def __init__(self, data_obj, scene_ref):
        QGraphicsItem.__init__(self)
        self.data_obj = data_obj
        self.scene_ref = scene_ref
        self.child_items = []  # Track children manually
        
        self.setFlag(QGraphicsItem.ItemIsSelectable, True)
        self.setFlag(QGraphicsItem.ItemIsMovable, True)
        # Note: No ItemHasNoContents - we want the group to be clickable via shape()
        
        self.rebuild_children()

    def rebuild_children(self):
        # Remove existing children from scene
        for child in self.child_items:
            if self.scene_ref:
                self.scene_ref.removeItem(child)
        self.child_items = []

        for child_obj in self.data_obj["objects"]:
            item = self.scene_ref.create_item(child_obj)
            if item:
                # Disable selection/movement on children - only parent group should be selectable
                item.setFlag(QGraphicsItem.ItemIsSelectable, False)
                item.setFlag(QGraphicsItem.ItemIsMovable, False)
                # Store reference to parent group for click-through selection
                item.parent_group = self
                # Set GLOBAL z-value from child's own layer data
                item.setZValue(child_obj.get("l", 0))
                # Add directly to scene, NOT as group child
                self.scene_ref.addItem(item)
                self.child_items.append(item)

    def boundingRect(self):
        # Compute bounding rect from all children in LOCAL coordinates
        # The group is positioned at (0,0) so we use scene coords directly since
        # children are added to the scene, not as Qt children of this item
        if not self.child_items:
            return QRectF()
        rect = QRectF()
        for child in self.child_items:
            child_rect = child.sceneBoundingRect()
            if rect.isEmpty():
                rect = child_rect
            else:
                rect = rect.united(child_rect)
        # Since GGroup is always at pos (0,0), scene coords == local coords
        return rect

    def shape(self):
        """Return a shape for hit testing - allows clicking to select the group."""
        path = QPainterPath()
        path.addRect(self.boundingRect())
        return path

    def paint(self, painter, option, widget=None):
        # Draw selection highlight if selected
        if self.isSelected():
            rect = self.boundingRect()
            pen = QPen(QColor(0, 120, 215))
            pen.setCosmetic(True)
            pen.setWidthF(1.0)
            pen.setStyle(Qt.DashLine)
            painter.setPen(pen)
            painter.setBrush(QBrush(Qt.NoBrush))
            painter.drawRect(rect)

    def mousePressEvent(self, event):
        super().mousePressEvent(event)
        # Store starting positions of all children for movement
        self._child_start_positions = [(child, child.pos()) for child in self.child_items]

    def mouseMoveEvent(self, event):
        super().mouseMoveEvent(event)
        # Move all children with the group
        if hasattr(self, '_child_start_positions'):
            delta = self.pos()
            for child, start_pos in self._child_start_positions:
                child.setPos(start_pos + delta)

    def mouseReleaseEvent(self, event):
        super().mouseReleaseEvent(event)
        self.sync_to_data()

    def sync_to_data(self):
        d = self.pos()
        dx, dy = d.x(), d.y()
        self.setPos(0, 0)
        
        # Reset child positions (they've been moved, now commit to data)
        for child in self.child_items:
            child.setPos(0, 0)
        
        # 1. Update Parameters for Smart Components
        if "c_params" in self.data_obj:
            p = self.data_obj["c_params"]
            if "cx" in p: p["cx"] += dx
            if "cy" in p: p["cy"] += dy
            if "ax" in p: p["ax"] += dx
            if "ay" in p: p["ay"] += dy
            if "bx" in p: p["bx"] += dx
            if "by" in p: p["by"] += dy
            
            # Regenerate geometry from new params
            if regenerate_component(self.data_obj):
                self.rebuild_children()
        else:
            # Dumb Group: move primitives
            ms_base.translate(self.data_obj["objects"], dx, dy)
            self.rebuild_children()

        # Update properties panel if selected
        if self.scene() and self.scene().views():
            win = self.scene().views()[0].window()
            if self.isSelected():
                win.update_properties([self.data_obj])

# --- Scene & View -------------------------------------------------------------

class ZoomableGraphicsView(QGraphicsView):
    """QGraphicsView with Ctrl+scroll zoom and right-click pan functionality."""
    
    def __init__(self, scene, parent=None):
        super().__init__(scene, parent)
        self.zoom_factor = 1.15  # Zoom step per scroll
        self.current_zoom = 1.0
        self.min_zoom = 0.1  # Minimum zoom (1/10th of previous)
        self.max_zoom = 1000.   # Maximum zoom (1/3rd of previous)
        
        # Panning state
        self._panning = False
        self._pan_start_pos = None
        
        # Movement threshold (in screen pixels) before drag starts
        self._drag_threshold = 20
        self._mouse_press_pos = None
        self._mouse_press_event = None
        self._threshold_exceeded = False
        self._pending_press = False
        
    def wheelEvent(self, event):
        """Handle Ctrl+scroll for zooming."""
        if event.modifiers() & Qt.ControlModifier:
            # Zoom with Ctrl+scroll
            if event.angleDelta().y() > 0:
                # Zoom in
                factor = self.zoom_factor
            else:
                # Zoom out
                factor = 1.0 / self.zoom_factor
            
            new_zoom = self.current_zoom * factor
            if self.min_zoom <= new_zoom <= self.max_zoom:
                self.current_zoom = new_zoom
                self.scale(factor, factor)
            
            event.accept()
        else:
            # Normal scroll (pan)
            super().wheelEvent(event)

    def mousePressEvent(self, event):
        """Handle mouse press - defer to scene only after threshold."""
        self._mouse_press_pos = event.pos()
        self._mouse_press_scene_pos = self.mapToScene(event.pos())
        self._mouse_press_button = event.button()
        self._threshold_exceeded = False
        
        if event.button() == Qt.RightButton:
            # Start panning with right click
            self._panning = True
            self._pan_start_pos = event.pos()
            self.setCursor(Qt.ClosedHandCursor)
            event.accept()
        elif event.button() == Qt.LeftButton:
            # Don't pass press to scene yet - wait for threshold or release
            self._pending_press = True
            event.accept()
        else:
            super().mousePressEvent(event)

    def _create_mouse_event(self, event_type, pos, button):
        """Create a synthetic mouse event."""
        from PyQt5.QtGui import QMouseEvent
        return QMouseEvent(event_type, pos, button, button, Qt.NoModifier)

    def mouseMoveEvent(self, event):
        """Handle panning movement and apply threshold."""
        if self._panning and self._pan_start_pos:
            # Right-click panning
            delta = event.pos() - self._pan_start_pos
            
            # Apply threshold for panning
            if not self._threshold_exceeded:
                if abs(delta.x()) > self._drag_threshold or abs(delta.y()) > self._drag_threshold:
                    self._threshold_exceeded = True
                else:
                    return
            
            self._pan_start_pos = event.pos()
            # Scroll the view
            self.horizontalScrollBar().setValue(
                self.horizontalScrollBar().value() - delta.x())
            self.verticalScrollBar().setValue(
                self.verticalScrollBar().value() - delta.y())
            event.accept()
        elif self._mouse_press_pos and event.buttons() & Qt.LeftButton:
            # Left-button drag - check threshold
            delta = event.pos() - self._mouse_press_pos
            
            if not self._threshold_exceeded:
                if abs(delta.x()) > self._drag_threshold or abs(delta.y()) > self._drag_threshold:
                    self._threshold_exceeded = True
                    self._pending_press = False
                    # Create and send synthetic press event to start drag
                    synthetic_press = self._create_mouse_event(
                        event.MouseButtonPress, self._mouse_press_pos, Qt.LeftButton)
                    super().mousePressEvent(synthetic_press)
                else:
                    # Below threshold - don't move anything
                    event.accept()
                    return
            
            # Threshold exceeded - pass movement to scene
            super().mouseMoveEvent(event)
        else:
            super().mouseMoveEvent(event)

    def mouseReleaseEvent(self, event):
        """End panning or regular drag."""
        if event.button() == Qt.RightButton:
            self._panning = False
            self._pan_start_pos = None
            self.setCursor(Qt.ArrowCursor)
            event.accept()
        elif event.button() == Qt.LeftButton:
            if self._pending_press and not self._threshold_exceeded:
                # Was a click, not a drag - forward press then release for selection
                synthetic_press = self._create_mouse_event(
                    event.MouseButtonPress, self._mouse_press_pos, Qt.LeftButton)
                super().mousePressEvent(synthetic_press)
            super().mouseReleaseEvent(event)
            self._pending_press = False
        else:
            super().mouseReleaseEvent(event)
        
        self._mouse_press_pos = None
        self._threshold_exceeded = False

class SketchScene(QGraphicsScene):
    def __init__(self, parent=None):
        super().__init__(parent)
        # Use NoIndex to ensure proper z-ordering (BSP tree can interfere)
        self.setItemIndexMethod(QGraphicsScene.NoIndex)
        self.sketch_data = None
        self.item_map = {} 
        self.mode = EditorMode.SELECT
        self.creation_data = {} 
        self.active_component_factory = None 
        
        self.defaults = {
            "linewidth": 1.0,
            "color": "black",
            "fontsize": 10,
            "scale": 10,
            "text_render_mode": "auto"  # Default for newly created text
        }

    def load_sketch(self, sketch):
        self.clear()
        self.sketch_data = sketch
        self.item_map = {}
        if "objects" in sketch:
            for obj in sketch["objects"]:
                self.add_sketch_object(obj)

    def create_item(self, obj):
        item = None
        if obj["type"] == "line":
            item = GLine(obj)
        elif obj["type"] == "circle":
            item = GCircle(obj)
        elif obj["type"] == "polygon":
            item = GPolygon(obj)
        elif obj["type"] == "arc":
            item = GArc(obj)
        elif obj["type"] == "text":
            item = GText(obj)
        elif obj["type"] == "group":
            item = GGroup(obj, self)
        
        if item:
            self.item_map[id(item)] = obj
            item.setData(0, obj) 
        return item

    def add_sketch_object(self, obj):
        item = self.create_item(obj)
        if item:
            self.addItem(item)
            return item
        return None

    def mousePressEvent(self, event):
        if event.button() == Qt.LeftButton:
            pos = event.scenePos()
            x, y = pos.x(), pos.y()

            if self.mode == EditorMode.SELECT:
                # Check if clicked item is a child of a group - select parent instead
                clicked_item = self.itemAt(pos, QTransform())
                if clicked_item and hasattr(clicked_item, 'parent_group'):
                    parent = clicked_item.parent_group
                    self.clearSelection()
                    parent.setSelected(True)
                    event.accept()
                else:
                    super().mousePressEvent(event)
            
            elif self.mode == EditorMode.DRAW_LINE:
                self.creation_data = {
                    "start": (x, y),
                    "temp_line": self.addLine(x, y, x, y, QPen(QColor(self.defaults["color"])))
                }

            elif self.mode == EditorMode.DRAW_RECT:
                self.creation_data = {
                    "start": (x, y),
                    "temp_rect": self.addRect(x, y, 0, 0, QPen(QColor(self.defaults["color"])))
                }

            elif self.mode == EditorMode.DRAW_CIRCLE:
                 self.creation_data = {
                    "start": (x, y),
                    "temp_circle": self.addEllipse(x, y, 0, 0, QPen(QColor(self.defaults["color"])))
                 }
            
            elif self.mode == EditorMode.DRAW_TEXT:
                 text, ok = QInputDialog.getText(None, "Add Text", "Enter text:")
                 if ok and text:
                     obj = ms_base.make_text(x, y, text, self.defaults["fontsize"], color=self.defaults["color"])
                     ms_base.add_to_sketch(self.sketch_data, obj)
                     self.add_sketch_object(obj)
            
            elif self.mode == EditorMode.PLACE_COMPONENT and self.active_component_factory:
                # Call factory with sketch, x, y
                # Note: We bind scale_factor=5.0 via partial in library
                self.active_component_factory(self.sketch_data, x, y) # This appends to sketch
                new_obj = self.sketch_data["objects"][-1]
                self.add_sketch_object(new_obj)
                self.parent().rebuild_tree()

        elif event.button() == Qt.RightButton:
            item = self.itemAt(event.scenePos(), QTransform())
            if item:
                # Find top-level group if item is part of one
                top_item = item
                while top_item.parentItem():
                    top_item = top_item.parentItem()
                self.show_context_menu(event.screenPos(), top_item)
            
        else:
            super().mousePressEvent(event)

    def mouseMoveEvent(self, event):
        pos = event.scenePos()
        x, y = pos.x(), pos.y()

        if self.mode == EditorMode.DRAW_LINE and "temp_line" in self.creation_data:
            start_x, start_y = self.creation_data["start"]
            self.creation_data["temp_line"].setLine(start_x, start_y, x, y)
        
        elif self.mode == EditorMode.DRAW_RECT and "temp_rect" in self.creation_data:
            start_x, start_y = self.creation_data["start"]
            w = x - start_x
            h = y - start_y
            rect = QRectF(min(start_x, x), min(start_y, y), abs(w), abs(h))
            self.creation_data["temp_rect"].setRect(rect)

        elif self.mode == EditorMode.DRAW_CIRCLE and "temp_circle" in self.creation_data:
            start_x, start_y = self.creation_data["start"]
            r = math.sqrt((x-start_x)**2 + (y-start_y)**2)
            self.creation_data["temp_circle"].setRect(start_x - r, start_y - r, 2*r, 2*r)

        super().mouseMoveEvent(event)

    def mouseReleaseEvent(self, event):
        if event.button() == Qt.LeftButton:
            pos = event.scenePos()
            x, y = pos.x(), pos.y()

            if self.mode == EditorMode.DRAW_LINE and "temp_line" in self.creation_data:
                start_x, start_y = self.creation_data["start"]
                self.removeItem(self.creation_data["temp_line"])
                self.creation_data = {}
                # Skip zero-length lines
                if start_x == x and start_y == y:
                    return
                obj = ms_base.make_line(start_x, start_y, x, y, 
                                        linewidth=self.defaults["linewidth"], edgecolor=self.defaults["color"])
                ms_base.add_to_sketch(self.sketch_data, obj)
                self.add_sketch_object(obj)
                self.parent().rebuild_tree()

            elif self.mode == EditorMode.DRAW_RECT and "temp_rect" in self.creation_data:
                start_x, start_y = self.creation_data["start"]
                self.removeItem(self.creation_data["temp_rect"])
                self.creation_data = {}
                # Skip zero-area rectangles
                if start_x == x or start_y == y:
                    return
                obj = ms_base.make_rectangle(start_x, start_y, x, y, 
                                            linewidth=self.defaults["linewidth"], edgecolor=self.defaults["color"])
                ms_base.add_to_sketch(self.sketch_data, obj)
                self.add_sketch_object(obj)
                self.parent().rebuild_tree()
            
            elif self.mode == EditorMode.DRAW_CIRCLE and "temp_circle" in self.creation_data:
                 start_x, start_y = self.creation_data["start"]
                 r = math.sqrt((x-start_x)**2 + (y-start_y)**2)
                 self.removeItem(self.creation_data["temp_circle"])
                 self.creation_data = {}
                 # Skip zero-radius circles
                 if r == 0:
                     return
                 obj = ms_base.make_circle(start_x, start_y, r, 
                                           linewidth=self.defaults["linewidth"], edgecolor=self.defaults["color"])
                 ms_base.add_to_sketch(self.sketch_data, obj)
                 self.add_sketch_object(obj)
                 self.parent().rebuild_tree()

            else:
                super().mouseReleaseEvent(event)
    
    def keyPressEvent(self, event):
        if event.key() == Qt.Key_Delete:
            self.delete_selected_items()
        else:
            super().keyPressEvent(event)

    def delete_selected_items(self):
        selected = self.selectedItems()
        for item in selected:
            # Use data_obj for consistent data lookup
            data = getattr(item, 'data_obj', None)
            if data is None:
                data = item.data(0)
            
            # Remove from sketch data if it's a top-level object
            if data in self.sketch_data["objects"]:
                self.sketch_data["objects"].remove(data)
            
            # For GGroup, also remove child items from the scene
            if isinstance(item, GGroup):
                for child in item.child_items:
                    self.removeItem(child)
            
            self.removeItem(item)
        self.parent().rebuild_tree()
    
    def show_context_menu(self, screen_pos, item):
        menu = QMenu()
        action_delete = menu.addAction("Delete")
        action_delete.triggered.connect(self.delete_selected_items)
        
        # Properties
        action_props = menu.addAction("Properties")
        def focus_props():
            self.parent().update_properties([item.data(0)])
            self.parent().dock_props.show()
            self.parent().dock_props.raise_()
        action_props.triggered.connect(focus_props)
        
        menu.exec_(screen_pos)
        
    def parent(self):
         return self.views()[0].window()

# --- Main Window --------------------------------------------------------------

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("MechanicsSketches Editor")
        self.resize(1300, 900)

        # Central Widget - View
        self.scene = SketchScene(self)
        self.view = ZoomableGraphicsView(self.scene)
        self.view.setRenderHint(QPainter.Antialiasing)
        self.view.setRenderHint(QPainter.TextAntialiasing)
        self.view.setRenderHint(QPainter.SmoothPixmapTransform)
        # Force high quality if possible
        try:
             self.view.setRenderHint(QPainter.HighQualityAntialiasing)
        except AttributeError:
             pass  # Not supported on this platform
        
        self.view.setDragMode(QGraphicsView.RubberBandDrag)
        
        # Initial Y-flip (zoom will be set by fit_to_content)
        self.view.scale(1, -1)
        
        self.setCentralWidget(self.view)

        # Docks
        self.create_tree_dock()
        self.create_library_dock()
        self.create_properties_dock()
        self.create_menus()
        self.create_toolbar()

        # Data
        self.current_sketch = ms_base.create_sketch("New Sketch")
        self.scene.load_sketch(self.current_sketch)
        self.rebuild_tree()
        
        # Apply initial fit after everything is set up
        # Use timer to ensure view has proper size
        from PyQt5.QtCore import QTimer
        QTimer.singleShot(100, self.fit_to_content)
        
        # Signals
        self.scene.selectionChanged.connect(self.on_scene_selection_changed)
        self.tree.itemSelectionChanged.connect(self.on_tree_selection_changed)
    
    def fit_to_content(self):
        """Fit the view to show all sketch content with appropriate zoom."""
        # Get view dimensions
        view_width = self.view.viewport().width()
        view_height = self.view.viewport().height()
        
        if view_width <= 0 or view_height <= 0:
            view_width, view_height = 800, 600  # Fallback
        
        # Calculate optimal zoom
        optimal_zoom = calculate_auto_zoom(self.current_sketch, view_width, view_height)
        
        # Reset transform and apply new zoom with Y-flip
        self.view.resetTransform()
        self.view.scale(optimal_zoom, -optimal_zoom)
        self.view.current_zoom = optimal_zoom
        
        # Center on content
        bounds = calculate_sketch_bounds(self.current_sketch)
        if bounds:
            min_x, min_y, max_x, max_y = bounds
            center_x = (min_x + max_x) / 2
            center_y = (min_y + max_y) / 2
            self.view.centerOn(center_x, center_y)

    def create_menus(self):
        # File Menu
        menu_file = self.menuBar().addMenu("File")
        
        action_new = QAction("New", self)
        action_new.setShortcut("Ctrl+N")
        action_new.triggered.connect(self.new_sketch)
        menu_file.addAction(action_new)

        action_open = QAction("Open", self)
        action_open.setShortcut("Ctrl+O")
        action_open.triggered.connect(self.load_sketch_dialog)
        menu_file.addAction(action_open)

        action_save = QAction("Save", self)
        action_save.setShortcut("Ctrl+S")
        action_save.triggered.connect(self.save_sketch)
        menu_file.addAction(action_save)

        menu_file.addSeparator()

        action_export_py = QAction("Export as Python Script...", self)
        action_export_py.triggered.connect(self.export_to_python)
        menu_file.addAction(action_export_py)

        action_import_py = QAction("Import Python Script...", self)
        action_import_py.triggered.connect(self.import_from_python)
        menu_file.addAction(action_import_py)

        menu_file.addSeparator()

        action_export = QAction("Export...", self)
        action_export.setShortcut("Ctrl+E")
        action_export.triggered.connect(self.on_export)
        menu_file.addAction(action_export)

        # View Menu
        menu_view = self.menuBar().addMenu("View")
        menu_view.addAction(self.dock_tree.toggleViewAction())
        menu_view.addAction(self.dock_lib.toggleViewAction())
        menu_view.addAction(self.dock_props.toggleViewAction())

    def create_toolbar(self):
        toolbar = QToolBar("Tools")
        self.addToolBar(Qt.TopToolBarArea, toolbar)
        
        # Actions
        ag = QAction("Select", self)
        ag.setCheckable(True)
        ag.setChecked(True)
        ag.triggered.connect(lambda: self.set_mode(EditorMode.SELECT))
        toolbar.addAction(ag)
        self.act_select = ag

        ag = QAction("Line", self)
        ag.setCheckable(True)
        ag.triggered.connect(lambda: self.set_mode(EditorMode.DRAW_LINE))
        toolbar.addAction(ag)
        self.act_line = ag

        ag = QAction("Circle", self)
        ag.setCheckable(True)
        ag.triggered.connect(lambda: self.set_mode(EditorMode.DRAW_CIRCLE))
        toolbar.addAction(ag)
        self.act_circle = ag

        ag = QAction("Rect", self)
        ag.setCheckable(True)
        ag.triggered.connect(lambda: self.set_mode(EditorMode.DRAW_RECT))
        toolbar.addAction(ag)
        self.act_rect = ag
        
        ag = QAction("Text", self)
        ag.setCheckable(True)
        ag.triggered.connect(lambda: self.set_mode(EditorMode.DRAW_TEXT))
        toolbar.addAction(ag)
        self.act_text = ag

        toolbar.addSeparator()

    def set_mode(self, mode):
        self.scene.mode = mode
        self.act_select.setChecked(False)
        self.act_line.setChecked(False)
        self.act_circle.setChecked(False)
        self.act_rect.setChecked(False)
        self.act_text.setChecked(False)
        
        if mode == EditorMode.SELECT:
            self.act_select.setChecked(True)
            self.view.setDragMode(QGraphicsView.RubberBandDrag)
        else:
            self.view.setDragMode(QGraphicsView.NoDrag)
            if mode == EditorMode.DRAW_LINE: self.act_line.setChecked(True)
            elif mode == EditorMode.DRAW_CIRCLE: self.act_circle.setChecked(True)
            elif mode == EditorMode.DRAW_RECT: self.act_rect.setChecked(True)
            elif mode == EditorMode.DRAW_TEXT: self.act_text.setChecked(True)

    def create_tree_dock(self):
        self.dock_tree = QDockWidget("Structure", self)
        self.dock_tree.setObjectName("DockTree")
        self.tree = QTreeWidget()
        self.tree.setHeaderLabel("Objects")
        self.tree.setSelectionMode(QAbstractItemView.ExtendedSelection)
        self.dock_tree.setWidget(self.tree)
        self.addDockWidget(Qt.LeftDockWidgetArea, self.dock_tree)
        
    def create_library_dock(self):
        self.dock_lib = QDockWidget("Library", self)
        self.dock_lib.setObjectName("DockLibrary")
        self.lib_list = QListWidget()
        self.dock_lib.setWidget(self.lib_list)
        self.addDockWidget(Qt.LeftDockWidgetArea, self.dock_lib)
        
        # Populate library - scale_factor will be applied from global defaults at creation time
        items = [
            ("Pinned Support (Festlager)", ms_elements.add_pinned_support),
            ("Roller Support (Loslager)", ms_elements.add_roller_support),
            ("Fixed Support (Einspannung)", ms_elements.add_fixed_support),
            ("Hinge (Gelenk)", ms_elements.add_hinge),
            ("Force (Kraft)", ms_elements.add_force),
            ("Moment", ms_elements.add_moment),
            ("Dimension Arrow", ms_elements.add_dimension_arrow),
            ("Coord System", ms_elements.add_coordinate_system)
        ]
        
        for name, func in items:
            item = QListWidgetItem(name)
            item.setData(Qt.UserRole, func)
            self.lib_list.addItem(item)
            
        self.lib_list.itemClicked.connect(self.on_library_item_clicked)

    def on_library_item_clicked(self, item):
        base_func = item.data(Qt.UserRole)
        # Wrap the function to use current global default scale
        scale = self.scene.defaults.get("scale", 10)
        wrapped_func = partial(base_func, scale_factor=scale)
        self.scene.mode = EditorMode.PLACE_COMPONENT
        self.scene.active_component_factory = wrapped_func
        self.set_mode(EditorMode.PLACE_COMPONENT) 

    def create_properties_dock(self):
        self.dock_props = QDockWidget("Properties", self)
        self.dock_props.setObjectName("DockProps")
        self.props_widget = QWidget()
        self.props_layout = QFormLayout()
        self.props_widget.setLayout(self.props_layout)
        self.dock_props.setWidget(self.props_widget)
        self.addDockWidget(Qt.RightDockWidgetArea, self.dock_props)
        self.update_global_settings_ui()

    def update_global_settings_ui(self):
        if self.scene.selectedItems():
            return
            
        while self.props_layout.count():
            child = self.props_layout.takeAt(0)
            if child.widget(): child.widget().deleteLater()
            
        self.props_layout.addRow("<b>Global Settings</b>", QWidget())
        
        w_lw = QDoubleSpinBox()
        w_lw.setValue(self.scene.defaults["linewidth"])
        w_lw.valueChanged.connect(lambda v: self.scene.defaults.update({"linewidth": v}))
        self.props_layout.addRow("Default Line Width", w_lw)
        
        w_fs = QDoubleSpinBox()
        w_fs.setValue(self.scene.defaults["fontsize"])
        w_fs.valueChanged.connect(lambda v: self.scene.defaults.update({"fontsize": int(v)}))
        self.props_layout.addRow("Default Font Size", w_fs)
        
        w_scale = QDoubleSpinBox()
        w_scale.setRange(0.1, 1000)
        w_scale.setSingleStep(1)
        w_scale.setValue(self.scene.defaults.get("scale", 10))
        w_scale.valueChanged.connect(lambda v: self.scene.defaults.update({"scale": v}))
        self.props_layout.addRow("Default Scale", w_scale)
        
        w_col = QLineEdit(self.scene.defaults["color"])
        w_col.textChanged.connect(lambda v: self.scene.defaults.update({"color": v}))
        self.props_layout.addRow("Default Color", w_col)
        
        # Text render mode dropdown
        w_render = QComboBox()
        w_render.addItems(["auto", "mpl_latex", "mpl_mathtext", "typst", "qt"])
        w_render.setCurrentText(self.scene.defaults.get("text_render_mode", "auto"))
        w_render.currentTextChanged.connect(lambda v: self.scene.defaults.update({"text_render_mode": v}))
        self.props_layout.addRow("Text Render Mode", w_render)

    def new_sketch(self):
        self.current_sketch = ms_base.create_sketch("New Sketch")
        self.scene.load_sketch(self.current_sketch)
        self.rebuild_tree()

    def save_sketch(self):
        fname, _ = QFileDialog.getSaveFileName(self, "Save Sketch", "", "JSON Files (*.json)")
        if fname:
            ms_base.save_sketch(self.current_sketch, fname)

    def load_sketch_dialog(self):
        fname, _ = QFileDialog.getOpenFileName(self, "Load Sketch", "", "JSON Files (*.json)")
        if fname:
            self.current_sketch = ms_base.load_sketch(fname)
            self.scene.load_sketch(self.current_sketch)
            self.rebuild_tree()
            self.fit_to_content()  # Auto-scale to fit loaded sketch

    def export_to_python(self):
        """Export current sketch as a Python script."""
        fname, _ = QFileDialog.getSaveFileName(self, "Export as Python Script", "", "Python Files (*.py)")
        if fname:
            # Derive PDF name from script name
            import os
            base_name = os.path.splitext(os.path.basename(fname))[0]
            pdf_name = base_name + ".pdf"
            
            script_code = generate_python_script(self.current_sketch, pdf_name)
            with open(fname, 'w', encoding='utf-8') as f:
                f.write(script_code)
            print(f"Exported to {fname}")

    def import_from_python(self):
        """Import a sketch from a Python script."""
        import re
        import tempfile
        import os as os_module
        fname, _ = QFileDialog.getOpenFileName(self, "Import Python Script", "", "Python Files (*.py)")
        if not fname:
            return
        
        try:
            with open(fname, 'r', encoding='utf-8') as f:
                script_content = f.read()
            
            # Find the sketch variable name from render() calls
            # Patterns: render(sketch, ...), ren.render(s, ...), renderer.render(my_sketch, ...)
            sketch_var_name = None
            render_patterns = [
                r'(?:ren|renderer)\.render\s*\(\s*([a-zA-Z_][a-zA-Z0-9_]*)',  # ren.render(s, ...)
                r'(?<![a-zA-Z_.])render\s*\(\s*([a-zA-Z_][a-zA-Z0-9_]*)',      # render(sketch, ...)
            ]
            for pattern in render_patterns:
                match = re.search(pattern, script_content)
                if match:
                    sketch_var_name = match.group(1)
                    break
            
            if not sketch_var_name:
                # Fallback: look for common variable names
                sketch_var_name = 'sketch'
            
            # Create a temp file for JSON output
            temp_json = tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False)
            temp_json_path = temp_json.name
            temp_json.close()
            
            # Modify script: replace render call with save_sketch call
            # We'll inject code to save the sketch variable to JSON
            modified_script = script_content
            
            # Replace render calls with no-op (they will be handled by our namespace)
            # The actual save will happen via our injected code at the end
            
            # Create module-like objects for base and ren/renderer imports
            class BaseModule:
                create_sketch = staticmethod(ms_base.create_sketch)
                add_to_sketch = staticmethod(ms_base.add_to_sketch)
                make_line = staticmethod(ms_base.make_line)
                make_circle = staticmethod(ms_base.make_circle)
                make_arc = staticmethod(ms_base.make_arc)
                make_polygon = staticmethod(ms_base.make_polygon)
                make_rectangle = staticmethod(ms_base.make_rectangle)
                make_text = staticmethod(ms_base.make_text)
                make_group = staticmethod(ms_base.make_group)
                translate = staticmethod(ms_base.translate)
                rotate = staticmethod(ms_base.rotate)
                scale = staticmethod(ms_base.scale)
                save_sketch = staticmethod(ms_base.save_sketch)
                load_sketch = staticmethod(ms_base.load_sketch)
            
            class RendererModule:
                @staticmethod
                def render(*args, **kwargs):
                    pass  # No-op
            
            class ElementsModule:
                add_pinned_support = staticmethod(ms_elements.add_pinned_support)
                add_roller_support = staticmethod(ms_elements.add_roller_support)
                add_fixed_support = staticmethod(ms_elements.add_fixed_support)
                add_hinge = staticmethod(ms_elements.add_hinge)
                add_beam = staticmethod(ms_elements.add_beam)
                add_truss = staticmethod(ms_elements.add_truss)
                add_arrow = staticmethod(ms_elements.add_arrow)
                add_force = staticmethod(ms_elements.add_force)
                add_moment = staticmethod(ms_elements.add_moment)
                add_coordinate_system = staticmethod(ms_elements.add_coordinate_system)
                add_dimension_arrow = staticmethod(ms_elements.add_dimension_arrow)
                add_dimension_thickness = staticmethod(ms_elements.add_dimension_thickness)
                add_text = staticmethod(ms_elements.add_text)
                make_pinned_support = staticmethod(ms_elements.make_pinned_support)
                make_roller_support = staticmethod(ms_elements.make_roller_support)
                make_fixed_support = staticmethod(ms_elements.make_fixed_support)
                make_hinge = staticmethod(ms_elements.make_hinge)
                make_beam = staticmethod(ms_elements.make_beam)
                make_truss = staticmethod(ms_elements.make_truss)
                make_arrow = staticmethod(ms_elements.make_arrow)
                make_force = staticmethod(ms_elements.make_force)
                make_moment = staticmethod(ms_elements.make_moment)
                make_coordinate_system = staticmethod(ms_elements.make_coordinate_system)
                make_dimension_arrow = staticmethod(ms_elements.make_dimension_arrow)
                make_dimension_thickness = staticmethod(ms_elements.make_dimension_thickness)
            
            # Build namespace with all possible import patterns
            namespace = {
                # Module-style imports (for 'import ... as base' or 'from . import base')
                'base': BaseModule,
                'ren': RendererModule,
                'renderer': RendererModule,
                'elements': ElementsModule,
                'ms_base': BaseModule,
                'ms_elements': ElementsModule,
                
                # Direct imports (for 'from MechanicsSketches import *')
                'create_sketch': ms_base.create_sketch,
                'add_to_sketch': ms_base.add_to_sketch,
                'make_line': ms_base.make_line,
                'make_circle': ms_base.make_circle,
                'make_arc': ms_base.make_arc,
                'make_polygon': ms_base.make_polygon,
                'make_rectangle': ms_base.make_rectangle,
                'make_text': ms_base.make_text,
                'make_group': ms_base.make_group,
                'translate': ms_base.translate,
                'rotate': ms_base.rotate,
                'scale': ms_base.scale,
                'save_sketch': ms_base.save_sketch,
                'load_sketch': ms_base.load_sketch,
                'add_pinned_support': ms_elements.add_pinned_support,
                'add_roller_support': ms_elements.add_roller_support,
                'add_fixed_support': ms_elements.add_fixed_support,
                'add_hinge': ms_elements.add_hinge,
                'add_beam': ms_elements.add_beam,
                'add_truss': ms_elements.add_truss,
                'add_arrow': ms_elements.add_arrow,
                'add_force': ms_elements.add_force,
                'add_moment': ms_elements.add_moment,
                'add_coordinate_system': ms_elements.add_coordinate_system,
                'add_dimension_arrow': ms_elements.add_dimension_arrow,
                'add_dimension_thickness': ms_elements.add_dimension_thickness,
                'add_text': ms_elements.add_text,
                'render': lambda *args, **kwargs: None,  # No-op for direct render calls
                
                # Standard library
                'math': __import__('math'),
                'os': __import__('os'),
                '__file__': fname,
                '__name__': '__main__',
                
                # For saving the result
                '_temp_json_path': temp_json_path,
                '_save_sketch': ms_base.save_sketch,
            }
            
            # Append code to save the detected sketch variable
            save_code = f'''
# --- Injected by MechanicsSketches Editor ---
try:
    _save_sketch({sketch_var_name}, _temp_json_path)
except NameError:
    pass  # Variable not found, will try other methods
'''
            modified_script = script_content + save_code
            
            # Execute the modified script
            exec(modified_script, namespace)
            
            # Try to load from temp JSON
            loaded_sketch = None
            if os_module.path.exists(temp_json_path) and os_module.path.getsize(temp_json_path) > 0:
                loaded_sketch = ms_base.load_sketch(temp_json_path)
            
            # Cleanup temp file
            try:
                os_module.unlink(temp_json_path)
            except:
                pass
            
            # If JSON approach didn't work, try to find sketch in namespace
            if not loaded_sketch:
                # Try the detected variable name first
                if sketch_var_name in namespace and isinstance(namespace[sketch_var_name], dict):
                    loaded_sketch = namespace[sketch_var_name]
                # Try common names
                for var_name in ['sketch', 's', 'sk', 'my_sketch']:
                    if var_name in namespace and isinstance(namespace[var_name], dict):
                        if 'objects' in namespace[var_name]:
                            loaded_sketch = namespace[var_name]
                            break
            
            if loaded_sketch and 'objects' in loaded_sketch:
                self.current_sketch = loaded_sketch
                self.scene.load_sketch(self.current_sketch)
                self.rebuild_tree()
                self.fit_to_content()  # Auto-scale to fit imported sketch
                print(f"Imported sketch: {self.current_sketch.get('name', 'Unknown')}")
            else:
                from PyQt5.QtWidgets import QMessageBox
                QMessageBox.warning(self, "Import Error", 
                    f"Could not find sketch variable. Looked for '{sketch_var_name}' and common names.")
                
        except Exception as e:
            import traceback
            from PyQt5.QtWidgets import QMessageBox
            QMessageBox.critical(self, "Import Error", f"Failed to import script:\n{str(e)}\n\n{traceback.format_exc()}")

    def on_export(self):
        """Export sketch to PDF, PNG, or SVG. Format determined by chosen file extension."""
        filename, selected_filter = QFileDialog.getSaveFileName(
            self,
            "Export Sketch",
            self.current_sketch.get("name", "sketch"),
            "PDF Document (*.pdf);;"
            "PNG Image (*.png);;"
            "SVG Vector (*.svg);;"
            "JPEG Image (*.jpg)"
        )
        
        if filename:
            try:
                # Try different import patterns for package/standalone execution
                try:
                    import MechanicsSketches.qt_renderer as qt_renderer
                except ImportError:
                    try:
                        from . import qt_renderer
                    except ImportError:
                        import qt_renderer
                
                qt_renderer.render_scene(self.scene, filename)
                
                from PyQt5.QtWidgets import QMessageBox
                QMessageBox.information(self, "Export Complete", f"Exported to:\n{filename}")
            except Exception as e:
                import traceback
                from PyQt5.QtWidgets import QMessageBox
                QMessageBox.critical(self, "Export Error", f"Failed to export:\n{str(e)}\n\n{traceback.format_exc()}")

    def rebuild_tree(self):
        self.tree.blockSignals(True)
        self.tree.clear()
        
        def add_node(parent_node, obj):
            name = obj.get("name", obj["type"])
            item = QTreeWidgetItem(parent_node)
            item.setText(0, name)
            item.setData(0, Qt.UserRole, obj) 
            
            if obj["type"] == "group":
                for child in obj["objects"]:
                    add_node(item, child)
            return item

        for obj in self.current_sketch["objects"]:
            add_node(self.tree, obj)
            
        self.tree.expandAll()
        self.tree.blockSignals(False)

    def on_scene_selection_changed(self):
        selected_items = self.scene.selectedItems()
        self.tree.blockSignals(True)
        self.tree.clearSelection()
        
        # Use data_obj for consistent object references
        selected_data_objs = [getattr(item, 'data_obj', None) for item in selected_items]
        selected_data_objs = [obj for obj in selected_data_objs if obj is not None]
        
        iterator = QTreeWidgetItemIterator(self.tree)
        while iterator.value():
            item = iterator.value()
            if item.data(0, Qt.UserRole) in selected_data_objs:
                item.setSelected(True)
            iterator += 1
            
        self.tree.blockSignals(False)
        self.update_properties(selected_data_objs)

    def on_tree_selection_changed(self):
        selected_nodes = self.tree.selectedItems()
        selected_data = [item.data(0, Qt.UserRole) for item in selected_nodes]
        
        self.scene.blockSignals(True)
        self.scene.clearSelection()
        
        for item in self.scene.items():
            # Use data_obj for consistent object references
            item_obj = getattr(item, 'data_obj', None)
            if item_obj in selected_data:
                item.setSelected(True)
        
        self.scene.blockSignals(False)
        self.update_properties(selected_data)

    def update_properties(self, selected_objs):
        while self.props_layout.count():
            child = self.props_layout.takeAt(0)
            if child.widget(): child.widget().deleteLater()
        
        if len(selected_objs) == 0:
            self.update_global_settings_ui()
            return
            
        if len(selected_objs) != 1:
            return 
        
        obj = selected_objs[0]
        
        # --- Parametric Component Editing ---
        if "c_type" in obj and "c_params" in obj:
            self.props_layout.addRow(f"<b>{obj.get('name', obj['c_type'])}</b>", QWidget())
            params = obj["c_params"]
            for key, value in params.items():
                if isinstance(value, (int, float)):
                    spin = QDoubleSpinBox()
                    spin.setRange(-10000, 10000)
                    spin.setSingleStep(0.1 if isinstance(value, float) else 1)
                    spin.setValue(float(value))
                    spin.setKeyboardTracking(True)
                    spin.valueChanged.connect(partial(self.update_component_param, obj, key))
                    self.props_layout.addRow(key, spin)
                elif isinstance(value, str):
                    le = QLineEdit(value)
                    le.editingFinished.connect(partial(self.update_component_param, obj, key, le))
                    self.props_layout.addRow(key, le)
            return

        # --- Standard Primitive Editing ---
        obj_type = obj.get("type")
        if obj_type:
            self.props_layout.addRow(f"<b>{obj_type.capitalize()}</b>", QWidget())
        else:
            self.props_layout.addRow("<b>Object</b>", QWidget())
        
        # Add geometry fields based on object type
        if obj_type == "line":
            self._add_line_geometry_fields(obj)
        elif obj_type == "polygon":
            self._add_polygon_geometry_fields(obj)
        elif obj_type == "circle":
            self._add_circle_geometry_fields(obj)
        elif obj_type == "arc":
            self._add_arc_geometry_fields(obj)
        elif obj_type == "text":
            self._add_text_geometry_fields(obj)
        elif obj_type == "group":
            # Non-component groups - just show name if available
            name = obj.get("name", "Unnamed Group")
            name_le = QLineEdit(name)
            name_le.textChanged.connect(partial(self.update_primitive_value, obj, "name"))
            self.props_layout.addRow("Name", name_le)
        
        # Add remaining non-geometry properties
        self.props_layout.addRow("<i>Style</i>", QWidget())
        skip_keys = ["objects", "type", "points", "x", "y", "r", "width", "height", 
                     "theta1", "theta2", "angle", "text", "fontsize", "rotation", "render_mode"]
        for key, value in obj.items():
            if key in skip_keys:
                continue
            
            # Special handling for linestyle - use combo box
            if key == "linestyle":
                combo = QComboBox()
                combo.addItems(["solid", "dashed", "dotted", "dashdot"])
                current_style = obj.get("linestyle", "solid")
                index = combo.findText(current_style)
                if index >= 0:
                    combo.setCurrentIndex(index)
                
                def on_linestyle_changed(new_style):
                    self.update_primitive_value(obj, "linestyle", new_style)
                
                combo.currentTextChanged.connect(on_linestyle_changed)
                self.props_layout.addRow(key, combo)
            elif isinstance(value, (int, float)):
                spin = QDoubleSpinBox()
                spin.setRange(-10000, 10000)
                spin.setSingleStep(0.1)
                spin.setValue(float(value))
                spin.setKeyboardTracking(True)
                spin.valueChanged.connect(partial(self.update_primitive_value, obj, key))
                self.props_layout.addRow(key, spin)
            elif isinstance(value, str):
                le = QLineEdit(value)
                le.textChanged.connect(partial(self.update_primitive_value, obj, key))
                self.props_layout.addRow(key, le)

    def _add_line_geometry_fields(self, obj):
        """Add editable fields for line start/end coordinates."""
        self.props_layout.addRow("<i>Geometry</i>", QWidget())
        
        # Start point
        spin_x0 = QDoubleSpinBox()
        spin_x0.setRange(-10000, 10000)
        spin_x0.setSingleStep(0.1)
        spin_x0.setValue(obj["x"][0])
        spin_x0.valueChanged.connect(partial(self._update_line_coord, obj, "x", 0))
        self.props_layout.addRow("Start X", spin_x0)
        
        spin_y0 = QDoubleSpinBox()
        spin_y0.setRange(-10000, 10000)
        spin_y0.setSingleStep(0.1)
        spin_y0.setValue(obj["y"][0])
        spin_y0.valueChanged.connect(partial(self._update_line_coord, obj, "y", 0))
        self.props_layout.addRow("Start Y", spin_y0)
        
        # End point
        spin_x1 = QDoubleSpinBox()
        spin_x1.setRange(-10000, 10000)
        spin_x1.setSingleStep(0.1)
        spin_x1.setValue(obj["x"][1])
        spin_x1.valueChanged.connect(partial(self._update_line_coord, obj, "x", 1))
        self.props_layout.addRow("End X", spin_x1)
        
        spin_y1 = QDoubleSpinBox()
        spin_y1.setRange(-10000, 10000)
        spin_y1.setSingleStep(0.1)
        spin_y1.setValue(obj["y"][1])
        spin_y1.valueChanged.connect(partial(self._update_line_coord, obj, "y", 1))
        self.props_layout.addRow("End Y", spin_y1)

    def _update_line_coord(self, obj, axis, index, value):
        """Update a single coordinate in a line's x or y list."""
        obj[axis][index] = value
        self.refresh_items_for_obj(obj)

    def _add_polygon_geometry_fields(self, obj):
        """Add editable fields for polygon vertices."""
        self.props_layout.addRow("<i>Vertices</i>", QWidget())
        points = obj.get("points", [])
        for i, (px, py) in enumerate(points):
            spin_x = QDoubleSpinBox()
            spin_x.setRange(-10000, 10000)
            spin_x.setSingleStep(0.1)
            spin_x.setValue(px)
            spin_x.valueChanged.connect(partial(self._update_polygon_point, obj, i, 0))
            self.props_layout.addRow(f"P{i+1} X", spin_x)
            
            spin_y = QDoubleSpinBox()
            spin_y.setRange(-10000, 10000)
            spin_y.setSingleStep(0.1)
            spin_y.setValue(py)
            spin_y.valueChanged.connect(partial(self._update_polygon_point, obj, i, 1))
            self.props_layout.addRow(f"P{i+1} Y", spin_y)

    def _update_polygon_point(self, obj, point_index, coord_index, value):
        """Update a single coordinate of a polygon vertex."""
        points = list(obj["points"])
        pt = list(points[point_index])
        pt[coord_index] = value
        points[point_index] = tuple(pt)
        obj["points"] = points
        self.refresh_items_for_obj(obj)

    def _add_circle_geometry_fields(self, obj):
        """Add editable fields for circle center and radius."""
        self.props_layout.addRow("<i>Geometry</i>", QWidget())
        
        spin_cx = QDoubleSpinBox()
        spin_cx.setRange(-10000, 10000)
        spin_cx.setSingleStep(0.1)
        spin_cx.setValue(obj["x"])
        spin_cx.valueChanged.connect(partial(self.update_primitive_value, obj, "x"))
        self.props_layout.addRow("Center X", spin_cx)
        
        spin_cy = QDoubleSpinBox()
        spin_cy.setRange(-10000, 10000)
        spin_cy.setSingleStep(0.1)
        spin_cy.setValue(obj["y"])
        spin_cy.valueChanged.connect(partial(self.update_primitive_value, obj, "y"))
        self.props_layout.addRow("Center Y", spin_cy)
        
        spin_r = QDoubleSpinBox()
        spin_r.setRange(0, 10000)
        spin_r.setSingleStep(0.1)
        spin_r.setValue(obj["r"])
        spin_r.valueChanged.connect(partial(self.update_primitive_value, obj, "r"))
        self.props_layout.addRow("Radius", spin_r)

    def _add_arc_geometry_fields(self, obj):
        """Add editable fields for arc parameters."""
        self.props_layout.addRow("<i>Geometry</i>", QWidget())
        
        fields = [
            ("Center X", "x"), ("Center Y", "y"),
            ("Width", "width"), ("Height", "height"),
            ("Start Angle", "theta1"), ("End Angle", "theta2"),
            ("Rotation", "angle")
        ]
        for label, key in fields:
            spin = QDoubleSpinBox()
            spin.setRange(-10000, 10000)
            spin.setSingleStep(0.1)
            spin.setValue(obj.get(key, 0))
            spin.valueChanged.connect(partial(self.update_primitive_value, obj, key))
            self.props_layout.addRow(label, spin)

    def _add_text_geometry_fields(self, obj):
        """Add editable fields for text position and properties."""
        self.props_layout.addRow("<i>Position</i>", QWidget())
        
        spin_x = QDoubleSpinBox()
        spin_x.setRange(-10000, 10000)
        spin_x.setSingleStep(0.1)
        spin_x.setValue(obj["x"])
        spin_x.valueChanged.connect(partial(self.update_primitive_value, obj, "x"))
        self.props_layout.addRow("X", spin_x)
        
        spin_y = QDoubleSpinBox()
        spin_y.setRange(-10000, 10000)
        spin_y.setSingleStep(0.1)
        spin_y.setValue(obj["y"])
        spin_y.valueChanged.connect(partial(self.update_primitive_value, obj, "y"))
        self.props_layout.addRow("Y", spin_y)
        
        self.props_layout.addRow("<i>Text Properties</i>", QWidget())
        
        le_text = QLineEdit(obj.get("text", ""))
        le_text.editingFinished.connect(lambda: self.update_primitive_value(obj, "text", le_text.text()))
        self.props_layout.addRow("Text", le_text)
        
        spin_fs = QDoubleSpinBox()
        spin_fs.setRange(1, 1000)
        spin_fs.setSingleStep(1)
        spin_fs.setValue(obj.get("fontsize", 20))
        spin_fs.valueChanged.connect(partial(self.update_primitive_value, obj, "fontsize"))
        self.props_layout.addRow("Font Size", spin_fs)
        
        spin_rot = QDoubleSpinBox()
        spin_rot.setRange(-360, 360)
        spin_rot.setSingleStep(1)
        spin_rot.setValue(obj.get("rotation", 0))
        spin_rot.valueChanged.connect(partial(self.update_primitive_value, obj, "rotation"))
        self.props_layout.addRow("Rotation", spin_rot)
        
        # Render mode dropdown
        combo_render = QComboBox()
        render_options = ["(default)", "auto", "mpl_latex", "mpl_mathtext", "typst", "qt"]
        combo_render.addItems(render_options)
        current_mode = obj.get("render_mode")
        if current_mode is None:
            combo_render.setCurrentText("(default)")
        else:
            combo_render.setCurrentText(current_mode)
        
        def on_render_mode_changed(mode):
            if mode == "(default)":
                obj["render_mode"] = None
            else:
                obj["render_mode"] = mode
            self.refresh_items_for_obj(obj)
        
        combo_render.currentTextChanged.connect(on_render_mode_changed)
        self.props_layout.addRow("Render Mode", combo_render)

    def update_primitive_value(self, obj, key, value):
        obj[key] = value
        self.refresh_items_for_obj(obj)

    def update_component_param(self, obj, key, value_or_widget):
        # Handle inputs from signals
        val = value_or_widget
        if isinstance(value_or_widget, QLineEdit):
            val = value_or_widget.text()
            
        obj["c_params"][key] = val
        
        # Regenerate geometry (Clean Rebuild)
        if regenerate_component(obj):
            # Find the GGroup and rebuild it
            for item in self.scene.items():
                # Use data_obj attribute check effectively avoids QVariant referencing issues
                if getattr(item, 'data_obj', None) == obj and isinstance(item, GGroup):
                    item.rebuild_children()
                    # Force update of selection frame logic if needed
                    item.update()
        
        self.scene.update()

    def refresh_items_for_obj(self, obj):
        # Generic update for primitives
        self.scene.update()
        for item in self.scene.items():
            # Use data_obj for consistent object references with selection handlers
            item_data_obj = getattr(item, 'data_obj', None)
            if item_data_obj == obj:
                if hasattr(item, 'update_style'):
                    item.update_style()
                # Update layer/zValue when 'l' property changes
                if hasattr(item, 'setZValue'):
                    item.setZValue(obj.get("l", 0))
                # Manual sync for transform props if needed
                if isinstance(item, QGraphicsLineItem) and 'x' in obj:
                     item.setLine(obj['x'][0], obj['y'][0], obj['x'][1], obj['y'][1])
                if isinstance(item, QGraphicsEllipseItem) and 'r' in obj:
                     r = obj['r']
                     item.setRect(obj['x']-r, obj['y']-r, 2*r, 2*r)
                if isinstance(item, QGraphicsPolygonItem) and 'points' in obj:
                     item.setPolygon(QPolygonF([QPointF(x, y) for x, y in obj['points']]))
                if isinstance(item, GArc) and hasattr(item, 'update_path'):
                     item.update_path()
                if isinstance(item, QGraphicsTextItem) and 'x' in obj:
                     item.setPos(obj['x'], obj['y'])
                item.update()


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec_())
