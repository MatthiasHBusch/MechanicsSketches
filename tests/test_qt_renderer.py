"""
Tests for Qt renderer error handling.

Uses subprocess to ensure QT_QPA_PLATFORM is set before any Qt imports.
This is necessary because Qt reads the platform at first import time.

Run with: python test_qt_renderer.py
"""

import os
import sys
import subprocess
import tempfile

def run_headless_script(script_code: str) -> tuple:
    """Run a Python script with offscreen Qt platform set.
    
    Returns:
        (returncode, stdout, stderr)
    """
    env = os.environ.copy()
    env['QT_QPA_PLATFORM'] = 'offscreen'
    
    result = subprocess.run(
        [sys.executable, '-c', script_code],
        env=env,
        capture_output=True,
        text=True,
        cwd=os.path.dirname(os.path.abspath(__file__))
    )
    return result.returncode, result.stdout, result.stderr


class TestRenderErrorRaised:
    """Test that RenderError is raised for various failure conditions."""
    
    def test_invalid_directory_raises_error(self):
        """Rendering to a non-existent directory should raise RenderError."""
        script = '''
import sys
sys.path.insert(0, '.')
from MechanicsSketches import create_sketch, render, RenderError
from MechanicsSketches.elements import add_beam

sketch = create_sketch("Test")
add_beam(sketch, 0, 0, 10, 0)

try:
    render(sketch, filename="/nonexistent/path/test.pdf")
    print("ERROR: No exception raised")
    sys.exit(1)
except RenderError as e:
    print(f"SUCCESS: RenderError raised: {e}")
    sys.exit(0)
except Exception as e:
    print(f"ERROR: Wrong exception type: {type(e).__name__}: {e}")
    sys.exit(1)
'''
        returncode, stdout, stderr = run_headless_script(script)
        assert returncode == 0, f"Test failed:\nstdout: {stdout}\nstderr: {stderr}"
        assert "SUCCESS" in stdout, f"Expected SUCCESS in output:\n{stdout}"
    
    def test_missing_filename_raises_error(self):
        """Rendering without a filename should raise ValueError."""
        script = '''
import sys
sys.path.insert(0, '.')
from MechanicsSketches import create_sketch, render
from MechanicsSketches.elements import add_beam

sketch = create_sketch("Test")
add_beam(sketch, 0, 0, 10, 0)

try:
    render(sketch, filename=None)
    print("ERROR: No exception raised")
    sys.exit(1)
except ValueError as e:
    print(f"SUCCESS: ValueError raised: {e}")
    sys.exit(0)
except Exception as e:
    print(f"ERROR: Wrong exception type: {type(e).__name__}: {e}")
    sys.exit(1)
'''
        returncode, stdout, stderr = run_headless_script(script)
        assert returncode == 0, f"Test failed:\nstdout: {stdout}\nstderr: {stderr}"


