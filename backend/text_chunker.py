"""Step 3 - Split page text into small overlapping chunks."""
from config import CHUNK_OVERLAP, CHUNK_SIZE


def _split(text: str, size: int, overlap: int) -> list[str]:
    pieces, start, n = [], 0, len(text)
    while start < n:
        end = min(start + size, n)
        if end < n:  # try to cut on a line break / space instead of mid-word
            cut = max(text.rfind("\n", start + size // 2, end),
                      text.rfind(" ", start + size // 2, end))
            if cut != -1:
                end = cut
        piece = text[start:end].strip()
        if piece:
            pieces.append(piece)
        if end >= n:
            break
        start = max(end - overlap, start + 1)
    return pieces


def chunk_pages(pages: list[dict]) -> list[dict]:
    """Return [{'id': 0, 'page': 1, 'text': '...'}, ...] keeping the page number."""
    chunks = []
    for page in pages:
        for piece in _split(page["text"], CHUNK_SIZE, CHUNK_OVERLAP):
            chunks.append({"id": len(chunks), "page": page["page"], "text": piece})
    return chunks
