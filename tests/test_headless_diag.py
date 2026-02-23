"""
Diagnostic script to test headless Qt rendering step by step.
Run with: set QT_QPA_PLATFORM=offscreen && python test_headless_diag.py
"""
import os
import sys

print("Step 1: Setting environment for headless mode...")
os.environ['QT_QPA_PLATFORM'] = 'offscreen'
print(f"  QT_QPA_PLATFORM = {os.environ.get('QT_QPA_PLATFORM')}")

print("\nStep 2: Importing PyQt5...")
try:
    from PyQt5.QtWidgets import QApplication
    from PyQt5.QtWidgets import QGraphicsScene
    from PyQt5.QtCore import Qt, QRectF
    print("  PyQt5 imported successfully")
except ImportError as e:
    print(f"  ERROR: {e}")
    sys.exit(1)

print("\nStep 3: Creating QApplication...")
try:
    app = QApplication.instance()
    if app is None:
        app = QApplication(sys.argv)
        print("  Created new QApplication")
    else:
        print("  Using existing QApplication")
except Exception as e:
    print(f"  ERROR: {e}")
    sys.exit(1)

print("\nStep 4: Creating QGraphicsScene...")
try:
    scene = QGraphicsScene()
    print("  QGraphicsScene created successfully")
except Exception as e:
    print(f"  ERROR: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)

print("\nStep 5: Importing MechanicsSketches...")
try:
    from MechanicsSketches import create_sketch
    from MechanicsSketches.elements import add_beam, add_pinned_support
    print("  MechanicsSketches imported successfully")
except Exception as e:
    print(f"  ERROR: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)

print("\nStep 6: Creating sketch...")
try:
    sketch = create_sketch("Test")
    add_beam(sketch, 0, 0, 10, 0)
    add_pinned_support(sketch, 0, 0)
    print(f"  Sketch created with {len(sketch['objects'])} objects")
except Exception as e:
    print(f"  ERROR: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)

print("\nStep 7: Importing SketchScene and loading sketch...")
try:
    from MechanicsSketches.editor import SketchScene
    sketch_scene = SketchScene(None)
    sketch_scene.load_sketch(sketch)
    print(f"  SketchScene loaded with {len(sketch_scene.items())} items")
except Exception as e:
    print(f"  ERROR: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)

print("\nStep 8: Rendering to PDF...")
try:
    from MechanicsSketches.qt_renderer import render_scene
    output_file = "test_diag_output.pdf"
    render_scene(sketch_scene, output_file)
    if os.path.exists(output_file):
        size = os.path.getsize(output_file)
        print(f"  SUCCESS: Created {output_file} ({size} bytes)")
        os.unlink(output_file)  # Clean up
    else:
        print(f"  FAILED: {output_file} was not created")
except Exception as e:
    print(f"  ERROR: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)

print("\n=== All steps completed successfully! ===")
