"""Embedding backends.

- `LocalEmbedder`: TF-IDF over word and identifier tokens, reduced with truncated SVD
  (latent semantic analysis). Runs offline in milliseconds and is fully deterministic,
  which is what the tests and CI use.
- `OpenAIEmbedder`: `text-embedding-3-*` over REST, with an on-disk cache keyed by
  content hash so re-ingesting an unchanged corpus costs nothing.
"""

from __future__ import annotations

import hashlib
import json
from pathlib import Path

import numpy as np

from .llm import _post
from .text import tokenize


def _l2(m: np.ndarray) -> np.ndarray:
    norms = np.linalg.norm(m, axis=1, keepdims=True)
    norms[norms == 0] = 1.0
    return m / norms


class LocalEmbedder:
    name = "local-lsa"

    def __init__(self, dims: int = 256, seed: int = 0):
        self.dims, self.seed = dims, seed
        self._vec = None
        self._svd = None

    def fit(self, texts: list[str]) -> "LocalEmbedder":
        from sklearn.decomposition import TruncatedSVD
        from sklearn.feature_extraction.text import TfidfVectorizer

        self._vec = TfidfVectorizer(
            analyzer=tokenize, sublinear_tf=True, min_df=1, norm="l2", dtype=np.float64
        )
        x = self._vec.fit_transform(texts)
        n_components = max(2, min(self.dims, x.shape[0] - 1, x.shape[1] - 1))
        self._svd = TruncatedSVD(n_components=n_components, random_state=self.seed, algorithm="arpack")
        self._svd.fit(x)
        return self

    def embed(self, texts: list[str]) -> np.ndarray:
        if self._vec is None:
            raise RuntimeError("LocalEmbedder must be fit on the corpus first")
        return _l2(self._svd.transform(self._vec.transform(texts)).astype(np.float32))


class OpenAIEmbedder:
    def __init__(self, api_key: str, model: str = "text-embedding-3-small", cache_dir: Path | None = None):
        if not api_key:
            raise ValueError("OPENAI_API_KEY is required for the OpenAI embedder")
        self.api_key, self.model = api_key, model
        self.name = f"openai-{model}"
        self.cache_path = (cache_dir / "embeddings" / f"{model}.json") if cache_dir else None
        self._cache: dict[str, list[float]] = {}
        if self.cache_path and self.cache_path.exists():
            self._cache = json.loads(self.cache_path.read_text())

    def fit(self, texts: list[str]) -> "OpenAIEmbedder":
        return self

    @staticmethod
    def _key(text: str) -> str:
        return hashlib.sha256(text.encode("utf-8")).hexdigest()[:24]

    def embed(self, texts: list[str], batch_size: int = 96) -> np.ndarray:
        missing = [t for t in dict.fromkeys(texts) if self._key(t) not in self._cache]
        for i in range(0, len(missing), batch_size):
            batch = missing[i : i + batch_size]
            out = _post(
                "https://api.openai.com/v1/embeddings",
                {"authorization": f"Bearer {self.api_key}"},
                {"model": self.model, "input": batch},
            )
            for text, item in zip(batch, sorted(out["data"], key=lambda d: d["index"])):
                self._cache[self._key(text)] = item["embedding"]
        if missing and self.cache_path:
            self.cache_path.parent.mkdir(parents=True, exist_ok=True)
            self.cache_path.write_text(json.dumps(self._cache))
        return _l2(np.array([self._cache[self._key(t)] for t in texts], dtype=np.float32))


def make_embedder(settings):
    if settings.embedder == "openai":
        return OpenAIEmbedder(settings.openai_api_key, settings.openai_embedding_model, settings.cache_dir)
    if settings.embedder == "local":
        return LocalEmbedder(settings.local_dims)
    raise ValueError(f"Unknown embedder {settings.embedder!r} (use 'local' or 'openai')")
