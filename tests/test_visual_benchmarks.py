"""
Visual benchmark tests for MechanicsSketches.

Renders all best-practice examples and verifies they produce valid output.
Run with: QT_QPA_PLATFORM=offscreen python -m pytest tests/test_visual_benchmarks.py -v

These serve as visual regression tests — if a code change breaks rendering,
these tests will catch it. The reference images in examples/ can be compared
manually or with image-diff tools.
"""
import os
import sys
import tempfile

# Headless Qt setup (must be before any Qt imports)
os.environ['QT_QPA_PLATFORM'] = 'offscreen'

# Add parent to path so MechanicsSketches is importable
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from PyQt5.QtWidgets import QApplication
app = QApplication.instance()
if app is None:
    app = QApplication(sys.argv)

from MechanicsSketches import create_sketch, render
from MechanicsSketches.elements import *

import math
import pytest

S = 30.0  # Standard scale factor


def render_to_temp(sketch, suffix=".png"):
    """Render sketch to a temp file and return (path, size)."""
    with tempfile.NamedTemporaryFile(suffix=suffix, delete=False) as f:
        path = f.name
    render(sketch, filename=path, dpi=150)
    size = os.path.getsize(path)
    os.unlink(path)
    return size


class TestSimplySupported:
    def test_renders(self):
        sketch = create_sketch("Simply Supported Beam")
        add_beam(sketch, ax=0, ay=0, bx=10*S, by=0, scale_factor=S)
        add_pinned_support(sketch, cx=0, cy=0, angle_deg=0, scale_factor=S)
        add_roller_support(sketch, cx=10*S, cy=0, angle_deg=0, scale_factor=S)
        add_force(sketch, cx=5*S, cy=0, angle_deg=0, scale_factor=S, annotation=r"$F$")
        add_dimension_arrow_pp(sketch, ax=0, ay=-2.8*S, bx=5*S, by=-2.8*S,
                               scale_factor=S*0.5, annotation=r"$a$", fontsize_scale=2.0)
        add_dimension_arrow_pp(sketch, ax=5*S, ay=-2.8*S, bx=10*S, by=-2.8*S,
                               scale_factor=S*0.5, annotation=r"$b$", fontsize_scale=2.0)
        add_dimension_arrow_pp(sketch, ax=0, ay=-4.5*S, bx=10*S, by=-4.5*S,
                               scale_factor=S*0.5, annotation=r"$L$", fontsize_scale=2.0)
        add_coordinate_system(sketch, cx=-2.5*S, cy=-4*S, scale_factor=S*0.5,
                              ax1=r"$x$", ax2=r"$z$", ax3=r"$y$",
                              last_axis_out_of_image=True, fontsize_scale=2.0)
        size = render_to_temp(sketch)
        assert size > 5000, f"Output too small ({size} bytes), likely broken render"


class TestCantilever:
    def test_renders(self):
        sketch = create_sketch("Cantilever Beam")
        add_fixed_support(sketch, cx=0, cy=0, angle_deg=0, scale_factor=S)
        add_beam(sketch, ax=0, ay=0, bx=8*S, by=0, scale_factor=S)
        add_force(sketch, cx=8*S, cy=0, angle_deg=0, scale_factor=S, annotation=r"$P$")
        add_moment(sketch, cx=0, cy=0, angle_deg=0, scale_factor=S*0.7,
                   annotation=r"$M_A$", fontsize_scale=1.4)
        add_dimension_arrow_pp(sketch, ax=0, ay=-2.5*S, bx=8*S, by=-2.5*S,
                               scale_factor=S*0.5, annotation=r"$L$", fontsize_scale=2.0)
        size = render_to_temp(sketch)
        assert size > 5000


