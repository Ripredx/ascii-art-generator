import sys
from PIL import Image

print("Testing image loading...")

try:
    img = Image.open("test_image.png")
    print(f"SUCCESS: Image loaded, size: {img.size}")
except Exception as e:
    print(f"ERROR: {e}")
    import traceback
    traceback.print_exc()

input("Press Enter to exit...")
