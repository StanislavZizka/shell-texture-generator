"""
Test script for Biological Heatmap functionality
"""
import sys
import os

# Fix Windows console encoding
if sys.platform == 'win32':
    import io
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8', errors='replace')

# Add parent directory to path
sys.path.insert(0, os.path.dirname(__file__))

from services.texture_generator import TextureGeneratorService

def test_heatmap_generation():
    """Test if heatmap generation works"""
    print("=" * 60)
    print("TESTING BIOLOGICAL HEATMAP GENERATION")
    print("=" * 60)

    service = TextureGeneratorService()

    print("\n[TEST 1] Generating texture WITHOUT heatmap...")
    image_path1, heatmap_path1 = service.generate_activator_inhibitor(
        K=1.0,
        t_max=50.0,
        delta_t=0.1,
        color1="#0000ff",
        color2="#ff0000",
        size=256,
        show_biological_heatmap=False
    )
    print(f"✓ Image path: {image_path1}")
    print(f"✓ Heatmap path: {heatmap_path1}")
    print(f"✓ Expected: heatmap_path should be None")
    assert heatmap_path1 is None, "Heatmap should be None when show_biological_heatmap=False"
    print("✓ TEST 1 PASSED\n")

    print("[TEST 2] Generating texture WITH heatmap...")
    image_path2, heatmap_path2 = service.generate_activator_inhibitor(
        K=1.0,
        t_max=50.0,
        delta_t=0.1,
        color1="#0000ff",
        color2="#ff0000",
        size=256,
        show_biological_heatmap=True
    )
    print(f"✓ Image path: {image_path2}")
    print(f"✓ Heatmap path: {heatmap_path2}")
    print(f"✓ Expected: heatmap_path should NOT be None")
    assert heatmap_path2 is not None, "Heatmap should be generated when show_biological_heatmap=True"

    # Check if file exists
    if os.path.exists(heatmap_path2):
        print(f"✓ Heatmap file exists: {heatmap_path2}")
        print(f"✓ File size: {os.path.getsize(heatmap_path2)} bytes")
    else:
        print(f"✗ ERROR: Heatmap file does NOT exist at {heatmap_path2}")
        return False

    print("✓ TEST 2 PASSED\n")

    print("=" * 60)
    print("ALL TESTS PASSED! ✓")
    print("=" * 60)
    return True

if __name__ == "__main__":
    try:
        success = test_heatmap_generation()
        sys.exit(0 if success else 1)
    except Exception as e:
        print(f"\n✗ TEST FAILED WITH ERROR:")
        print(f"  {type(e).__name__}: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
