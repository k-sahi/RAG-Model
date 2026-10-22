"""Grid search for the local reranker weights, with 2-fold cross-validation.

    python -m evals.tune

Features are computed once per (question, candidate); each weight vector then ranks
documents by their best chunk. We report doc-level hit@1 and recall@3 on the full set
and, for the weights picked on each half, on the other (held-out) half.
"""

from __future__ import annotations

import itertools
import json

from helix_rag.config import Settings
from helix_rag.index import load_or_build
from helix_rag.retrieval import Retriever

FEATURES = ("coverage", "dense", "title", "rrf", "doc_dense")
GRID = (0.0, 0.1, 0.2, 0.3, 0.4)


def collect(retriever: Retriever, questions: list[dict]) -> list[tuple[set, list[tuple[str, tuple]]]]:
    idx = retriever.index
    data = []
    for q in questions:
        cands = retriever.candidates([q["query"]])
        top = cands[0].rrf
        qv = idx.embedder.embed([q["query"]])[0]
        doc_sims = idx.doc_vectors @ qv
        rows = []
        for c in cands:
            pos = idx.by_id[c.chunk.chunk_id]
            rows.append(
                (
                    c.chunk.source,
                    (
                        retriever._coverage(q["query"], pos),
                        max(c.dense, 0.0),
                        retriever._coverage(q["query"], pos, title_only=True),
                        c.rrf / top,
                        max(float(doc_sims[idx.doc_pos[c.chunk.source]]), 0.0),
                    ),
                )
            )
        data.append((set(q["expected_sources"]), rows))
    return data


def score(weights, data) -> tuple[float, float]:
    h1 = r3 = 0.0
    for expected, rows in data:
        best: dict[str, float] = {}
        for src, f in rows:
            s = sum(w * x for w, x in zip(weights, f))
            best[src] = max(best.get(src, 0.0), s)
        order = sorted(best, key=best.get, reverse=True)
        h1 += order[0] in expected
        r3 += len(expected & set(order[:3])) / len(expected)
    return round(h1 / len(data), 3), round(r3 / len(data), 3)


def main() -> None:
    s = Settings()
    retriever = Retriever(load_or_build(s), s)
    questions = json.loads((s.corpus_dir / "test_set.json").read_text())["queries"]
    data = collect(retriever, questions)
    grid = [w for w in itertools.product(GRID, repeat=len(FEATURES)) if sum(w) > 0]

    current = tuple(Retriever.WEIGHTS[f] for f in FEATURES)
    print("features:", FEATURES)
    print("current weights", current, "hit@1, recall@3 =", score(current, data))
    ranked = sorted(grid, key=lambda w: sum(score(w, data)), reverse=True)
    print("best on full set:", ranked[0], score(ranked[0], data))
    for fold in (0, 1):
        train = [d for i, d in enumerate(data) if i % 2 == fold]
        test = [d for i, d in enumerate(data) if i % 2 != fold]
        w = max(grid, key=lambda w: sum(score(w, train)))
        print(f"fold {fold}: tuned {w} train {score(w, train)} held-out {score(w, test)}; current weights held-out {score(current, test)}")


if __name__ == "__main__":
    main()
