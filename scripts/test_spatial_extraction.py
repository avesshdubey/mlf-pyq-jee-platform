import fitz

doc = fitz.open(r'Quiz 1- Improvement, Foundation, diploma, Degree\IIT M DIPLOMA AN EXAM QDD2 26 Oct 2025.pdf')
page = doc[78]

elements = []
for b in page.get_text('blocks'):
    elements.append({
        'type': 'text',
        'bbox': b[:4],
        'y0': b[1],
        'y1': b[3],
        'text': b[4]
    })

for img in page.get_image_info(xrefs=True):
    elements.append({
        'type': 'image',
        'bbox': img['bbox'],
        'y0': img['bbox'][1],
        'y1': img['bbox'][3],
        'xref': img['xref'],
        'width': img['width'],
        'height': img['height']
    })

elements.sort(key=lambda e: (e['y0'], e['bbox'][0]))

for el in elements:
    if el['type'] == 'text':
        txt_preview = repr(el['text'].strip()[:60])
        print(f"TEXT  [y: {el['y0']:6.1f} - {el['y1']:6.1f}]: {txt_preview}")
    else:
        print(f"IMAGE [y: {el['y0']:6.1f} - {el['y1']:6.1f}]: xref={el['xref']} ({el['width']}x{el['height']})")

print("\n" + "="*50 + "\nPAGE 80\n" + "="*50)
page2 = doc[79]
elements2 = []
for b in page2.get_text('blocks'):
    elements2.append({'type': 'text', 'bbox': b[:4], 'y0': b[1], 'y1': b[3], 'text': b[4]})
for img in page2.get_image_info(xrefs=True):
    elements2.append({'type': 'image', 'bbox': img['bbox'], 'y0': img['bbox'][1], 'y1': img['bbox'][3], 'xref': img['xref'], 'width': img['width'], 'height': img['height']})
elements2.sort(key=lambda e: (e['y0'], e['bbox'][0]))
for el in elements2:
    if el['type'] == 'text':
        txt_preview = repr(el['text'].strip()[:60])
        print(f"TEXT  [y: {el['y0']:6.1f} - {el['y1']:6.1f}]: {txt_preview}")
    else:
        print(f"IMAGE [y: {el['y0']:6.1f} - {el['y1']:6.1f}]: xref={el['xref']} ({el['width']}x{el['height']})")
