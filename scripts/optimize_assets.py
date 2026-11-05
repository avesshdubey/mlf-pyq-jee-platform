import os
import glob
from PIL import Image

ASSETS_DIR = r"C:\Users\avesh\Desktop\PYQS\assets\q_images"

files = glob.glob(os.path.join(ASSETS_DIR, "*.*"))
print(f"Optimizing {len(files)} images in {ASSETS_DIR}...")

saved_bytes = 0

for f in files:
    size = os.path.getsize(f)
    if size > 100 * 1024: # Greater than 100 KB
        try:
            with Image.open(f) as img:
                # Convert RGBA to RGB if saving as JPEG
                if img.mode in ("RGBA", "P"):
                    img = img.convert("RGB")
                    
                w, h = img.size
                if w > 800 or h > 600:
                    img.thumbnail((800, 600), Image.Resampling.LANCZOS)
                    
                img.save(f, format="JPEG", quality=80, optimize=True)
                new_size = os.path.getsize(f)
                saved_bytes += (size - new_size)
        except Exception as e:
            pass

new_total = sum(os.path.getsize(f) for f in glob.glob(os.path.join(ASSETS_DIR, "*.*"))) / 1024 / 1024
print(f"Optimization complete! Saved {saved_bytes / 1024 / 1024:.1f} MB.")
print(f"New total size of assets/q_images: {new_total:.1f} MB.")
