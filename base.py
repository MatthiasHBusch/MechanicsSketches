import math
import json
from math import cos, sin, radians

# --- Sketch Structure ---------------------------------------------------------

def create_sketch(name="Sketch", parameters=None):
    if parameters is None:
        parameters = {}
    return {"name": name, "objects": [], "parameters": parameters}

def add_to_sketch(sketch, obj):
    """Adds a primitive or group to the sketch."""
    if isinstance(obj, list):
        sketch["objects"].extend(obj)
    else:
        sketch["objects"].append(obj)

def make_group(objects, name):
    """
    Creates a group of objects.
    """
    return {
        "type": "group",
        "name": name,
        "objects": objects
    }

def save_sketch(sketch, filename):
    """Saves the sketch to a JSON file."""
    with open(filename, 'w') as f:
        json.dump(sketch, f, indent=4)

def load_sketch(filename):
    """Loads a sketch from a JSON file."""
    with open(filename, 'r') as f:
        return json.load(f)

# --- Primitives -------------------------------------------------------

def make_line(x0, y0, x1, y1, linewidth=1.0, layer=5, edgecolor="black", linestyle="solid"):
    return {"type": "line", "x": [float(x0), float(x1)], "y": [float(y0), float(y1)], "lw": linewidth, "l": layer, "edgecolor": edgecolor, "linestyle": linestyle}

def make_circle(x, y, r, linewidth=1.0, layer=5, facecolor="white", edgecolor="black"):
    return {"type": "circle", "x": float(x), "y": float(y), "r": float(r), "lw": linewidth, "l": layer, "facecolor": facecolor, "edgecolor": edgecolor}

def make_arc(x, y, width, height, theta1, theta2, angle=0.0, linewidth=1.0, layer=5, edgecolor="black"):
    return {
        "type": "arc",
        "x": float(x),
        "y": float(y),
        "width": float(width),
        "height": float(height),
        "theta1": float(theta1),
        "theta2": float(theta2),
        "angle": float(angle),
        "lw": linewidth,
        "l": layer,
        "edgecolor": edgecolor
    }

def make_polygon(points, linewidth=1.0, layer=5, facecolor="white", edgecolor="black"):
    return {"type": "polygon", "points": [tuple(map(float, p)) for p in points], "lw": linewidth, "l": layer, "edgecolor": edgecolor, "facecolor": facecolor}

def make_rectangle(x0, y0, x1, y1, linewidth=1.0, layer=5, facecolor="white", edgecolor="black"):
    return {"type": "polygon", "points": [(float(x0), float(y0)), (float(x1), float(y0)), (float(x1), float(y1)), (float(x0), float(y1))], "lw": linewidth, "l": layer, "edgecolor": edgecolor, "facecolor": facecolor}

def make_text(x, y, text, fontsize=75, layer=10, color="black", ha="center", va="center", rotation=0.0, render_mode=None):
    """Create a text primitive.
    
    render_mode: None uses global default. Options: "auto", "mpl_latex", "mpl_mathtext", "typst", "qt"
    """
    return {"type": "text", "x": float(x), "y": float(y), "text": text, "fontsize": fontsize, "l": layer, "color": color, "ha": ha, "va": va, "rotation": rotation, "render_mode": render_mode}

# --- Helpers ---------------------------------------------------------

def _as_list(obj_or_list):
    """Ensures input is a list."""
    if isinstance(obj_or_list, list):
        return obj_or_list
    else:
        return [obj_or_list]

# --- Transformations ---------------------------------------------------------

def translate(obj_or_list, dx, dy):
    """Translates lines/circles by (dx,dy)."""
    objs = _as_list(obj_or_list)
    out = []
    for obj in objs:
        o = dict(obj)  # Copy
        if o["type"] == "line":
            o["x"] = [o["x"][0] + dx, o["x"][1] + dx]
            o["y"] = [o["y"][0] + dy, o["y"][1] + dy]
        elif o["type"] == "circle":
            o["x"] += dx
            o["y"] += dy
        elif o["type"] == "polygon":
            o["points"] = [(x + dx, y + dy) for x, y in o["points"]]
        elif o["type"] == "arc":
            o["x"] += dx
            o["y"] += dy
        elif o["type"] == "text":
            o["x"] += dx
            o["y"] += dy
        elif o["type"] == "group":
             o["objects"] = translate(o["objects"], dx, dy)
        out.append(o)
    return out if isinstance(obj_or_list, list) else out[0]

def rotate(obj_or_list, cx, cy, angle_deg, ignore_text=False):
    """Rotates lines/circles around (cx,cy)."""
    objs = _as_list(obj_or_list)
    out = []
    ang = radians(angle_deg)
    ca, sa = cos(ang), sin(ang)

    def _rot(x, y):
        dx, dy = x - cx, y - cy
        return cx + dx*ca - dy*sa, cy + dx*sa + dy*ca

    for obj in objs:
        o = dict(obj)
        if o["type"] == "line":
            x0, y0 = _rot(o["x"][0], o["y"][0])
            x1, y1 = _rot(o["x"][1], o["y"][1])
            o["x"] = [x0, x1]
            o["y"] = [y0, y1]
        elif o["type"] == "circle":
            x, y = _rot(o["x"], o["y"])
            o["x"], o["y"] = x, y
        elif o["type"] == "polygon":
            o["points"] = [_rot(x, y) for x, y in o["points"]]
        elif o["type"] == "arc":
            o["x"], o["y"] = _rot(o["x"], o["y"])
            o["theta1"] += angle_deg
            o["theta2"] += angle_deg
        elif o["type"] == "text":
            o["x"], o["y"] = _rot(o["x"], o["y"])
            if not ignore_text:
                o["rotation"] = o.get("rotation", 0.0) + angle_deg
        elif o["type"] == "group":
             o["objects"] = rotate(o["objects"], cx, cy, angle_deg)
        out.append(o)
    return out if isinstance(obj_or_list, list) else out[0]

def scale(obj_or_list, cx, cy, factor, scale_linewidth=False):
    """Scales lines/circles relative to (cx,cy)."""
    objs = _as_list(obj_or_list)
    out = []

    for obj in objs:
        o = dict(obj)
        if o["type"] == "line":
            o["x"] = [cx + (x - cx)*factor for x in o["x"]]
            o["y"] = [cy + (y - cy)*factor for y in o["y"]]
            if scale_linewidth:
                o["lw"] *= factor
        elif o["type"] == "circle":
            o["x"] = cx + (o["x"] - cx)*factor
            o["y"] = cy + (o["y"] - cy)*factor
            o["r"] *= factor
            if scale_linewidth:
                o["lw"] *= factor
        elif o["type"] == "polygon":
            o["points"] = [(cx + (x - cx)*factor, cy + (y - cy)*factor) for x, y in o["points"]]
            if scale_linewidth:
                o["lw"] *= factor
        elif o["type"] == "arc":
            o["x"], o["y"] = (cx + (o["x"] - cx)*factor, cy + (o["y"] - cy)*factor)
            o["width"], o["height"] = (o["width"] * factor, o["height"] * factor)
            if scale_linewidth:
                o["lw"] *= factor
        elif o["type"] == "text":
            o["x"] = cx + (o["x"] - cx)*factor
            o["y"] = cy + (o["y"] - cy)*factor
            o["fontsize"] = o["fontsize"] * factor
        elif o["type"] == "group":
             o["objects"] = scale(o["objects"], cx, cy, factor, scale_linewidth)
        out.append(o)
    return out if isinstance(obj_or_list, list) else out[0]
