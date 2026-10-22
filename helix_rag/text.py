"""Tokenisation shared by BM25, the local embedder and the reranker.

Support content is full of identifiers that a naive tokenizer destroys: error codes
(`429`), ticket ids (`HX-1267`), header names (`X-Helix-Signature`), function names
(`pg_last_wal_receive_lsn`) and prices (`$299`). Compound tokens are kept whole *and*
split into their parts, so "x-helix-signature" matches both the header and "signature".
"""

from __future__ import annotations

import re

_TOKEN_RE = re.compile(r"\$?[a-z0-9]+(?:[-_./:][a-z0-9]+)*")

STOPWORDS = frozenset(
    """a about above after again against all am an and any are as at be because been before
    being below between both but by can could did do does doing down during each few for from
    further had has have having he her here hers herself him himself his how i if in into is it
    its itself just me more most my myself no nor not now of off on once only or other our ours
    ourselves out over own same she should so some such than that the their theirs them
    themselves then there these they this those through to too under until up very was we were
    what when where which while who whom why will with would you your yours yourself yourselves
    s t d ll m re ve y get got also us let lets please hi hey ok okay im""".split()
)

_SUFFIXES = ("ations", "ation", "ingly", "ings", "ing", "edly", "ied", "ies", "ed", "es", "s")


def stem(word: str) -> str:
    """A deliberately light suffix stripper: enough to match plurals and verb forms
    ("retries" / "retried", "cancel" / "cancelled" / "cancellation") without mangling
    identifiers. A doubled final letter is collapsed so "cancell" and "cancel" meet."""
    if not word.isalpha():
        return word
    if len(word) > 4:
        for suf in _SUFFIXES:
            if word.endswith(suf) and len(word) - len(suf) >= 3:
                if suf == "s" and word.endswith("ss"):
                    break
                word = word[: -len(suf)] + ("i" if suf in ("ies", "ied") else "")
                break
    if len(word) >= 4 and word[-1] == word[-2] and word[-1] not in "sz":
        word = word[:-1]
    return word


def tokenize(text: str, keep_stopwords: bool = False) -> list[str]:
    tokens: list[str] = []
    for raw in _TOKEN_RE.findall(text.lower()):
        raw = raw.strip("./:")
        if not raw:
            continue
        compound = re.search(r"[-_./:]", raw) is not None
        if compound:
            tokens.append(raw)
            parts = [p for p in re.split(r"[-_./:]", raw.lstrip("$")) if p]
        else:
            parts = [raw.lstrip("$")] if raw.startswith("$") else [raw]
            if raw.startswith("$"):
                tokens.append(raw)
        for p in parts:
            if not keep_stopwords and p in STOPWORDS:
                continue
            tokens.append(stem(p))
    return tokens
