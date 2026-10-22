"""One object that ties retrieval and generation together."""

from __future__ import annotations

import time

from .config import Settings
from .generation import Answer, generate
from .index import Index, load_or_build
from .llm import ChatModel, chat_model_from_settings
from .retrieval import Retriever


class RAGPipeline:
    def __init__(self, settings: Settings | None = None, index: Index | None = None, llm: ChatModel | None = None):
        self.settings = settings or Settings()
        self.index = index or load_or_build(self.settings)
        self.llm = llm if llm is not None else chat_model_from_settings(self.settings)
        self.retriever = Retriever(self.index, self.settings, self.llm)

    def ask(self, query: str) -> Answer:
        """Retrieve once and generate from that retrieval. The returned Answer carries
        the RetrievalResult, so evaluation never has to retrieve a second time."""
        t0 = time.perf_counter()
        retrieval = self.retriever.retrieve(query)
        t1 = time.perf_counter()
        answer = generate(retrieval, self.llm)
        t2 = time.perf_counter()
        answer.timings = {"retrieve_ms": round((t1 - t0) * 1000, 1), "generate_ms": round((t2 - t1) * 1000, 1)}
        return answer
