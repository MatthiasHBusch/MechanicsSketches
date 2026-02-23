# MechanicsSketches package
# Provides tools for creating engineering mechanics sketches

import os
import sys

# =============================================================================
# Automatic Headless Mode Setup
# =============================================================================
# Set offscreen Qt platform BEFORE importing any Qt modules.
# This allows headless rendering to work automatically when importing the package.
# 
# When user runs editor directly (python editor.py), this code doesn't run,
# so the editor uses normal display. Only script/library usage triggers offscreen.
#
# User can override by setting QT_QPA_PLATFORM before importing.

def _setup_headless_qt():
    """Configure Qt for headless rendering if not already configured."""
    # Don't override user's explicit setting
    if 'QT_QPA_PLATFORM' in os.environ:
        return
    
    # Check if a QApplication already exists (e.g., running inside editor)
    # Can't import Qt to check this, but we can check if Qt modules are loaded
    if 'PyQt5.QtWidgets' in sys.modules:
        return  # Qt already loaded, don't change platform
    
    # Set offscreen platform for headless use
    os.environ['QT_QPA_PLATFORM'] = 'offscreen'

_setup_headless_qt()

# =============================================================================
# Package Exports
# =============================================================================
from .base import *
from .elements import *
from .renderer import mpl_render           # matplotlib renderer (original)
from .qt_renderer import render            # Qt renderer (new)
from .qt_renderer import RenderError       # Error type for catching render failures
