import fitz
import os
import glob
import re

base_path = r"C:\Users\avesh\Desktop\PYQS"
pdf_files = sorted(glob.glob(os.path.join(base_path, "**", "*.pdf"), recursive=True))

def find_mlf_pages(doc):
    start_pno = None
    end_pno = None
    num_pages = len(doc)
    
    # Locate page with MLF section header
    for pno in range(num_pages):
        text = doc[pno].get_text()
        # Look for explicit section header line
        lines = [l.strip() for l in text.split('\n') if l.strip()]
        for idx, line in enumerate(lines):
            # Check for section title
            if line == "MLF" or line == "Machine Learning Foundations" or ("MACHINE LEARNING FOUNDATIONS" in line.upper() and ("DIPLOMA LEVEL" in line.upper() or "SECTION" in line.upper() or "SUBJECT" in line.upper())):
                # Verify it is in section header context
                context = " ".join(lines[max(0, idx-3):min(len(lines), idx+10)])
                if "Number of Questions" in context or "Section Id" in context or "Section Marks" in context or "ARE YOU SURE" in context:
                    start_pno = pno
                    break
        if start_pno is not None:
            break
            
    if start_pno is None:
        return None, None
        
    # Locate end page
    for pno in range(start_pno + 1, num_pages):
        text = doc[pno].get_text()
        lines = [l.strip() for l in text.split('\n') if l.strip()]
        for idx, line in enumerate(lines):
            # Check for next section header
            if re.search(r'(?<!Sub-)Section\s+(Id|Number)\s*:', line):
                # Check what subject is above or near this
                sub_context = " ".join(lines[max(0, idx-5):min(len(lines), idx+5)])
                if not re.search(r'\bMLF\b', sub_context) and "MACHINE LEARNING FOUNDATIONS" not in sub_context.upper():
                    end_pno = pno
                    break
            # Also check for direct subject names appearing as section headers in 2022 papers
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

results = []
for p in pdf_files:
    rel = os.path.relpath(p, base_path)
    try:
        doc = fitz.open(p)
        sp, ep = find_mlf_pages(doc)
        if sp is not None:
            # Count questions in this range
            sec_text = ""
            for pno in range(sp, ep + 1):
                sec_text += doc[pno].get_text() + "\n"
            q_matches = re.findall(r'Question Number\s*:\s*(\d+)', sec_text)
            # Filter out confirmation question (0 marks or 'ARE YOU SURE')
            results.append((rel, sp+1, ep+1, len(set(q_matches)), set(q_matches)))
        doc.close()
    except Exception as e:
        print(f"Error {rel}: {e}")

print(f"Identified MLF in {len(results)} PDFs:")
total_q_count = 0
for rel, sp, ep, qcount, qnums in results:
    total_q_count += qcount
    print(f"  {rel}: pages {sp}-{ep} ({qcount} questions)")

print(f"\nTotal raw question instances found across papers: {total_q_count}")
