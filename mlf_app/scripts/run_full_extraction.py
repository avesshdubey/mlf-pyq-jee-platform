import fitz
import os
import glob
import re
import json
import hashlib
import asyncio
from pathlib import Path

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
        f_obj = await win_storage.StorageFile.get_file_from_path_async(os.path.abspath(image_path))
        stream = await f_obj.open_async(win_storage.FileAccessMode.READ)
        decoder = await win_imaging.BitmapDecoder.create_async(stream)
        bitmap = await decoder.get_software_bitmap_async()
        engine = win_ocr.OcrEngine.try_create_from_user_profile_languages()
        res = await engine.recognize_async(bitmap)
        return res.text.strip()
    except Exception:
        return ""

def save_image_bytes(image_bytes, ext="png"):
    img_hash = hashlib.md5(image_bytes).hexdigest()
    filename = f"qimg_{img_hash[:12]}.{ext}"
    rel_path = f"assets/q_images/{filename}"
    full_path = os.path.join(BASE_DIR, "assets", "q_images", filename)
    if not os.path.exists(full_path):
        with open(full_path, "wb") as f:
            f.write(image_bytes)
    return rel_path

# Syllabus hierarchy
CATEGORIES = {
    "Week 1 - ML Foundations": [
        ("ML Concepts", ["machine learning", "hypothesis", "hypothesis space", "overfitting", "underfitting", "generalization", "bias-variance", "inductive bias", "validation", "test set", "training set", "curse of dimensionality", "feature engineering"]),
        ("Types of Learning", ["supervised", "unsupervised", "reinforcement", "semi-supervised", "clustering", "active learning", "learning paradigm", "type of learning"]),
        ("ML Tasks", ["task", "classification", "clustering", "dimensionality reduction", "anomaly detection", "spam", "digit recognition", "object recognition", "ranking", "recommendation"]),
        ("Data & Models", ["feature", "features", "label", "labels", "data-point", "data point", "dataset", "parametric", "non-parametric", "linear model", "model complexity", "sample"]),
        ("Regression Basics", ["regression problem", "simple linear regression", "regression model", "continuous target", "slope", "intercept", "residual", "predicting"])
    ],
    "Week 2 - Mathematical Foundations": [
        ("Sets & Number Systems", ["set", "subset", "union", "intersection", "cartesian product", "complement", "rational", "irrational", "supremum", "infimum", "bounded set", "field"]),
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
        ("Error Calculations", ["error", "mean squared error", "mse", "rmse", "mae", "residual sum of squares", "loss function", "cost function", "error calculation"]),
        ("Regression", ["multiple regression", "linear regression", "feature weights", "best fit", "regression line"]),
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
    if has_kw("mean squared error", combined) or has_kw("mse", combined) or has_kw("residual sum of squares", combined):
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
    if has_kw("regression", combined):
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

def clean_text(text):
    text = re.sub(r'\s+', ' ', text)
    return text.strip()

def extract_from_digital_paper(pdf_path):
    rel_path = os.path.relpath(pdf_path, BASE_DIR)
    doc = fitz.open(pdf_path)
    start_pno, end_pno = find_mlf_page_range(doc)
    
    if start_pno is None:
        doc.close()
        return []
        
    # Extract page text & images
    page_data = []
    for pno in range(start_pno, end_pno + 1):
        page = doc[pno]
        images = []
        for img_info in page.get_images():
            xref = img_info[0]
            base = doc.extract_image(xref)
            w = base['width']
            h = base['height']
            
            is_icon = False
            icon_type = None
            if w == 16 and h == 16:
                try:
                    pix = fitz.Pixmap(doc, xref)
                    r, g, b = pix.pixel(8, 8)[:3]
                    if g > r and g > 100:
                        is_icon = True
                        icon_type = "green_check"
                    elif r > g and r > 100:
                        is_icon = True
                        icon_type = "red_cross"
                except Exception:
                    pass
                    
            img_rel = None
            if not is_icon and w > 20 and h > 15:
                img_rel = save_image_bytes(base['image'], base['ext'])
                
            images.append({
                "xref": xref,
                "width": w,
                "height": h,
                "is_icon": is_icon,
                "icon_type": icon_type,
                "image_path": img_rel
            })
            
        page_data.append({
            "page_num": pno + 1,
            "text": page.get_text(),
            "images": images
        })
    doc.close()
    
    # Process text chunks
    full_text = ""
    for pd in page_data:
        full_text += f"\n<<<PAGE_{pd['page_num']}>>>\n" + pd['text']
        
    raw_chunks = re.split(r'Question Number\s*:\s*', full_text)
    paper_questions = []
    
    current_comprehension = ""
    
    for chunk in raw_chunks[1:]:
        chunk_lines = [l.strip() for l in chunk.split('\n') if l.strip()]
        if not chunk_lines:
            continue
            
        first_line = chunk_lines[0]
        q_num_match = re.match(r'^(\d+)', first_line)
        q_num = q_num_match.group(1) if q_num_match else "0"
        
        q_id_match = re.search(r'Question Id\s*:\s*(\d+)', chunk)
        q_id = q_id_match.group(1) if q_id_match else f"QID-{q_num}"
        
        q_type = "MCQ"
        if "Question Type : MSQ" in chunk or "Multiple Select Question" in chunk:
            q_type = "MSQ"
        elif "Question Type : SA" in chunk or "Short Answer Question" in chunk or "Response Type : Numeric" in chunk:
            q_type = "SA"
            
        marks_match = re.search(r'Correct Marks\s*:\s*([0-9.]+)', chunk)
        marks = float(marks_match.group(1)) if marks_match else 3.0
        
        # Skip attendance/confirmation check
        if marks == 0 or "ARE YOU SURE YOU HAVE TO WRITE EXAM FOR THIS SUBJECT" in chunk:
            continue
            
        if "Comprehension" in chunk and "Sub questions" in chunk:
            comp_match = re.search(r'Question Label : Comprehension\s*(.*?)\s*Sub questions', chunk, re.DOTALL)
            if comp_match:
                current_comprehension = clean_text(comp_match.group(1))
                
        # Question text extraction
        q_text = ""
        label_match = re.search(r'Question Label\s*:\s*[^\n]+\n(.*?)(?=(?:Options\s*:|NOTE\s*:|Response Type\s*:|Sub-Section|$))', chunk, re.DOTALL)
        if label_match:
            raw_qt = label_match.group(1)
            clean_lines = []
            for line in raw_qt.split('\n'):
                line = line.strip()
                if not line or line.startswith("<<<PAGE") or "Mandatory : " in line or "Question Id :" in line or "Calculator : " in line:
                    continue
                clean_lines.append(line)
            q_text = clean_text(" ".join(clean_lines))
            
        # Options extraction
        options = []
        correct_answer = []
        
        if q_type in ["MCQ", "MSQ"]:
            opt_block_match = re.search(r'Options\s*:\s*(.*?)(?=(?:Sub-Section|Question Number|Question Id\s*:|Section Id|Section Number|\n(?:MLF|Java|MLT|DBMS|PDSA|BDM)\s*\n|$))', chunk, re.DOTALL)
            if opt_block_match:
                opt_raw = opt_block_match.group(1)
                opt_items = re.split(r'\n(?=[0-9]{5,}\.|\b[A-E]\.\s+)', "\n" + opt_raw)
                opt_index = 1
                for item in opt_items:
                    item = item.strip()
                    if not item:
                        continue
                    id_match = re.match(r'^([0-9]{5,}|[A-E])\.\s*(.*)', item, re.DOTALL)
                    if id_match:
                        opt_id_str = id_match.group(1)
                        opt_txt = clean_text(re.sub(r'<<<PAGE_\d+>>>', '', id_match.group(2)))
                        opt_label = chr(64 + opt_index) if opt_index <= 5 else str(opt_index)
                        options.append({
                            "id": opt_label,
                            "option_id": opt_id_str,
                            "text": opt_txt
                        })
                        opt_index += 1
                        
        elif q_type == "SA":
            ans_match = re.search(r'Possible Answers\s*:\s*([^\n]+)', chunk)
            if ans_match:
                correct_answer.append(clean_text(ans_match.group(1)))
                
        # Link diagram/matrix images
        stem_images = []
        for pd in page_data:
            for img in pd['images']:
                if img['image_path'] and not img['is_icon']:
                    if img['width'] > 50 and img['height'] > 20:
                        stem_images.append(img['image_path'])
                        
        if current_comprehension and (len(q_text) < 40 or "above data" in q_text or "matrix a" in q_text.lower()):
            q_text = f"[Comprehension Data: {current_comprehension}] {q_text}"
            
        week, subtopic = classify_question(q_text, " ".join(o['text'] for o in options))
        
        paper_questions.append({
            "question_number": q_num,
            "question_id": q_id,
            "source_paper": rel_path,
            "question_type": q_type,
            "marks": int(marks),
            "question_text": q_text,
            "images": list(set(stem_images))[:2],
            "options": options,
            "correct_answer": correct_answer,
            "explanation": "",
            "week": week,
            "subtopic": subtopic
        })
        
    return paper_questions

async def extract_from_scanned_pdf(pdf_path):
    rel_path = os.path.relpath(pdf_path, BASE_DIR)
    doc = fitz.open(pdf_path)
    num_pages = len(doc)
    questions = []
    
    print(f"Running OCR on scanned compilation: {rel_path} ({num_pages} pages)...")
    
    for pno in range(num_pages):
        page = doc[pno]
        pix = page.get_pixmap(dpi=150)
        temp_img = os.path.join(ASSETS_DIR, f"temp_scan_{pno}.png")
        pix.save(temp_img)
        
        ocr_text = await run_ocr_on_file(temp_img)
        
        if os.path.exists(temp_img):
            # Save crop/image as diagram if it has matrices
            img_rel = save_image_bytes(open(temp_img, "rb").read(), "png")
            try:
                os.remove(temp_img)
            except Exception:
                pass
        else:
            img_rel = None
            
        if not ocr_text or len(ocr_text) < 40:
            continue
            
        # Parse fields from OCR text
        q_num_match = re.search(r'Question\s*(\d+)', ocr_text)
        q_num = q_num_match.group(1) if q_num_match else str(pno + 1)
        
        marks_match = re.search(r'\+(\d+)', ocr_text)
        marks = int(marks_match.group(1)) if marks_match else 2
        
        q_type = "MCQ"
        if "Numerical answer" in ocr_text:
            q_type = "SA"
        elif "Multiple correct" in ocr_text or "Select all that apply" in ocr_text:
            q_type = "MSQ"
            
        ans_match = re.search(r'Correct answer:\s*([^\n\r]+)', ocr_text)
        correct_ans = [clean_text(ans_match.group(1))] if ans_match else []
        
        exp_match = re.search(r'(?:EXPLANATION|What the question asks)\s*(.*)', ocr_text, re.DOTALL)
        explanation = clean_text(exp_match.group(1)[:400]) if exp_match else ""
        
        # Isolate question text
        qt_clean = ocr_text
        for header_pat in [r'.*?Instructions', r'.*?answer']:
            qt_clean = re.sub(header_pat, '', qt_clean, count=1, flags=re.DOTALL)
        qt_clean = re.sub(r'Your answer.*', '', qt_clean, flags=re.DOTALL)
        qt_clean = re.sub(r'Correct answer:.*', '', qt_clean, flags=re.DOTALL)
        qt_clean = clean_text(qt_clean)
        
        if len(qt_clean) < 15:
            qt_clean = clean_text(ocr_text[:200])
            
        options = []
        if q_type in ["MCQ", "MSQ"]:
            # Check for multiple lines or choices
            lines = [l.strip() for l in ocr_text.split('\n') if len(l.strip()) > 10 and not l.startswith('Question') and not l.startswith('Correct') and not l.startswith('Your answer')]
            for o_idx, l in enumerate(lines[:4], 1):
                options.append({
                    "id": chr(64 + o_idx),
                    "text": clean_text(l)
                })
                
        week, subtopic = classify_question(qt_clean, " ".join(o['text'] for o in options))
        
        questions.append({
            "question_number": q_num,
            "question_id": f"SCAN-P{pno+1}",
            "source_paper": rel_path,
            "question_type": q_type,
            "marks": marks,
            "question_text": qt_clean,
            "images": [img_rel] if img_rel else [],
            "options": options,
            "correct_answer": correct_ans,
            "explanation": explanation,
            "week": week,
            "subtopic": subtopic
        })
        
    doc.close()
    return questions

async def main():
    print("=== STARTING MLF QUESTION EXTRACTION & DEDUPLICATION PIPELINE ===")
    pdf_files = sorted(glob.glob(os.path.join(BASE_DIR, "**", "*.pdf"), recursive=True))
    print(f"Total PDFs found: {len(pdf_files)}")
    
    all_raw_questions = []
    
    # 1. Process digital PDFs
    for p in pdf_files:
        if "PDF_COM_202611031249451070" in p:
            continue
        try:
            extracted = extract_from_digital_paper(p)
            if extracted:
                print(f"  Extracted {len(extracted)} MLF questions from {os.path.basename(p)}")
                all_raw_questions.extend(extracted)
        except Exception as e:
            print(f"  Error processing {os.path.basename(p)}: {e}")
            
    # 2. Process scanned compilation
    scan_pdf = os.path.join(BASE_DIR, "PDF_COM_202611031249451070.pdf")
    if os.path.exists(scan_pdf):
        try:
            scanned_q = await extract_from_scanned_pdf(scan_pdf)
            print(f"  Extracted {len(scanned_q)} questions from scanned compilation.")
            all_raw_questions.extend(scanned_q)
        except Exception as e:
            print(f"  Error OCR processing scanned compilation: {e}")
            
    print(f"\nTotal raw questions gathered across all sources: {len(all_raw_questions)}")
    
    # 3. Deduplication Engine
    unique_bank = {}
    
    for q in all_raw_questions:
        # Create canonical normalized signature:
        # 1. Normalized stem text (lowercased, alphanumeric and single spaces)
        norm_text = re.sub(r'[^a-z0-9]', '', q['question_text'].lower())
        # 2. Normalized options text
        norm_opts = "".join(re.sub(r'[^a-z0-9]', '', o['text'].lower()) for o in q.get('options', []))
        
        # If question text is empty but has an image
        if len(norm_text) < 10 and q.get('images'):
            sig = f"img_{hashlib.md5(q['images'][0].encode()).hexdigest()}_{norm_opts[:30]}"
        else:
            sig = hashlib.md5((norm_text[:120] + "_" + norm_opts[:80]).encode()).hexdigest()
            
        if sig in unique_bank:
            # Merge source paper info
            existing = unique_bank[sig]
            if q['source_paper'] not in existing['source_papers']:
                existing['source_papers'].append(q['source_paper'])
            # Enrich answers or explanation if missing
            if not existing['correct_answer'] and q['correct_answer']:
                existing['correct_answer'] = q['correct_answer']
            if not existing['explanation'] and q.get('explanation'):
                existing['explanation'] = q['explanation']
            if not existing.get('options') and q.get('options'):
                existing['options'] = q['options']
        else:
            q_copy = dict(q)
            q_copy['source_papers'] = [q['source_paper']]
            del q_copy['source_paper']
            unique_bank[sig] = q_copy
            
    deduped_questions = list(unique_bank.values())
    
    # Assign sequential clean IDs: MLF-001, MLF-002, etc.
    # Group by Week & Subtopic for clean ordering
    week_order = [
        "Week 1 - ML Foundations",
        "Week 2 - Mathematical Foundations",
        "Week 3 - Linear Algebra & Subspaces",
        "Week 4 - Regression & Eigenvalues"
    ]
    
    deduped_questions.sort(key=lambda x: (
        week_order.index(x['week']) if x['week'] in week_order else 99,
        x['subtopic'],
        x['question_type'],
        x['question_text']
    ))
    
    for idx, q in enumerate(deduped_questions, 1):
        q['id'] = f"MLF-Q{idx:03d}"
        
    print(f"Total UNIQUE questions after deduplication: {len(deduped_questions)}")
    
    # Category summary
    summary = {}
    for q in deduped_questions:
        w = q['week']
        st = q['subtopic']
        summary.setdefault(w, {}).setdefault(st, 0)
        summary[w][st] += 1
        
    print("\n=== CATEGORY BREAKDOWN ===")
    for w in week_order:
        print(f"\n{w} (Total: {sum(summary.get(w, {}).values())}):")
        for st, count in sorted(summary.get(w, {}).items()):
            print(f"  - {st}: {count} questions")
            
    # Save output to data/questions.json
    output_path = os.path.join(DATA_DIR, "questions.json")
    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(deduped_questions, f, indent=2, ensure_ascii=False)
        
    print(f"\nSaved structured question bank to: {output_path}")
    
    # Save summary stats
    stats = {
        "total_unique_questions": len(deduped_questions),
        "total_raw_scanned": len(all_raw_questions),
        "breakdown": summary
    }
    with open(os.path.join(DATA_DIR, "stats.json"), "w", encoding="utf-8") as f:
        json.dump(stats, f, indent=2)

if __name__ == "__main__":
    asyncio.run(main())
