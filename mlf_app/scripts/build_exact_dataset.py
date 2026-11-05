import fitz
import os
import re
import json
import glob
import hashlib
from PIL import Image

APP_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
BASE_DIR = os.path.dirname(APP_DIR)
DATA_DIR = os.path.join(APP_DIR, "data")
ASSETS_DIR = os.path.join(APP_DIR, "assets", "q_images")
CARDS_DIR = os.path.join(APP_DIR, "assets", "q_cards")
os.makedirs(DATA_DIR, exist_ok=True)
os.makedirs(ASSETS_DIR, exist_ok=True)
os.makedirs(CARDS_DIR, exist_ok=True)

# 4-Week Taxonomy Mapping
CATEGORIES = {
    "Week 1 - ML Foundations": [
        ("ML Concepts", ["machine learning", "hypothesis", "hypothesis space", "overfitting", "underfitting", "generalization", "bias-variance", "inductive bias", "validation", "test set", "training set", "curse of dimensionality", "feature engineering"]),
        ("Types of Learning", ["supervised", "unsupervised", "reinforcement", "semi-supervised", "clustering", "active learning", "learning paradigm", "type of learning"]),
        ("ML Tasks", ["task", "classification", "clustering", "dimensionality reduction", "anomaly detection", "spam", "digit recognition", "object recognition", "ranking", "recommendation"]),
        ("Data & Models", ["feature", "features", "label", "labels", "data-point", "data point", "dataset", "parametric", "non-parametric", "linear model", "model complexity", "sample"]),
        ("Regression Basics", ["regression problem", "simple linear regression", "regression model", "continuous target", "slope", "intercept", "residual", "predicting"])
    ],
    "Week 2 - Mathematical Foundations": [
        ("Sets & Number Systems", ["set", "subset", "union", "intersection", "cartesian product", "complement", "rational", "irrational", "supremum", "infimum", "bounded set", "field", "octal", "decimal representation", "binary representation"]),
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
    return bool(re.search(r'\b' + re.escape(kw) + r'\b', text, re.IGNORECASE))

def classify_question(text, options_text=""):
    combined = (text + " " + options_text).lower()
    if has_kw("eigenvalue", combined) or has_kw("eigenvalues", combined) or has_kw("diagonalizable", combined):
        return "Week 4 - Regression & Eigenvalues", "Eigenvalues"
    if has_kw("eigenvector", combined) or has_kw("eigenvectors", combined) or has_kw("eigenspace", combined):
        return "Week 4 - Regression & Eigenvalues", "Eigenvectors"
    if has_kw("least squares", combined) or has_kw("least square", combined) or has_kw("best fit line", combined) or has_kw("normal equation", combined):
        return "Week 4 - Regression & Eigenvalues", "Least Squares"
    if has_kw("squared loss", combined) or has_kw("mean squared error", combined) or has_kw("mse", combined) or has_kw("loss function", combined) or has_kw("residual sum", combined):
        return "Week 4 - Regression & Eigenvalues", "Error Calculations"
        
    if has_kw("directional derivative", combined) or has_kw("differentiable", combined) or has_kw("derivative", combined) or has_kw("gradient", combined) or has_kw("hessian", combined):
        return "Week 2 - Mathematical Foundations", "Derivatives"
    if has_kw("continuous", combined) or has_kw("continuity", combined) or has_kw("discontinuous", combined):
        return "Week 2 - Mathematical Foundations", "Continuity"
    if has_kw("metric space", combined) or has_kw("metric", combined) or has_kw("distance function", combined) or has_kw("triangle inequality", combined):
        return "Week 2 - Mathematical Foundations", "Metric Spaces"
    if has_kw("sequence", combined) or has_kw("converges", combined) or has_kw("diverges", combined) or has_kw("cauchy", combined):
        return "Week 2 - Mathematical Foundations", "Sequences & Limits"
    if has_kw("injective", combined) or has_kw("surjective", combined) or has_kw("bijective", combined) or (has_kw("domain", combined) and has_kw("codomain", combined)):
        return "Week 2 - Mathematical Foundations", "Functions"
    if has_kw("octal", combined) or has_kw("decimal representation", combined) or has_kw("subset", combined) or has_kw("supremum", combined) or has_kw("infimum", combined):
        return "Week 2 - Mathematical Foundations", "Sets & Number Systems"
        
    if has_kw("column space", combined) or has_kw("row space", combined) or has_kw("null space", combined) or has_kw("subspace", combined) or has_kw("nullity", combined):
        return "Week 3 - Linear Algebra & Subspaces", "Subspaces"
    if has_kw("linearly independent", combined) or has_kw("linearly dependent", combined) or has_kw("linear independence", combined):
        return "Week 3 - Linear Algebra & Subspaces", "Linear Independence"
    if has_kw("span", combined) or has_kw("basis", combined) or has_kw("dimension", combined):
        return "Week 3 - Linear Algebra & Subspaces", "Span & Basis"
    if has_kw("dot product", combined) or has_kw("inner product", combined) or has_kw("norm", combined) or has_kw("orthogonal", combined) or has_kw("orthonormal", combined):
        return "Week 3 - Linear Algebra & Subspaces", "Dot Product & Norms"
    if has_kw("matrix", combined) or has_kw("matrices", combined) or has_kw("transpose", combined) or has_kw("determinant", combined) or has_kw("invertible", combined):
        return "Week 3 - Linear Algebra & Subspaces", "Matrices"
        
    if has_kw("supervised", combined) or has_kw("unsupervised", combined) or has_kw("reinforcement", combined) or has_kw("semi-supervised", combined):
        return "Week 1 - ML Foundations", "Types of Learning"
    if has_kw("task", combined) or has_kw("classification", combined) or has_kw("clustering", combined) or has_kw("dimensionality reduction", combined) or has_kw("anomaly", combined):
        return "Week 1 - ML Foundations", "ML Tasks"
    if has_kw("hypothesis", combined) or has_kw("overfitting", combined) or has_kw("generalization", combined) or has_kw("inductive bias", combined) or has_kw("bias-variance", combined):
        return "Week 1 - ML Foundations", "ML Concepts"
    if has_kw("polynomial regression", combined) or has_kw("linear regression", combined) or has_kw("regression", combined):
        return "Week 1 - ML Foundations", "Regression Basics"
        
    best_score = 0
    best_week = "Week 1 - ML Foundations"
    best_subtopic = "ML Concepts"
    for week, subtopics in CATEGORIES.items():
        for subtopic, keywords in subtopics:
            score = sum(len(kw) for kw in keywords if has_kw(kw, combined))
            if score > best_score:
                best_score = score
                best_week = week
                best_subtopic = subtopic
    return best_week, best_subtopic

def save_image_bytes(image_bytes, ext="png"):
    img_hash = hashlib.md5(image_bytes).hexdigest()
    filename = f"qimg_{img_hash[:12]}.{ext}"
    rel_path = f"assets/q_images/{filename}"
    full_path = os.path.join(ASSETS_DIR, filename)
    if not os.path.exists(full_path):
        with open(full_path, "wb") as f:
            f.write(image_bytes)
    return rel_path

def find_mlf_bounds(doc):
    """
    Locates the starting page and y0 of the MLF section,
    and the ending page and y0 of the subsequent section.
    """
    start_pno = None
    y_start = 0
    end_pno = None
    y_end = 99999
    num_pages = len(doc)
    
    for pno in range(num_pages):
        page = doc[pno]
        text = page.get_text()
        if "MLF" in text or "Machine Learning Foundations" in text or "MACHINE LEARNING FOUNDATIONS" in text:
            blocks = page.get_text("blocks")
            for b in blocks:
                txt = b[4].strip()
                lines = [l.strip() for l in txt.split('\n') if l.strip()]
                for l in lines:
                    if l == "MLF" or l == "Machine Learning Foundations" or ("MACHINE LEARNING FOUNDATIONS" in l.upper() and ("SECTION" in l.upper() or "DIPLOMA" in l.upper() or len(l) < 35)):
                        start_pno = pno
                        y_start = b[1]
                        break
                if start_pno is not None:
                    break
        if start_pno is not None:
            break
            
    if start_pno is None:
        return None, 0, None, 99999
        
    for pno in range(start_pno + 1, num_pages):
        page = doc[pno]
        blocks = page.get_text("blocks")
        for b in blocks:
            txt = b[4].strip()
            lines = [l.strip() for l in txt.split('\n') if l.strip()]
            for l in lines:
                if l in ["DBMS", "PDSA", "MLT", "Java", "AppDev-2", "BDM", "System Commands", "Business Analytics", "MLP", "MAD 1", "MAD 2"]:
                    end_pno = pno
                    y_end = b[1]
                    break
                if re.search(r'(?<!Sub-)Section\s+(Id|Number)\s*:', l):
                    if not re.search(r'\bMLF\b', txt) and "MACHINE LEARNING FOUNDATIONS" not in txt.upper():
                        end_pno = pno
                        y_end = b[1]
                        break
            if end_pno is not None:
                break
        if end_pno is not None:
            break
            
    if end_pno is None:
        end_pno = min(num_pages - 1, start_pno + 20)
        y_end = 99999
        
    return start_pno, y_start, end_pno, y_end

def clean_stem_text(raw_text):
    pa = None
    m_pa = re.search(r'Possible Answers\s*:\s*([^\n\r]+|\d+(?:\.\d+)?(?:\s*to\s*\d+(?:\.\d+)?)?)', raw_text, re.IGNORECASE)
    if m_pa:
        pa = m_pa.group(1).strip()
        pa = re.split(r'(?:MLF|MLT|DBMS|PDSA|Java|BDM|System|Section)', pa)[0].strip()
        
    cleaned = re.sub(r'Possible Answers\s*:.*$', '', raw_text, flags=re.DOTALL | re.IGNORECASE)
    cleaned = re.sub(r'(?:MLF|MLT|DBMS|PDSA|Java|BDM|System Commands)\s+Number of Questions\s*:.*$', '', cleaned, flags=re.DOTALL | re.IGNORECASE)
    cleaned = re.sub(r'Section Marks\s*:.*$', '', cleaned, flags=re.DOTALL | re.IGNORECASE)
    cleaned = re.sub(r'Response Type\s*:.*?(?=NOTE|$)', '', cleaned, flags=re.DOTALL | re.IGNORECASE)
    cleaned = re.sub(r'Evaluation Required.*?(?=NOTE|$)', '', cleaned, flags=re.DOTALL | re.IGNORECASE)
    cleaned = re.sub(r'Show Word Count.*?(?=NOTE|$)', '', cleaned, flags=re.DOTALL | re.IGNORECASE)
    cleaned = re.sub(r'Answers Type.*?(?=NOTE|$)', '', cleaned, flags=re.DOTALL | re.IGNORECASE)
    cleaned = re.sub(r'Text Areas.*?(?=NOTE|$)', '', cleaned, flags=re.DOTALL | re.IGNORECASE)
    cleaned = re.sub(r'Time\s*:\s*\d+', '', cleaned, flags=re.IGNORECASE)
    cleaned = re.sub(r'Max\.\s*Selectable Options\s*:\s*\d+', '', cleaned, flags=re.IGNORECASE)
    cleaned = re.sub(r'Sub-Section Number\s*:.*?(?=\n|$)', '', cleaned, flags=re.IGNORECASE)
    cleaned = re.sub(r'Sub-Section Id\s*:.*?(?=\n|$)', '', cleaned, flags=re.IGNORECASE)
    cleaned = re.sub(r'Question Shuffling Allowed\s*:.*?(?=\n|$)', '', cleaned, flags=re.IGNORECASE)
    cleaned = re.sub(r'Mandatory\s*:.*?(?=\n|$)', '', cleaned, flags=re.IGNORECASE)
    cleaned = re.sub(r'Calculator\s*:.*?(?=\n|$)', '', cleaned, flags=re.IGNORECASE)
    cleaned = re.sub(r'\s+', ' ', cleaned).strip()
    return cleaned, pa

def clean_opt_text(opt_raw):
    t = re.sub(r'^[0-9]{5,}\.\s*', '', opt_raw)
    t = re.sub(r'^[A-D]\.\s*', '', t)
    t = re.split(r'Sub-Section\s+(?:Number|Id)\s*:', t, flags=re.IGNORECASE)[0]
    t = re.split(r'Question\s+Shuffling\s+Allowed\s*:', t, flags=re.IGNORECASE)[0]
    t = re.sub(r'\s+', ' ', t).strip()
    return t

print("Step 1: Discovering all papers with strict MLF boundaries...")
all_files = sorted(glob.glob(os.path.join(BASE_DIR, "**", "*.pdf"), recursive=True))

paper_list = []
for f in all_files:
    if "PDF_COM" in f or "mlf_questions_categorized" in f or "mlf_app" in f:
        continue
    try:
        doc = fitz.open(f)
        s_pno, y_s, e_pno, y_e = find_mlf_bounds(doc)
        doc.close()
        if s_pno is not None:
            paper_list.append((f, s_pno, y_s, e_pno, y_e))
    except:
        pass

print(f"Found {len(paper_list)} digital papers containing strictly bounded MLF section.")

raw_questions = []

for pdf_path, start_pno, y_start_page, end_pno, y_end_page in paper_list:
    rel_path = os.path.relpath(pdf_path, BASE_DIR)
    doc = fitz.open(pdf_path)
    
    current_comp = None
    
    for pno in range(start_pno, end_pno + 1):
        page = doc[pno]
        blocks = page.get_text('blocks')
        
        # Check for comprehension block
        for b in blocks:
            if "Question Label : Comprehension" in b[4] or "Question Type : COMPREHENSION" in b[4]:
                m_range = re.search(r'Question Numbers\s*:\s*\((?:(\d+)\s*to\s*(\d+)|\d+)\)', b[4])
                q_from = int(m_range.group(1)) if m_range and m_range.group(1) else 0
                q_to = int(m_range.group(2)) if m_range and m_range.group(2) else 9999
                
                rect_comp = fitz.Rect(18, max(15, b[1] - 5), page.rect.width - 18, min(page.rect.height - 15, b[3] + 250))
                for sub_b in blocks:
                    if re.search(r'Question Number\s*:\s*\d+', sub_b[4]) and sub_b[1] > b[1]:
                        rect_comp = fitz.Rect(18, max(15, b[1] - 5), page.rect.width - 18, sub_b[1] - 5)
                        break
                        
                pix_comp = page.get_pixmap(clip=rect_comp, dpi=150)
                im_comp = Image.frombytes('RGB', [pix_comp.width, pix_comp.height], pix_comp.samples)
                
                current_comp = {
                    'text': b[4].strip(),
                    'image': im_comp,
                    'q_from': q_from,
                    'q_to': q_to
                }
                
        # Find all questions starting on this page
        q_starts = []
        for b in blocks:
            m = re.search(r'Question Number\s*:\s*(\d+)', b[4])
            if m:
                # Boundary check: on start page, must be below y_start_page
                if pno == start_pno and b[1] < y_start_page:
                    continue
                # On end page, must be above y_end_page
                if pno == end_pno and b[1] >= y_end_page:
                    continue
                    
                q_starts.append({
                    'num': int(m.group(1)),
                    'y0': b[1],
                    'y1': b[3],
                    'raw_header': b[4].strip(),
                    'block': b
                })
                
        q_starts.sort(key=lambda x: x['y0'])
        
        for idx_q, qs in enumerate(q_starts):
            q_num = qs['num']
            header = qs['raw_header']
            
            # Check question ID and Type
            m_id = re.search(r'Question Id\s*:\s*(\d+)', header)
            m_type = re.search(r'Question Type\s*:\s*(\w+)', header)
            if not m_type:
                # Check Question Label
                if "Multiple Choice" in header:
                    q_type = "MCQ"
                elif "Multiple Select" in header:
                    q_type = "MSQ"
                elif "Short Answer" in header:
                    q_type = "SA"
                else:
                    q_type = "MCQ"
            else:
                q_type = m_type.group(1)
                
            q_id = m_id.group(1) if m_id else f"QID-{q_num}"
            
            # Marks check
            m_marks = re.search(r'Correct Marks\s*:\s*([0-9.]+)', header)
            marks = float(m_marks.group(1)) if m_marks else 2.0
            if marks <= 0 or "ARE YOU SURE" in header:
                continue
                
            # Vertical span of question on this page
            y_start = max(15, qs['y0'] - 5)
            
            if idx_q + 1 < len(q_starts):
                next_boundary_y = max(y_start + 40, q_starts[idx_q + 1]['y0'] - 5)
                spans_next_page = False
            else:
                # Check if next section starts on this page
                if pno == end_pno and y_end_page < page.rect.height:
                    next_boundary_y = y_end_page - 5
                    spans_next_page = False
                else:
                    next_boundary_y = page.rect.height - 15
                    spans_next_page = True
                    
            clip_rect = fitz.Rect(15, y_start, page.rect.width - 15, next_boundary_y)
            pix = page.get_pixmap(clip=clip_rect, dpi=150)
            im_q = Image.frombytes('RGB', [pix.width, pix.height], pix.samples)
            
            # Multi-page stitching if needed
            y_end_next = 0
            if spans_next_page and pno + 1 <= end_pno:
                next_p = doc[pno + 1]
                next_blocks = next_p.get_text('blocks')
                y_end_next = next_p.rect.height - 15
                for nb in next_blocks:
                    if re.search(r'Question Number\s*:\s*\d+', nb[4]):
                        y_end_next = max(20, nb[1] - 5)
                        break
                    if "Question Label : Comprehension" in nb[4]:
                        y_end_next = max(20, nb[1] - 5)
                        break
                    if pno + 1 == end_pno and nb[1] >= y_end_page:
                        y_end_next = max(20, y_end_page - 5)
                        break
                        
                if y_end_next > 25:
                    clip_next = fitz.Rect(15, 15, next_p.rect.width - 15, y_end_next)
                    pix_next = next_p.get_pixmap(clip=clip_next, dpi=150)
                    im_next = Image.frombytes('RGB', [pix_next.width, pix_next.height], pix_next.samples)
                    
                    stitched = Image.new('RGB', (max(im_q.width, im_next.width), im_q.height + im_next.height), (255, 255, 255))
                    stitched.paste(im_q, (0, 0))
                    stitched.paste(im_next, (0, im_q.height))
                    im_q = stitched
                    
            # Prepend comprehension if active
            if current_comp and current_comp['q_from'] <= q_num <= current_comp['q_to']:
                comp_img = current_comp['image']
                c_w = max(comp_img.width, im_q.width)
                c_h = comp_img.height + im_q.height + 15
                im_full = Image.new('RGB', (c_w, c_h), (255, 255, 255))
                im_full.paste(comp_img, (0, 0))
                im_full.paste(im_q, (0, comp_img.height + 15))
                im_q = im_full
                
            # Resize card if width > 1200
            if im_q.width > 1200:
                h_new = int(im_q.height * 1200 / im_q.width)
                im_q = im_q.resize((1200, h_new), Image.Resampling.LANCZOS)
                
            # Save Card Image
            card_filename = f"card_{q_id}_{q_num}.jpg"
            card_rel_path = f"assets/q_cards/{card_filename}"
            card_full_path = os.path.join(CARDS_DIR, card_filename)
            if not os.path.exists(card_full_path):
                im_q.save(card_full_path, quality=85, optimize=True)
            
            # Extract Text and Options
            full_q_text = page.get_text(clip=clip_rect)
            if spans_next_page and pno + 1 <= end_pno and y_end_next > 25:
                full_q_text += "\n" + doc[pno + 1].get_text(clip=fitz.Rect(15, 15, page.rect.width - 15, y_end_next))
                
            stem_part = full_q_text.split("Options :")[0] if "Options :" in full_q_text else full_q_text
            stem_part = re.sub(r'^Question Number\s*:.*?(?=Question Label|$)', '', stem_part, flags=re.DOTALL)
            stem_part = re.sub(r'^Question Label\s*:.*?\n', '', stem_part)
            clean_stem, possible_ans = clean_stem_text(stem_part)
            
            # Detect Green Checkmark Icons
            green_icons = []
            
            # Scan page pno
            for img_info in page.get_image_info(xrefs=True):
                if img_info['width'] <= 24 and img_info['height'] <= 24 and y_start - 10 <= img_info['bbox'][1] <= next_boundary_y + 10:
                    try:
                        pix_ic = fitz.Pixmap(doc, img_info['xref'])
                        if pix_ic.n >= 3:
                            cx, cy = pix_ic.width // 2, pix_ic.height // 2
                            r, g, b = pix_ic.pixel(cx, cy)[:3]
                            if g > r + 15 and g > b + 15:
                                green_icons.append(('p0', img_info['bbox'][1]))
                    except:
                        pass
                        
            # If multi-page, scan page pno + 1
            if spans_next_page and pno + 1 <= end_pno and y_end_next > 25:
                next_p = doc[pno + 1]
                for img_info in next_p.get_image_info(xrefs=True):
                    if img_info['width'] <= 24 and img_info['height'] <= 24 and img_info['bbox'][1] <= y_end_next + 10:
                        try:
                            pix_ic = fitz.Pixmap(doc, img_info['xref'])
                            if pix_ic.n >= 3:
                                cx, cy = pix_ic.width // 2, pix_ic.height // 2
                                r, g, b = pix_ic.pixel(cx, cy)[:3]
                                if g > r + 15 and g > b + 15:
                                    green_icons.append(('p1', img_info['bbox'][1]))
                        except:
                            pass
                            
            # Extract Options & Option Blocks
            options = []
            correct_ans = []
            
            if q_type in ["MCQ", "MSQ"]:
                opt_blocks = []
                
                # Check blocks on page pno
                for b in blocks:
                    if y_start <= b[1] <= next_boundary_y:
                        txt = b[4].strip()
                        m = re.match(r'^([0-9]{5,}|[A-D])\.\s*(.*)', txt, re.DOTALL)
                        if m:
                            opt_blocks.append(('p0', b[1], m.group(1), m.group(2)))
                            
                # Check blocks on page pno + 1
                if spans_next_page and pno + 1 <= end_pno and y_end_next > 25:
                    for b in doc[pno + 1].get_text('blocks'):
                        if b[1] <= y_end_next:
                            txt = b[4].strip()
                            m = re.match(r'^([0-9]{5,}|[A-D])\.\s*(.*)', txt, re.DOTALL)
                            if m:
                                opt_blocks.append(('p1', b[1], m.group(1), m.group(2)))
                                
                opt_blocks.sort(key=lambda x: (x[0], x[1]))
                
                # If regex blocks didn't catch, fallback to string splitting
                if not opt_blocks and "Options :" in full_q_text:
                    opts_part = full_q_text.split("Options :")[1]
                    m_list = list(re.finditer(r'([0-9]{5,}|[A-D])\.\s*(.*?)(?=\n(?:[0-9]{5,}|[A-D])\.|\n\s*Question Number|\n\s*Sub-Section|$)', opts_part, re.DOTALL))
                    for m_item in m_list:
                        opt_blocks.append(('p0', 0, m_item.group(1), m_item.group(2)))
                        
                correct_indices = set()
                for ic_tag, ic_y in green_icons:
                    candidates = [(k, o) for k, o in enumerate(opt_blocks) if o[0] == ic_tag and o[1] > 0]
                    if candidates:
                        best_k, best_opt = min(candidates, key=lambda item: abs(item[1][1] - ic_y))
                        if abs(best_opt[1] - ic_y) < 8.0:
                            correct_indices.add(best_k)

                for k, opt_data in enumerate(opt_blocks):
                    letter = chr(65 + k)
                    page_tag, opt_y, opt_id_str, raw_opt_txt = opt_data
                    clean_opt = clean_opt_text(raw_opt_txt)
                    is_correct = k in correct_indices
                    
                    # Extract Option Formula Image if text is empty
                    opt_img_rel = None
                    if not clean_opt and opt_y > 0:
                        target_page = page if page_tag == 'p0' else doc[pno + 1]
                        for img_info in target_page.get_image_info(xrefs=True):
                            if (img_info['width'] > 25 or img_info['height'] > 25) and abs(img_info['bbox'][1] - opt_y) < 40:
                                try:
                                    pix_opt = fitz.Pixmap(doc, img_info['xref'])
                                    opt_img_rel = save_image_bytes(pix_opt.tobytes(), "png")
                                    break
                                except:
                                    pass
                                    
                    options.append({
                        'id': letter,
                        'option_id': opt_id_str,
                        'text': clean_opt,
                        'image': opt_img_rel,
                        'is_correct': is_correct
                    })
                    if is_correct:
                        correct_ans.append(letter)
                        
            elif q_type == "SA":
                if possible_ans:
                    correct_ans.append(possible_ans)
                    
            raw_questions.append({
                'question_number': str(q_num),
                'question_id': q_id,
                'source_paper': rel_path,
                'question_type': q_type,
                'marks': int(marks),
                'question_text': clean_stem,
                'card_image': card_rel_path,
                'images': [card_rel_path],
                'options': options,
                'correct_answer': correct_ans
            })
            
    doc.close()

print(f"\nExtracted {len(raw_questions)} raw question cards across all digital papers.")

# Extract scanned compilation (PDF_COM_202611031249451070.pdf)
scan_pdf = os.path.join(BASE_DIR, "PDF_COM_202611031249451070.pdf")
if os.path.exists(scan_pdf):
    doc_scan = fitz.open(scan_pdf)
    print(f"Extracting scanned compilation: {len(doc_scan)} pages at high resolution...")
    for pno in range(len(doc_scan)):
        page = doc_scan[pno]
        rect = fitz.Rect(40, 40, page.rect.width - 40, page.rect.height - 40)
        pix = page.get_pixmap(clip=rect, dpi=150)
        im = Image.frombytes('RGB', [pix.width, pix.height], pix.samples)
        if im.width > 1200:
            h_new = int(im.height * 1200 / im.width)
            im = im.resize((1200, h_new), Image.Resampling.LANCZOS)
            
        card_f = f"card_scan_p{pno+1}.jpg"
        card_p = os.path.join(CARDS_DIR, card_f)
        if not os.path.exists(card_p):
            im.save(card_p, quality=85, optimize=True)
        
        raw_questions.append({
            'question_number': str(pno + 1),
            'question_id': f"SCAN-P{pno+1}",
            'source_paper': "PDF_COM_202611031249451070.pdf",
            'question_type': "MCQ",
            'marks': 2,
            'question_text': f"Portal Examination Question {pno+1}",
            'card_image': f"assets/q_cards/{card_f}",
            'images': [f"assets/q_cards/{card_f}"],
            'options': [
                {'id': 'A', 'option_id': '1', 'text': 'Option A (Refer to question card image)', 'image': None, 'is_correct': False},
                {'id': 'B', 'option_id': '2', 'text': 'Option B (Refer to question card image)', 'image': None, 'is_correct': False},
                {'id': 'C', 'option_id': '3', 'text': 'Option C (Refer to question card image)', 'image': None, 'is_correct': False},
                {'id': 'D', 'option_id': '4', 'text': 'Option D (Refer to question card image)', 'image': None, 'is_correct': False}
            ],
            'correct_answer': []
        })
    doc_scan.close()

# Deduplicate questions
print("\nDeduplicating questions...")
unique_map = {}

for q in raw_questions:
    q_id = q['question_id']
    if q_id and len(q_id) >= 10 and q_id.isdigit():
        sig = f"ID_{q_id}"
    else:
        norm_txt = re.sub(r'[^a-zA-Z0-9]', '', q['question_text'].lower())[:60]
        if len(norm_txt) >= 15:
            sig = f"TXT_{norm_txt}"
        else:
            sig = f"NUM_{q['source_paper']}_{q['question_number']}"
            
    if sig not in unique_map:
        unique_map[sig] = {
            'question_number': q['question_number'],
            'question_id': q['question_id'],
            'question_type': q['question_type'],
            'marks': q['marks'],
            'question_text': q['question_text'],
            'card_image': q['card_image'],
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
            
        if not merged['correct_answer'] and q['correct_answer']:
            merged['correct_answer'] = list(q['correct_answer'])
            
        if len(q['question_text']) > len(merged['question_text']):
            merged['question_text'] = q['question_text']
            
        if not merged['options'] and q['options']:
            merged['options'] = [dict(o) for o in q['options']]

# Build Final Classified List
final_questions = []
idx = 1

for sig, q in unique_map.items():
    opts_str = " ".join(o.get('text', '') for o in q.get('options', []))
    week, subtopic = classify_question(q['question_text'], opts_str)
    
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
        'question_number': q['question_number'],
        'question_id': q['question_id'],
        'question_type': q['question_type'],
        'marks': q['marks'],
        'question_text': q['question_text'],
        'card_image': q['card_image'],
        'images': [q['card_image']],
        'options': clean_opts,
        'correct_answer': q['correct_answer'],
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

# Save to data/questions_data.js
js_path = os.path.join(DATA_DIR, "questions_data.js")
with open(js_path, "w", encoding="utf-8") as f:
    f.write("window.MLF_QUESTIONS = " + json.dumps(final_questions, ensure_ascii=False, indent=2) + ";\n")
print(f"Saved to {js_path}")
