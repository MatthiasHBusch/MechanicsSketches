"""
Test script for headless Qt rendering with error handling.

Run with: set QT_QPA_PLATFORM=offscreen && python test_headless_rendering.py

This tests both successful rendering and error handling.
"""
import os
import sys
import tempfile

# MUST set before any Qt imports!
os.environ['QT_QPA_PLATFORM'] = 'offscreen'

# Now we can import
from PyQt5.QtWidgets import QApplication

# Create QApplication before importing MechanicsSketches
app = QApplication.instance()
if app is None:
    app = QApplication(sys.argv)

# Now import MechanicsSketches
from MechanicsSketches import create_sketch, render, RenderError
from MechanicsSketches.elements import add_beam, add_pinned_support


def test_successful_pdf_render():
    """Test that PDF rendering works and creates valid output."""
    print("\n=== Test: Successful PDF Render ===")
    
    sketch = create_sketch("Test PDF")
    add_beam(sketch, 0, 0, 10, 0)
    add_pinned_support(sketch, 0, 0)
    
    with tempfile.NamedTemporaryFile(suffix=".pdf", delete=False) as f:
        output_path = f.name
    
    try:
        render(sketch, filename=output_path)
        
        if os.path.exists(output_path):
            size = os.path.getsize(output_path)
            print(f"  PASS: PDF created ({size} bytes)")
            return True
        else:
            print("  FAIL: PDF not created")
            return False
    except Exception as e:
        print(f"  FAIL: Exception raised: {e}")
        return False
    finally:
        if os.path.exists(output_path):
            os.unlink(output_path)


def test_successful_png_render():
    """Test that PNG rendering works and creates valid output."""
    print("\n=== Test: Successful PNG Render ===")
    
    sketch = create_sketch("Test PNG")
    add_beam(sketch, 0, 0, 10, 0)
    
    with tempfile.NamedTemporaryFile(suffix=".png", delete=False) as f:
        output_path = f.name
    
    try:
        render(sketch, filename=output_path)
        
        if os.path.exists(output_path):
            size = os.path.getsize(output_path)
            print(f"  PASS: PNG created ({size} bytes)")
            return True
        else:
            print("  FAIL: PNG not created")
            return False
    except Exception as e:
        print(f"  FAIL: Exception raised: {e}")
        return False
    finally:
        if os.path.exists(output_path):
            os.unlink(output_path)


def test_missing_filename_raises_valueerror():
    """Test that missing filename raises ValueError."""
    print("\n=== Test: Missing Filename Raises ValueError ===")
    
    sketch = create_sketch("Test")
    add_beam(sketch, 0, 0, 10, 0)
    
    try:
        render(sketch, filename=None)
        print("  FAIL: No exception raised")
        return False
    except ValueError as e:
        print(f"  PASS: ValueError raised: {e}")
        return True
    except Exception as e:
        print(f"  FAIL: Wrong exception type: {type(e).__name__}: {e}")
        return False


def test_invalid_path_raises_rendererror():
    """Test that invalid path raises RenderError."""
    print("\n=== Test: Invalid Path Raises RenderError ===")
    
    sketch = create_sketch("Test")
    add_beam(sketch, 0, 0, 10, 0)
    
    try:
        render(sketch, filename="/nonexistent/path/test.pdf")
        print("  FAIL: No exception raised")
        return False
    except RenderError as e:
        print(f"  PASS: RenderError raised: {e}")
        return True
    except Exception as e:
        print(f"  FAIL: Wrong exception type: {type(e).__name__}: {e}")
        return False


def test_render_error_is_exported():
    """Test that RenderError is exported from the package."""
    print("\n=== Test: RenderError Is Exported ===")
    
    try:
        from MechanicsSketches import RenderError
        print(f"  PASS: RenderError is {RenderError}")
        return True
    except ImportError as e:
        print(f"  FAIL: Cannot import RenderError: {e}")
        return False


if __name__ == "__main__":
    tests = [
        test_render_error_is_exported,
        test_missing_filename_raises_valueerror,
        test_invalid_path_raises_rendererror,
        test_successful_pdf_render,
        test_successful_png_render,
    ]
    
    passed = 0
    failed = 0
    
    for test in tests:
        try:
            if test():
                passed += 1
            else:
                failed += 1
        except Exception as e:
            print(f"  ERROR: {e}")
            import traceback
            traceback.print_exc()
            failed += 1
    
    print(f"\n{'='*50}")
    print(f"Results: {passed} passed, {failed} failed")
    print(f"{'='*50}")
    
    sys.exit(0 if failed == 0 else 1)
