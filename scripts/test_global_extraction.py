import fitz
import os
import re
import hashlib
import sys

sys.stdout.reconfigure(encoding='utf-8')

BASE_DIR = r"C:\Users\avesh\Desktop\PYQS"
ASSETS_DIR = os.path.join(BASE_DIR, "assets", "q_images")

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

elements = []
for pno in range(78, 82):
    page = doc[pno]
    offset_y = pno * 1000.0
    
    for b in page.get_text('blocks'):
        text = b[4].strip()
        if not text:
            continue
        elements.append({
            'type': 'text',
            'gy0': offset_y + b[1],
            'gy1': offset_y + b[3],
            'x0': b[0],
            'x1': b[2],
            'text': text,
            'pno': pno
        })
        
    for img_info in page.get_image_info(xrefs=True):
        xref = img_info['xref']
        w = img_info['width']
        h = img_info['height']
        bbox = img_info['bbox']
        
        is_icon = False
        icon_type = None
        if w <= 20 and h <= 20:
            try:
                pix = fitz.Pixmap(doc, xref)
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
            
        elements.append({
            'type': 'image',
            'gy0': offset_y + bbox[1],
            'gy1': offset_y + bbox[3],
            'x0': bbox[0],
            'x1': bbox[2],
            'xref': xref,
            'width': w,
            'height': h,
            'is_icon': is_icon,
            'icon_type': icon_type,
            'image_path': img_rel,
            'pno': pno
        })

elements.sort(key=lambda e: (e['gy0'], e['x0']))

# Track comprehensions and questions
current_comp = None

# A boundary is: Question Number OR Comprehension
# Let's tag elements with comprehension context
i = 0
questions = []

