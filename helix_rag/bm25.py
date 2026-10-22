"""Okapi BM25 over pre-tokenised chunks."""

from __future__ import annotations

import math
from collections import Counter

from .text import tokenize


class BM25:
    def __init__(self, docs: list[str], k1: float = 1.4, b: float = 0.75):
        self.k1, self.b = k1, b
        self.tfs = [Counter(tokenize(d)) for d in docs]
        self.lengths = [sum(tf.values()) for tf in self.tfs]
        self.avgdl = sum(self.lengths) / max(len(self.lengths), 1)
        df: Counter = Counter()
        for tf in self.tfs:
            df.update(tf.keys())
        n = len(docs)
        self.idf = {t: math.log(1 + (n - f + 0.5) / (f + 0.5)) for t, f in df.items()}

    def scores(self, query: str) -> list[float]:
        q = tokenize(query)
        out = []
        for tf, dl in zip(self.tfs, self.lengths):
            s = 0.0
            norm = self.k1 * (1 - self.b + self.b * dl / self.avgdl)
            for t in q:
                f = tf.get(t)
                if f:
                    s += self.idf[t] * f * (self.k1 + 1) / (f + norm)
            out.append(s)
        return out

    def top(self, query: str, n: int) -> list[tuple[int, float]]:
        s = self.scores(query)
        ranked = sorted(range(len(s)), key=lambda i: s[i], reverse=True)
        return [(i, s[i]) for i in ranked[:n] if s[i] > 0]
