import fitz
import os
import re
import hashlib
import glob
import asyncio
from PIL import Image

BASE_DIR = r"C:\Users\avesh\Desktop\PYQS"
ASSETS_DIR = os.path.join(BASE_DIR, "assets", "q_images")
os.makedirs(ASSETS_DIR, exist_ok=True)

# WinRT OCR
try:
    import winrt.windows.media.ocr as win_ocr
    import winrt.windows.graphics.imaging as win_imaging
    import winrt.windows.storage as win_storage
    OCR_AVAILABLE = True
except Exception:
    OCR_AVAILABLE = False

async def run_ocr_on_file(image_path):
    if not OCR_AVAILABLE or not os.path.exists(image_path):
        return ""
    try:
        # 2x upscale for small formula/stem images
        im = Image.open(image_path)
        if im.width < 800 or im.height < 100:
            scale = 2
            im_scaled = im.resize((im.width * scale, im.height * scale), Image.Resampling.LANCZOS)
            bg = Image.new('RGB', (im_scaled.width + 40, im_scaled.height + 40), (255, 255, 255))
            if im_scaled.mode == 'RGBA':
                bg.paste(im_scaled, (20, 20), im_scaled)
            else:
                bg.paste(im_scaled, (20, 20))
            temp_path = image_path + ".scaled.png"
            bg.save(temp_path)
            f_obj = await win_storage.StorageFile.get_file_from_path_async(os.path.abspath(temp_path))
        else:
            temp_path = None
            f_obj = await win_storage.StorageFile.get_file_from_path_async(os.path.abspath(image_path))
            
        stream = await f_obj.open_async(win_storage.FileAccessMode.READ)
        decoder = await win_imaging.BitmapDecoder.create_async(stream)
        bitmap = await decoder.get_software_bitmap_async()
        engine = win_ocr.OcrEngine.try_create_from_user_profile_languages()
        res = await engine.recognize_async(bitmap)
        if temp_path and os.path.exists(temp_path):
            try: os.remove(temp_path)
            except: pass
        return res.text.strip()
    except Exception:
        return ""

def save_image_bytes(image_bytes, ext="png"):
    img_hash = hashlib.md5(image_bytes).hexdigest()
    filename = f"qimg_{img_hash[:12]}.{ext}"
    rel_path = f"assets/q_images/{filename}"
    full_path = os.path.join(ASSETS_DIR, filename)
    if not os.path.exists(full_path):
        with open(full_path, "wb") as f:
            f.write(image_bytes)
    return rel_path

def find_mlf_page_range(doc):
    start_pno = None
    end_pno = None
    num_pages = len(doc)
    for pno in range(num_pages):
        text = doc[pno].get_text()
        lines = [l.strip() for l in text.split('\n') if l.strip()]
        for idx, line in enumerate(lines):
            if line == "MLF" or line == "Machine Learning Foundations" or ("MACHINE LEARNING FOUNDATIONS" in line.upper() and ("DIPLOMA LEVEL" in line.upper() or "SECTION" in line.upper() or "SUBJECT" in line.upper())):
                context = " ".join(lines[max(0, idx-3):min(len(lines), idx+10)])
                if "Number of Questions" in context or "Section Id" in context or "Section Marks" in context or "ARE YOU SURE" in context:
                    start_pno = pno
                    break
        if start_pno is not None:
            break
            
    if start_pno is None:
        return None, None
        
    for pno in range(start_pno + 1, num_pages):
        text = doc[pno].get_text()
        lines = [l.strip() for l in text.split('\n') if l.strip()]
        for idx, line in enumerate(lines):
            if re.search(r'(?<!Sub-)Section\s+(Id|Number)\s*:', line):
                sub_context = " ".join(lines[max(0, idx-5):min(len(lines), idx+5)])
                if not re.search(r'\bMLF\b', sub_context) and "MACHINE LEARNING FOUNDATIONS" not in sub_context.upper():
                    end_pno = pno
                    break
            if line in ["DBMS", "PDSA", "MLT", "Java", "AppDev-2", "BDM", "System Commands", "Business Analytics", "MLP", "MAD 1", "MAD 2"]:
                context = " ".join(lines[max(0, idx-2):min(len(lines), idx+5)])
                if "Number of Questions" in context or "Section Marks" in context:
                    end_pno = pno
                    break
        if end_pno is not None:
            break
            
    if end_pno is None:
        end_pno = min(num_pages - 1, start_pno + 20)
        
    return start_pno, end_pno