while i < len(elements):
    el = elements[i]
    if el['type'] == 'text' and ("Question Label : Comprehension" in el['text'] or "Question Type : COMPREHENSION" in el['text']):
        # Scan forward for comprehension details
        comp_text = el['text']
        comp_imgs = []
        j = i + 1
        while j < len(elements) and not (elements[j]['type'] == 'text' and re.search(r'Question Number\s*:\s*\d+', elements[j]['text'])):
            if elements[j]['type'] == 'text':
                comp_text += " " + elements[j]['text']
            elif elements[j]['type'] == 'image' and elements[j]['image_path']:
                comp_imgs.append(elements[j]['image_path'])
            j += 1
            
        m_range = re.search(r'Question Numbers\s*:\s*\((?:(\d+)\s*to\s*(\d+)|\d+)\)', comp_text)
        if m_range and m_range.group(1):
            q_from = int(m_range.group(1))
            q_to = int(m_range.group(2))
        else:
            q_from, q_to = 0, 9999
            
        current_comp = {
            'text': comp_text,
            'images': comp_imgs,
            'q_from': q_from,
            'q_to': q_to
        }
        i = j
        continue
        
    if el['type'] == 'text' and re.search(r'Question Number\s*:\s*\d+', el['text']):
        # Found a question!
        start_idx = i
        j = i + 1
        while j < len(elements):
            next_el = elements[j]
            if next_el['type'] == 'text':
                if re.search(r'Question Number\s*:\s*\d+', next_el['text']):
                    break
                if "Question Label : Comprehension" in next_el['text'] or "Question Type : COMPREHENSION" in next_el['text']:
                    break
                if re.search(r'(?<!Sub-)Section\s+(?:Id|Number)\s*:', next_el['text']):
                    break
            j += 1
            
        q_elements = elements[start_idx:j]
        header_text = el['text']
        m_num = re.search(r'Question Number\s*:\s*(\d+)', header_text)
        m_id = re.search(r'Question Id\s*:\s*(\d+)', header_text)
        m_type = re.search(r'Question Type\s*:\s*(\w+)', header_text)
        q_num = int(m_num.group(1)) if m_num else 0
        q_id = m_id.group(1) if m_id else "?"
        q_type = m_type.group(1) if m_type else "MCQ"
        
        # Check marks
        marks_match = None
        for qe in q_elements[:4]:
            if qe['type'] == 'text':
                m = re.search(r'Correct Marks\s*:\s*([0-9.]+)', qe['text'])
                if m:
                    marks_match = m
                    break
        marks = float(marks_match.group(1)) if marks_match else 3.0
        
        # Skip if 0 marks (attendance/check)
        if marks > 0:
            opts_idx = None
            for idx_e, qe in enumerate(q_elements):
                if qe['type'] == 'text' and re.match(r'^Options\s*:', qe['text']):
                    opts_idx = idx_e
                    break
                    
            stem_elements = q_elements[1:opts_idx] if opts_idx is not None else q_elements[1:]
            opt_elements = q_elements[opts_idx+1:] if opts_idx is not None else []
            
            clean_stem_texts = []
            stem_imgs = []
            for se in stem_elements:
                if se['type'] == 'text':
                    t = se['text']
                    if not re.search(r'^(?:Correct Marks|Question Label|Question Id|Mandatory|Calculator|Response Type|Show Word|Evaluation Required|Answers Type|Text Areas)', t):
                        clean_stem_texts.append(t)
                elif se['type'] == 'image' and se['image_path']:
                    stem_imgs.append(se['image_path'])
                    
            # Check comprehension context
            comp_imgs_to_add = []
            if current_comp and current_comp['q_from'] <= q_num <= current_comp['q_to']:
                comp_imgs_to_add = current_comp['images']
                
            # Options
            options = []
            correct_ans = []
            if q_type in ["MCQ", "MSQ"]:
                opt_starts = []
                for idx_e, oe in enumerate(opt_elements):
                    if oe['type'] == 'text' and re.search(r'^[0-9]{5,}\.', oe['text']):
                        opt_starts.append(idx_e)
                        
                for k, o_idx in enumerate(opt_starts):
                    o_next = opt_starts[k+1] if k+1 < len(opt_starts) else len(opt_elements)
                    sub_chunk = opt_elements[o_idx:o_next]
                    
                    o_raw = " ".join(e['text'] for e in sub_chunk if e['type'] == 'text')
                    o_match = re.search(r'([0-9]{5,})\.\s*(.*)', o_raw, re.DOTALL)
                    opt_id_str = o_match.group(1) if o_match else "?"
                    opt_text = o_match.group(2).strip() if o_match else o_raw
                    opt_text = re.sub(r'\s+', ' ', opt_text).strip()
                    
                    opt_imgs = [e['image_path'] for e in sub_chunk if e['type'] == 'image' and e['image_path']]
                    is_correct = any(e['type'] == 'image' and e['icon_type'] == 'green_check' for e in sub_chunk)
                    
                    letter = chr(65 + k)
                    if is_correct:
                        correct_ans.append(letter)
                        
                    options.append({
                        'id': letter,
                        'option_id': opt_id_str,
                        'text': opt_text,
                        'images': opt_imgs,
                        'image': opt_imgs[0] if opt_imgs else None,
                        'is_correct': is_correct
                    })
            elif q_type == "SA":
                for qe in q_elements:
                    if qe['type'] == 'text':
                        m_ans = re.search(r'Possible Answers\s*:\s*([^\n]+)', qe['text'])
                        if m_ans:
                            correct_ans.append(m_ans.group(1).strip())
                            
            questions.append({
                'num': q_num,
                'id': q_id,
                'type': q_type,
                'marks': marks,
                'stem_text': " ".join(clean_stem_texts),
                'stem_images': comp_imgs_to_add + stem_imgs,
                'options': options,
                'correct_ans': correct_ans
            })
            
        i = j
        continue
        
    i += 1

print(f"\nExtracted {len(questions)} questions:")
for q in questions:
    print(f"\nQ#{q['num']} ({q['type']}, Marks: {q['marks']}, ID: {q['id']})")
    print(f"  Stem: {q['stem_text'][:120]}")
    print(f"  Stem Images: {q['stem_images']}")
    print(f"  Correct Answer: {q['correct_ans']}")
    for o in q['options']:
        print(f"    ({o['id']}) text='{o['text']}' image={o['image']} is_correct={o['is_correct']}")
