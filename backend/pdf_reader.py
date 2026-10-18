"""Step 2 - Read the text of a typed (digital) PDF, page by page."""
import re
from pathlib import Path

import pymupdf  # PyMuPDF


class PDFReadError(Exception):
    """Raised when text cannot be extracted."""


def _clean(text: str) -> str:
    text = text.replace("\u00a0", " ")
    text = re.sub(r"[ \t]+", " ", text)
    text = re.sub(r"\n{3,}", "\n\n", text)
    return text.strip()


def read_pdf(path: Path) -> list[dict]:
    """Return [{'page': 1, 'text': '...'}, ...] (empty pages are skipped)."""
    try:
        doc = pymupdf.open(path)
    except Exception as exc:
        raise PDFReadError("Could not open the PDF. The file may be damaged.") from exc

    if doc.needs_pass:
        raise PDFReadError("The PDF is password protected.")

    pages = []
    for number, page in enumerate(doc, start=1):
        text = _clean(page.get_text("text"))
        if text:
            pages.append({"page": number, "text": text})
    doc.close()

    if not pages:
        raise PDFReadError(
            "No text found. This looks like a scanned PDF, "
            "and only typed PDFs are supported for now."
        )
    return pages
