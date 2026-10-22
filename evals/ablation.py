"""Retrieval ablation: how much each stage adds.

    python -m evals.ablation
"""

from __future__ import annotations

import json
from copy import copy

from helix_rag.config import Settings
from helix_rag.index import load_or_build
from helix_rag.retrieval import Retriever

from .metrics import context_precision, context_recall, mean


def main() -> None:
    s = Settings()
    index = load_or_build(s)
    questions = json.loads((s.corpus_dir / "test_set.json").read_text())["queries"]
    k = 5

    def dense_only(q):
        return [cid for cid, _ in index.store.query(index.embedder.embed([q])[0], k)]

    def bm25_only(q):
        return [index.chunks[i].chunk_id for i, _ in index.bm25.top(q, k)]

    s_rrf = copy(s)
    s_rrf.reranker = "none"
    r_rrf = Retriever(index, s_rrf)
    r_full = Retriever(index, s)

    def rrf(q):
        return [c.chunk.chunk_id for c in r_rrf.retrieve(q).candidates[:k]]

    def rerank(q):
        return [c.chunk.chunk_id for c in r_full.retrieve(q).candidates[:k]]

    def full(q):
        return [c.chunk.chunk_id for c in r_full.retrieve(q).chunks]

    systems = [
        (f"Dense only (LSA), top-{k}", dense_only),
        (f"BM25 only, top-{k}", bm25_only),
        (f"Hybrid RRF, top-{k}", rrf),
        (f"Hybrid RRF + rerank, top-{k}", rerank),
        ("Hybrid RRF + rerank + document-aware cutoff", full),
    ]
    print("| retrieval | context precision | context recall | chunks / query |")
    print("|---|---|---|---|")
    for name, fn in systems:
        p, r, n = [], [], []
        for q in questions:
            ids = fn(q["query"])
            src = [index.chunk(i).source for i in ids]
            p.append(context_precision(src, q["expected_sources"]))
            r.append(context_recall(src, q["expected_sources"]))
            n.append(len(ids))
        print(f"| {name} | {mean(p):.3f} | {mean(r):.3f} | {mean(n):.1f} |")


if __name__ == "__main__":
    main()
