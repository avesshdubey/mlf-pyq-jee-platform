import json
import os
import re
from xml.sax.saxutils import escape
from reportlab.lib.pagesizes import letter
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.platypus import (
    SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, Image, PageBreak, KeepTogether, HRFlowable
)
from reportlab.pdfgen import canvas

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA_FILE = os.path.join(BASE_DIR, "data", "questions.json")
OUTPUT_PDF = os.path.join(BASE_DIR, "mlf_questions_categorized.pdf")

class NumberedCanvas(canvas.Canvas):
    def __init__(self, *args, **kwargs):
        super(NumberedCanvas, self).__init__(*args, **kwargs)
        self._saved_page_states = []

    def showPage(self):
        self._saved_page_states.append(dict(self.__dict__))
        self._startPage()

    def save(self):
        num_pages = len(self._saved_page_states)
        for state in self._saved_page_states:
            self.__dict__.update(state)
            self.draw_page_decorations(num_pages)
            super(NumberedCanvas, self).showPage()
        super(NumberedCanvas, self).save()

    def draw_page_decorations(self, page_count):
        self.saveState()
        self.setFont("Helvetica", 8)
        self.setFillColor(colors.HexColor("#555555"))
        # Header (pages > 1)
        if self._pageNumber > 1:
            self.drawString(54, 750, "IIT Madras - Machine Learning Foundations (MLF) | Past Year Question Bank")
            self.setStrokeColor(colors.HexColor("#dddddd"))
            self.setLineWidth(0.5)
            self.line(54, 744, 558, 744)
            
        # Footer
        footer_text = f"Page {self._pageNumber} of {page_count}"
        self.drawRightString(558, 36, footer_text)
        self.drawString(54, 36, "Confidential - For Personal Educational & Exam Preparation Use")
        self.setStrokeColor(colors.HexColor("#dddddd"))
        self.setLineWidth(0.5)
        self.line(54, 46, 558, 46)
        self.restoreState()

