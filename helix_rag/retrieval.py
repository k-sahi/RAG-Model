"""Hybrid retrieval: dense + BM25, fused with reciprocal rank fusion, then reranked,
cut adaptively, and checked against a confidence floor before anything is generated.

    query ──► [rewrite] ──► dense top-N ─┐
                       └──► BM25 top-N ──┴─► RRF ─► rerank ─► relative cutoff ─► abstain?
"""

from __future__ import annotations

import logging
import math
from dataclasses import dataclass, field

from .config import Settings
from .documents import Chunk
from .index import Index
from .llm import ChatModel, LLMError, parse_json
from .text import tokenize

log = logging.getLogger(__name__)


@dataclass
class Scored:
    chunk: Chunk
    score: float = 0.0  # final (reranked) score, 0..1
    rrf: float = 0.0
    dense: float = 0.0
    bm25: float = 0.0
    coverage: float = 0.0  # IDF-weighted share of query terms present in the chunk
    doc_dense: float = 0.0  # cosine between the query and the whole source document
    dense_rank: int | None = None
    bm25_rank: int | None = None

    def to_dict(self) -> dict:
        return {
            "chunk_id": self.chunk.chunk_id,
            "source": self.chunk.source,
            "section": self.chunk.section,
            "score": round(self.score, 4),
            "rrf": round(self.rrf, 5),
            "dense": round(self.dense, 4),
            "bm25": round(self.bm25, 3),
            "coverage": round(self.coverage, 3),
            "doc_dense": round(self.doc_dense, 4),
        }


@dataclass
class RetrievalResult:
    query: str
    chunks: list[Scored]  # what goes to the generator
    candidates: list[Scored] = field(default_factory=list)  # everything after fusion
    queries: list[str] = field(default_factory=list)  # original + rewrites
    confidence: float = 0.0
    abstained: bool = False

    @property
    def sources(self) -> list[str]:
        return list(dict.fromkeys(s.chunk.source for s in self.chunks))


def rrf_fuse(rankings: list[list[str]], k: int = 60) -> dict[str, float]:
    """Reciprocal rank fusion: score(d) = sum over rankings of 1 / (k + rank)."""
    fused: dict[str, float] = {}
    for ranking in rankings:
        for rank, cid in enumerate(ranking, start=1):
            fused[cid] = fused.get(cid, 0.0) + 1.0 / (k + rank)
    return fused


REWRITE_SYSTEM = (
    "You rewrite search queries for a B2B SaaS support knowledge base (product docs, "
    "internal runbooks, resolved tickets). Return JSON: {\"queries\": [..]} with up to 2 "
    "alternative phrasings that use the vocabulary the documentation would use (feature "
    "names, settings paths, error codes). Do not answer the question."
)

RERANK_SYSTEM = (
    "You judge whether passages help answer a question. For each passage id, give an "
    "integer 0-10 (10 = directly answers it, 0 = irrelevant). Return JSON only: "
    "{\"scores\": {\"<id>\": <int>, ...}}"
)


