"""Command line interface.

    python -m helix_rag ingest                 # load, chunk, embed and save the index
    python -m helix_rag ask "question" [--json] [--show-context]
    python -m helix_rag search "question"      # retrieval only, with scores
    python -m helix_rag chat                   # interactive loop
"""

from __future__ import annotations

import argparse
import json
import logging
import sys

from .config import Settings
from .index import build_index


def _print_answer(ans, show_context: bool) -> None:
    print(ans.answer)
    print()
    if ans.sources:
        print("Sources:")
        for s in ans.sources:
            print(f"  [{s['n']}] {s['source']}  ({s['section']})")
    flag = "  (abstained)" if ans.abstained else ""
    print(f"Confidence: {ans.confidence}, retrieval {ans.retrieval_confidence:.2f}, via {ans.provider}{flag}")
    if show_context and ans.retrieval:
        print("\nRetrieved:")
        for s in ans.retrieval.chunks:
            print(f"  {s.score:.3f}  {s.chunk.chunk_id}  {s.chunk.section}")


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(prog="helix_rag", description="Question answering over the Helix knowledge base")
    parser.add_argument("-v", "--verbose", action="store_true")
    sub = parser.add_subparsers(dest="cmd", required=True)
    sub.add_parser("ingest", help="build the index from the corpus")
    for name in ("ask", "search"):
        p = sub.add_parser(name)
        p.add_argument("query")
        p.add_argument("--json", action="store_true", help="print JSON")
        p.add_argument("--show-context", action="store_true")
    sub.add_parser("chat", help="interactive question loop")
    args = parser.parse_args(argv)

    logging.basicConfig(level=logging.INFO if args.verbose else logging.WARNING, format="%(levelname)s %(name)s: %(message)s")
    settings = Settings()

    if args.cmd == "ingest":
        index = build_index(settings)
        print(json.dumps(index.manifest, indent=2))
        return 0

    from .pipeline import RAGPipeline

    rag = RAGPipeline(settings)
    if args.cmd == "search":
        res = rag.retriever.retrieve(args.query)
        if args.json:
            print(json.dumps({"confidence": res.confidence, "abstained": res.abstained, "chunks": [c.to_dict() for c in res.chunks]}, indent=2))
        else:
            print(f"confidence {res.confidence:.3f}{'  (abstain)' if res.abstained else ''}")
            for c in res.chunks:
                print(f"{c.score:.3f}  {c.chunk.chunk_id:60s} {c.chunk.section}")
        return 0
    if args.cmd == "ask":
        ans = rag.ask(args.query)
        if args.json:
            print(json.dumps(ans.to_dict(include_context=args.show_context), indent=2))
        else:
            _print_answer(ans, args.show_context)
        return 0

    print("Ask about Helix (empty line to quit).")
    while True:
        try:
            q = input("\n> ").strip()
        except EOFError:
            break
        if not q:
            break
        _print_answer(rag.ask(q), show_context=False)
    return 0


if __name__ == "__main__":
    sys.exit(main())
