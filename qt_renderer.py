"""
Qt-based renderer for MechanicsSketches.

This module provides PDF, PNG, and SVG export using Qt's native rendering.
All rendering logic is centralized here and shared by both:
  - The editor GUI (via render_scene)
  - Headless scripting (via render)

Usage:
    from MechanicsSketches import qt_render
    
    sketch = create_sketch("My Sketch")
    add_beam(sketch, 0, 0, 10, 0)
    qt_render(sketch, filename="output.pdf")

Requires: PyQt5
"""

import sys
import os

# For headless rendering support:
# Set offscreen platform BEFORE importing PyQt5.
# This is needed because Qt reads the platform at DLL load time.
#
# This file (qt_renderer) is imported when users do `from MechanicsSketches import render`.
# The editor (editor.py) imports PyQt5 directly at its top level, BEFORE this file,
# so when the editor runs standalone, PyQt5 is already loaded with normal display.
#
# User can override by setting QT_QPA_PLATFORM before importing.

def _setup_offscreen_platform():
    """Set offscreen Qt platform for headless rendering if not already configured."""
    # User explicitly set platform - respect their choice
    if 'QT_QPA_PLATFORM' in os.environ:
        return
    
    # Check if Qt is already loaded (e.g., editor already running)
    # If so, don't try to change the platform
    if 'PyQt5.QtWidgets' in sys.modules:
        return
    
    # Set offscreen platform for headless rendering
    os.environ['QT_QPA_PLATFORM'] = 'offscreen'
    
    # Fix font loading for offscreen platform on Windows
    # Qt's offscreen plugin can't find fonts without this
    if sys.platform == 'win32' and 'QT_QPA_FONTDIR' not in os.environ:
        # Use Windows system fonts directory
        windir = os.environ.get('WINDIR', 'C:\\Windows')
        fontdir = os.path.join(windir, 'Fonts')
        if os.path.isdir(fontdir):
            os.environ['QT_QPA_FONTDIR'] = fontdir

_setup_offscreen_platform()


def _setup_font_directory():
    """Set font directory for offscreen Qt platform on Windows."""
    # Only needed for offscreen platform
    if os.environ.get('QT_QPA_PLATFORM') != 'offscreen':
        return
    
    # Don't override if user already set it
    if 'QT_QPA_FONTDIR' in os.environ:
        return
    
    # On Windows, point to system fonts
    if sys.platform == 'win32':
        windir = os.environ.get('WINDIR', 'C:\\Windows')
        fontdir = os.path.join(windir, 'Fonts')
        if os.path.isdir(fontdir):
            os.environ['QT_QPA_FONTDIR'] = fontdir

_setup_font_directory()


# PyQt5 is optional - allows package to be imported even without PyQt5
HAS_PYQT5 = False
try:
    from PyQt5.QtWidgets import QApplication
    from PyQt5.QtCore import Qt, QRectF, QMarginsF, QSizeF
    from PyQt5.QtGui import QImage, QPainter, QPageSize
    from PyQt5.QtPrintSupport import QPrinter
    from PyQt5.QtSvg import QSvgGenerator
    HAS_PYQT5 = True
    
    # Create QApplication immediately for headless mode
    # This prevents crashes when editor.py is imported and creates QGraphicsScene
    if QApplication.instance() is None:
        _headless_app = QApplication(sys.argv)
except ImportError:
    pass


class RenderError(Exception):
    """Raised when rendering fails. Contains actionable error message."""
    pass


def _check_pyqt5():
    """Raise ImportError with helpful message if PyQt5 is not available."""
    if not HAS_PYQT5:
        raise ImportError(
            "PyQt5 is required for qt_render(). "
            "Install it with: pip install PyQt5\n"
            "Alternatively, use the matplotlib renderer: render(sketch, filename=...)"
        )

# Import SketchScene for creating scenes from sketch data
# This import is delayed to avoid circular imports
_SketchScene = None

def _get_sketch_scene_class():
    """Lazily import SketchScene to avoid circular imports.
    
    CRITICAL: Import MUST happen after QApplication exists because
    editor.py imports PyQt5 at module level and some Qt operations
    fail without an app. We ensure QApp exists before importing.
    """
    global _SketchScene
    if _SketchScene is None:
        # Create QApplication BEFORE importing editor.py
        # This prevents crashes on Windows where Qt needs an app instance
        _ensure_qapp()
        from .editor import SketchScene
        _SketchScene = SketchScene
    return _SketchScene


