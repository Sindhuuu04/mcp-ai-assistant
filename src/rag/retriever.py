"""Day 16 baseline: lexical (TF-IDF) retrieval. Only plural normalization (no real stemming, no synonyms),
so true paraphrase failures stay visible and can be compared against semantic search (Day 17)."""
import math, re
from collections import Counter

STOPWORDS = {"a", "an", "the", "is", "are", "of", "to", "in", "on", "for", "and", "or", "do", "does",
             "i", "my", "we", "can", "be", "must", "what", "how", "when", "who", "if", "it", "at",
             "by", "with", "that", "this", "as", "from", "should", "get", "per", "much", "many"}


def _singular(t: str) -> str:
    return t[:-1] if len(t) > 3 and t.endswith("s") and not t.endswith("ss") else t


def tokenize(text: str) -> list[str]:
    return [_singular(t) for t in re.findall(r"[a-z0-9]+", text.lower()) if t not in STOPWORDS]


class KeywordRetriever:
    def __init__(self, chunks: list[dict]):
        self.chunks = chunks
        self.tfs = [Counter(tokenize(c["text"])) for c in chunks]
        n = len(chunks)
        df = Counter(t for tf in self.tfs for t in tf)
        self.idf = {t: math.log((n + 1) / (d + 1)) + 1 for t, d in df.items()}

    def search(self, query: str, k: int = 3) -> list[dict]:
        q = tokenize(query)
        scored = []
        for chunk, tf in zip(self.chunks, self.tfs):
            s = sum(tf[t] * self.idf[t] for t in q if t in tf)
            if s > 0:
                scored.append({**chunk, "score": round(s, 4)})
        scored.sort(key=lambda r: (-r["score"], r["chunk_id"]))   # deterministic tie-break
        return scored[:k]