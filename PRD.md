# Product Requirements Document (PRD) - MLF PYQ & JEE CBT Test Platform

## Tasks Breakdown

- [x] **Task 1: Establish Git & 4-Tier Configuration Baseline**
  - Verify `.gitignore` ignores large 850MB PDF binaries.
  - Create initial commit with 4-tier configuration files.
  - Link private GitHub remote repository via GitHub CLI (`gh repo create`) and enable auto-push upstream tracking.

- [x] **Task 2: Build Multi-Paper MLF Section Scanner & Text Extractor**
  - Implement `extractor.py` utilizing `fitz` (PyMuPDF) to iterate across all 65 PDF files.
  - Precisely identify MLF section headers, section boundaries, question numbers, question types (MCQ, MSQ, SA/NAT), questions text, options, and answer keys.
  - Extract questions verbatim word-by-word.

- [x] **Task 3: Deduplication Engine & Taxonomic Syllabus Classifier**
  - Implement normalized string hashing and exact text matching to identify and eliminate duplicate questions.
  - Implement keyword and conceptual classification matching the user's 4-week syllabus hierarchy:
    - Week 1: ML Concepts, Types of Learning, ML Tasks, Data & Models, Regression Basics
    - Week 2: Sets & Number Systems, Metric Spaces, Sequences & Limits, Functions, Continuity, Derivatives
    - Week 3: Vectors, Matrices, Dot Product & Norms, Linear Independence, Span & Basis, Subspaces
    - Week 4: Regression, Least Squares, Error Calculations, Eigenvalues, Eigenvectors
  - Output structured JSON to `data/questions.json` with comprehensive metadata (source paper, question number, type, text, options, correct answer, week, subtopic).

- [x] **Task 4: Categorized PDF Generator (`generate_pdf.py`)**
  - Use ReportLab to build a formatted PDF `mlf_questions_categorized.pdf`.
  - Structure by Week and Subtopic with tables of contents, question headers, clean option formatting, and solution keys.

- [x] **Task 5: Interactive JEE Exam Test CBT Web Application (`index.html`)**
  - Create a web application emulating the NTA / JEE CBT examination interface:
    - JEE Top Bar: Candidate name, Exam name ("Machine Learning Foundations"), Subject/Week selector tabs, Live countdown timer with pause/resume.
    - Question Panel: Question number, type, marking scheme (+3 / -1 or +4 / 0), question text, radio buttons / checkboxes for options, or numeric input for SA questions.
    - Control Buttons: "Clear Response", "Mark for Review & Next", "Save & Next", "Previous".
    - Palette Sidebar: Legend with 5 standard JEE status indicators, grid of question buttons with real-time status updates.
    - Exam Modals: "Question Paper" (full question paper view) and "Submit Exam" modal with confirmation and detailed breakdown.
    - Result Dashboard: Score summary, accuracy %, category-wise performance analysis, and detailed question review with explanations.

- [x] **Task 6: Verification, CodeRabbit QA & Git Auto-Push**
  - Execute automated tests to verify question counts, option consistency, JSON schema validity, and HTML responsiveness.
  - Run CodeRabbit CLI review (`cr review --agent`) and resolve any flagged issues.
  - Commit all changes and auto-push to GitHub remote.

- [x] **Task 7: User Authentication, Admin Control Panel & GitHub Pages Public Deployment**
  - Implement Login & Sign Up modal with persistent session management (`js/auth.js`).
  - Build Admin Control Panel with Dashboard analytics, user status control, test submissions log, question bank explorer, and CSV export (`js/admin.js`).
  - Make GitHub repository public (`avesshdubey/mlf-pyq-jee-platform`).
  - Deploy application to GitHub Pages (`https://avesshdubey.github.io/mlf-pyq-jee-platform/`).
  - Pass CodeRabbit review audit and all automated unit tests.

- [x] **Task 8: Precision Question & Option Extraction with Exact Images & Formulas**
  - Implement spatial coordinate grouping (`scripts/run_precision_extraction.py`) to extract option formula images, stem plots, and icons.
  - Eliminate blank option text by linking 279 formula images and 396 option texts.
  - Enhance `generate_pdf.py` to embed option images inside table rows.
  - Enhance `js/jee_app.js` and `css/jee_style.css` to render option images and multiple stem diagrams across exam view, question paper modal, and scorecard review.

- [x] **Task 9: Complete 100% Visual Fidelity via High-Resolution Question Paper Cards & Closest-Icon Answer Key Matching**
  - High-resolution 150 DPI question paper card cropper (`scripts/build_exact_dataset.py`) capturing exact question stems, inline math formulas, matrices, plots, and options directly from source exam papers.
  - Sub-pixel closest-matching algorithm (< 5 pt) mapping TCS iON green checkmark icons to exact option choices, eliminating duplicate correct answers.
  - Multi-page question stitching and comprehension passage pre-attachment to guarantee context completeness.
  - Regenerated `mlf_questions_categorized.pdf` (40.47 MB, 677 unique questions) embedding exact question paper cards and official answer keys.
  - Updated web application (`index.html`, `js/jee_app.js`, `css/jee_style.css`) with clean card-first presentation across main examination view, question paper modal, and post-submission scorecard review.
  - Passed all verification test suites (`tests/test_platform.py`).

- [x] **Task 10: Isolate Application & Categorized PDF into Dedicated `mlf_app` Folder with Root Gateway Redirect**
  - Moved all MLF app components (`index.html`, `css/`, `js/`, `data/`, `assets/`, `scripts/`, `tests/`, `mlf_questions_categorized.pdf`, `extractor.py`) into isolated directory `mlf_app/`.
  - Created root gateway `index.html` with instant redirection (`<meta http-equiv="refresh">` and `window.location.replace("mlf_app/")`) preserving GitHub Pages public deployment URL (`https://avesshdubey.github.io/mlf-pyq-jee-platform/`).
  - Updated `.gitignore` to ignore raw exam archives (`*.zip`) and root exam PDFs so the root workspace remains clean for other subjects.
  - Updated extraction scripts to exclude `mlf_app/` during any future paper scans.
  - Verified test suite passes (`python mlf_app/tests/test_platform.py`).
