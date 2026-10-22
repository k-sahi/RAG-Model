"""Run the pipeline over the test set and score it.

    python -m evals.run_eval                    # retrieval metrics, offline
    python -m evals.run_eval --judge            # + faithfulness / correctness (needs an API key)
    python -m evals.run_eval --min-precision 0.6 --min-recall 0.6   # exit 1 below thresholds

Each question is answered once; retrieval metrics are read from the same retrieval the
answer was generated from.
"""

from __future__ import annotations

import argparse
import json
import re
import sys
import time
from collections import defaultdict
from pathlib import Path

from helix_rag.config import ROOT, Settings
from helix_rag.generation import format_context
from helix_rag.llm import ChatModel
from helix_rag.pipeline import RAGPipeline

from . import judge as judge_mod
from .metrics import context_precision, context_recall, hit, mean, reciprocal_rank

RESULTS_DIR = ROOT / "evals" / "results"
_FACT_RE = re.compile(r"\$?\d[\d,.]*%?|\b[A-Z]{2,}[-_]?\d+\b|`[^`]+`")


def key_facts(text: str) -> set[str]:
    """Numbers, prices, percentages, codes and `literals` from a reference answer."""
    facts = set()
    for m in _FACT_RE.findall(text):
        f = m.strip("`.,").lower().replace(",", "")
        if f and f not in {"1", "2", "3", "4", "5"}:  # list numbering, not facts
            facts.add(f)
    return facts


def key_fact_recall(answer: str, reference: str) -> float | None:
    facts = key_facts(reference)
    if not facts:
        return None
    a = answer.lower().replace(",", "")
    return sum(1 for f in facts if f in a) / len(facts)


def evaluate(settings: Settings, use_judge: bool = False, limit: int | None = None) -> dict:
    test = json.loads((settings.corpus_dir / "test_set.json").read_text())["queries"][:limit]
    rag = RAGPipeline(settings)
    judge: ChatModel | None = rag.llm if use_judge else None
    if use_judge and judge is None:
        raise SystemExit("--judge needs ANTHROPIC_API_KEY or OPENAI_API_KEY")

    rows = []
    for q in test:
        ans = rag.ask(q["query"])
        ret = ans.retrieval
        got = [s.chunk.source for s in ret.chunks]
        ranked_docs = list(dict.fromkeys(s.chunk.source for s in ret.candidates))
        exp = q["expected_sources"]
        row = {
            "id": q["id"],
            "difficulty": q["difficulty"],
            "category": q["category"],
            "query": q["query"],
            "expected_sources": exp,
            "retrieved": [s.to_dict() for s in ret.chunks],
            "answer": ans.answer,
            "cited_sources": [s["source"] for s in ans.sources],
            "abstained": ans.abstained,
            "retrieval_confidence": round(ret.confidence, 3),
            "context_precision": context_precision(got, exp),
            "context_recall": context_recall(got, exp),
            "mrr": reciprocal_rank(ranked_docs, exp),
            "hit@1": hit(ranked_docs[:1], exp),
            "hit@3": hit(ranked_docs[:3], exp),
            "doc_recall@5": context_recall(ranked_docs[:5], exp),
            "key_fact_recall": key_fact_recall(ans.answer, q["ground_truth_answer"]),
            "chunks_returned": len(got),
            **ans.timings,
        }
        if judge:
            ctx = format_context(ret.chunks)
            row["faithfulness"], row["faithfulness_note"] = judge_mod.faithfulness(judge, ans.answer, ctx)
            row["answer_correctness"], row["correctness_note"] = judge_mod.correctness(
                judge, q["query"], ans.answer, q["ground_truth_answer"], q.get("notes", "")
            )
        rows.append(row)

    oos = json.loads((ROOT / "evals" / "out_of_scope.json").read_text())["queries"]
    oos_abstained = [rag.retriever.retrieve(x).abstained for x in oos]

    return {
        "run_at": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
        "config": {
            "embedder": rag.index.manifest["embedder"],
            "reranker": settings.reranker,
            "query_rewrite": settings.query_rewrite,
            "generator": rag.llm.provider + ":" + rag.llm.model if rag.llm else "extractive",
            "chunk_size": settings.chunk_size,
            "chunk_overlap": settings.chunk_overlap,
            "top_k": settings.top_k,
            "max_docs": settings.max_docs,
            "per_doc": settings.per_doc,
            "relative_cutoff": settings.relative_cutoff,
            "chunk_cutoff": settings.chunk_cutoff,
            "abstain_threshold": settings.abstain_threshold,
            "chunks_indexed": len(rag.index.chunks),
        },
        "summary": summarise(rows),
        "by_difficulty": group(rows, "difficulty"),
        "by_category": group(rows, "category"),
        "abstention": {
            "out_of_scope_queries": len(oos),
            "out_of_scope_abstained": sum(oos_abstained),
            "in_scope_false_abstentions": sum(1 for r in rows if r["abstained"]),
        },
        "rows": rows,
    }


