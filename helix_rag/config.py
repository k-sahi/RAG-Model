"""Settings, read from environment variables (and a local .env file if present)."""

from __future__ import annotations

import os
from dataclasses import dataclass
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent


def _load_dotenv(path: Path = ROOT / ".env") -> None:
    if not path.exists():
        return
    for line in path.read_text().splitlines():
        line = line.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue
        key, value = line.split("=", 1)
        os.environ.setdefault(key.strip(), value.strip().strip('"').strip("'"))


_load_dotenv()


def _env(name: str, default: str) -> str:
    return os.environ.get(name, default)


@dataclass
class Settings:
    corpus_dir: Path = Path(_env("HELIX_CORPUS_DIR", str(ROOT / "corpus")))
    index_dir: Path = Path(_env("HELIX_INDEX_DIR", str(ROOT / ".index")))
    cache_dir: Path = Path(_env("HELIX_CACHE_DIR", str(ROOT / ".cache")))

    # Chunking
    chunk_size: int = int(_env("HELIX_CHUNK_SIZE", "900"))  # characters
    chunk_overlap: int = int(_env("HELIX_CHUNK_OVERLAP", "150"))

    # Embeddings: "local" (TF-IDF + SVD, no network) or "openai"
    embedder: str = _env("HELIX_EMBEDDER", "local")
    openai_embedding_model: str = _env("OPENAI_EMBEDDING_MODEL", "text-embedding-3-small")
    local_dims: int = int(_env("HELIX_LOCAL_DIMS", "256"))

    # Retrieval
    candidates: int = int(_env("HELIX_CANDIDATES", "30"))  # per retriever, before fusion
    rrf_k: int = int(_env("HELIX_RRF_K", "60"))
    top_k: int = int(_env("HELIX_TOP_K", "8"))  # max chunks sent to the generator
    max_docs: int = int(_env("HELIX_MAX_DOCS", "3"))
    per_doc: int = int(_env("HELIX_PER_DOC", "3"))
    relative_cutoff: float = float(_env("HELIX_RELATIVE_CUTOFF", "0.75"))  # doc score vs best doc
    chunk_cutoff: float = float(_env("HELIX_CHUNK_CUTOFF", "0.7"))  # chunk score vs its doc's best
    abstain_threshold: float = float(_env("HELIX_ABSTAIN_THRESHOLD", "0.36"))
    reranker: str = _env("HELIX_RERANKER", "local")  # "local" | "llm" | "none"
    query_rewrite: bool = _env("HELIX_QUERY_REWRITE", "0") == "1"

    # Generation: "anthropic", "openai" or "extractive" (no LLM). "auto" picks
    # whichever API key is set, falling back to extractive.
    llm_provider: str = _env("HELIX_LLM_PROVIDER", "auto")
    anthropic_model: str = _env("ANTHROPIC_MODEL", "claude-sonnet-4-5")
    openai_model: str = _env("OPENAI_MODEL", "gpt-4o-mini")

    # Optional Pinecone vector store
    pinecone_host: str = _env("PINECONE_INDEX_HOST", "")

    @property
    def anthropic_api_key(self) -> str:
        return os.environ.get("ANTHROPIC_API_KEY", "")

    @property
    def openai_api_key(self) -> str:
        return os.environ.get("OPENAI_API_KEY", "")

    @property
    def pinecone_api_key(self) -> str:
        return os.environ.get("PINECONE_API_KEY", "")

    def resolved_provider(self) -> str:
        if self.llm_provider != "auto":
            return self.llm_provider
        if self.anthropic_api_key:
            return "anthropic"
        if self.openai_api_key:
            return "openai"
        return "extractive"
