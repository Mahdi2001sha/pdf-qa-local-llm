"""Step 6 - Append every question and answer to logs/qa_log.csv."""
import csv
import threading
from datetime import datetime

from config import CSV_LOG_PATH

_FIELDS = ["timestamp", "pdf_version", "question", "answer", "pages"]
_lock = threading.Lock()


def log_qa(pdf_version: str, question: str, answer: str, pages: list[int]) -> None:
    with _lock:
        is_new = not CSV_LOG_PATH.exists() or CSV_LOG_PATH.stat().st_size == 0
        # utf-8-sig so Excel shows Persian text correctly
        with open(CSV_LOG_PATH, "a", newline="", encoding="utf-8-sig") as f:
            writer = csv.writer(f)
            if is_new:
                writer.writerow(_FIELDS)
            writer.writerow([
                datetime.now().isoformat(timespec="seconds"),
                pdf_version, question, answer, ", ".join(map(str, pages)),
            ])