def _ensure_qapp():
    """Ensure a QApplication exists (needed for headless rendering).
    
    For headless mode, we set the 'offscreen' platform plugin if no display
    is available to prevent crashes on Windows.
    """
    app = QApplication.instance()
    if app is None:
        # For headless rendering, try offscreen platform first
        # This prevents crashes on Windows when no display is available
        if 'QT_QPA_PLATFORM' not in os.environ:
            os.environ['QT_QPA_PLATFORM'] = 'offscreen'
        
        try:
            app = QApplication(sys.argv)
        except Exception as e:
            raise RenderError(
                f"Failed to create Qt application for headless rendering: {e}. "
                f"Try setting QT_QPA_PLATFORM=offscreen environment variable."
            ) from e
    return app



def _get_scene_bounds(scene, margin=0.05):
    """Get the bounding rect of scene contents with margin."""
    bounds = scene.itemsBoundingRect()
    if bounds.isEmpty():
        bounds = QRectF(0, 0, 100, 100)
    
    # calculate bounds relative to scene width and height
    return bounds.adjusted(
        -margin * bounds.width(),
        -margin * bounds.height(),
        margin * bounds.width(),
        margin * bounds.height()
    )


# =============================================================================
# Core Rendering Functions (shared by editor and headless API)
# =============================================================================

def render_scene_to_pdf(scene, filename, margin=0.05):
    """
    Render a QGraphicsScene to vector PDF.
    
    Args:
        scene: QGraphicsScene instance
        filename: Output PDF path
        margin: Border margin in scene units
    """
    bounds = _get_scene_bounds(scene, margin)
    
    printer = QPrinter(QPrinter.HighResolution)
    printer.setOutputFormat(QPrinter.PdfFormat)
    printer.setOutputFileName(filename)
    
    # Set page size to match content bounds (convert scene units to millimeters)
    # Scene units are roughly points, 1 point = 0.3528 mm
    width_mm = bounds.width() * 0.3528
    height_mm = bounds.height() * 0.3528
    page_size = QPageSize(QSizeF(width_mm, height_mm), QPageSize.Millimeter)
    printer.setPageSize(page_size)
    
    # Handle different PyQt5 signatures for setPageMargins
    try:
        from PyQt5.QtGui import QPageLayout
        printer.setPageMargins(QMarginsF(0, 0, 0, 0), QPageLayout.Millimeter)
    except (TypeError, ImportError):
        # Fallback for older PyQt5 versions
        printer.setPageMargins(0, 0, 0, 0, QPrinter.Millimeter)
    
    painter = QPainter(printer)
    if not painter.isActive():
        raise RenderError(
            f"Failed to create PDF painter for '{filename}'. "
            f"Check that the path is writable and not in use."
        )
    
    # Get the actual page rect we're painting to
    page_rect = printer.pageRect(QPrinter.DevicePixel)
    
    # Apply Y-flip transformation to match editor view orientation
    painter.translate(0, page_rect.height())
    painter.scale(1, -1)
    
    # Define target rectangle (full page) and render
    target_rect = QRectF(0, 0, page_rect.width(), page_rect.height())
    scene.render(painter, target_rect, bounds)
    painter.end()


def render_scene_to_image(scene, filename, dpi=300, margin=0.05):
    """
    Render a QGraphicsScene to raster image (PNG, JPG).
    
    Args:
        scene: QGraphicsScene instance
        filename: Output image path
        dpi: Dots per inch for output resolution
        margin: Border margin in scene units
    """
    bounds = _get_scene_bounds(scene, margin)
    
    # Calculate pixel dimensions from scene size and DPI
    # Assuming scene units are roughly points (1/72 inch)
    scale = dpi / 72.0
    width = int(bounds.width() * scale)
    height = int(bounds.height() * scale)
    
    # Ensure minimum size
    width = max(width, 1)
    height = max(height, 1)
    
    # Create image with white background
    image = QImage(width, height, QImage.Format_ARGB32)
    image.fill(Qt.white)
    
    painter = QPainter(image)
    painter.setRenderHint(QPainter.Antialiasing)
    painter.setRenderHint(QPainter.TextAntialiasing)
    painter.setRenderHint(QPainter.SmoothPixmapTransform)
    
    # Apply Y-flip transformation to match editor view orientation
    painter.translate(0, height)
    painter.scale(1, -1)
    
    # Define target rectangle (full image)
    target_rect = QRectF(0, 0, width, height)
    
    # Render scene - let Qt handle the mapping from source to target
    scene.render(painter, target_rect, bounds)
    painter.end()
    
    if not image.save(filename):
        raise RenderError(
            f"Failed to save image to '{filename}'. "
            f"Check that the path is writable and the format is supported."
        )


