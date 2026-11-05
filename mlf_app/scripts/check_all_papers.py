import fitz
import os
import glob
import re

base_path = r"C:\Users\avesh\Desktop\PYQS"
pdf_files = sorted(glob.glob(os.path.join(base_path, "**", "*.pdf"), recursive=True))

print(f"Total PDF files: {len(pdf_files)}")

mlf_papers = []
non_mlf_papers = []

for p in pdf_files:
    rel = os.path.relpath(p, base_path)
    try:
        doc = fitz.open(p)
        found_mlf = False
        mlf_info = []
        for pno in range(len(doc)):
            text = doc[pno].get_text()
            # Look for MLF or Machine Learning Foundations
            if re.search(r'\bMLF\b', text, re.IGNORECASE) or "Machine Learning Foundations" in text:
                found_mlf = True
                mlf_info.append(pno + 1)
        doc.close()
        if found_mlf:
            mlf_papers.append((rel, mlf_info))
        else:
            non_mlf_papers.append(rel)
    except Exception as e:
        print(f"Error {rel}: {e}")

print(f"\nPapers with MLF: {len(mlf_papers)}")
for p, pages in mlf_papers[:15]:
    print(f"  {p} -> pages {pages[:5]}")

print(f"\nPapers WITHOUT MLF: {len(non_mlf_papers)}")
for p in non_mlf_papers[:15]:
    print(f"  {p}")
