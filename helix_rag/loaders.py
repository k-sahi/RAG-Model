"""Load markdown docs, PDF runbooks (with OCR for scanned pages) and HTML tickets."""

from __future__ import annotations

import hashlib
import json
import logging
import re
from pathlib import Path

from .documents import Document

log = logging.getLogger(__name__)

# A page with less extractable text than this is treated as scanned.
MIN_TEXT_CHARS_PER_PAGE = 80


# --------------------------------------------------------------------------- markdown


def load_markdown(path: Path, source: str) -> Document:
    text = path.read_text(encoding="utf-8")
    m = re.search(r"^#\s+(.+)$", text, flags=re.M)
    title = m.group(1).strip() if m else path.stem.replace("-", " ").title()
    return Document(source=source, doc_type="markdown", title=title, text=text)


# --------------------------------------------------------------------------- pdf

_HEADING_RE = re.compile(r"^[A-Z0-9][A-Z0-9 &/,'()\-–—:]{2,70}$")


def _is_heading(line: str) -> bool:
    s = line.strip()
    return bool(_HEADING_RE.match(s)) and any(c.isalpha() for c in s) and not s.startswith("INTERNAL")


def _ocr_pdf(path: Path, cache_dir: Path | None) -> str:
    """OCR every page. Results are cached by file hash because OCR is slow (~5 s/page)."""
    digest = hashlib.sha256(path.read_bytes()).hexdigest()[:20]
    cache_file = cache_dir / "ocr" / f"{digest}.txt" if cache_dir else None
    if cache_file and cache_file.exists():
        return cache_file.read_text(encoding="utf-8")
    try:
        import pytesseract
        from pdf2image import convert_from_path
    except ImportError:  # pragma: no cover - depends on the environment
        log.warning("OCR libraries missing; skipping scanned PDF %s", path)
        return ""
    try:
        pages = convert_from_path(str(path), dpi=300)
        text = "\n\n".join(pytesseract.image_to_string(p) for p in pages)
    except Exception as exc:  # poppler or tesseract binary missing, corrupt file...
        log.warning("OCR failed for %s: %s", path, exc)
        return ""
    if cache_file:
        cache_file.parent.mkdir(parents=True, exist_ok=True)
        cache_file.write_text(text, encoding="utf-8")
    return text


def _normalise_pdf_text(raw: str) -> str:
    """Re-flow wrapped lines into paragraphs while keeping section headings on their
    own lines, so the chunker can split on them."""
    out: list[str] = []
    para: list[str] = []

    def flush() -> None:
        if para:
            out.append(" ".join(para))
            para.clear()

    for line in raw.splitlines():
        s = re.sub(r"\s+", " ", line).strip()
        if not s:
            flush()
            continue
        if not out and not para:  # first line is the document title
            out.append(s)
            continue
        if s.startswith("INTERNAL"):  # audience banner under the title
            flush()
            out.append(s)
            continue
        if _is_heading(s):
            flush()
            out.append("")
            out.append(s)
            continue
        para.append(s)
    flush()
    text = "\n".join(out)
    return re.sub(r"\n{3,}", "\n\n", text).strip()


def load_pdf(path: Path, source: str, cache_dir: Path | None = None) -> Document:
    from pypdf import PdfReader

    reader = PdfReader(str(path))
    pages = [(p.extract_text() or "") for p in reader.pages]
    native_chars = sum(len(p.strip()) for p in pages)
    scanned = native_chars < MIN_TEXT_CHARS_PER_PAGE * max(len(pages), 1)
    raw = _ocr_pdf(path, cache_dir) if scanned else "\n".join(pages)
    text = _normalise_pdf_text(raw)

    lines = [ln for ln in text.splitlines() if ln.strip()]
    title = lines[0].strip() if lines else path.stem.replace("-", " ").title()
    audience = next((ln.strip() for ln in lines[1:3] if ln.strip().startswith("INTERNAL")), "")
    return Document(
        source=source,
        doc_type="pdf",
        title=title,
        text=text,
        metadata={
            "pages": len(pages),
            "scanned": scanned,
            "ocr_ok": bool(text) if scanned else None,
            "audience": audience,
        },
    )


# --------------------------------------------------------------------------- html tickets


