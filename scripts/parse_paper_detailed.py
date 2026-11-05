import fitz
import re
import os
import json

def parse_mlf_paper(pdf_path, img_dir):
    os.makedirs(img_dir, exist_ok=True)
    doc = fitz.open(pdf_path)
    
    # 1. Find MLF section range
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
        doc.close()
        return []
        
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
        
    print(f"Parsing {os.path.basename(pdf_path)}: pages {start_pno+1} to {end_pno+1}")
    
    # Extract blocks & images across the pages
    raw_text = ""
    for pno in range(start_pno, end_pno + 1):
        raw_text += f"\n<<<PAGE_BREAK_{pno+1}>>>\n" + doc[pno].get_text()
        
    doc.close()
    return raw_text

text = parse_mlf_paper(r"C:\Users\avesh\Desktop\PYQS\Jan 2024\IIT M DIPLOMA AN2 EXAM QDD2 25 Feb 2024.pdf", r"C:\Users\avesh\Desktop\PYQS\assets\q_images")
print(f"Extracted {len(text)} characters of raw MLF text.")
with open(r"C:\Users\avesh\Desktop\PYQS\scripts\sample_mlf_raw.txt", "w", encoding="utf-8") as f:
    f.write(text)
print("Saved to scripts/sample_mlf_raw.txt")
