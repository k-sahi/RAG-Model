"""Structure-aware chunking, one strategy per document type.

- Markdown: split on headings and carry the heading path as a breadcrumb. Tables and
  code fences are atomic blocks and are never cut in half.
- PDF runbooks: split on the ALL-CAPS section headings the runbooks use, then fall back
  to a recursive paragraph/sentence splitter with overlap for long sections.
- Tickets: short tickets stay whole (the resolution is usually in the last turn, so
  splitting would separate question from answer). Long tickets get a summary chunk
  (subject + first customer message + resolution) plus overlapping windows of turns.
"""

from __future__ import annotations

import re
from dataclasses import dataclass

from .documents import Chunk, Document

MIN_SECTION_CHARS = 180  # sections shorter than this are merged into the next one


@dataclass
class ChunkerConfig:
    chunk_size: int = 900
    chunk_overlap: int = 150


# --------------------------------------------------------------------------- helpers


def split_recursive(text: str, size: int, overlap: int) -> list[str]:
    """Split on the coarsest separator that works (paragraph, line, sentence, word),
    then pack pieces into windows of at most `size` characters with `overlap`."""
    text = text.strip()
    if len(text) <= size:
        return [text] if text else []

    pieces: list[str] = [text]
    for sep in ("\n\n", "\n", r"(?<=[.!?;])\s+", " "):
        if all(len(p) <= size for p in pieces):
            break
        nxt: list[str] = []
        for p in pieces:
            if len(p) <= size:
                nxt.append(p)
            else:
                parts = re.split(sep, p) if sep.startswith("(") else p.split(sep)
                nxt.extend(x.strip() for x in parts if x.strip())
        pieces = nxt
    # Hard split anything still too long (a single enormous token).
    flat: list[str] = []
    for p in pieces:
        while len(p) > size:
            flat.append(p[:size])
            p = p[size - overlap :]
        flat.append(p)

    windows: list[str] = []
    current: list[str] = []
    length = 0
    for p in flat:
        if current and length + len(p) + 1 > size:
            windows.append(" ".join(current) if "\n" not in "".join(current) else "\n".join(current))
            # Start the next window with trailing pieces that fit in the overlap budget.
            carry: list[str] = []
            carry_len = 0
            for prev in reversed(current):
                if carry_len + len(prev) > overlap:
                    break
                carry.insert(0, prev)
                carry_len += len(prev) + 1
            current, length = carry, carry_len
        current.append(p)
        length += len(p) + 1
    if current:
        windows.append(" ".join(current) if "\n" not in "".join(current) else "\n".join(current))
    return windows


def _md_blocks(body: str) -> list[str]:
    """Split markdown into blocks on blank lines, keeping code fences and tables whole."""
    blocks: list[str] = []
    buf: list[str] = []
    in_fence = False
    for line in body.splitlines():
        if line.strip().startswith("```"):
            in_fence = not in_fence
            buf.append(line)
            continue
        if not in_fence and not line.strip():
            if buf:
                blocks.append("\n".join(buf))
                buf = []
            continue
        buf.append(line)
    if buf:
        blocks.append("\n".join(buf))
    return blocks


def _pack_blocks(blocks: list[str], size: int, overlap: int) -> list[str]:
    """Pack whole blocks into chunks. A single oversized block is split only if it is
    prose; tables and code stay intact even when longer than `size`."""
    out: list[str] = []
    current: list[str] = []
    length = 0
    for b in blocks:
        atomic = b.lstrip().startswith(("```", "|"))
        if len(b) > size and not atomic:
            if current:
                out.append("\n\n".join(current))
                current, length = [], 0
            out.extend(split_recursive(b, size, overlap))
            continue
        if current and length + len(b) + 2 > size:
            out.append("\n\n".join(current))
            current, length = [], 0
        current.append(b)
        length += len(b) + 2
    if current:
        out.append("\n\n".join(current))
    return out


def _merge_small(sections: list[tuple[str, str]]) -> list[tuple[str, str]]:
    """Merge sections that are too short to be useful into the following section."""
    merged: list[tuple[str, str]] = []
    pending: tuple[str, str] | None = None
    for crumb, body in sections:
        if pending:
            # The short section keeps its own heading line inside its body, so it
            # stays readable after being prepended to the next section.
            body = f"{pending[1]}\n\n{body}".strip()
            pending = None
        if len(body) < MIN_SECTION_CHARS:
            pending = (crumb, body)
            continue
        merged.append((crumb, body))
    if pending:
        if merged:
            c, b = merged[-1]
            merged[-1] = (c, f"{b}\n\n{pending[1]}")
        else:
            merged.append(pending)
    return merged


# --------------------------------------------------------------------------- markdown


