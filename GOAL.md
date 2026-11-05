# Machine Learning Foundations (MLF) PYQ Extraction, Categorization & JEE CBT Test Platform

## 1. Objective
Extract, clean, deduplicate, and systematically categorize all Machine Learning Foundations ("MLF") questions word-by-word with options from the IIT Madras past year exam papers located in `C:\Users\avesh\Desktop\PYQS`. Provide both an exportable categorized PDF question repository and an interactive, high-fidelity Computer-Based Test (CBT) web application replicating the official JEE examination test-taking interface.

---

## 2. Acceptance Criteria
- [ ] **Comprehensive PDF Extraction**: Traverse all 65 PDF documents across all subdirectories (`2022 term papers`, `Jan 2023`, `Jan 2024`, `Jan 25`, `May 2023`, `May 2025`, `May 24`, `Sept 2023`, `Sept 2024`, `Quiz 1- Improvement, Foundation, diploma, Degree`, etc.) and isolate the "MLF" sections.
- [ ] **Fidelity & Deduplication**:
  - Extract question text, options (A, B, C, D / 1, 2, 3, 4), question types (MCQ, MSQ, NAT/SA), and marks verbatim without altering technical wording.
  - Detect and remove duplicate questions (preserving identical questions only once).
- [ ] **Taxonomic Categorization**:
  Categorize each unique question precisely into the user-specified syllabus hierarchy:
  - **Week 1 - ML Foundations**:
    - ML Concepts
    - Types of Learning
    - ML Tasks
    - Data & Models
    - Regression Basics
  - **Week 2 - Mathematical Foundations**:
    - Sets & Number Systems
    - Metric Spaces
    - Sequences & Limits
    - Functions
    - Continuity
    - Derivatives
  - **Week 3 - Linear Algebra & Subspaces**:
    - Vectors
    - Matrices
    - Dot Product & Norms
    - Linear Independence
    - Span & Basis
    - Subspaces
  - **Week 4 - Regression & Eigenvalues**:
    - Regression
    - Least Squares
    - Error Calculations
    - Eigenvalues
    - Eigenvectors
- [ ] **PDF Document Output**:
  - Generate a professional, print-ready `mlf_questions_categorized.pdf` containing all unique questions organized by Week and Subtopic, with complete options and answer keys.
- [ ] **JEE Exam CBT Interface (HTML/CSS/JS)**:
  - Replicate the official JEE / NTA Computer Based Test layout:
    - Candidate info bar, live countdown timer, and exam title.
    - Question palette on the right with standard JEE status states:
      - Gray: Not Visited
      - Red: Not Answered
      - Green: Answered
      - Purple: Marked for Review
      - Purple + Green circle: Answered & Marked for Review
    - Section / Category filtering (by Week 1, Week 2, Week 3, Week 4).
    - Question viewer with crisp typography, mathematical notation rendering, and option selection.
    - Action controls: "Save & Next", "Clear Response", "Mark for Review & Next", "Previous".
    - "Question Paper" view modal to preview all questions at once.
    - "Submit" dialog with test summary (Total Questions, Answered, Unanswered, Marked) and instant score card / review report.
- [ ] **Verification & Code Quality**:
  - Automated tests verifying extractor output, question counts, deduplication logic, and JSON schema integrity.
  - Review diffs with CodeRabbit CLI before finalizing.

---

## 3. Constraints & Tech Stack Boundaries
- **Language**: Python 3.13 (`fitz` / PyMuPDF, `reportlab`)
- **Frontend**: Pure Vanilla HTML5, CSS3, JavaScript (zero heavy bloated frameworks, offline-ready, responsive, accessible)
- **Data Persistence**: `questions.json` storing structured question bank
- **Git & Automation**: Git with private GitHub remote, atomic commits and automatic pushing upon task milestones.

---

## 4. Milestone Decomposition
1. **M1: 4-Tier Setup & Git Remote Configuration**: Setup `GOAL.md`, `PRD.md`, `progress.txt`, `STEERING.md`, `.clinerules`, local Git, and private GitHub remote via `gh`.
2. **M2: PDF Parser & Verbatim MLF Extraction Pipeline**: Implement parser in Python using PyMuPDF to scan all PDFs, detect MLF boundaries, extract question text, options, answers, and images.
3. **M3: Deduplication & Syllabus Categorization**: Implement strict deduplication and map questions into the 4-week hierarchy. Save clean dataset to `data/questions.json`.
4. **M4: Categorized PDF Generation**: Build `generate_pdf.py` using ReportLab to compile a categorized PDF document `mlf_questions_categorized.pdf`.
5. **M5: JEE CBT Test Interface Development**: Build `index.html` replicating the full JEE examination interface with timer, status palette, question viewer, scoring, and review mode.
6. **M6: Verification, CodeRabbit Audit & Delivery**: Execute test suite, run CodeRabbit review, commit, auto-push, and report results to user.
