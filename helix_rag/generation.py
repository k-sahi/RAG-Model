"""Answer generation with citations.

The model only sees the retrieved chunks, numbered [1]..[n], and must return JSON with
the answer, the context numbers it used, and whether the context was sufficient. When
no LLM key is configured an extractive answerer picks the best-supported sentences
from the context instead, so the whole pipeline still runs offline.
"""

from __future__ import annotations

import logging
import re
from dataclasses import dataclass, field

from .llm import ChatModel, LLMError, parse_json
from .retrieval import RetrievalResult, Scored
from .text import tokenize

log = logging.getLogger(__name__)

NO_ANSWER = (
    "I couldn't find this in the Helix knowledge base, so I'd rather not guess. "
    "Try rephrasing with the feature or error name, or escalate to the support team."
)

SYSTEM_PROMPT = """You are the Helix support assistant. Helix is a B2B workflow automation platform.
Answer the question using ONLY the numbered context passages. They come from product
docs, internal runbooks and resolved support tickets.

Rules:
- Every factual sentence must be supported by a passage; cite it inline like [2].
- Keep exact numbers, limits, prices, error codes, settings paths and names as written.
- If passages disagree, prefer product docs and runbooks over individual tickets, and say so.
- If the passages do not contain the answer, set "insufficient_context" to true and say
  what is missing instead of guessing. Do not use outside knowledge about other products.
- Be concise: a direct answer first, then steps or caveats if they matter.

Return only JSON:
{"answer": "<answer with [n] citations>", "citations": [<n>, ...],
 "confidence": "high" | "medium" | "low", "insufficient_context": <true|false>}"""


@dataclass
class Answer:
    query: str
    answer: str
    sources: list[dict] = field(default_factory=list)  # [{n, source, section, chunk_id}]
    confidence: str = "low"  # model's own label
    retrieval_confidence: float = 0.0
    abstained: bool = False
    provider: str = "extractive"
    retrieval: RetrievalResult | None = None
    timings: dict = field(default_factory=dict)

    def to_dict(self, include_context: bool = False) -> dict:
        d = {
            "query": self.query,
            "answer": self.answer,
            "sources": self.sources,
            "confidence": self.confidence,
            "retrieval_confidence": round(self.retrieval_confidence, 3),
            "abstained": self.abstained,
            "provider": self.provider,
            "timings": self.timings,
        }
        if include_context and self.retrieval:
            d["retrieved"] = [s.to_dict() for s in self.retrieval.chunks]
        return d


def format_context(chunks: list[Scored]) -> str:
    blocks = []
    for i, s in enumerate(chunks, start=1):
        c = s.chunk
        kind = {"markdown": "product doc", "pdf": "runbook", "ticket": "support ticket"}[c.doc_type]
        where = f"{c.title} > {c.section}" if c.section and c.section != c.title else c.title
        blocks.append(f"[{i}] ({kind}) {c.source}\n{where}\n{c.text}")
    return "\n\n---\n\n".join(blocks)


def _source_list(chunks: list[Scored], used: list[int] | None = None) -> list[dict]:
    out = []
    for i, s in enumerate(chunks, start=1):
        if used is not None and i not in used:
            continue
        out.append({"n": i, "source": s.chunk.source, "section": s.chunk.section, "chunk_id": s.chunk.chunk_id})
    return out


def _confidence_label(score: float) -> str:
    return "high" if score >= 0.6 else "medium" if score >= 0.45 else "low"


# --------------------------------------------------------------------------- LLM


def generate_llm(llm: ChatModel, retrieval: RetrievalResult) -> Answer:
    chunks = retrieval.chunks
    user = f"Context:\n\n{format_context(chunks)}\n\nQuestion: {retrieval.query}"
    raw = llm.complete(SYSTEM_PROMPT, user)
    try:
        data = parse_json(raw)
    except (LLMError, ValueError):
        log.warning("Model did not return JSON; using the raw text")
        data = {"answer": raw.strip(), "citations": [], "confidence": "low", "insufficient_context": False}

    text = str(data.get("answer", "")).strip()
    cited = {int(n) for n in data.get("citations", []) if str(n).isdigit()}
    cited |= {int(n) for n in re.findall(r"\[(\d+)\]", text)}
    cited = sorted(n for n in cited if 1 <= n <= len(chunks))
    insufficient = bool(data.get("insufficient_context"))
    return Answer(
        query=retrieval.query,
        answer=text or NO_ANSWER,
        sources=_source_list(chunks, cited),
        confidence="low" if insufficient else str(data.get("confidence", "medium")),
        retrieval_confidence=retrieval.confidence,
        abstained=insufficient,
        provider=llm.provider,
        retrieval=retrieval,
    )


# --------------------------------------------------------------------------- extractive

_SENT_SPLIT = re.compile(r"(?<=[.!?])\s+(?=[A-Z0-9(\"'`$])|\n+")


def generate_extractive(retrieval: RetrievalResult, max_sentences: int = 3) -> Answer:
    """Pick the context sentences that share the most terms with the question (scaled
    by the chunk's retrieval score) and stitch them together with citations. Sentences
    with concrete values (numbers, prices, codes) get a small bonus, because that is
    usually what a support question is after. (IDF weighting was tried and scored
    lower on key-fact recall: it over-rewards rare words that are not the answer.)"""
    q_terms = set(tokenize(retrieval.query))
    total = len(q_terms) or 1
    scored: list[tuple[float, int, str]] = []
    for i, s in enumerate(retrieval.chunks, start=1):
        for sent in _SENT_SPLIT.split(s.chunk.text):
            heading = sent.lstrip().startswith("#")
            sent = sent.replace("**", "").strip(" -*#|")
            # A heading is only an answer when it carries a value ("Pro — $299/month").
            if heading and not re.search(r"\d", sent):
                continue
            if len(sent) < (8 if heading else 15) or sent.startswith("```"):
                continue
            terms = set(tokenize(sent))
            overlap = len(q_terms & terms) / total
            concrete = 1.15 if re.search(r"\d", sent) else 1.0
            scored.append((overlap * concrete * (0.5 + s.score), i, sent))
    scored.sort(key=lambda x: x[0], reverse=True)
    picked, seen = [], set()
    for score, n, sent in scored:
        if score <= 0 or sent in seen:
            continue
        picked.append((n, sent))
        seen.add(sent)
        if len(picked) == max_sentences:
            break
    if not picked:
        return Answer(retrieval.query, NO_ANSWER, [], "low", retrieval.confidence, True, "extractive", retrieval)
    text = " ".join(f"{sent.rstrip('.')}. [{n}]" for n, sent in picked)
    used = sorted({n for n, _ in picked})
    return Answer(
        query=retrieval.query,
        answer=text,
        sources=_source_list(retrieval.chunks, used),
        confidence=_confidence_label(retrieval.confidence),
        retrieval_confidence=retrieval.confidence,
        abstained=False,
        provider="extractive",
        retrieval=retrieval,
    )


def generate(retrieval: RetrievalResult, llm: ChatModel | None = None) -> Answer:
    if retrieval.abstained or not retrieval.chunks:
        return Answer(
            query=retrieval.query,
            answer=NO_ANSWER,
            confidence="low",
            retrieval_confidence=retrieval.confidence,
            abstained=True,
            provider=llm.provider if llm else "extractive",
            retrieval=retrieval,
        )
    if llm is None:
        return generate_extractive(retrieval)
    try:
        return generate_llm(llm, retrieval)
    except LLMError as exc:
        log.error("Generation failed (%s); falling back to extractive answer", exc)
        return generate_extractive(retrieval)