class TestSuccessfulRender:
    """Test that successful renders produce valid output."""
    
    def test_pdf_export_creates_file(self):
        """PDF export should create a non-empty file."""
        with tempfile.NamedTemporaryFile(suffix=".pdf", delete=False) as f:
            output_path = f.name
        
        script = f'''
import sys
import os
sys.path.insert(0, '.')
from MechanicsSketches import create_sketch, render
from MechanicsSketches.elements import add_beam, add_pinned_support

sketch = create_sketch("Test PDF")
add_beam(sketch, 0, 0, 10, 0)
add_pinned_support(sketch, 0, 0)

output_path = r"{output_path}"
render(sketch, filename=output_path)

if os.path.exists(output_path):
    size = os.path.getsize(output_path)
    print(f"SUCCESS: Created file with {{size}} bytes")
    sys.exit(0)
else:
    print("ERROR: File not created")
    sys.exit(1)
'''
        try:
            returncode, stdout, stderr = run_headless_script(script)
            assert returncode == 0, f"Test failed:\nstdout: {stdout}\nstderr: {stderr}"
            assert os.path.exists(output_path), "PDF file was not created"
            assert os.path.getsize(output_path) > 0, "PDF file is empty"
        finally:
            if os.path.exists(output_path):
                os.unlink(output_path)
    
    def test_png_export_creates_file(self):
        """PNG export should create a non-empty file."""
        with tempfile.NamedTemporaryFile(suffix=".png", delete=False) as f:
            output_path = f.name
        
        script = f'''
import sys
import os
sys.path.insert(0, '.')
from MechanicsSketches import create_sketch, render
from MechanicsSketches.elements import add_beam

sketch = create_sketch("Test PNG")
add_beam(sketch, 0, 0, 10, 0)

output_path = r"{output_path}"
render(sketch, filename=output_path)

if os.path.exists(output_path):
    size = os.path.getsize(output_path)
    print(f"SUCCESS: Created file with {{size}} bytes")
    sys.exit(0)
else:
    print("ERROR: File not created")
    sys.exit(1)
'''
        try:
            returncode, stdout, stderr = run_headless_script(script)
            assert returncode == 0, f"Test failed:\nstdout: {stdout}\nstderr: {stderr}"
            assert os.path.exists(output_path), "PNG file was not created"
            assert os.path.getsize(output_path) > 0, "PNG file is empty"
        finally:
            if os.path.exists(output_path):
                os.unlink(output_path)
    
    def test_svg_export_creates_file(self):
        """SVG export should create a non-empty file."""
        with tempfile.NamedTemporaryFile(suffix=".svg", delete=False) as f:
            output_path = f.name
        
        script = f'''
import sys
import os
sys.path.insert(0, '.')
from MechanicsSketches import create_sketch, render
from MechanicsSketches.elements import add_beam

sketch = create_sketch("Test SVG")
add_beam(sketch, 0, 0, 10, 0)

output_path = r"{output_path}"
render(sketch, filename=output_path)

if os.path.exists(output_path):
    size = os.path.getsize(output_path)
    print(f"SUCCESS: Created file with {{size}} bytes")
    sys.exit(0)
else:
    print("ERROR: File not created")
    sys.exit(1)
'''
        try:
            returncode, stdout, stderr = run_headless_script(script)
            assert returncode == 0, f"Test failed:\nstdout: {stdout}\nstderr: {stderr}"
            assert os.path.exists(output_path), "SVG file was not created"
            assert os.path.getsize(output_path) > 0, "SVG file is empty"
        finally:
            if os.path.exists(output_path):
                os.unlink(output_path)


class TestEditorNotAffected:
    """Verify that editor code path still works (uses render_scene directly)."""
    
    def test_render_scene_available(self):
        """render_scene function should still be importable and callable."""
        script = '''
import sys
sys.path.insert(0, '.')
# Import Qt first with offscreen platform
from MechanicsSketches.qt_renderer import render_scene
print(f"SUCCESS: render_scene is {type(render_scene)}")
'''
        returncode, stdout, stderr = run_headless_script(script)
        assert returncode == 0, f"Test failed:\nstdout: {stdout}\nstderr: {stderr}"
        assert "SUCCESS" in stdout, f"Expected SUCCESS in output:\n{stdout}"


if __name__ == "__main__":
    # Run tests manually
    import traceback
    
    tests = [
        ("test_missing_filename_raises_error", TestRenderErrorRaised().test_missing_filename_raises_error),
        ("test_invalid_directory_raises_error", TestRenderErrorRaised().test_invalid_directory_raises_error),
        ("test_pdf_export_creates_file", TestSuccessfulRender().test_pdf_export_creates_file),
        ("test_png_export_creates_file", TestSuccessfulRender().test_png_export_creates_file),
        ("test_svg_export_creates_file", TestSuccessfulRender().test_svg_export_creates_file),
        ("test_render_scene_available", TestEditorNotAffected().test_render_scene_available),
    ]
    
    passed = 0
    failed = 0
    
    for name, test_func in tests:
        try:
            test_func()
            print(f"PASS: {name}")
            passed += 1
        except Exception as e:
            print(f"FAIL: {name}")
            traceback.print_exc()
            failed += 1
    
    print(f"\n{passed} passed, {failed} failed")
    sys.exit(1 if failed > 0 else 0)