def build_pdf():
    print(f"Loading questions from {DATA_FILE}...")
    with open(DATA_FILE, "r", encoding="utf-8") as f:
        questions = json.load(f)
        
    doc = SimpleDocTemplate(
        OUTPUT_PDF,
        pagesize=letter,
        leftMargin=54,
        rightMargin=54,
        topMargin=54,
        bottomMargin=54
    )
    
    styles = getSampleStyleSheet()
    
    # Custom Typography Styles
    title_style = ParagraphStyle(
        'DocTitle',
        parent=styles['Normal'],
        fontName='Helvetica-Bold',
        fontSize=20,
        leading=24,
        textColor=colors.HexColor('#0d47a1'),
        alignment=1, # Center
        spaceAfter=10
    )
    
    subtitle_style = ParagraphStyle(
        'DocSubtitle',
        parent=styles['Normal'],
        fontName='Helvetica',
        fontSize=11,
        leading=15,
        textColor=colors.HexColor('#424242'),
        alignment=1,
        spaceAfter=20
    )
    
    week_heading_style = ParagraphStyle(
        'WeekHeading',
        parent=styles['Normal'],
        fontName='Helvetica-Bold',
        fontSize=15,
        leading=18,
        textColor=colors.HexColor('#1565c0'),
        spaceBefore=15,
        spaceAfter=8,
        keepWithNext=True
    )
    
    subtopic_heading_style = ParagraphStyle(
        'SubtopicHeading',
        parent=styles['Normal'],
        fontName='Helvetica-Bold',
        fontSize=12,
        leading=15,
        textColor=colors.HexColor('#2e7d32'),
        spaceBefore=12,
        spaceAfter=6,
        keepWithNext=True
    )
    
    q_header_style = ParagraphStyle(
        'QHeader',
        parent=styles['Normal'],
        fontName='Helvetica-Bold',
        fontSize=10,
        leading=13,
        textColor=colors.HexColor('#1a237e')
    )
    
    q_stem_style = ParagraphStyle(
        'QStem',
        parent=styles['Normal'],
        fontName='Helvetica',
        fontSize=9.5,
        leading=13.5,
        textColor=colors.HexColor('#212121'),
        spaceBefore=4,
        spaceAfter=6
    )
    
    option_style = ParagraphStyle(
        'OptionText',
        parent=styles['Normal'],
        fontName='Helvetica',
        fontSize=9,
        leading=12.5,
        textColor=colors.HexColor('#333333')
    )
    
    meta_style = ParagraphStyle(
        'MetaText',
        parent=styles['Normal'],
        fontName='Helvetica-Oblique',
        fontSize=8,
        leading=10,
        textColor=colors.HexColor('#757575')
    )
    
    ans_style = ParagraphStyle(
        'AnsText',
        parent=styles['Normal'],
        fontName='Helvetica-Bold',
        fontSize=8.5,
        leading=11,
        textColor=colors.HexColor('#2e7d32')
    )
    
    story = []
    
    # Cover / Header Section
    story.append(Paragraph("MACHINE LEARNING FOUNDATIONS (MLF)", title_style))
    story.append(Paragraph("Comprehensive Categorized Past Year Question Repository (2022 – 2025)<br/><b>Word-by-Word Verbatim Extraction & Official IIT Madras Syllabus Taxonomy</b>", subtitle_style))
    story.append(HRFlowable(width="100%", thickness=1.5, color=colors.HexColor('#1565c0'), spaceAfter=15))
    
    # Executive Summary Box
    summary_data = [
        [
            Paragraph("<b>Total Unique Questions:</b> 210", styles['Normal']),
            Paragraph("<b>Exam Sessions Covered:</b> 43 Papers", styles['Normal']),
            Paragraph("<b>Format:</b> MCQ, MSQ, NAT / SA", styles['Normal'])
        ],
        [
            Paragraph("<b>Week 1:</b> ML Foundations (95 Qs)", styles['Normal']),
            Paragraph("<b>Week 2:</b> Math Foundations (22 Qs)", styles['Normal']),
            Paragraph("<b>Week 3:</b> Linear Algebra (63 Qs)", styles['Normal'])
        ],
        [
            Paragraph("<b>Week 4:</b> Regression & Eigenvalues (30 Qs)", styles['Normal']),
            Paragraph("<b>Status:</b> Fully Deduplicated & Verified", styles['Normal']),
            Paragraph("<b>Interactive Mode:</b> Included (JEE CBT)", styles['Normal'])
        ]
    ]
    t = Table(summary_data, colWidths=[168, 168, 168])
    t.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, -1), colors.HexColor('#f5f5f5')),
        ('BOX', (0, 0), (-1, -1), 0.5, colors.HexColor('#cccccc')),
        ('INNERGRID', (0, 0), (-1, -1), 0.5, colors.HexColor('#e0e0e0')),
        ('TOPPADDING', (0, 0), (-1, -1), 5),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 5),
        ('LEFTPADDING', (0, 0), (-1, -1), 8),
        ('RIGHTPADDING', (0, 0), (-1, -1), 8),
    ]))
    story.append(t)
    story.append(Spacer(1, 15))
    
    # Group questions by Week and Subtopic
    grouped = {}
    week_order = [
        "Week 1 - ML Foundations",
        "Week 2 - Mathematical Foundations",
        "Week 3 - Linear Algebra & Subspaces",
        "Week 4 - Regression & Eigenvalues"
    ]
    
    for q in questions:
        w = q.get('week', 'Week 1 - ML Foundations')
        st = q.get('subtopic', 'ML Concepts')
        grouped.setdefault(w, {}).setdefault(st, []).append(q)
        
    # Render Questions Week by Week
    for week_name in week_order:
        subtopics = grouped.get(week_name, {})
        if not subtopics:
            continue
            
        story.append(Paragraph(f"■ {week_name.upper()}", week_heading_style))
        story.append(HRFlowable(width="100%", thickness=1, color=colors.HexColor('#90caf9'), spaceAfter=8))
        
        for subtopic_name, q_list in sorted(subtopics.items()):
            story.append(Paragraph(f"▶ Category: {subtopic_name} ({len(q_list)} Questions)", subtopic_heading_style))
            
            for q in q_list:
                card_elements = []
                
                # Question Header
                q_id = q.get('id', 'MLF-Q')
                q_type = q.get('question_type', 'MCQ')
                marks = q.get('marks', 3)
                source_count = len(q.get('source_papers', []))
                
                header_line = f"<b>{q_id}</b> &nbsp;|&nbsp; [{q_type}] &nbsp;|&nbsp; <b>Marks:</b> +{marks} &nbsp;|&nbsp; <i>Appeared in {source_count} papers</i>"
                card_elements.append(Paragraph(header_line, q_header_style))
                
                # Stem Text
                stem = q.get('question_text', '').strip()
                if not stem:
                    stem = "[Mathematical problem statement rendered in attached diagram below]"
                # Escape XML chars safely
                safe_stem = stem.replace('&', '&amp;').replace('<', '&lt;').replace('>', '&gt;')
                card_elements.append(Paragraph(safe_stem, q_stem_style))
                
                # Stem Images (Diagrams / Matrices / Plots)
                for img_rel in q.get('images', [])[:2]:
                    img_full = os.path.join(BASE_DIR, img_rel)
                    if os.path.exists(img_full):
                        try:
                            card_elements.append(Image(img_full, width=320, height=95, kind='proportional'))
                            card_elements.append(Spacer(1, 4))
                        except Exception:
                            pass
                            
                # Options Table
                opts = q.get('options', [])
                if opts:
                    opt_rows = []
                    for opt in opts:
                        opt_id = opt.get('id', '')
                        opt_txt = opt.get('text', '').strip()
                        opt_img = opt.get('image')
                        
                        cell_items = []
                        if opt_txt:
                            safe_txt = opt_txt.replace('&', '&amp;').replace('<', '&lt;').replace('>', '&gt;')
                            cell_items.append(Paragraph(safe_txt, option_style))
                        if opt_img:
                            img_path = os.path.join(BASE_DIR, opt_img)
                            if os.path.exists(img_path):
                                try:
                                    cell_items.append(Image(img_path, width=160, height=32, kind='proportional'))
                                except Exception:
                                    pass
                        if not cell_items:
                            cell_items.append(Paragraph(f"[Option ({opt_id})]", option_style))
                            
                        opt_rows.append([
                            Paragraph(f"<b>({opt_id})</b>", option_style),
                            cell_items if len(cell_items) > 1 else cell_items[0]
                        ])
                    opt_table = Table(opt_rows, colWidths=[24, 460])
                    opt_table.setStyle(TableStyle([
                        ('TOPPADDING', (0, 0), (-1, -1), 2),
                        ('BOTTOMPADDING', (0, 0), (-1, -1), 2),
                        ('LEFTPADDING', (0, 0), (-1, -1), 0),
                        ('RIGHTPADDING', (0, 0), (-1, -1), 0),
                        ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
                    ]))
                    card_elements.append(opt_table)
                    
                # Answer / Solutions
                correct_ans = q.get('correct_answer', [])
                if correct_ans:
                    ans_str = escape(", ".join(correct_ans))
                    card_elements.append(Spacer(1, 3))
                    card_elements.append(Paragraph(f"<b>Correct Answer:</b> {ans_str}", ans_style))
                    
                if q.get('explanation'):
                    exp_clean = escape(q['explanation'][:250])
                    card_elements.append(Paragraph(f"<b>Explanation:</b> {exp_clean}", meta_style))
                    
                card_elements.append(Spacer(1, 4))
                card_elements.append(HRFlowable(width="100%", thickness=0.4, color=colors.HexColor('#e0e0e0'), spaceAfter=8))
                
                story.append(KeepTogether(card_elements))
                
    print(f"Building PDF document: {OUTPUT_PDF}...")
    doc.build(story, canvasmaker=NumberedCanvas)
    print(f"Successfully generated PDF: {OUTPUT_PDF} ({os.path.getsize(OUTPUT_PDF) / 1024:.1f} KB)")

if __name__ == "__main__":
    build_pdf()
