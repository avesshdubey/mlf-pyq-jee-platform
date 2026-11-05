import fitz
import os
import re
import json
import glob
import hashlib
import asyncio
from PIL import Image

BASE_DIR = r"C:\Users\avesh\Desktop\PYQS"
DATA_DIR = os.path.join(BASE_DIR, "data")
ASSETS_DIR = os.path.join(BASE_DIR, "assets", "q_images")
os.makedirs(DATA_DIR, exist_ok=True)
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
        im = Image.open(image_path)
        # upscale small formula images for OCR accuracy
        if im.width < 700 or im.height < 100:
            scale = 2
            im_scaled = im.resize((im.width * scale, im.height * scale), Image.Resampling.LANCZOS)
            bg = Image.new('RGB', (im_scaled.width + 40, im_scaled.height + 40), (255, 255, 255))
            if im_scaled.mode == 'RGBA':
                bg.paste(im_scaled, (20, 20), im_scaled)
            else:
                bg.paste(im_scaled, (20, 20))
            temp_path = image_path + ".scaled.png"
            bg.save(temp_path)
            target = temp_path
        else:
            temp_path = None
            target = image_path
            
        f_obj = await win_storage.StorageFile.get_file_from_path_async(os.path.abspath(target))
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

# Syllabus hierarchy & classifier
CATEGORIES = {
    "Week 1 - ML Foundations": [
        ("ML Concepts", ["machine learning", "hypothesis", "hypothesis space", "overfitting", "underfitting", "generalization", "bias-variance", "inductive bias", "validation", "test set", "training set", "curse of dimensionality", "feature engineering"]),
        ("Types of Learning", ["supervised", "unsupervised", "reinforcement", "semi-supervised", "clustering", "active learning", "learning paradigm", "type of learning"]),
        ("ML Tasks", ["task", "classification", "clustering", "dimensionality reduction", "anomaly detection", "spam", "digit recognition", "object recognition", "ranking", "recommendation"]),
        ("Data & Models", ["feature", "features", "label", "labels", "data-point", "data point", "dataset", "parametric", "non-parametric", "linear model", "model complexity", "sample"]),
        ("Regression Basics", ["regression problem", "simple linear regression", "regression model", "continuous target", "slope", "intercept", "residual", "predicting"])
    ],
    "Week 2 - Mathematical Foundations": [
        ("Sets & Number Systems", ["set", "subset", "union", "intersection", "cartesian product", "complement", "rational", "irrational", "supremum", "infimum", "bounded set", "field", "octal", "decimal representation"]),
        ("Metric Spaces", ["metric space", "metric", "distance function", "triangle inequality", "open ball", "closed ball", "open set", "closed set", "neighborhood", "euclidean metric", "manhattan"]),
        ("Sequences & Limits", ["sequence", "limit of sequence", "convergence", "convergent", "divergent", "cauchy", "subsequence", "bolzano", "limit superior", "limit inferior", "epsilon"]),
        ("Functions", ["function", "functions", "domain", "codomain", "range", "injective", "surjective", "bijective", "one-to-one", "onto", "composite", "inverse function"]),
        ("Continuity", ["continuous", "continuity", "discontinuous", "discontinuity", "intermediate value", "uniform continuity", "limit of f(x)"]),
        ("Derivatives", ["derivative", "derivatives", "differentiable", "differentiability", "directional derivative", "partial derivative", "gradient", "chain rule", "mean value", "taylor", "stationary point", "hessian", "critical point"])
    ],
    "Week 3 - Linear Algebra & Subspaces": [
        ("Vectors", ["vector", "vectors", "vector space", "scalar multiplication", "coordinates", "standard basis"]),
        ("Matrices", ["matrix", "matrices", "transpose", "inverse of", "invertible", "symmetric matrix", "skew-symmetric", "rank", "determinant", "orthogonal matrix", "matrix multiplication"]),
        ("Dot Product & Norms", ["dot product", "inner product", "norm", "norms", "l1 norm", "l2 norm", "orthogonal", "orthonormal", "cauchy-schwarz", "angle between"]),
        ("Linear Independence", ["linearly independent", "linear independence", "linearly dependent", "linear combination", "linear dependence"]),
        ("Span & Basis", ["span", "spanning", "basis", "dimension", "coordinates with respect to basis", "minimal spanning"]),
        ("Subspaces", ["subspace", "subspaces", "null space", "column space", "row space", "nullity", "kernel", "image", "orthogonal complement", "rank-nullity"])
    ],
    "Week 4 - Regression & Eigenvalues": [
        ("Least Squares", ["least squares", "least square", "best fit line", "normal equation", "normal equations", "x^t x", "rss", "projection"]),
        ("Error Calculations", ["error", "mean squared error", "mse", "rmse", "mae", "residual sum of squares", "loss function", "cost function", "error calculation", "squared loss"]),
        ("Regression", ["multiple regression", "linear regression", "feature weights", "best fit", "regression line", "polynomial regression"]),
        ("Eigenvalues", ["eigenvalue", "eigenvalues", "characteristic equation", "characteristic polynomial", "diagonalizable", "diagonalization", "trace", "multiplicity"]),
        ("Eigenvectors", ["eigenvector", "eigenvectors", "eigenspace", "orthogonal diagonalization", "p^-1 a p", "eigenbasis"])
    ]
}