def render_scene_to_svg(scene, filename, margin=0.05):
    """
    Render a QGraphicsScene to vector SVG.
    
    Args:
        scene: QGraphicsScene instance
        filename: Output SVG path
        margin: Border margin in scene units
    """
    bounds = _get_scene_bounds(scene, margin)
    
    generator = QSvgGenerator()
    generator.setFileName(filename)
    generator.setSize(bounds.size().toSize())
    generator.setViewBox(QRectF(0, 0, bounds.width(), bounds.height()))
    generator.setTitle("MechanicsSketches Export")
    
    painter = QPainter(generator)
    
    # Apply Y-flip transformation to match editor view orientation
    painter.translate(0, bounds.height())
    painter.scale(1, -1)
    
    # Define target rectangle (full SVG)
    target_rect = QRectF(0, 0, bounds.width(), bounds.height())
    
    # Render scene - let Qt handle the mapping from source to target
    scene.render(painter, target_rect, bounds)
    painter.end()


def render_scene(scene, filename, dpi=300, margin=0.05):
    """
    Unified export function - determines format from filename extension.
    
    This is the main function called by both:
    - The editor's Export dialog
    - The headless render() API (after creating a scene)
    
    Args:
        scene: QGraphicsScene instance (e.g., SketchScene)
        filename: Output path. Format determined by extension:
                  - .pdf → Vector PDF
                  - .png/.jpg/.jpeg → Raster image at specified DPI
                  - .svg → Vector SVG
        dpi: Dots per inch for raster output (default 300)
        margin: Border margin in scene units (default 10)
    
    Raises:
        ValueError: If file extension is not supported
    """
    ext = os.path.splitext(filename)[1].lower()
    
    if ext == '.pdf':
        render_scene_to_pdf(scene, filename, margin)
    elif ext in ['.png', '.jpg', '.jpeg']:
        render_scene_to_image(scene, filename, dpi, margin)
    elif ext == '.svg':
        render_scene_to_svg(scene, filename, margin)
    else:
        raise ValueError(
            f"Unsupported export format: '{ext}'. "
            f"Supported formats: .pdf, .png, .jpg, .svg"
        )


# =============================================================================
# Public API for Headless Rendering
# =============================================================================

def render(sketch, filename=None, dpi=300, margin=0.05):
    """
    Render a sketch dictionary to file without opening a GUI.
    
    This creates a temporary SketchScene, loads the sketch, and uses
    the same render_scene() function as the editor for consistent output.
    
    Args:
        sketch: Sketch dictionary from base.create_sketch()
        figsize: Tuple (width, height) - currently unused, kept for API 
                 compatibility with matplotlib renderer
        filename: Output path. Format determined by extension:
                  - .pdf → Vector PDF
                  - .png/.jpg/.jpeg → Raster image
                  - .svg → Vector SVG
                  If None, raises ValueError
        dpi: Dots per inch for raster output (default 300)
        margin: Border margin in scene units (default 10)
    
    Returns:
        None (saves to file)
    
    Raises:
        ValueError: If filename is None or format not supported
    
    Example:
        from MechanicsSketches import qt_render, create_sketch
        from MechanicsSketches.elements import add_beam
        
        sketch = create_sketch("Test")
        add_beam(sketch, 0, 0, 10, 0)
        
        qt_render(sketch, filename="output.pdf")   # Vector PDF
        qt_render(sketch, filename="output.png")   # Raster PNG
    """
    if filename is None:
        raise ValueError("filename is required for qt_render()")
    
    # Check PyQt5 is available
    _check_pyqt5()
    
    # Ensure QApplication exists
    _ensure_qapp()
    
    # Create a temporary scene and load the sketch
    SketchScene = _get_sketch_scene_class()
    scene = SketchScene(None)
    scene.load_sketch(sketch)
    
    # Use the shared rendering function
    try:
        render_scene(scene, filename, dpi, margin)
    except RenderError:
        raise  # Re-raise our own errors as-is
    except Exception as e:
        raise RenderError(f"Rendering failed: {e}") from e
    
    # Validate output file was created
    if not os.path.exists(filename):
        raise RenderError(f"Output file was not created: '{filename}'")
    
    file_size = os.path.getsize(filename)
    if file_size == 0:
        raise RenderError(f"Output file is empty: '{filename}'")
    
    print(f"Exported to {filename} ({file_size} bytes)")
