"""Core data types shared by every stage of the pipeline."""

from __future__ import annotations

import hashlib
from dataclasses import dataclass, field


@dataclass
class Document:
    """One source file after loading, before chunking."""

    source: str  # path relative to the corpus root, e.g. "product-docs/api/errors.md"
    doc_type: str  # "markdown" | "pdf" | "ticket"
    title: str
    text: str
    metadata: dict = field(default_factory=dict)


@dataclass
class Chunk:
    """A retrievable unit of text with enough context to stand on its own."""

    chunk_id: str
    source: str
    doc_type: str
    title: str
    section: str  # breadcrumb, e.g. "API Errors > Retrying"
    text: str  # the chunk body as shown to the LLM
    metadata: dict = field(default_factory=dict)

    @property
    def index_text(self) -> str:
        """Text used for embedding and keyword search: title and section give short
        chunks the context they would otherwise lose."""
        header = self.title if self.section in ("", self.title) else f"{self.title} > {self.section}"
        return f"{header}\n{self.text}"

    @property
    def content_hash(self) -> str:
        return hashlib.sha256(self.index_text.encode("utf-8")).hexdigest()[:16]

    def to_dict(self) -> dict:
        return {
            "chunk_id": self.chunk_id,
            "source": self.source,
            "doc_type": self.doc_type,
            "title": self.title,
            "section": self.section,
            "text": self.text,
            "metadata": self.metadata,
        }

    @classmethod
    def from_dict(cls, d: dict) -> "Chunk":
        return cls(**d)
