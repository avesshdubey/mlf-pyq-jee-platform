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
