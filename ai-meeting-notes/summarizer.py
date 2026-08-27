import re
from collections import Counter
from math import log

STOPWORDS = {
    "the", "a", "an", "and", "or", "but", "if", "so", "of", "in", "on", "at", "to",
    "for", "with", "by", "is", "are", "was", "were", "be", "been", "being", "am",
    "it", "its", "this", "that", "these", "those", "i", "you", "we", "they", "he",
    "she", "them", "us", "our", "your", "their", "as", "from", "have", "has", "had",
    "do", "does", "did", "will", "would", "should", "could", "can", "may", "might",
    "not", "no", "yes", "there", "here", "what", "which", "who", "when", "where",
    "why", "how", "than", "then", "just", "also", "into", "about", "up", "down",
    "out", "over", "under", "again", "more", "some", "any", "all", "each", "very",
    "too", "so", "one", "two", "like", "get", "got", "go", "going",
}

SENTENCE_SPLIT = re.compile(r"(?<=[.!?])\s+(?=[A-Z0-9])")
WORD_RE = re.compile(r"[A-Za-z][A-Za-z'-]+")

ACTION_TRIGGERS = [
    r"\bwe (?:will|'ll|need to|should|must|are going to|have to)\b",
    r"\bi (?:will|'ll|need to|should|must|am going to|have to)\b",
    r"\byou (?:will|'ll|need to|should|must|are going to|have to)\b",
    r"\blet's\b",
    r"\baction item\b",
    r"\bto[- ]?do\b",
    r"\bfollow[- ]?up\b",
    r"\bnext step\b",
    r"\bassigned? to\b",
    r"\bby (?:monday|tuesday|wednesday|thursday|friday|saturday|sunday|tomorrow|end of (?:day|week|month))\b",
    r"\bdeadline\b",
    r"\bowner:?\b",
    r"\bdue\b",
]
ACTION_RE = re.compile("|".join(ACTION_TRIGGERS), re.I)


def split_sentences(text: str) -> list[str]:
    text = re.sub(r"\s+", " ", text).strip()
    if not text:
        return []
    parts = SENTENCE_SPLIT.split(text)
    return [p.strip() for p in parts if p.strip()]


def tokenize(text: str) -> list[str]:
    return [w.lower() for w in WORD_RE.findall(text) if w.lower() not in STOPWORDS]


def score_sentences(sentences: list[str]) -> list[float]:
    docs = [tokenize(s) for s in sentences]
    df: Counter = Counter()
    for d in docs:
        df.update(set(d))
    n = len(docs) or 1
    scores = []
    for words in docs:
        if not words:
            scores.append(0.0)
            continue
        tf = Counter(words)
        score = sum(tf[w] * log((n + 1) / (df[w] + 1)) + 1 for w in tf)
        scores.append(score / (len(words) ** 0.5))
    return scores


def extractive_summary(text: str, num_sentences: int = 6) -> list[str]:
    sentences = split_sentences(text)
    if len(sentences) <= num_sentences:
        return sentences
    scores = score_sentences(sentences)
    ranked = sorted(range(len(sentences)), key=lambda i: scores[i], reverse=True)
    chosen = sorted(ranked[:num_sentences])
    return [sentences[i] for i in chosen]


def action_items(text: str) -> list[str]:
    seen: list[str] = []
    for s in split_sentences(text):
        if ACTION_RE.search(s):
            clean = s.strip()
            if clean not in seen:
                seen.append(clean)
    return seen