class Retriever:
    def __init__(self, index: Index, settings: Settings | None = None, llm: ChatModel | None = None):
        self.index = index
        self.s = settings or Settings()
        self.llm = llm
        self._token_sets = [set(tokenize(c.index_text)) for c in index.chunks]
        self._title_sets = [set(tokenize(f"{c.title} {c.section}")) for c in index.chunks]

    # ------------------------------------------------------------------ candidates

    def _rewrite(self, query: str) -> list[str]:
        if not (self.s.query_rewrite and self.llm):
            return [query]
        try:
            alts = parse_json(self.llm.complete(REWRITE_SYSTEM, query)).get("queries", [])
        except (LLMError, ValueError) as exc:
            log.warning("Query rewrite failed, using the original query: %s", exc)
            return [query]
        return [query] + [q for q in alts if isinstance(q, str) and q.strip()][:2]

    def candidates(self, queries: list[str]) -> list[Scored]:
        n = self.s.candidates
        rankings: list[list[str]] = []
        dense_best: dict[str, float] = {}
        bm25_best: dict[str, float] = {}
        dense_rank: dict[str, int] = {}
        bm25_rank: dict[str, int] = {}
        for q in queries:
            qv = self.index.embedder.embed([q])[0]
            dense = self.index.store.query(qv, n)
            rankings.append([cid for cid, _ in dense])
            for r, (cid, sim) in enumerate(dense, 1):
                dense_best[cid] = max(dense_best.get(cid, -1.0), sim)
                dense_rank[cid] = min(dense_rank.get(cid, r), r)
            lexical = self.index.bm25.top(q, n)
            rankings.append([self.index.chunks[i].chunk_id for i, _ in lexical])
            for r, (i, sc) in enumerate(lexical, 1):
                cid = self.index.chunks[i].chunk_id
                bm25_best[cid] = max(bm25_best.get(cid, 0.0), sc)
                bm25_rank[cid] = min(bm25_rank.get(cid, r), r)

        fused = rrf_fuse(rankings, self.s.rrf_k)
        out = [
            Scored(
                chunk=self.index.chunk(cid),
                rrf=score,
                dense=dense_best.get(cid, 0.0),
                bm25=bm25_best.get(cid, 0.0),
                dense_rank=dense_rank.get(cid),
                bm25_rank=bm25_rank.get(cid),
            )
            for cid, score in fused.items()
        ]
        out.sort(key=lambda s: s.rrf, reverse=True)
        return out

    # ------------------------------------------------------------------ reranking

    def _coverage(self, query: str, chunk_pos: int, title_only: bool = False) -> float:
        terms = set(tokenize(query))
        if not terms:
            return 0.0
        idf = self.index.bm25.idf
        default = max(idf.values()) if idf else 1.0
        target = self._title_sets[chunk_pos] if title_only else self._token_sets[chunk_pos]
        total = sum(idf.get(t, default) for t in terms)
        hit = sum(idf.get(t, default) for t in terms if t in target)
        return hit / total if total else 0.0

    # Feature weights for the local reranker. Chosen with a grid search on the eval
    # set and checked with 2-fold cross-validation (see eval-report.md); the held-out
    # folds lose little, so the weights are not just memorising the 50 questions.
    WEIGHTS = {"coverage": 0.15, "dense": 0.15, "title": 0.20, "rrf": 0.20, "doc_dense": 0.30}

    def rerank_local(self, query: str, cands: list[Scored]) -> list[Scored]:
        """Linear mix of chunk evidence (term coverage, cosine, heading match, fused
        rank) and document evidence (query vs whole document). Most features are
        absolute, so scores are comparable across queries and the abstain threshold
        means something; a purely rank-based score cannot do that."""
        if not cands:
            return cands
        w = self.WEIGHTS
        top_rrf = cands[0].rrf
        qv = self.index.embedder.embed([query])[0]
        doc_sims = self.index.doc_vectors @ qv
        for c in cands:
            pos = self.index.by_id[c.chunk.chunk_id]
            c.coverage = self._coverage(query, pos)
            c.doc_dense = float(doc_sims[self.index.doc_pos[c.chunk.source]])
            c.score = (
                w["coverage"] * c.coverage
                + w["dense"] * max(c.dense, 0.0)
                + w["title"] * self._coverage(query, pos, title_only=True)
                + w["rrf"] * (c.rrf / top_rrf)
                + w["doc_dense"] * max(c.doc_dense, 0.0)
            )
        return sorted(cands, key=lambda c: c.score, reverse=True)

    def rerank_llm(self, query: str, cands: list[Scored], limit: int = 15) -> list[Scored]:
        head = self.rerank_local(query, cands)[:limit]
        passages = "\n\n".join(
            f"<passage id=\"{i}\" source=\"{c.chunk.source}\">\n{c.chunk.index_text[:1200]}\n</passage>"
            for i, c in enumerate(head)
        )
        try:
            scores = parse_json(self.llm.complete(RERANK_SYSTEM, f"Question: {query}\n\n{passages}"))["scores"]
        except (LLMError, ValueError, KeyError) as exc:
            log.warning("LLM rerank failed, keeping local scores: %s", exc)
            return head
        for i, c in enumerate(head):
            llm_score = float(scores.get(str(i), 0)) / 10.0
            c.score = 0.8 * llm_score + 0.2 * c.score
        return sorted(head, key=lambda c: c.score, reverse=True)

    # ------------------------------------------------------------------ public

    def select(self, ranked: list[Scored]) -> list[Scored]:
        """Document-aware adaptive cutoff.

        1. Score each document by its best chunk and keep documents within
           `relative_cutoff` of the best document (at most `max_docs`). A fixed top-k
           pads easy single-document questions with loosely related documents, which
           hurts precision and gives the generator distractors.
        2. From each kept document take up to `per_doc` chunks that score within
           `chunk_cutoff` of that document's best chunk, so a hit on one section also
           brings the neighbouring sections that usually complete the answer.
        """
        if not ranked:
            return []
        by_doc: dict[str, list[Scored]] = {}
        for c in ranked:
            by_doc.setdefault(c.chunk.source, []).append(c)
        doc_order = sorted(by_doc, key=lambda d: by_doc[d][0].score, reverse=True)
        best = by_doc[doc_order[0]][0].score
        kept_docs = [d for d in doc_order if by_doc[d][0].score >= best * self.s.relative_cutoff][: self.s.max_docs]

        chosen: list[Scored] = []
        for d in kept_docs:
            head = by_doc[d][0].score
            chosen.extend([c for c in by_doc[d] if c.score >= head * self.s.chunk_cutoff][: self.s.per_doc])
        chosen.sort(key=lambda c: c.score, reverse=True)
        return chosen[: self.s.top_k]

    @staticmethod
    def confidence(ranked: list[Scored]) -> float:
        """How sure we are that the corpus covers the question at all, in 0..1.

        Uses lexical evidence only: the best IDF-weighted term coverage of any candidate
        and the best BM25 score (squashed with b / (b + 8)). Cosine similarity is left
        out on purpose: with LSA vectors a three-word off-topic question can still land
        near some chunk, while it cannot fake matching rare corpus terms.
        """
        if not ranked:
            return 0.0
        cov = max(c.coverage for c in ranked)
        b = max(c.bm25 for c in ranked)
        return float(min(max(0.5 * cov + 0.5 * b / (b + 8.0), 0.0), 1.0))

    def retrieve(self, query: str) -> RetrievalResult:
        queries = self._rewrite(query)
        cands = self.candidates(queries)
        if self.s.reranker == "llm" and self.llm:
            ranked = self.rerank_llm(query, cands)
        elif self.s.reranker == "none":
            top = cands[0].rrf if cands else 1.0
            for c in cands:
                pos = self.index.by_id[c.chunk.chunk_id]
                c.coverage = self._coverage(query, pos)
                c.score = c.rrf / top
            ranked = cands
        else:
            ranked = self.rerank_local(query, cands)

        if not ranked:
            return RetrievalResult(query, [], [], queries, 0.0, True)
        confidence = self.confidence(ranked)
        abstained = confidence < self.s.abstain_threshold or not math.isfinite(confidence)
        chosen = [] if abstained else self.select(ranked)
        return RetrievalResult(query, chosen, ranked, queries, confidence, abstained)
