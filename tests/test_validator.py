import unittest
import os
import tempfile
import fitz
from pdf_booklet.validator import PDFValidator
from pdf_booklet.exceptions import BookletError, PDFCorruptedError, PDFEncryptedError, InvalidPDFPageError

class TestPDFValidator(unittest.TestCase):
    def setUp(self):
        self.temp_dir = tempfile.TemporaryDirectory()
        
    def tearDown(self):
        self.temp_dir.cleanup()

    def create_mock_pdf(self, filename, page_count, width=595, height=842):
        path = os.path.join(self.temp_dir.name, filename)
        doc = fitz.open()
        for i in range(page_count):
            page = doc.new_page(width=width, height=height)
            page.insert_text((50, 50), f"Page {i+1}")
        doc.save(path)
        doc.close()
        return path

    def test_validation_successful(self):
        # Create a mock 4-page PDF
        pdf_path = self.create_mock_pdf("valid.pdf", 4)
        
        metadata = PDFValidator.validate(pdf_path)
        self.assertEqual(metadata["page_count"], 4)
        self.assertFalse(metadata["is_encrypted"])
        self.assertEqual(len(metadata["page_sizes"]), 4)
        self.assertEqual(metadata["page_sizes"][0], (595.0, 842.0))

    def test_validation_empty_pdf(self):
        # Create an empty 0-byte file (unreadable/corrupted)
        pdf_path = os.path.join(self.temp_dir.name, "empty.pdf")
        with open(pdf_path, "wb") as f:
            f.write(b"")
        
        with self.assertRaises(PDFCorruptedError):
            PDFValidator.validate(pdf_path)

    def test_validation_file_not_found(self):
        with self.assertRaises(FileNotFoundError):
            PDFValidator.validate("non_existent_file.pdf")

    def test_validation_corrupted_file(self):
        # Create a corrupted PDF by writing garbage bytes
        pdf_path = os.path.join(self.temp_dir.name, "corrupted.pdf")
        with open(pdf_path, "wb") as f:
            f.write(b"NOT A PDF FILE %PDF-1.4 garbage garbage")
            
        with self.assertRaises(BookletError):
            PDFValidator.validate(pdf_path)

if __name__ == "__main__":
    unittest.main()
