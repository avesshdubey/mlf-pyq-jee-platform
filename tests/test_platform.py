import json
import os
import unittest
import fitz

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

class TestMLFPlatform(unittest.TestCase):

    def test_questions_json_exists_and_valid(self):
        json_path = os.path.join(BASE_DIR, "data", "questions.json")
        self.assertTrue(os.path.exists(json_path), "data/questions.json must exist")
        with open(json_path, "r", encoding="utf-8") as f:
            questions = json.load(f)
        self.assertIsInstance(questions, list)
        self.assertGreaterEqual(len(questions), 200, "Should have extracted at least 200 unique questions")
        
        # Verify schema of each question
        required_fields = ["id", "question_type", "marks", "question_text", "options", "week", "subtopic", "source_papers"]
        for q in questions:
            for field in required_fields:
                self.assertIn(field, q, f"Question {q.get('id')} missing field: {field}")
            self.assertIn(q['week'], [
                "Week 1 - ML Foundations",
                "Week 2 - Mathematical Foundations",
                "Week 3 - Linear Algebra & Subspaces",
                "Week 4 - Regression & Eigenvalues"
            ], f"Invalid week assignment: {q['week']}")

    def test_pdf_document_exists_and_readable(self):
        pdf_path = os.path.join(BASE_DIR, "mlf_questions_categorized.pdf")
        self.assertTrue(os.path.exists(pdf_path), "mlf_questions_categorized.pdf must exist")
        self.assertLess(os.path.getsize(pdf_path), 50 * 1024 * 1024, "PDF size must be optimized under 50MB")
        doc = fitz.open(pdf_path)
        self.assertGreater(len(doc), 50, "PDF must have over 50 pages of categorized questions")
        doc.close()

    def test_html_and_assets_exist(self):
        index_html = os.path.join(BASE_DIR, "index.html")
        css_file = os.path.join(BASE_DIR, "css", "jee_style.css")
        js_file = os.path.join(BASE_DIR, "js", "jee_app.js")
        data_js = os.path.join(BASE_DIR, "data", "questions_data.js")

        self.assertTrue(os.path.exists(index_html), "index.html must exist")
        self.assertTrue(os.path.exists(css_file), "css/jee_style.css must exist")
        self.assertTrue(os.path.exists(js_file), "js/jee_app.js must exist")
        self.assertTrue(os.path.exists(data_js), "data/questions_data.js must exist")

    def test_category_coverage(self):
        json_path = os.path.join(BASE_DIR, "data", "questions.json")
        with open(json_path, "r", encoding="utf-8") as f:
            questions = json.load(f)
        
        weeks = set(q['week'] for q in questions)
        self.assertEqual(len(weeks), 4, "All 4 weeks must be present in the dataset")

if __name__ == "__main__":
    unittest.main()
