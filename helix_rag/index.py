"""Build, save and load the search index (chunks + vectors + BM25)."""

from __future__ import annotations

import hashlib
import json
import logging
import time
from dataclasses import dataclass
from pathlib import Path

from .bm25 import BM25
from .chunking import ChunkerConfig, chunk_corpus
from .config import Settings
from .documents import Chunk
from .embeddings import LocalEmbedder, make_embedder
from .loaders import load_corpus, summarise
from .store import NumpyStore, PineconeStore

log = logging.getLogger(__name__)


@dataclass
class Index:
    chunks: list[Chunk]
    embedder: object
    store: object
    bm25: BM25
    manifest: dict

    def __post_init__(self) -> None:
        self.by_id = {c.chunk_id: i for i, c in enumerate(self.chunks)}
        # Whole-document vectors, used by the reranker as document-level evidence:
        # a chunk from a document that is about the question as a whole is a better
        # bet than an equally similar chunk from a document that mentions it once.
        texts: dict[str, list[str]] = {}
        for c in self.chunks:
            texts.setdefault(c.source, []).append(c.index_text)
        self.doc_sources = list(texts)
        self.doc_pos = {s: i for i, s in enumerate(self.doc_sources)}
        self.doc_vectors = self.embedder.embed(["\n".join(t)[:24000] for t in texts.values()])

    def chunk(self, chunk_id: str) -> Chunk:
        return self.chunks[self.by_id[chunk_id]]


def _corpus_fingerprint(chunks: list[Chunk]) -> str:
    h = hashlib.sha256()
    for c in chunks:
        h.update(c.content_hash.encode())
    return h.hexdigest()[:16]


def build_index(settings: Settings | None = None, save: bool = True) -> Index:
    settings = settings or Settings()
    t0 = time.time()
    docs = load_corpus(settings.corpus_dir, settings.cache_dir)
    chunks = chunk_corpus(docs, ChunkerConfig(settings.chunk_size, settings.chunk_overlap))
    texts = [c.index_text for c in chunks]

    embedder = make_embedder(settings).fit(texts)
    vectors = embedder.embed(texts)

    store = NumpyStore()
    store.upsert([c.chunk_id for c in chunks], vectors)
    if settings.pinecone_host:
        PineconeStore(settings.pinecone_api_key, settings.pinecone_host).upsert(
            [c.chunk_id for c in chunks], vectors
        )

    manifest = {
        "built_at": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
        "embedder": embedder.name,
        "dims": int(vectors.shape[1]),
        "chunk_size": settings.chunk_size,
        "chunk_overlap": settings.chunk_overlap,
        "fingerprint": _corpus_fingerprint(chunks),
        "corpus": summarise(docs),
        "chunks": len(chunks),
        "build_seconds": round(time.time() - t0, 1),
    }
    index = Index(chunks, embedder, store, BM25(texts), manifest)
    if save:
        save_index(index, settings.index_dir)
    log.info("Indexed %d chunks from %d documents", len(chunks), len(docs))
    return index


def save_index(index: Index, index_dir: Path) -> None:
    index_dir.mkdir(parents=True, exist_ok=True)
    (index_dir / "chunks.json").write_text(json.dumps([c.to_dict() for c in index.chunks], indent=1))
    (index_dir / "manifest.json").write_text(json.dumps(index.manifest, indent=2))
    index.store.save(index_dir / "vectors.npy")


def load_index(settings: Settings | None = None) -> Index:
    settings = settings or Settings()
    d = settings.index_dir
    if not (d / "chunks.json").exists():
        raise FileNotFoundError(f"No index in {d}. Run `python -m helix_rag ingest` first.")
    chunks = [Chunk.from_dict(x) for x in json.loads((d / "chunks.json").read_text())]
    manifest = json.loads((d / "manifest.json").read_text())
    texts = [c.index_text for c in chunks]

    embedder = make_embedder(settings)
    if manifest["embedder"] != embedder.name:
        raise ValueError(
            f"Index was built with {manifest['embedder']} but HELIX_EMBEDDER gives {embedder.name}; re-run ingest"
        )
    if isinstance(embedder, LocalEmbedder):
        embedder.fit(texts)  # deterministic: same chunks + seed -> same projection
    store = NumpyStore()
    store.load([c.chunk_id for c in chunks], d / "vectors.npy")
    if settings.pinecone_host:
        store = PineconeStore(settings.pinecone_api_key, settings.pinecone_host)
    return Index(chunks, embedder, store, BM25(texts), manifest)


def load_or_build(settings: Settings | None = None) -> Index:
    settings = settings or Settings()
    try:
        return load_index(settings)
    except (FileNotFoundError, ValueError):
        return build_index(settings)


__all__ = ["Index", "build_index", "load_index", "load_or_build", "save_index"]
