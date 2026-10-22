"""Retrieval metrics computed against `expected_sources` (no LLM needed)."""

from __future__ import annotations


def context_precision(retrieved_sources: list[str], expected: list[str]) -> float:
    """Share of retrieved chunks that come from an expected source document."""
    if not retrieved_sources:
        return 0.0
    exp = set(expected)
    return sum(1 for s in retrieved_sources if s in exp) / len(retrieved_sources)


def context_recall(retrieved_sources: list[str], expected: list[str]) -> float:
    """Share of expected source documents with at least one retrieved chunk."""
    if not expected:
        return 1.0
    got = set(retrieved_sources)
    return sum(1 for e in expected if e in got) / len(expected)


def reciprocal_rank(retrieved_sources: list[str], expected: list[str]) -> float:
    exp = set(expected)
    for rank, s in enumerate(retrieved_sources, start=1):
        if s in exp:
            return 1.0 / rank
    return 0.0


def hit(retrieved_sources: list[str], expected: list[str]) -> float:
    return 1.0 if set(retrieved_sources) & set(expected) else 0.0


def mean(xs) -> float:
    xs = list(xs)
    return sum(xs) / len(xs) if xs else 0.0
