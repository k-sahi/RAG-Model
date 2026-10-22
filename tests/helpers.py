"""Shared fixtures: build the real index once per test run (offline, deterministic)."""

from __future__ import annotations

import functools
import shutil
import tempfile
from pathlib import Path

from helix_rag.config import ROOT, Settings
from helix_rag.index import build_index

CORPUS = ROOT / "corpus"


def has_ocr() -> bool:
    return bool(shutil.which("tesseract") and shutil.which("pdftoppm"))


@functools.lru_cache(maxsize=1)
def settings() -> Settings:
    s = Settings()
    s.index_dir = Path(tempfile.mkdtemp(prefix="helix-index-"))
    s.llm_provider = "extractive"
    s.embedder = "local"
    return s


@functools.lru_cache(maxsize=1)
def index():
    return build_index(settings(), save=True)
