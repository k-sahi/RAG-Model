"""LLM-as-judge metrics: faithfulness and answer correctness.

Both use the same chat model as generation (or a different one via JUDGE_* env vars)
at temperature 0 and return a score in 0..1 with a short rationale.
"""

from __future__ import annotations

from helix_rag.llm import ChatModel, LLMError, parse_json

FAITHFULNESS_SYSTEM = """You check whether an answer is grounded in the provided context.
1. Split the answer into atomic factual claims (ignore citations like [1] and filler).
2. For each claim decide if the context explicitly supports it.
Return only JSON: {"claims": [{"claim": "...", "supported": true|false}], "notes": "..."}
If the answer says the information is unavailable and makes no factual claims, return
{"claims": [], "notes": "no claims"}."""

CORRECTNESS_SYSTEM = """You grade a support answer against a reference answer.
Score 1.0 if it contains every key fact the grading notes require and contradicts none,
0.5 if it is partially right (some required facts missing, nothing wrong), 0.0 if it is
wrong, contradicts the reference, or does not answer. Extra correct detail is fine.
Return only JSON: {"score": 0.0|0.5|1.0, "reason": "..."}"""


def faithfulness(judge: ChatModel, answer: str, context: str) -> tuple[float | None, str]:
    try:
        data = parse_json(judge.complete(FAITHFULNESS_SYSTEM, f"Context:\n{context}\n\nAnswer:\n{answer}"))
    except (LLMError, ValueError) as exc:
        return None, f"judge error: {exc}"
    claims = data.get("claims", [])
    if not claims:
        return 1.0, data.get("notes", "no claims")
    supported = sum(1 for c in claims if c.get("supported"))
    unsupported = [c.get("claim", "") for c in claims if not c.get("supported")]
    return supported / len(claims), "; ".join(unsupported)[:300]


def correctness(judge: ChatModel, question: str, answer: str, reference: str, notes: str) -> tuple[float | None, str]:
    prompt = f"Question: {question}\n\nReference answer: {reference}\n\nGrading notes: {notes}\n\nAnswer to grade:\n{answer}"
    try:
        data = parse_json(judge.complete(CORRECTNESS_SYSTEM, prompt))
        return float(data["score"]), str(data.get("reason", ""))[:300]
    except (LLMError, ValueError, KeyError) as exc:
        return None, f"judge error: {exc}"
