import fitz
import re
import json

def extract_mlf_section_from_pdf(pdf_path):
    doc = fitz.open(pdf_path)
    mlf_start_page = None
    mlf_end_page = None
    total_pages = len(doc)
    
    # 1. Locate MLF Section
    for pno in range(total_pages):
        text = doc[pno].get_text()
        # Look for section indicator
        if re.search(r'\bMLF\b', text) or "MACHINE LEARNING FOUNDATIONS" in text.upper():
            # Check if this is a section header (e.g. has 'Number of Questions' or 'Section Number' or 'Section Id')
            if "Number of Questions" in text or "Section Id" in text or "Section Marks" in text or "ARE YOU SURE YOU HAVE TO WRITE EXAM FOR THIS SUBJECT" in text:
                mlf_start_page = pno
                break
                
    if mlf_start_page is None:
        doc.close()
        return None
        
    # 2. Locate end of MLF section (where next section starts)
    for pno in range(mlf_start_page + 1, total_pages):
        text = doc[pno].get_text()
        # Look for another section header
        # Patterns like: 'Section Number :', 'Section Marks :', 'Section Id :' followed by another subject
        # Subjects: DBMS, Java, PDSA, BDM, MLT, MLP, etc.
        lines = [l.strip() for l in text.split('\n') if l.strip()]
        for idx, line in enumerate(lines):
            if line in ["DBMS", "PDSA", "MLT", "Java", "AppDev-2", "BDM", "System Commands", "Business Analytics", "MLP", "MAD 1", "MAD 2"]:
                mlf_end_page = pno
                break
            if "Section Id :" in line and pno > mlf_start_page + 1:
                # Check if subject is different
                sub_context = " ".join(lines[max(0, idx-5):idx+5])
                if not re.search(r'\bMLF\b', sub_context) and "MACHINE LEARNING FOUNDATIONS" not in sub_context.upper():
                    mlf_end_page = pno
                    break
        if mlf_end_page is not None:
            break
            
    if mlf_end_page is None:
        # Default to end of document or ~15 pages after start
        mlf_end_page = min(total_pages - 1, mlf_start_page + 16)
        
    print(f"File: {pdf_path}")
    print(f"MLF Section found: pages {mlf_start_page+1} to {mlf_end_page+1} (total {mlf_end_page - mlf_start_page + 1} pages)")
    
    section_text = []
    for pno in range(mlf_start_page, mlf_end_page + 1):
        section_text.append(f"--- PAGE {pno+1} ---\n" + doc[pno].get_text())
        
    full_section = "\n".join(section_text)
    doc.close()
    return full_section

res1 = extract_mlf_section_from_pdf(r"C:\Users\avesh\Desktop\PYQS\2022 term papers\IIT M DIPLOMA QUIZ EXAM QPG1.pdf")
print("Length of section text in QPG1:", len(res1) if res1 else 0)

res2 = extract_mlf_section_from_pdf(r"C:\Users\avesh\Desktop\PYQS\Jan 2024\IIT M DIPLOMA AN2 EXAM QDD2 25 Feb 2024.pdf")
print("Length of section text in Jan 2024:", len(res2) if res2 else 0)