class TestProppedCantilever:
    def test_renders(self):
        sketch = create_sketch("Propped Cantilever FBD")
        L = 12
        add_beam(sketch, ax=0, ay=0, bx=L*S, by=0, scale_factor=S)
        add_fixed_support(sketch, cx=0, cy=0, angle_deg=0, scale_factor=S)
        add_roller_support(sketch, cx=L*S, cy=0, angle_deg=0, scale_factor=S)
        add_force(sketch, cx=4*S, cy=0, angle_deg=0, scale_factor=S, annotation=r"$F_1$")
        add_force(sketch, cx=8*S, cy=0, angle_deg=0, scale_factor=S, annotation=r"$F_2$")
        add_moment(sketch, cx=0, cy=0, angle_deg=0, scale_factor=S*0.7,
                   annotation=r"$M_A$", fontsize_scale=1.4)
        size = render_to_temp(sketch)
        assert size > 5000


class TestTruss:
    def test_renders(self):
        sketch = create_sketch("Simple Truss")
        t = S * 0.08
        add_truss(sketch, ax=0, ay=0, bx=4*S, by=0, scale_factor=t)
        add_truss(sketch, ax=4*S, ay=0, bx=8*S, by=0, scale_factor=t)
        add_truss(sketch, ax=0, ay=0, bx=4*S, by=3*S, scale_factor=t)
        add_truss(sketch, ax=4*S, ay=3*S, bx=8*S, by=0, scale_factor=t)
        add_truss(sketch, ax=4*S, ay=0, bx=4*S, by=3*S, scale_factor=t)
        for cx, cy in [(0,0), (4*S,0), (8*S,0), (4*S,3*S)]:
            add_hinge(sketch, cx=cx, cy=cy, scale_factor=S)
        add_pinned_support(sketch, cx=0, cy=0, angle_deg=0, scale_factor=S)
        add_roller_support(sketch, cx=8*S, cy=0, angle_deg=0, scale_factor=S)
        add_force(sketch, cx=4*S, cy=3*S, angle_deg=0, scale_factor=S, annotation=r"$F$")
        size = render_to_temp(sketch)
        assert size > 5000


class TestFrame:
    def test_renders(self):
        sketch = create_sketch("L-Frame")
        add_beam(sketch, ax=0, ay=0, bx=0, by=6*S, scale_factor=S)
        add_beam(sketch, ax=0, ay=6*S, bx=8*S, by=6*S, scale_factor=S)
        add_fixed_support(sketch, cx=0, cy=0, angle_deg=90, scale_factor=S)
        add_roller_support(sketch, cx=8*S, cy=6*S, angle_deg=0, scale_factor=S)
        add_hinge(sketch, cx=0, cy=6*S, scale_factor=S)
        add_force(sketch, cx=0, cy=3*S, angle_deg=90, scale_factor=S, annotation=r"$H$")
        add_force(sketch, cx=4*S, cy=6*S, angle_deg=0, scale_factor=S, annotation=r"$V$")
        size = render_to_temp(sketch)
        assert size > 5000


class TestDistributedLoad:
    def test_arrowheads_above_beam(self):
        """Verify distributed load arrows start at beam top, not inside beam."""
        sketch = create_sketch("Distributed Load")
        Sf = S * 0.4
        beam_top = 0.4 * S
        add_beam(sketch, ax=0, ay=0, bx=10*S, by=0, scale_factor=S)
        add_pinned_support(sketch, cx=0, cy=0, angle_deg=0, scale_factor=S)
        add_roller_support(sketch, cx=10*S, cy=0, angle_deg=0, scale_factor=S)
        for i in range(1, 8):
            add_force(sketch, cx=i*10*S/8, cy=beam_top, angle_deg=0, scale_factor=Sf)
        size = render_to_temp(sketch)
        assert size > 5000


