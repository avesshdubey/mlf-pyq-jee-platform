import fitz

doc = fitz.open(r"C:\Users\avesh\Desktop\PYQS\Jan 2024\IIT M DIPLOMA AN2 EXAM QDD2 25 Feb 2024.pdf")
page = doc[127] # Page 128

for img in page.get_images():
    xref = img[0]
    base = doc.extract_image(xref)
    if base['width'] == 16 and base['height'] == 16:
        # Check colors
        pix = fitz.Pixmap(doc, xref)
        # Sample center pixel
        r, g, b = pix.pixel(8, 8)[:3]
        print(f"Icon xref {xref}: width={base['width']}, height={base['height']}, center pixel: R={r}, G={g}, B={b}")
        if g > r and g > 100:
            print("  -> DETERMINED: GREEN CHECKMARK (Correct Answer)")
        elif r > g and r > 100:
            print("  -> DETERMINED: RED CROSS (Incorrect Answer)")
doc.close()
