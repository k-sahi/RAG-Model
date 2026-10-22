"""Vector stores: an in-process numpy store (default) and an optional Pinecone store."""

from __future__ import annotations

import numpy as np

from .llm import _post


class NumpyStore:
    """Exact cosine search. At a few thousand chunks this is faster than any network
    round-trip to a hosted index."""

    def __init__(self) -> None:
        self.ids: list[str] = []
        self.vectors = np.zeros((0, 0), dtype=np.float32)

    def upsert(self, ids: list[str], vectors: np.ndarray) -> None:
        self.ids = list(ids)
        self.vectors = vectors.astype(np.float32)

    def query(self, vector: np.ndarray, n: int) -> list[tuple[str, float]]:
        if not self.ids:
            return []
        sims = self.vectors @ vector.astype(np.float32)
        order = np.argsort(-sims)[:n]
        return [(self.ids[i], float(sims[i])) for i in order]

    def save(self, path) -> None:
        np.save(path, self.vectors)

    def load(self, ids: list[str], path) -> None:
        self.ids, self.vectors = list(ids), np.load(path)


class PineconeStore:
    """Thin REST wrapper around a Pinecone serverless index (cosine metric, dims must
    match the embedder). Set PINECONE_API_KEY and PINECONE_INDEX_HOST to use it."""

    def __init__(self, api_key: str, host: str, namespace: str = "helix"):
        if not (api_key and host):
            raise ValueError("PINECONE_API_KEY and PINECONE_INDEX_HOST are required")
        self.host = host if host.startswith("http") else f"https://{host}"
        self.headers = {"Api-Key": api_key, "X-Pinecone-API-Version": "2025-01"}
        self.namespace = namespace

    def upsert(self, ids: list[str], vectors: np.ndarray, batch: int = 100) -> None:
        for i in range(0, len(ids), batch):
            _post(
                f"{self.host}/vectors/upsert",
                self.headers,
                {
                    "namespace": self.namespace,
                    "vectors": [
                        {"id": cid, "values": vec.tolist()} for cid, vec in zip(ids[i : i + batch], vectors[i : i + batch])
                    ],
                },
            )

    def query(self, vector: np.ndarray, n: int) -> list[tuple[str, float]]:
        out = _post(
            f"{self.host}/query",
            self.headers,
            {"namespace": self.namespace, "vector": vector.tolist(), "topK": n, "includeValues": False},
        )
        return [(m["id"], float(m["score"])) for m in out.get("matches", [])]
