"""
Test automatic headless mode - no manual QT_QPA_PLATFORM setting required.
"""
import sys
import os
import tempfile

# Simply import MechanicsSketches - it should auto-configure for headless
from MechanicsSketches import create_sketch, render, RenderError
from MechanicsSketches.elements import add_beam, add_pinned_support

print(f"QT_QPA_PLATFORM = {os.environ.get('QT_QPA_PLATFORM', 'NOT SET')}")

# Create a test sketch
sketch = create_sketch("Auto Headless Test")
add_beam(sketch, 0, 0, 10, 0)
add_pinned_support(sketch, 0, 0)

# Try rendering to PDF
with tempfile.NamedTemporaryFile(suffix=".pdf", delete=False) as f:
    output_path = f.name

try:
    render(sketch, filename=output_path)
    size = os.path.getsize(output_path)
    print(f"SUCCESS: Created {output_path} ({size} bytes)")
except Exception as e:
    print(f"FAILED: {e}")
    import traceback
    traceback.print_exc()
finally:
    if os.path.exists(output_path):
        os.unlink(output_path)
