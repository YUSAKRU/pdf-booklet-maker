import os
import fitz
from pdf_booklet.exceptions import PDFCorruptedError, PDFEncryptedError, InvalidPDFPageError
from pdf_booklet.logger import get_logger

logger = get_logger()

class PDFValidator:
    """Validator for input PDF documents to detect corruption, encryption, and basic anomalies."""

    @staticmethod
    def validate(file_path: str) -> dict:
        """
        Validates the PDF at the given path.
        
        Args:
            file_path: Absolute path to the PDF file.
            
        Returns:
            dict: Metadata about the validated PDF.
            
        Raises:
            PDFCorruptedError: If the PDF is corrupted or unreadable.
            PDFEncryptedError: If the PDF is encrypted/DRM-protected.
            InvalidPDFPageError: If the PDF has no pages.
        """
        if not os.path.exists(file_path):
            logger.error("File not found", details={"file_path": file_path})
            raise FileNotFoundError(f"File not found: {file_path}")

        logger.info("Starting PDF validation", details={"file_path": file_path})
        
        try:
            doc = fitz.open(file_path)
        except Exception as e:
            logger.error("Failed to open PDF (corrupted)", details={"file_path": file_path, "error": str(e)})
            raise PDFCorruptedError(f"PDF file is corrupted or could not be read: {str(e)}")

        try:
            if doc.is_encrypted:
                logger.error("PDF is encrypted", details={"file_path": file_path})
                raise PDFEncryptedError("The PDF file is encrypted or DRM-protected.")
            
            page_count = len(doc)
            if page_count == 0:
                logger.error("PDF is empty", details={"file_path": file_path})
                raise InvalidPDFPageError("The PDF file contains no pages.")
                
            # Read page sizes to check for consistency/anomalies
            page_sizes = []
            for idx in range(page_count):
                try:
                    page = doc.load_page(idx)
                    rect = page.rect
                    page_sizes.append((rect.width, rect.height))
                except Exception as e:
                    logger.error("Failed to load page in PDF", details={"file_path": file_path, "page_index": idx, "error": str(e)})
                    raise PDFCorruptedError(f"Failed to load page {idx}: {str(e)}")

            # Log basic metadata
            metadata = {
                "file_path": file_path,
                "file_size_bytes": os.path.getsize(file_path),
                "page_count": page_count,
                "is_encrypted": doc.is_encrypted,
                "page_sizes": page_sizes,
            }
            logger.info("PDF validation completed successfully", details={
                "file_path": file_path,
                "page_count": page_count,
                "file_size_bytes": metadata["file_size_bytes"]
            })
            return metadata
            
        finally:
            doc.close()
