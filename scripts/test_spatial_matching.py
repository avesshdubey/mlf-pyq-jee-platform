import fitz
import os
import re

doc = fitz.open(r"C:\Users\avesh\Desktop\PYQS\Quiz 1- Improvement, Foundation, diploma, Degree\IIT M DIPLOMA AN EXAM QDD2 26 Oct 2025.pdf")
page = doc[78] # page 79

# Find Option text blocks
blocks = page.get_text("blocks")
option_blocks = []
for b in blocks:
    txt = b[4].strip()
    match = re.match(r'^([0-9]{5,})\.', txt)
    if match:
        option_blocks.append((b[1], b[3], match.group(1), txt))

print("Option blocks on page 79:")
for ob in option_blocks:
    print(f"  y: {ob[0]:.1f} to {ob[1]:.1f} | ID: {ob[2]}")

# Find images
images = []
for img in page.get_images():
    xref = img[0]
    base = doc.extract_image(xref)
    rects = page.get_image_rects(xref)
    if rects:
        r = rects[0]
        w, h = base['width'], base['height']
        is_green = False
        if w == 16 and h == 16:
            pix = fitz.Pixmap(doc, xref)
            r_val, g_val, b_val = pix.pixel(8, 8)[:3]
            if g_val > r_val and g_val > 100:
                is_green = True
        images.append((r.y0, r.y1, xref, w, h, is_green))

print("\nImages on page 79:")
for im in sorted(images, key=lambda x: x[0]):
    print(f"  y: {im[0]:.1f} to {im[1]:.1f} | xref {im[2]} ({im[3]}x{im[4]}) | Green check: {im[5]}")

doc.close()
