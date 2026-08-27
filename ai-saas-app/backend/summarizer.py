import re
from collections import Counter
from math import log

STOPWORDS = {
    "the", "a", "an", "and", "or", "of", "in", "on", "to", "for", "is", "are",
    "was", "were", "be", "been", "it", "this", "that", "as", "with", "by",
    "from", "at", "we", "you", "they", "i", "he", "she", "have", "has", "had",
}

_SENT = re.compile(r"(?<=[.!?])\s+(?=[A-Z0-9])")
_WORD = re.compile(r"[A-Za-z][A-Za-z']+")


def _sentences(text: str) -> list[str]:
    text = re.sub(r"\s+", " ", text).strip()
    return [s.strip() for s in _SENT.split(text) if s.strip()]


def _tokens(text: str) -> list[str]:
    return [w.lower() for w in _WORD.findall(text) if w.lower() not in STOPWORDS]


def summarize(text: str, n: int = 5) -> list[str]:
    sents = _sentences(text)
    if len(sents) <= n:
        return sents
    docs = [_tokens(s) for s in sents]
    df = Counter()
    for d in docs:
        df.update(set(d))
    scores = []
    total = len(docs)
    for words in docs:
        if not words:
            scores.append(0.0)
            continue
        tf = Counter(words)
        s = sum(tf[w] * log((total + 1) / (df[w] + 1)) + 1 for w in tf)
        scores.append(s / (len(words) ** 0.5))
    top = sorted(sorted(range(len(sents)), key=lambda i: -scores[i])[:n])
    return [sents[i] for i in top]