def has_kw(kw, text):
    return bool(re.search(r'\b' + re.escape(kw) + r'\b', text))

def classify_question(text, options_text=""):
    combined = (text + " " + options_text).lower()
    
    if has_kw("eigenvalue", combined) or has_kw("eigenvalues", combined):
        return "Week 4 - Regression & Eigenvalues", "Eigenvalues"
    if has_kw("eigenvector", combined) or has_kw("eigenvectors", combined):
        return "Week 4 - Regression & Eigenvalues", "Eigenvectors"
    if has_kw("least squares", combined) or has_kw("least square", combined) or has_kw("best fit line", combined):
        return "Week 4 - Regression & Eigenvalues", "Least Squares"
    if has_kw("squared loss", combined) or has_kw("mean squared error", combined) or has_kw("mse", combined) or has_kw("loss function", combined):
        return "Week 4 - Regression & Eigenvalues", "Error Calculations"
        
    if has_kw("directional derivative", combined) or has_kw("differentiable", combined) or has_kw("derivative", combined) or has_kw("gradient", combined):
        return "Week 2 - Mathematical Foundations", "Derivatives"
    if has_kw("continuous", combined) or has_kw("continuity", combined):
        return "Week 2 - Mathematical Foundations", "Continuity"
    if has_kw("metric space", combined) or has_kw("metric", combined) or has_kw("distance function", combined):
        return "Week 2 - Mathematical Foundations", "Metric Spaces"
    if has_kw("sequence", combined) or has_kw("converges", combined) or has_kw("diverges", combined):
        return "Week 2 - Mathematical Foundations", "Sequences & Limits"
    if has_kw("injective", combined) or has_kw("surjective", combined) or has_kw("bijective", combined) or (has_kw("domain", combined) and has_kw("codomain", combined)):
        return "Week 2 - Mathematical Foundations", "Functions"
    if has_kw("octal", combined) or has_kw("decimal representation", combined) or has_kw("subset", combined):
        return "Week 2 - Mathematical Foundations", "Sets & Number Systems"
        
    if has_kw("column space", combined) or has_kw("row space", combined) or has_kw("null space", combined) or has_kw("subspace", combined):
        return "Week 3 - Linear Algebra & Subspaces", "Subspaces"
    if has_kw("linearly independent", combined) or has_kw("linearly dependent", combined):
        return "Week 3 - Linear Algebra & Subspaces", "Linear Independence"
    if has_kw("span", combined) or has_kw("basis", combined):
        return "Week 3 - Linear Algebra & Subspaces", "Span & Basis"
    if has_kw("dot product", combined) or has_kw("norm", combined) or has_kw("orthogonal", combined):
        return "Week 3 - Linear Algebra & Subspaces", "Dot Product & Norms"
    if has_kw("matrix", combined) or has_kw("matrices", combined) or has_kw("transpose", combined) or has_kw("determinant", combined):
        return "Week 3 - Linear Algebra & Subspaces", "Matrices"
        
    if has_kw("supervised", combined) or has_kw("unsupervised", combined) or has_kw("reinforcement", combined):
        return "Week 1 - ML Foundations", "Types of Learning"
    if has_kw("task", combined) or has_kw("classification", combined) or has_kw("clustering", combined) or has_kw("dimensionality reduction", combined):
        return "Week 1 - ML Foundations", "ML Tasks"
    if has_kw("hypothesis", combined) or has_kw("overfitting", combined) or has_kw("generalization", combined) or has_kw("inductive bias", combined):
        return "Week 1 - ML Foundations", "ML Concepts"
    if has_kw("polynomial regression", combined) or has_kw("linear regression", combined) or has_kw("regression", combined):
        return "Week 1 - ML Foundations", "Regression Basics"
        
    best_score = 0
    best_week = "Week 1 - ML Foundations"
    best_subtopic = "ML Concepts"
    
    for week, subtopics in CATEGORIES.items():
        for subtopic, keywords in subtopics:
            score = 0
            for kw in keywords:
                if has_kw(kw, combined):
                    score += len(kw)
            if score > best_score:
                best_score = score
                best_week = week
                best_subtopic = subtopic
                
    return best_week, best_subtopic

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