def chunk_markdown(doc: Document, cfg: ChunkerConfig) -> list[tuple[str, str]]:
    heading_re = re.compile(r"^(#{1,6})\s+(.+?)\s*#*$")
    path: list[tuple[int, str]] = []
    sections: list[tuple[str, str]] = []
    buf: list[str] = []
    in_fence = False

    def crumb() -> str:
        return " > ".join(t for _, t in path)

    def flush() -> None:
        body = "\n".join(buf).strip()
        if body:
            sections.append((crumb(), body))
        buf.clear()

    for line in doc.text.splitlines():
        if line.strip().startswith("```"):
            in_fence = not in_fence
        m = None if in_fence else heading_re.match(line)
        if m:
            flush()
            level, title = len(m.group(1)), m.group(2).strip()
            while path and path[-1][0] >= level:
                path.pop()
            path.append((level, title))
            if level > 1:
                buf.append(line)  # keep the sub-heading in the body for readability
            continue
        buf.append(line)
    flush()

    out: list[tuple[str, str]] = []
    for crumb_text, body in _merge_small(sections):
        for piece in _pack_blocks(_md_blocks(body), cfg.chunk_size, cfg.chunk_overlap):
            out.append((crumb_text, piece))
    return out


# --------------------------------------------------------------------------- pdf


def chunk_pdf(doc: Document, cfg: ChunkerConfig) -> list[tuple[str, str]]:
    from .loaders import _is_heading

    lines = doc.text.splitlines()
    sections: list[tuple[str, str]] = []
    current = "Overview"
    buf: list[str] = []
    for i, line in enumerate(lines):
        if i == 0 and line.strip() == doc.title:
            continue
        if line.strip().startswith("INTERNAL") and i < 3:
            continue
        if _is_heading(line):
            if buf:
                sections.append((current, "\n".join(buf).strip()))
                buf = []
            current = line.strip().title()
            buf.append(line.strip())
            continue
        if line.strip():
            buf.append(line.strip())
    if buf:
        sections.append((current, "\n".join(buf).strip()))

    # Runbook sections are short, so pack consecutive sections together up to the
    # chunk size; the breadcrumb lists every section in the chunk.
    out: list[tuple[str, str]] = []
    group: list[tuple[str, str]] = []
    length = 0

    def emit() -> None:
        if group:
            out.append((", ".join(n for n, _ in group), "\n".join(b for _, b in group)))

    for name, body in sections:
        if len(body) > cfg.chunk_size:
            emit()
            group, length = [], 0
            for piece in split_recursive(body, cfg.chunk_size, cfg.chunk_overlap):
                out.append((name, piece))
            continue
        if group and length + len(body) + 1 > cfg.chunk_size:
            emit()
            # Overlap: repeat the last section when it is small enough.
            last = group[-1]
            group, length = ([last], len(last[1])) if len(last[1]) <= cfg.chunk_overlap else ([], 0)
        group.append((name, body))
        length += len(body) + 1
    emit()
    return out


# --------------------------------------------------------------------------- tickets


def chunk_ticket(doc: Document, cfg: ChunkerConfig) -> list[tuple[str, str]]:
    if len(doc.text) <= cfg.chunk_size * 2.5:
        return [("Full ticket", doc.text)]

    turns = doc.metadata.get("turns", [])
    resolution = doc.metadata.get("resolution", "")
    first_customer = next((t["text"] for t in turns if t["role"] == "Customer"), "")
    out = [("Summary", f"Problem: {first_customer}\n\nResolution: {resolution}".strip())]

    lines = [f"[{t['role']}] {t['speaker']}: {t['text']}" for t in turns]
    window: list[str] = []
    length = 0
    start = 1
    for i, line in enumerate(lines, start=1):
        if window and length + len(line) > cfg.chunk_size * 1.5:
            out.append((f"Conversation turns {start}-{i - 1}", "\n".join(window)))
            window, length, start = [window[-1]], len(window[-1]), i - 1  # one-turn overlap
        window.append(line)
        length += len(line) + 1
    if window:
        out.append((f"Conversation turns {start}-{len(lines)}", "\n".join(window)))
    return out


# --------------------------------------------------------------------------- entry point

_STRATEGIES = {"markdown": chunk_markdown, "pdf": chunk_pdf, "ticket": chunk_ticket}


def chunk_document(doc: Document, cfg: ChunkerConfig | None = None) -> list[Chunk]:
    cfg = cfg or ChunkerConfig()
    pieces = _STRATEGIES[doc.doc_type](doc, cfg)
    meta = {k: v for k, v in doc.metadata.items() if k != "turns"}
    chunks = []
    for i, (section, text) in enumerate(pieces):
        if not text.strip():
            continue
        chunks.append(
            Chunk(
                chunk_id=f"{doc.source}#{i}",
                source=doc.source,
                doc_type=doc.doc_type,
                title=doc.title,
                section=section,
                text=text.strip(),
                metadata=meta,
            )
        )
    return chunks


def chunk_corpus(docs: list[Document], cfg: ChunkerConfig | None = None) -> list[Chunk]:
    out: list[Chunk] = []
    for d in docs:
        out.extend(chunk_document(d, cfg))
    return out