async def extract_paper(pdf_path):
    rel_path = os.path.relpath(pdf_path, BASE_DIR)
    doc = fitz.open(pdf_path)
    start_pno, end_pno = find_mlf_page_range(doc)
    if start_pno is None:
        doc.close()
        return []
        
    elements = []
    for pno in range(start_pno, end_pno + 1):
        page = doc[pno]
        offset_y = pno * 1000.0
        
        for b in page.get_text('blocks'):
            text = b[4].strip()
            if not text: continue
            elements.append({
                'type': 'text',
                'gy0': offset_y + b[1],
                'gy1': offset_y + b[3],
                'cy': offset_y + (b[1] + b[3]) / 2.0,
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
                'cy': offset_y + (bbox[1] + bbox[3]) / 2.0,
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
    doc.close()
    
    elements.sort(key=lambda e: (e['gy0'], e['x0']))
    
    # Process sequential chunks
    current_comp = None
    i = 0
    paper_questions = []
    
    while i < len(elements):
        el = elements[i]
        
        # Check comprehension block
        if el['type'] == 'text' and ("Question Label : Comprehension" in el['text'] or "Question Type : COMPREHENSION" in el['text']):
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
            
        # Check Question header
        if el['type'] == 'text' and re.search(r'Question Number\s*:\s*\d+', el['text']):
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
            
            # Marks
            marks = 3.0
            for qe in q_elements[:4]:
                if qe['type'] == 'text':
                    m = re.search(r'Correct Marks\s*:\s*([0-9.]+)', qe['text'])
                    if m:
                        marks = float(m.group(1))
                        break
                        
            # Skip 0 marks (attendance check)
            if marks > 0 and "ARE YOU SURE" not in header_text:
                # Find Options : separator
                opts_idx = None
                for idx_e, qe in enumerate(q_elements):
                    if qe['type'] == 'text' and re.match(r'^Options\s*:', qe['text']):
                        opts_idx = idx_e
                        break
                        
                stem_elements = q_elements[1:opts_idx] if opts_idx is not None else q_elements[1:]
                opt_elements = q_elements[opts_idx+1:] if opts_idx is not None else []
                
                # Extract clean stem text and images
                clean_stem_texts = []
                stem_imgs = []
                for se in stem_elements:
                    if se['type'] == 'text':
                        t = se['text']
                        if not re.search(r'^(?:Correct Marks|Question Label|Question Id|Mandatory|Calculator|Response Type|Show Word|Evaluation Required|Answers Type|Text Areas)', t):
                            clean_stem_texts.append(t)
                    elif se['type'] == 'image' and se['image_path']:
                        stem_imgs.append(se['image_path'])
                        
                stem_text = re.sub(r'\s+', ' ', " ".join(clean_stem_texts)).strip()
                
                # If stem text is empty and stem image exists, try OCR on the image
                if (not stem_text or len(stem_text) < 15 or stem_text.startswith("NOTE:")) and stem_imgs:
                    ocr_res = await run_ocr_on_file(os.path.join(BASE_DIR, stem_imgs[-1]))
                    if ocr_res:
                        stem_text = ocr_res if not stem_text else f"{ocr_res} {stem_text}"
                        
                # Add comprehension diagram if applicable
                comp_imgs = []
                if current_comp and current_comp['q_from'] <= q_num <= current_comp['q_to']:
                    comp_imgs = current_comp['images']
                    
                total_stem_imgs = comp_imgs + [img for img in stem_imgs if img not in comp_imgs]
                
                # Options
                options = []
                correct_ans = []
                if q_type in ["MCQ", "MSQ"]:
                    # Option text blocks
                    opt_blocks = []
                    for idx_e, oe in enumerate(opt_elements):
                        if oe['type'] == 'text':
                            m_opt = re.search(r'([0-9]{5,})\.\s*(.*)', oe['text'], re.DOTALL)
                            if m_opt:
                                opt_blocks.append({
                                    'opt_id': m_opt.group(1),
                                    'text': re.sub(r'\s+', ' ', m_opt.group(2)).strip(),
                                    'cy': oe['cy'],
                                    'element_idx': idx_e
                                })
                                
                    # Match images and icons by vertical proximity (within 35 points of option cy)
                    opt_images_on_page = [e for e in opt_elements if e['type'] == 'image' and e['image_path']]
                    opt_icons_on_page = [e for e in opt_elements if e['type'] == 'image' and e['is_icon']]
                    
                    for k, ob in enumerate(opt_blocks):
                        letter = chr(65 + k)
                        
                        # Find closest formula image within 35 points
                        matching_img = None
                        min_d = 999
                        for img in opt_images_on_page:
                            d = abs(img['cy'] - ob['cy'])
                            if d < min_d and d < 35:
                                min_d = d
                                matching_img = img['image_path']
                                
                        # Find closest icon within 35 points
                        is_correct = False
                        min_icon_d = 999
                        for ic in opt_icons_on_page:
                            d = abs(ic['cy'] - ob['cy'])
                            if d < min_icon_d and d < 35:
                                min_icon_d = d
                                if ic['icon_type'] == 'green_check':
                                    is_correct = True
                                    
                        if is_correct:
                            correct_ans.append(letter)
                            
                        # If option has an image and no text, try quick OCR
                        opt_txt = ob['text']
                        if not opt_txt and matching_img:
                            ocr_opt = await run_ocr_on_file(os.path.join(BASE_DIR, matching_img))
                            if ocr_opt:
                                opt_txt = ocr_opt
                                
                        options.append({
                            'id': letter,
                            'option_id': ob['opt_id'],
                            'text': opt_txt,
                            'image': matching_img,
                            'is_correct': is_correct
                        })
                        
                elif q_type == "SA":
                    for qe in q_elements:
                        if qe['type'] == 'text':
                            m_ans = re.search(r'Possible Answers\s*:\s*([^\n]+)', qe['text'])
                            if m_ans:
                                ans_clean = m_ans.group(1).strip()
                                # Clean up answer string e.g. "458" or "10 to 12"
                                ans_clean = re.sub(r'[\r\n]+', ' ', ans_clean).strip()
                                correct_ans.append(ans_clean)
                                
                paper_questions.append({
                    'question_number': q_num,
                    'question_id': q_id,
                    'source_paper': rel_path,
                    'question_type': q_type,
                    'marks': int(marks),
                    'question_text': stem_text,
                    'images': total_stem_imgs,
                    'options': options,
                    'correct_answer': correct_ans
                })
                
            i = j
            continue
            
        i += 1
        
    return paper_questions

async def main():
    papers = [
        r"Quiz 1- Improvement, Foundation, diploma, Degree\IIT M DIPLOMA AN EXAM QDD2 26 Oct 2025.pdf",
        r"2022 term papers\IIT M DIPLOMA QUIZ EXAM QPG1.pdf",
        r"Jan 2023\Quiz 1 Jan23  .pdf"
    ]
    for p in papers:
        full_p = os.path.join(BASE_DIR, p)
        qs = await extract_paper(full_p)
        print(f"\n==================== {p} ====================")
        print(f"Extracted {len(qs)} questions:")
        for q in qs[:4]:
            print(f"  Q#{q['question_number']} ({q['question_type']}, Marks: {q['marks']}, ID: {q['question_id']})")
            print(f"    Stem: {q['question_text'][:80]}")
            print(f"    Stem Images: {q['images']}")
            print(f"    Correct Ans: {q['correct_answer']}")
            for o in q['options']:
                print(f"      ({o['id']}) text='{o['text']}' img={o['image']} corr={o['is_correct']}")

if __name__ == '__main__':
    asyncio.run(main())
