from pypdf import PdfReader
from io import BytesIO
from core.error_handlers import ProcessingError
from core.config import settings
import logging

logger = logging.getLogger(__name__)


def extract_text_from_pdf(file_bytes: bytes, filename: str) -> dict:
    """
    Extract text from a PDF file using pypdf (pure Python).
    Returns: { text: str, title: str, page_count: int }
    """
    # Check file size
    size_mb = len(file_bytes) / (1024 * 1024)
    if size_mb > settings.MAX_PDF_SIZE_MB:
        raise ProcessingError(
            f"PDF too large ({size_mb:.1f}MB). Maximum size is {settings.MAX_PDF_SIZE_MB}MB."
        )

    try:
        reader = PdfReader(BytesIO(file_bytes))
    except Exception as e:
        logger.error(f"Failed to open PDF: {e}")
        raise ProcessingError("Failed to open PDF. The file may be corrupted.")

    if len(reader.pages) == 0:
        raise ProcessingError("The PDF has no pages.")

    pages_text = []
    for page in reader.pages:
        text = page.extract_text()
        if text and text.strip():
            pages_text.append(text.strip())

    if not pages_text:
        raise ProcessingError(
            "No readable text found in the PDF. It may be scanned or image-based."
        )

    full_text = "\n\n".join(pages_text)

    if len(full_text.strip()) < 50:
        raise ProcessingError(
            "PDF text too short to generate meaningful content."
        )

    # Use filename without extension as title
    title = filename.rsplit(".", 1)[0] if "." in filename else filename

    return {
        "text": full_text,
        "title": title,
        "page_count": len(pages_text),
    }
