import fitz
import os
import glob
import re

base_path = r"C:\Users\avesh\Desktop\PYQS"

sample_pdfs = [
    r"2022 term papers\IIT M DIPLOMA QUIZ EXAM QPG1.pdf",
    r"Jan 2023\Quiz 1 Jan23  .pdf",
    r"Jan 2024\IIT M DIPLOMA AN2 EXAM QDD2 25 Feb 2024.pdf",
    r"MLF.pdf",
    r"Sept 2024\IIT M DIPLOMA AN EXAM QDD2.pdf"
]

for rel_path in sample_pdfs:
    full_path = os.path.join(base_path, rel_path)
    if not os.path.exists(full_path):
        continue
    print("=" * 60)
    print("PDF:", rel_path)
    doc = fitz.open(full_path)
    
    # Scan for section headers:
    for page_num in range(len(doc)):
        text = doc[page_num].get_text()
        if "Section Marks :" in text or "Number of Questions :" in text:
            lines = [l.strip() for l in text.split("\n") if l.strip()]
            for idx, line in enumerate(lines):
                if "Number of Questions :" in line:
                    context = lines[max(0, idx-3):min(len(lines), idx+4)]
                    print(f"  Page {page_num+1} Section Header: {' | '.join(context)}")
    doc.close()
