import json
import os
import re
from xml.sax.saxutils import escape
from PIL import Image as PILImage
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
    
    title_style = ParagraphStyle(
        'DocTitle',
        parent=styles['Normal'],
        fontName='Helvetica-Bold',
        fontSize=18,
        leading=22,
        textColor=colors.HexColor('#0d47a1'),
        alignment=1,
        spaceAfter=8
    )
    
    subtitle_style = ParagraphStyle(
        'DocSubtitle',
        parent=styles['Normal'],
        fontName='Helvetica',
        fontSize=10.5,
        leading=14,
        textColor=colors.HexColor('#424242'),
        alignment=1,
        spaceAfter=15
    )
    
    week_heading_style = ParagraphStyle(
        'WeekHeading',
        parent=styles['Normal'],
        fontName='Helvetica-Bold',
        fontSize=14,
        leading=17,
        textColor=colors.HexColor('#1565c0'),
        spaceBefore=14,
        spaceAfter=6,
        keepWithNext=True
    )
    
    subtopic_heading_style = ParagraphStyle(
        'SubtopicHeading',
        parent=styles['Normal'],
        fontName='Helvetica-Bold',
        fontSize=11,
        leading=14,
        textColor=colors.HexColor('#2e7d32'),
        spaceBefore=10,
        spaceAfter=5,
        keepWithNext=True
    )
    
    q_header_style = ParagraphStyle(
        'QHeader',
        parent=styles['Normal'],
        fontName='Helvetica-Bold',
        fontSize=9.5,
        leading=12,
        textColor=colors.HexColor('#1e3a8a')
    )
    
    q_stem_style = ParagraphStyle(
        'QStem',
        parent=styles['Normal'],
        fontName='Helvetica',
        fontSize=9,
        leading=12.5,
        textColor=colors.HexColor('#212121'),
        spaceAfter=4
    )
    
    meta_style = ParagraphStyle(
        'MetaText',
        parent=styles['Normal'],
        fontName='Helvetica-Oblique',
        fontSize=8,
        leading=10,
        textColor=colors.HexColor('#64748b'),
        spaceAfter=4
    )
    
    ans_style = ParagraphStyle(
        'AnsText',
        parent=styles['Normal'],
        fontName='Helvetica-Bold',
        fontSize=9,
        leading=12,
        textColor=colors.HexColor('#16a34a')
    )
    
    story = []
    
    # Cover / Header Section
    story.append(Paragraph("MACHINE LEARNING FOUNDATIONS (MLF)", title_style))
    story.append(Paragraph("Comprehensive Categorized Past Year Question Repository (2022 – 2026)<br/><b>100% Exact Question Paper Cards with Mathematical Precision & Answer Keys</b>", subtitle_style))
    story.append(HRFlowable(width="100%", thickness=1.5, color=colors.HexColor('#1565c0'), spaceAfter=12))
    
    # Dynamic Executive Summary Box
    total_q = len(questions)
    w1_count = sum(1 for q in questions if "Week 1" in q.get('week', ''))
    w2_count = sum(1 for q in questions if "Week 2" in q.get('week', ''))
    w3_count = sum(1 for q in questions if "Week 3" in q.get('week', ''))
    w4_count = sum(1 for q in questions if "Week 4" in q.get('week', ''))
    
    summary_data = [
        [
            Paragraph(f"<b>Total Unique Questions:</b> {total_q}", styles['Normal']),
            Paragraph("<b>Exam Sessions Covered:</b> 44 Papers", styles['Normal']),
            Paragraph("<b>Format:</b> MCQ, MSQ, NAT / SA", styles['Normal'])
        ],
        [
            Paragraph(f"<b>Week 1:</b> ML Foundations ({w1_count} Qs)", styles['Normal']),
            Paragraph(f"<b>Week 2:</b> Math Foundations ({w2_count} Qs)", styles['Normal']),
            Paragraph(f"<b>Week 3:</b> Linear Algebra ({w3_count} Qs)", styles['Normal'])
        ],
        [
            Paragraph(f"<b>Week 4:</b> Regression & Eigenvalues ({w4_count} Qs)", styles['Normal']),
            Paragraph("<b>Fidelity:</b> Official TCS iON Cards", styles['Normal']),
            Paragraph("<b>Interactive Mode:</b> NTA JEE CBT Online", styles['Normal'])
        ]
    ]
    t = Table(summary_data, colWidths=[168, 168, 168])
    t.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, -1), colors.HexColor('#f8fafc')),
        ('BOX', (0, 0), (-1, -1), 0.5, colors.HexColor('#cbd5e1')),
        ('INNERGRID', (0, 0), (-1, -1), 0.5, colors.HexColor('#e2e8f0')),
        ('TOPPADDING', (0, 0), (-1, -1), 4),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 4),
        ('LEFTPADDING', (0, 0), (-1, -1), 8),
        ('RIGHTPADDING', (0, 0), (-1, -1), 8),
    ]))
    story.append(t)
    story.append(Spacer(1, 12))
    
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
                
                # Header
                q_id = q.get('id', 'MLF-Q')
                q_type = q.get('question_type', 'MCQ')
                marks = q.get('marks', 2)
                sources = q.get('source_papers', ['Official IITM Paper'])
                source_count = len(sources)
                first_src = os.path.basename(sources[0]).replace('.pdf', '')
                
                header_line = f"<b>{q_id}</b> &nbsp;|&nbsp; [{q_type}] &nbsp;|&nbsp; <b>Marks:</b> +{marks} &nbsp;|&nbsp; <i>{first_src}</i>"
                if source_count > 1:
                    header_line += f" <i>(+{source_count - 1} more papers)</i>"
                    
                card_elements.append(Paragraph(header_line, q_header_style))
                card_elements.append(Paragraph(f"<i>Category: {q.get('week')} &rsaquo; {q.get('subtopic')}</i>", meta_style))
                card_elements.append(Spacer(1, 3))
                
                # Question Paper Card Image
                card_rel = q.get('card_image')
                has_card = False
                h_pt = 0
                if card_rel:
                    card_full = os.path.join(BASE_DIR, card_rel)
                    if os.path.exists(card_full):
                        try:
                            with PILImage.open(card_full) as im:
                                iw, ih = im.size
                            scale = min(490.0 / iw, 500.0 / ih)
                            w_pt = iw * scale
                            h_pt = ih * scale
                            card_elements.append(Image(card_full, width=w_pt, height=h_pt))
                            card_elements.append(Spacer(1, 4))
                            has_card = True
                        except Exception:
                            pass
                            
                # Fallback text if card image was missing
                if not has_card:
                    stem = q.get('question_text', '').strip() or "[Refer to exam paper]"
                    safe_stem = escape(stem)
                    card_elements.append(Paragraph(safe_stem, q_stem_style))
                    
                # Official Answer
                correct_ans = q.get('correct_answer', [])
                if correct_ans:
                    ans_str = escape(", ".join(correct_ans))
                    if q_type in ["MCQ", "MSQ"]:
                        ans_line = f"<b>✔ Official Answer Key:</b> Option ({ans_str})"
                    else:
                        ans_line = f"<b>✔ Official Answer Key (NAT):</b> {ans_str}"
                    card_elements.append(Paragraph(ans_line, ans_style))
                    
                if q.get('explanation'):
                    exp_clean = escape(q['explanation'][:250])
                    card_elements.append(Paragraph(f"<b>Explanation:</b> {exp_clean}", meta_style))
                    
                card_elements.append(Spacer(1, 4))
                card_elements.append(HRFlowable(width="100%", thickness=0.4, color=colors.HexColor('#e2e8f0'), spaceAfter=8))
                
                # Keep compact cards together; let tall cards flow naturally
                if h_pt <= 320:
                    story.append(KeepTogether(card_elements))
                else:
                    for elem in card_elements:
                        story.append(elem)
                        
    print(f"Building PDF document: {OUTPUT_PDF}...")
    doc.build(story, canvasmaker=NumberedCanvas)
    print(f"Successfully generated PDF: {OUTPUT_PDF} ({os.path.getsize(OUTPUT_PDF) / (1024*1024):.2f} MB)")

if __name__ == "__main__":
    build_pdf()
