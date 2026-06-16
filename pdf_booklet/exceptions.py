class BookletError(Exception):
    """Base exception for pdf-booklet-maker."""
    pass

class PDFCorruptedError(BookletError):
    """Raised when the input PDF is corrupted or unreadable."""
    pass

class PDFEncryptedError(BookletError):
    """Raised when the input PDF is encrypted or DRM-protected."""
    pass

class InvalidPDFPageError(BookletError):
    """Raised when the PDF has no pages or has page dimensions that cannot be processed."""
    pass

class LayoutError(BookletError):
    """Raised when booklet imposition layout calculations fail."""
    pass
