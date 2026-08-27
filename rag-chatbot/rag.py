import re
from dataclasses import dataclass
from typing import Iterable

import numpy as np


def chunk_text(text: str, chunk_size: int = 400, overlap: int = 80) -> list[str]:
    text = re.sub(r"\s+", " ", text).strip()
    if not text:
        return []
    words = text.split()
    step = max(1, chunk_size - overlap)
    chunks = []
    for i in range(0, len(words), step):
        piece = " ".join(words[i:i + chunk_size])
        if piece:
            chunks.append(piece)
        if i + chunk_size >= len(words):
            break
    return chunks


@dataclass
class Passage:
    source: str
    text: str


class RagIndex:
    def __init__(self, model_name: str = "sentence-transformers/all-MiniLM-L6-v2"):
        from sentence_transformers import SentenceTransformer
        self.model = SentenceTransformer(model_name)
        self.passages: list[Passage] = []
        self.embeddings: np.ndarray | None = None

    def add(self, source: str, text: str, chunk_size: int = 400, overlap: int = 80):
        for chunk in chunk_text(text, chunk_size, overlap):
            self.passages.append(Passage(source=source, text=chunk))

    def build(self):
        if not self.passages:
            self.embeddings = None
            return
        vecs = self.model.encode(
            [p.text for p in self.passages],
            normalize_embeddings=True,
            show_progress_bar=False,
        )
        self.embeddings = np.asarray(vecs, dtype=np.float32)

    def query(self, question: str, k: int = 4) -> list[tuple[Passage, float]]:
        if self.embeddings is None or not self.passages:
            return []
        q = self.model.encode([question], normalize_embeddings=True)
        q = np.asarray(q, dtype=np.float32)[0]
        scores = self.embeddings @ q
        top = np.argsort(-scores)[:k]
        return [(self.passages[i], float(scores[i])) for i in top]


def answer(question: str, hits: list[tuple[Passage, float]]) -> str:
    if not hits:
        return "I couldn't find anything relevant in the indexed documents."
    lines = [f"**Question:** {question}", "", "**Most relevant passages:**", ""]
    for i, (p, score) in enumerate(hits, 1):
        lines.append(f"{i}. _{p.source}_ (score {score:.2f})")
        lines.append(f"   > {p.text}")
        lines.append("")
    return "\n".join(lines)
