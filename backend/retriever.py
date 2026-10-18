"""Step 4 - Find the chunks most relevant to a question.

Uses embeddings (semantic search). If the embedding model is not available,
it automatically falls back to TF-IDF keyword search so the app still works.
"""
import numpy as np
from sklearn.feature_extraction.text import TfidfVectorizer

import llm_client
from config import EMBED_BATCH_SIZE, TOP_K


class Retriever:
    def __init__(self, chunks: list[dict]):
        self.chunks = chunks
        self.mode = "embeddings"
        texts = [c["text"] for c in chunks]
        try:
            vectors = []
            for i in range(0, len(texts), EMBED_BATCH_SIZE):
                vectors.extend(llm_client.embed(texts[i:i + EMBED_BATCH_SIZE]))
            self.matrix = self._normalize(np.array(vectors, dtype="float32"))
        except Exception:
            self.mode = "tfidf"
            self.vectorizer = TfidfVectorizer(analyzer="char_wb", ngram_range=(2, 4))
            self.matrix = self.vectorizer.fit_transform(texts)

    @staticmethod
    def _normalize(m: np.ndarray) -> np.ndarray:
        norms = np.linalg.norm(m, axis=1, keepdims=True)
        return m / np.clip(norms, 1e-9, None)

    def search(self, question: str, k: int = TOP_K) -> list[dict]:
        if self.mode == "embeddings":
            q = self._normalize(np.array(llm_client.embed([question]), dtype="float32"))
            scores = (self.matrix @ q.T).ravel()
        else:
            q = self.vectorizer.transform([question])
            scores = (self.matrix @ q.T).toarray().ravel()
        top = np.argsort(scores)[::-1][:k]
        return [self.chunks[i] for i in sorted(top)]  # keep document order