METRICS = [
    "context_precision",
    "context_recall",
    "mrr",
    "hit@1",
    "hit@3",
    "doc_recall@5",
    "key_fact_recall",
    "faithfulness",
    "answer_correctness",
    "chunks_returned",
    "retrieve_ms",
]


def summarise(rows: list[dict]) -> dict:
    out = {"n": len(rows)}
    for m in METRICS:
        vals = [r[m] for r in rows if r.get(m) is not None]
        if vals:
            out[m] = round(mean(vals), 3)
    return out


def group(rows: list[dict], key: str) -> dict:
    buckets: dict[str, list[dict]] = defaultdict(list)
    for r in rows:
        buckets[r[key]].append(r)
    return {k: summarise(v) for k, v in sorted(buckets.items())}


def to_markdown(result: dict) -> str:
    s = result["summary"]
    cols = [m for m in METRICS if m in s]
    lines = [
        f"# Eval run {result['run_at']}",
        "",
        "Config: " + ", ".join(f"`{k}={v}`" for k, v in result["config"].items()),
        "",
        "| metric | value |",
        "|---|---|",
        *[f"| {m} | {s[m]} |" for m in cols],
        "",
        "## By difficulty",
        "",
        "| difficulty | n | " + " | ".join(cols) + " |",
        "|---|---|" + "---|" * len(cols),
    ]
    for k, v in result["by_difficulty"].items():
        lines.append(f"| {k} | {v['n']} | " + " | ".join(str(v.get(m, "")) for m in cols) + " |")
    a = result["abstention"]
    lines += [
        "",
        f"Abstention: {a['out_of_scope_abstained']}/{a['out_of_scope_queries']} out-of-scope questions refused, "
        f"{a['in_scope_false_abstentions']} in-scope questions wrongly refused.",
        "",
        "## Per question",
        "",
        "| id | diff | precision | recall | first expected doc rank | retrieved docs |",
        "|---|---|---|---|---|---|",
    ]
    for r in result["rows"]:
        docs = list(dict.fromkeys(x["source"] for x in r["retrieved"]))
        rank = round(1 / r["mrr"]) if r["mrr"] else "-"
        lines.append(
            f"| {r['id']} | {r['difficulty']} | {r['context_precision']:.2f} | {r['context_recall']:.2f} | {rank} | "
            + "<br>".join(d.split("/")[-1] for d in docs)
            + " |"
        )
    return "\n".join(lines) + "\n"


def main(argv: list[str] | None = None) -> int:
    p = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    p.add_argument("--judge", action="store_true", help="add LLM-judged faithfulness and correctness")
    p.add_argument("--limit", type=int, help="only the first N questions")
    p.add_argument("--min-precision", type=float)
    p.add_argument("--min-recall", type=float)
    p.add_argument("--min-faithfulness", type=float)
    p.add_argument("--out", type=Path, default=RESULTS_DIR)
    args = p.parse_args(argv)

    result = evaluate(Settings(), use_judge=args.judge, limit=args.limit)
    args.out.mkdir(parents=True, exist_ok=True)
    (args.out / "latest.json").write_text(json.dumps(result, indent=2))
    (args.out / "latest.md").write_text(to_markdown(result))

    s = result["summary"]
    print(json.dumps({"summary": s, "abstention": result["abstention"]}, indent=2))
    failures = []
    if args.min_precision is not None and s["context_precision"] < args.min_precision:
        failures.append(f"context_precision {s['context_precision']} < {args.min_precision}")
    if args.min_recall is not None and s["context_recall"] < args.min_recall:
        failures.append(f"context_recall {s['context_recall']} < {args.min_recall}")
    if args.min_faithfulness is not None and s.get("faithfulness", 0) < args.min_faithfulness:
        failures.append(f"faithfulness {s.get('faithfulness')} < {args.min_faithfulness}")
    for f in failures:
        print("FAIL:", f, file=sys.stderr)
    return 1 if failures else 0


if __name__ == "__main__":
    sys.exit(main())