def load_ticket(path: Path, source: str) -> Document:
    from bs4 import BeautifulSoup

    soup = BeautifulSoup(path.read_text(encoding="utf-8"), "html.parser")

    def text_of(node) -> str:
        return re.sub(r"\s+", " ", node.get_text(" ", strip=True)).strip() if node else ""

    ticket_id = text_of(soup.select_one(".ticket-id")).replace("TICKET", "").strip()
    subject = text_of(soup.select_one("h1")) or text_of(soup.title)
    meta: dict[str, str] = {}
    for span in soup.select(".meta-row > span"):
        label = span.find("strong")
        if label:
            key = label.get_text(strip=True).rstrip(":").lower()
            value = text_of(span).split(":", 1)[-1].strip()
            meta[key] = value

    turns = []
    for msg in soup.select(".message"):
        role_raw = text_of(msg.select_one(".role-badge"))
        role = "Customer" if role_raw.lower() == "customer" else "Agent"
        body_node = msg.select_one(".message-body")
        paragraphs = [text_of(p) for p in body_node.find_all(["p", "li"])] if body_node else []
        body = "\n".join(p for p in paragraphs if p) or text_of(body_node)
        turns.append(
            {
                "speaker": text_of(msg.select_one(".sender-name")),
                "role": role,
                "timestamp": text_of(msg.select_one(".timestamp")),
                "text": body,
            }
        )
    resolution_node = soup.select_one(".resolution p")
    resolution = text_of(resolution_node)

    title = f"Ticket {ticket_id}: {subject}" if ticket_id else subject
    header = " | ".join(f"{k.title()}: {v}" for k, v in meta.items() if k in ("status", "category", "priority"))
    parts = [title, header, ""]
    for t in turns:
        parts.append(f"[{t['role']}] {t['speaker']}: {t['text']}")
    if resolution:
        parts += ["", f"RESOLUTION: {resolution}"]

    return Document(
        source=source,
        doc_type="ticket",
        title=title,
        text="\n".join(parts).strip(),
        metadata={
            "ticket_id": ticket_id,
            "subject": subject,
            **{k: v for k, v in meta.items() if k in ("status", "category", "priority")},
            "turns": turns,
            "resolution": resolution,
        },
    )


# --------------------------------------------------------------------------- corpus

LOADERS = {".md": "markdown", ".pdf": "pdf", ".html": "ticket", ".htm": "ticket"}
SKIP = {"README.md", "test_set.json"}


def iter_corpus_files(corpus_dir: Path) -> list[Path]:
    files = []
    for p in sorted(corpus_dir.rglob("*")):
        if not p.is_file() or p.suffix.lower() not in LOADERS:
            continue
        if p.relative_to(corpus_dir).as_posix() in SKIP:
            continue
        files.append(p)
    return files


def load_document(path: Path, corpus_dir: Path, cache_dir: Path | None = None) -> Document:
    source = path.relative_to(corpus_dir).as_posix()
    kind = LOADERS[path.suffix.lower()]
    if kind == "markdown":
        return load_markdown(path, source)
    if kind == "pdf":
        return load_pdf(path, source, cache_dir)
    return load_ticket(path, source)


def load_corpus(corpus_dir: Path, cache_dir: Path | None = None) -> list[Document]:
    """Load every supported file. A file that fails to parse is logged and skipped
    rather than aborting the whole ingest."""
    docs: list[Document] = []
    for path in iter_corpus_files(corpus_dir):
        try:
            doc = load_document(path, corpus_dir, cache_dir)
        except Exception as exc:
            log.error("Failed to load %s: %s", path, exc)
            continue
        if not doc.text.strip():
            log.warning("No text extracted from %s; skipped", doc.source)
            continue
        docs.append(doc)
    return docs


def summarise(docs: list[Document]) -> dict:
    by_type: dict[str, int] = {}
    for d in docs:
        by_type[d.doc_type] = by_type.get(d.doc_type, 0) + 1
    scanned = [d.source for d in docs if d.metadata.get("scanned")]
    return {"documents": len(docs), "by_type": by_type, "ocr": scanned}


if __name__ == "__main__":  # pragma: no cover
    import sys

    from .config import Settings

    s = Settings()
    print(json.dumps(summarise(load_corpus(Path(sys.argv[1]) if len(sys.argv) > 1 else s.corpus_dir, s.cache_dir)), indent=2))
