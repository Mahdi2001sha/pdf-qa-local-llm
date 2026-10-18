"""Step 1 - Receive the uploaded PDF, validate it, and save a versioned copy."""
import re
from datetime import datetime
from pathlib import Path

from config import MAX_UPLOAD_MB, PDF_LOG_DIR


class PDFLoadError(Exception):
    """Raised when the uploaded file is not usable."""


def _safe_name(filename: str) -> str:
    stem = Path(filename or "document").stem
    stem = re.sub(r"[^\w\-]+", "_", stem, flags=re.UNICODE).strip("_")
    return stem[:60] or "document"


def save_pdf(file_bytes: bytes, original_name: str) -> tuple[str, Path]:
    """Validate and store the PDF. Returns (version_id, saved_path)."""
    if not file_bytes:
        raise PDFLoadError("The file is empty.")
    if len(file_bytes) > MAX_UPLOAD_MB * 1024 * 1024:
        raise PDFLoadError(f"The file is larger than {MAX_UPLOAD_MB} MB.")
    if not file_bytes.lstrip().startswith(b"%PDF"):
        raise PDFLoadError("This does not look like a PDF file.")

    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    version_id = f"{timestamp}_{_safe_name(original_name)}"
    path = PDF_LOG_DIR / f"{version_id}.pdf"
    path.write_bytes(file_bytes)
    return version_id, path
