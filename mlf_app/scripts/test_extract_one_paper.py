import fitz
import os
import re
import hashlib
from PIL import Image

BASE_DIR = r"C:\Users\avesh\Desktop\PYQS"
ASSETS_DIR = os.path.join(BASE_DIR, "assets", "q_images")
os.makedirs(ASSETS_DIR, exist_ok=True)

def save_image_bytes(image_bytes, ext="png"):
    img_hash = hashlib.md5(image_bytes).hexdigest()
    filename = f"qimg_{img_hash[:12]}.{ext}"
    rel_path = f"assets/q_images/{filename}"
    full_path = os.path.join(ASSETS_DIR, filename)
    if not os.path.exists(full_path):
        with open(full_path, "wb") as f:
            f.write(image_bytes)
    return rel_path

pdf_path = os.path.join(BASE_DIR, r"Quiz 1- Improvement, Foundation, diploma, Degree\IIT M DIPLOMA AN EXAM QDD2 26 Oct 2025.pdf")
doc = fitz.open(pdf_path)

# Let's inspect page 79 (index 78) and page 80 (index 79)
for pno in [78, 79]:
    page = doc[pno]
    print(f"\n================ PAGE {pno+1} ================")
    
    # Text blocks
    blocks = page.get_text('blocks')
    # Images with bbox
    img_infos = page.get_image_info(xrefs=True)
    
    # Classify images
    images_classified = []
    for info in img_infos:
        xref = info['xref']
        w = info['width']
        h = info['height']
        bbox = info['bbox']
        
        is_icon = False
        icon_type = None
        if w <= 20 and h <= 20:
            try:
                pix = fitz.Pixmap(doc, xref)
                # check center pixel
                if pix.n >= 3:
                    cx, cy = min(pix.width-1, 8), min(pix.height-1, 8)
                    r, g, b = pix.pixel(cx, cy)[:3]
                    if g > r + 20 and g > b + 20:
                        is_icon = True
                        icon_type = "green_check"
                    elif r > g + 20 and r > b + 20:
                        is_icon = True
                        icon_type = "red_cross"
            except Exception:
                pass
                
        img_rel = None
        if not is_icon and w > 20 and h > 15:
            base = doc.extract_image(xref)
            img_rel = save_image_bytes(base['image'], base['ext'])
            
        images_classified.append({
            'xref': xref,
            'bbox': bbox,
            'y0': bbox[1],
            'y1': bbox[3],
            'cy': (bbox[1] + bbox[3]) / 2.0,
            'width': w,
            'height': h,
            'is_icon': is_icon,
            'icon_type': icon_type,
            'image_path': img_rel
        })
        
    for img in images_classified:
        if img['is_icon']:
            print(f"  ICON: {img['icon_type']} at y={img['y0']:.1f}")
        else:
            print(f"  IMAGE: xref={img['xref']} ({img['width']}x{img['height']}) path={img['image_path']} at y={img['y0']:.1f}")