async def extract_digital_paper(pdf_path):
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
            q_id = m_id.group(1) if m_id else f"QID-{q_num}"
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
                possible_ans_str = None
                
                for se in stem_elements:
                    if se['type'] == 'text':
                        t = se['text']
                        m_pa = re.search(r'Possible Answers\s*:\s*([^\n\r]+)', t)
                        if m_pa:
                            possible_ans_str = m_pa.group(1).strip()
                            continue
                        if not re.search(r'^(?:Correct Marks|Question Label|Question Id|Mandatory|Calculator|Response Type|Show Word|Evaluation Required|Answers Type|Text Areas|Sub-Section)', t):
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
                    if possible_ans_str:
                        clean_pa = re.sub(r'[\r\n]+', ' ', possible_ans_str).strip()
                        correct_ans.append(clean_pa)
                    else:
                        for qe in q_elements:
                            if qe['type'] == 'text':
                                m_ans = re.search(r'Possible Answers\s*:\s*([^\n]+)', qe['text'])
                                if m_ans:
                                    ans_clean = re.sub(r'[\r\n]+', ' ', m_ans.group(1).strip()).strip()
                                    correct_ans.append(ans_clean)
                                    break
                                    
                paper_questions.append({
                    'question_number': str(q_num),
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

async def extract_scanned_pdf(pdf_path):
    rel_path = os.path.relpath(pdf_path, BASE_DIR)
    doc = fitz.open(pdf_path)
    num_pages = len(doc)
    questions = []
    
    print(f"Extracting scanned compilation: {rel_path} ({num_pages} pages)...")
    
    for pno in range(num_pages):
        page = doc[pno]
        pix = page.get_pixmap(dpi=150)
        temp_img = os.path.join(ASSETS_DIR, f"temp_scan_{pno}.png")
        pix.save(temp_img)
        
        ocr_text = await run_ocr_on_file(temp_img)
        
        img_rel = None
        if os.path.exists(temp_img):
            img_rel = save_image_bytes(open(temp_img, "rb").read(), "png")
            try: os.remove(temp_img)
            except: pass
            
        m_qnum = re.search(r'Question\s*(\d+)', ocr_text)
        q_num = m_qnum.group(1) if m_qnum else str(pno + 1)
        
        q_type = "MCQ"
        if "Multiple correct" in ocr_text or "Select all that apply" in ocr_text:
            q_type = "MSQ"
        elif "Numerical answer" in ocr_text or "Enter a number" in ocr_text:
            q_type = "SA"
            
        # Correct answer
        correct_answer = []
        m_corr = re.search(r'Correct answer:\s*([^\n\r]+)', ocr_text)
        if m_corr:
            ans_str = m_corr.group(1).strip()
            ans_str = re.sub(r'[\(\+\-].*$', '', ans_str).strip()
            correct_answer.append(ans_str)
            
        # Explanation
        explanation = ""
        m_exp = re.search(r'EXPLANATION\s*(.*)', ocr_text, re.DOTALL)
        if m_exp:
            explanation = m_exp.group(1).strip()
            explanation = re.sub(r'\s+', ' ', explanation)
            
        # Stem
        stem_text = ""
        m_stem = re.search(r'(?:Consider|Let|Which|If|Find|A\s+|What|Given)(.*?)(?=(?:Your answer|Enter a number|Correct answer|Options|EXPLANATION|\(a\)|\(b\)|Select all))', ocr_text, re.DOTALL)
        if m_stem:
            stem_text = m_stem.group(0).strip()
            stem_text = re.sub(r'\s+', ' ', stem_text)
        else:
            stem_text = f"IITM Portal Examination Question {q_num} (See visual problem statement in attached scan)"
            
        week, subtopic = classify_question(stem_text, "")
        
        questions.append({
            'question_number': q_num,
            'question_id': f"SCAN-P{pno+1}",
            'source_paper': rel_path,
            'question_type': q_type,
            'marks': 2,
            'question_text': stem_text,
            'images': [img_rel] if img_rel else [],
            'options': [],
            'correct_answer': correct_answer,
            'explanation': explanation,
            'week': week,
            'subtopic': subtopic
        })
        
    doc.close()
    return questions

def generate_question_signature(q):
    norm_stem = re.sub(r'[^a-z0-9]', '', q['question_text'].lower())
    
    # If stem has distinct text (>25 chars), use stem + first option text
    if len(norm_stem) >= 25:
        first_opt_text = ""
        if q['options']:
            first_opt_text = re.sub(r'[^a-z0-9]', '', q['options'][0].get('text', '').lower())[:30]
        return f"STEM:{norm_stem[:100]}|OPT:{first_opt_text}"
        
    # If stem has images, use image hash
    if q['images']:
        img_name = os.path.basename(q['images'][0])
        return f"IMG:{img_name}|STEM:{norm_stem}"
        
    return f"FALLBACK:{q['question_id']}"

async def run_full_pipeline():
    print("Scanning all PDF files in workspace...")
    all_files = sorted(glob.glob(os.path.join(BASE_DIR, "**", "*.pdf"), recursive=True))
    
    raw_questions = []
    processed_count = 0
    
    for f in all_files:
        rel = os.path.relpath(f, BASE_DIR)
        if "PDF_COM" in f:
            continue
        try:
            doc = fitz.open(f)
            t = doc[0].get_text() if len(doc) > 0 else ""
            has_mlf = False
            for pno in range(min(len(doc), 150)):
                if "MLF" in doc[pno].get_text() or "Machine Learning Foundations" in doc[pno].get_text():
                    has_mlf = True
                    break
            doc.close()
            
            if has_mlf:
                print(f"Extracting: {rel}...")
                qs = await extract_digital_paper(f)
                if qs:
                    raw_questions.extend(qs)
                    processed_count += 1
        except Exception as e:
            print(f"Error extracting {rel}: {e}")
            
    print(f"\nExtracted {len(raw_questions)} raw question instances across {processed_count} digital papers.")
    
    # Add scanned compilation
    scan_pdf = os.path.join(BASE_DIR, "PDF_COM_202611031249451070.pdf")
    if os.path.exists(scan_pdf):
        scan_qs = await extract_scanned_pdf(scan_pdf)
        print(f"Extracted {len(scan_qs)} questions from scanned compilation.")
    else:
        scan_qs = []
        
    # Deduplicate and Merge
    print("\nDeduplicating and cross-merging question banks...")
    unique_map = {}
    
    for q in raw_questions:
        sig = generate_question_signature(q)
        if sig not in unique_map:
            unique_map[sig] = {
                'question_number': q['question_number'],
                'question_id': q['question_id'],
                'question_type': q['question_type'],
                'marks': q['marks'],
                'question_text': q['question_text'],
                'images': list(q['images']),
                'options': [dict(o) for o in q['options']],
                'correct_answer': list(q['correct_answer']),
                'explanation': '',
                'source_papers': [q['source_paper']]
            }
        else:
            merged = unique_map[sig]
            if q['source_paper'] not in merged['source_papers']:
                merged['source_papers'].append(q['source_paper'])
                
            # Merge longer/cleaner stem text
            if len(q['question_text']) > len(merged['question_text']):
                merged['question_text'] = q['question_text']
                
            # Merge images
            for img in q['images']:
                if img not in merged['images']:
                    merged['images'].append(img)
                    
            # Merge correct answers if available
            if not merged['correct_answer'] and q['correct_answer']:
                merged['correct_answer'] = list(q['correct_answer'])
            elif q['correct_answer']:
                for ca in q['correct_answer']:
                    if ca not in merged['correct_answer']:
                        merged['correct_answer'].append(ca)
                        
            # Merge options (preserve images and text)
            if not merged['options'] and q['options']:
                merged['options'] = [dict(o) for o in q['options']]
            elif merged['options'] and q['options']:
                for i_o, opt in enumerate(q['options']):
                    if i_o < len(merged['options']):
                        m_opt = merged['options'][i_o]
                        if not m_opt.get('text') and opt.get('text'):
                            m_opt['text'] = opt['text']
                        if not m_opt.get('image') and opt.get('image'):
                            m_opt['image'] = opt['image']
                        if not m_opt.get('is_correct') and opt.get('is_correct'):
                            m_opt['is_correct'] = True
                            
    # Now merge scanned compilation questions
    for sq in scan_qs:
        sig = generate_question_signature(sq)
        matched = False
        for k, v in unique_map.items():
            # Check text similarity
            if sq['question_text'] and len(sq['question_text']) > 30:
                norm_sq = re.sub(r'[^a-z0-9]', '', sq['question_text'].lower())[:60]
                norm_v = re.sub(r'[^a-z0-9]', '', v['question_text'].lower())[:60]
                if norm_sq in norm_v or norm_v in norm_sq:
                    if sq['explanation'] and not v['explanation']:
                        v['explanation'] = sq['explanation']
                    if sq['correct_answer'] and not v['correct_answer']:
                        v['correct_answer'] = sq['correct_answer']
                    matched = True
                    break
        if not matched:
            unique_map[f"SCAN:{sq['question_id']}"] = sq
            
    # Classify all unique questions into 4-week hierarchy
    final_questions = []
    idx = 1
    
    for sig, q in unique_map.items():
        opts_text = " ".join(o.get('text', '') for o in q.get('options', []))
        week, subtopic = classify_question(q['question_text'], opts_text)
        
        # Ensure clean options schema
        clean_opts = []
        for o in q.get('options', []):
            clean_opts.append({
                'id': o['id'],
                'option_id': o.get('option_id', ''),
                'text': o.get('text', ''),
                'image': o.get('image', None)
            })
            
        final_questions.append({
            'id': f"MLF-Q{idx:03d}",
            'question_number': str(q['question_number']),
            'question_id': str(q['question_id']),
            'question_type': q['question_type'],
            'marks': q['marks'],
            'question_text': q['question_text'],
            'images': q['images'],
            'options': clean_opts,
            'correct_answer': sorted(list(set(q['correct_answer']))),
            'explanation': q.get('explanation', ''),
            'week': week,
            'subtopic': subtopic,
            'source_papers': q.get('source_papers', [])
        })
        idx += 1
        
    print(f"\nFinal Deduplicated Question Bank: {len(final_questions)} unique questions.")
    
    # Save to data/questions.json
    json_path = os.path.join(DATA_DIR, "questions.json")
    with open(json_path, "w", encoding="utf-8") as f:
        json.dump(final_questions, f, ensure_ascii=False, indent=2)
    print(f"Saved to {json_path}")
    
    # Save to data/questions_data.js (Zero-CORS bundle)
    js_path = os.path.join(DATA_DIR, "questions_data.js")
    with open(js_path, "w", encoding="utf-8") as f:
        f.write("window.MLF_QUESTIONS = " + json.dumps(final_questions, ensure_ascii=False, indent=2) + ";\n")
    print(f"Saved to {js_path}")
    
    # Audit summary
    opts_with_imgs = sum(1 for q in final_questions for o in q['options'] if o.get('image'))
    opts_with_txt = sum(1 for q in final_questions for o in q['options'] if o.get('text'))
    stem_with_imgs = sum(1 for q in final_questions if q.get('images'))
    with_corr = sum(1 for q in final_questions if q.get('correct_answer'))
    
    print(f"\nAudit Summary:")
    print(f"  Total Questions: {len(final_questions)}")
    print(f"  Questions with Stem Images/Diagrams: {stem_with_imgs}")
    print(f"  Options with Images: {opts_with_imgs}")
    print(f"  Options with Text: {opts_with_txt}")
    print(f"  Questions with Verified Correct Answers: {with_corr} / {len(final_questions)}")

if __name__ == '__main__':
    asyncio.run(run_full_pipeline())