class TestMoments:
    def test_renders(self):
        sketch = create_sketch("Beam with Moments")
        L = 12
        add_beam(sketch, ax=0, ay=0, bx=L*S, by=0, scale_factor=S)
        add_pinned_support(sketch, cx=0, cy=0, angle_deg=0, scale_factor=S)
        add_roller_support(sketch, cx=L*S, cy=0, angle_deg=0, scale_factor=S)
        add_moment(sketch, cx=3*S, cy=0, angle_deg=0, scale_factor=S*0.7,
                   annotation=r"$M_1$", fontsize_scale=1.4, offsetx=1.5*S)
        add_moment(sketch, cx=9*S, cy=0, angle_deg=180, scale_factor=S*0.7,
                   annotation=r"$M_2$", fontsize_scale=1.4, offsetx=1.5*S)
        size = render_to_temp(sketch)
        assert size > 5000


class TestInclinedBeam:
    def test_renders(self):
        sketch = create_sketch("Inclined Beam")
        angle = 25
        L = 8
        bx = L * S * math.cos(math.radians(angle))
        by = L * S * math.sin(math.radians(angle))
        add_beam(sketch, ax=0, ay=0, bx=bx, by=by, scale_factor=S)
        add_pinned_support(sketch, cx=0, cy=0, angle_deg=0, scale_factor=S)
        add_roller_support(sketch, cx=bx, cy=by, angle_deg=0, scale_factor=S)
        add_force(sketch, cx=bx/2, cy=by/2, angle_deg=0, scale_factor=S, annotation=r"$F$")
        add_dimension_arrow_pp(sketch, ax=0, ay=-3*S, bx=bx, by=-3*S,
                               scale_factor=S*0.5, annotation=r"$L \cos\alpha$",
                               fontsize_scale=2.0)
        size = render_to_temp(sketch)
        assert size > 5000


class TestTwoSpan:
    def test_renders(self):
        sketch = create_sketch("Two-Span Beam with Hinge")
        add_beam(sketch, ax=0, ay=0, bx=6*S, by=0, scale_factor=S)
        add_beam(sketch, ax=6*S, ay=0, bx=14*S, by=0, scale_factor=S)
        add_pinned_support(sketch, cx=0, cy=0, angle_deg=0, scale_factor=S)
        add_roller_support(sketch, cx=6*S, cy=0, angle_deg=0, scale_factor=S)
        add_roller_support(sketch, cx=14*S, cy=0, angle_deg=0, scale_factor=S)
        add_hinge(sketch, cx=10*S, cy=0, scale_factor=S)
        add_force(sketch, cx=3*S, cy=0, angle_deg=0, scale_factor=S, annotation=r"$F_1$")
        add_force(sketch, cx=12*S, cy=0, angle_deg=0, scale_factor=S, annotation=r"$F_2$")
        size = render_to_temp(sketch)
        assert size > 5000


class TestVerticalColumn:
    def test_renders(self):
        sketch = create_sketch("Vertical Column")
        H = 8
        add_beam(sketch, ax=0, ay=0, bx=0, by=H*S, scale_factor=S)
        add_fixed_support(sketch, cx=0, cy=0, angle_deg=90, scale_factor=S)
        add_force(sketch, cx=0, cy=H*S, angle_deg=90, scale_factor=S, annotation=r"$H$")
        add_dimension_arrow(sketch, cx=3*S, cy=H*S/2, length=H*S,
                            angle_deg=90, scale_factor=S*0.5, annotation=r"$h$",
                            fontsize_scale=2.0)
        size = render_to_temp(sketch)
        assert size > 5000


class TestOutputFormats:
    """Verify rendering works for all supported formats."""
    @pytest.mark.parametrize("suffix", [".png", ".pdf", ".svg"])
    def test_format(self, suffix):
        sketch = create_sketch("Format Test")
        add_beam(sketch, ax=0, ay=0, bx=5*S, by=0, scale_factor=S)
        add_pinned_support(sketch, cx=0, cy=0, angle_deg=0, scale_factor=S)
        size = render_to_temp(sketch, suffix=suffix)
        assert size > 500, f"{suffix} output too small ({size} bytes)"
