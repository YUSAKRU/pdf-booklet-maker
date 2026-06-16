import unittest
import os
import tempfile
import fitz
from pdf_booklet.engine import BookletEngine
from pdf_booklet.exceptions import PDFCorruptedError

class TestBookletEngine(unittest.TestCase):
    def setUp(self):
        self.temp_dir = tempfile.TemporaryDirectory()
        self.engine = BookletEngine()
        
    def tearDown(self):
        self.temp_dir.cleanup()

    def create_mock_pdf(self, filename, page_count, width=595, height=842):
        path = os.path.join(self.temp_dir.name, filename)
        doc = fitz.open()
        for i in range(page_count):
            page = doc.new_page(width=width, height=height)
            # Insert distinct text to trace page numbers in the output
            page.insert_text((100, 100), f"PAGE_ID_{i+1}", fontsize=12)
        doc.save(path)
        doc.close()
        return path

    def test_imposition_4_pages(self):
        # 4 pages -> 1 sheet, no padding
        pdf_path = self.create_mock_pdf("input_4.pdf", 4)
        output_dir = os.path.join(self.temp_dir.name, "out")
        
        result = self.engine.make_booklet(pdf_path, output_dir)
        
        self.assertEqual(result["status"], "success")
        self.assertEqual(result["original_pages"], 4)
        self.assertEqual(result["padded_pages"], 4)
        self.assertEqual(result["sheets_count"], 1)
        self.assertEqual(result["padding_applied"], 0)
        
        # Verify output files exist
        self.assertTrue(os.path.exists(result["front_pdf"]))
        self.assertTrue(os.path.exists(result["back_pdf"]))
        
        # Verify mapping contents
        # Front should have: Page 4 (left), Page 1 (right)
        front_doc = fitz.open(result["front_pdf"])
        self.assertEqual(len(front_doc), 1)
        front_text = front_doc[0].get_text()
        self.assertIn("PAGE_ID_4", front_text)
        self.assertIn("PAGE_ID_1", front_text)
        
        # Back should have: Page 2 (left), Page 3 (right)
        back_doc = fitz.open(result["back_pdf"])
        self.assertEqual(len(back_doc), 1)
        back_text = back_doc[0].get_text()
        self.assertIn("PAGE_ID_2", back_text)
        self.assertIn("PAGE_ID_3", back_text)
        
        front_doc.close()
        back_doc.close()

    def test_imposition_with_padding(self):
        # 3 pages -> should pad to 4 (1 blank page added)
        pdf_path = self.create_mock_pdf("input_3.pdf", 3)
        output_dir = os.path.join(self.temp_dir.name, "out")
        
        result = self.engine.make_booklet(pdf_path, output_dir)
        
        self.assertEqual(result["padded_pages"], 4)
        self.assertEqual(result["padding_applied"], 1)
        
        # Front should have Page 4 (blank, so no PAGE_ID_4 text) and Page 1
        front_doc = fitz.open(result["front_pdf"])
        front_text = front_doc[0].get_text()
        self.assertNotIn("PAGE_ID_4", front_text)
        self.assertIn("PAGE_ID_1", front_text)
        
        # Back should have Page 2 and Page 3
        back_doc = fitz.open(result["back_pdf"])
        back_text = back_doc[0].get_text()
        self.assertIn("PAGE_ID_2", back_text)
        self.assertIn("PAGE_ID_3", back_text)
        
        front_doc.close()
        back_doc.close()

    def test_imposition_8_pages(self):
        # 8 pages -> 2 sheets
        pdf_path = self.create_mock_pdf("input_8.pdf", 8)
        output_dir = os.path.join(self.temp_dir.name, "out")
        
        result = self.engine.make_booklet(pdf_path, output_dir)
        self.assertEqual(result["sheets_count"], 2)
        
        # Sheet 1 (j=0): Front: 8 | 1, Back: 2 | 7
        # Sheet 2 (j=1): Front: 6 | 3, Back: 4 | 5
        front_doc = fitz.open(result["front_pdf"])
        self.assertEqual(len(front_doc), 2)
        
        sheet1_front = front_doc[0].get_text()
        self.assertIn("PAGE_ID_8", sheet1_front)
        self.assertIn("PAGE_ID_1", sheet1_front)
        
        sheet2_front = front_doc[1].get_text()
        self.assertIn("PAGE_ID_6", sheet2_front)
        self.assertIn("PAGE_ID_3", sheet2_front)
        
        back_doc = fitz.open(result["back_pdf"])
        self.assertEqual(len(back_doc), 2)
        
        sheet1_back = back_doc[0].get_text()
        self.assertIn("PAGE_ID_2", sheet1_back)
        self.assertIn("PAGE_ID_7", sheet1_back)
        
        sheet2_back = back_doc[1].get_text()
        self.assertIn("PAGE_ID_4", sheet2_back)
        self.assertIn("PAGE_ID_5", sheet2_back)
        
        front_doc.close()
        back_doc.close()

    def test_imposition_with_gutter_and_creep(self):
        # Ensure that running with gutter and creep does not throw errors
        pdf_path = self.create_mock_pdf("input_gutter_creep.pdf", 8)
        output_dir = os.path.join(self.temp_dir.name, "out")
        
        result = self.engine.make_booklet(pdf_path, output_dir, base_gutter=10.0, creep_step=1.5)
        self.assertEqual(result["status"], "success")

if __name__ == "__main__":
    unittest.main()
