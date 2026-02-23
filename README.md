# MechanicsSketches

A Python library for creating and rendering technical sketches for engineering mechanics — beams, supports, forces, moments, dimensions, and more.

![Python 3.8+](https://img.shields.io/badge/python-3.8%2B-blue) ![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)

## Features

- **Programmatic API** — Build sketches from primitives (lines, circles, polygons, arcs, text) and pre-built mechanical components
- **Qt-based renderer** — High-quality PDF, PNG, and SVG output with automatic headless mode
- **Matplotlib fallback** — Alternative rendering via matplotlib with LaTeX support
- **Graphical editor** — Interactive PyQt5 editor with drawing tools, component library, and property editing
- **Transformations** — Translate, rotate, and scale any primitive or group (non-destructive)
- **JSON serialization** — Save and load sketches as JSON files
- **OpenClaw AgentSkill** — Let AI agents generate sketches autonomously via the bundled [OpenClaw](https://openclaw.ai) skill

## Installation

```bash
pip install matplotlib PyQt5
```

For LaTeX text rendering, install a LaTeX distribution (e.g., TeX Live or MiKTeX).

## Quick Start

```python
from MechanicsSketches import *
import os

sketch = create_sketch("Simply Supported Beam")
S = 30.0  # Scale factor

# Beam
add_beam(sketch, ax=0, ay=0, bx=10*S, by=0, scale_factor=S)

# Supports
add_pinned_support(sketch, cx=0, cy=0, angle_deg=0, scale_factor=S)
add_roller_support(sketch, cx=10*S, cy=0, angle_deg=0, scale_factor=S)

# Force with LaTeX label
add_force(sketch, cx=5*S, cy=0, angle_deg=0, scale_factor=S, annotation=r"$F$")

# Render to PDF
script_dir = os.path.dirname(os.path.abspath(__file__))
render(sketch, filename=os.path.join(script_dir, "beam.pdf"), dpi=300)
```

## Available Components

| Component | Function | Description |
|-----------|----------|-------------|
| Pinned support | `add_pinned_support()` | Triangle with hatching (Festlager) |
| Roller support | `add_roller_support()` | Support with sliding gap (Loslager) |
| Fixed support | `add_fixed_support()` | Wall with hatching (Einspannung) |
| Hinge | `add_hinge()` | Joint circle (Gelenk) |
| Beam | `add_beam()` | Rectangular beam between two points |
| Truss | `add_truss()` | Line member between two points |
| Force | `add_force()` | Arrow with optional annotation |
| Moment | `add_moment()` | Curved arrow with optional annotation |
| Dimension | `add_dimension_arrow()` | Double-headed measuring arrow |
| Thickness | `add_dimension_thickness()` | Inward-pointing dimension |
| Coord. system | `add_coordinate_system()` | x-y-z axis indicator |

Each component has a `make_*` variant that returns primitives without adding to a sketch.

## OpenClaw Integration

This library includes an [OpenClaw](https://openclaw.ai) AgentSkill, so AI agents can generate mechanics sketches autonomously. To install:

```bash
cp -r skills/mechanics-sketches ~/.openclaw/skills/
```

See [`skills/mechanics-sketches/SKILL.md`](skills/mechanics-sketches/SKILL.md) for details.

## Project Structure

```
MechanicsSketches/
├── __init__.py       # Package exports
├── base.py           # Primitives, transformations, sketch management
├── elements.py       # Pre-built mechanical components
├── qt_renderer.py    # Qt-based renderer (default)
├── renderer.py       # Matplotlib renderer (fallback)
├── editor.py         # PyQt5 graphical editor
├── docs.md           # Full API documentation
└── skills/           # OpenClaw AgentSkill
    └── mechanics-sketches/
        ├── SKILL.md
        ├── scripts/generate_sketch.py
        └── references/api_reference.md
```

## Documentation

See [docs.md](docs.md) for the complete API reference, including all function signatures, parameters, orientation conventions, and additional examples.

## License

This project is licensed under the [MIT License](LICENSE).
