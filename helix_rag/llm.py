"""Minimal REST clients for Anthropic and OpenAI (stdlib only, no SDKs)."""

from __future__ import annotations

import json
import logging
import time
import urllib.error
import urllib.request

log = logging.getLogger(__name__)


class LLMError(RuntimeError):
    pass


def _post(url: str, headers: dict, payload: dict, timeout: float = 60, retries: int = 3) -> dict:
    data = json.dumps(payload).encode("utf-8")
    for attempt in range(retries):
        req = urllib.request.Request(url, data=data, headers={"content-type": "application/json", **headers})
        try:
            with urllib.request.urlopen(req, timeout=timeout) as resp:
                return json.loads(resp.read().decode("utf-8"))
        except urllib.error.HTTPError as exc:
            body = exc.read().decode("utf-8", "replace")[:500]
            if exc.code in (429, 500, 502, 503, 529) and attempt < retries - 1:
                wait = float(exc.headers.get("retry-after") or 2 ** attempt)
                log.warning("LLM API %s, retrying in %.1fs", exc.code, wait)
                time.sleep(wait)
                continue
            raise LLMError(f"HTTP {exc.code} from {url}: {body}") from exc
        except urllib.error.URLError as exc:
            if attempt < retries - 1:
                time.sleep(2 ** attempt)
                continue
            raise LLMError(f"Could not reach {url}: {exc.reason}") from exc
    raise LLMError("unreachable")


class ChatModel:
    """`complete(system, user)` -> text, for either provider."""

    def __init__(self, provider: str, model: str, api_key: str, max_tokens: int = 1024):
        if provider not in ("anthropic", "openai"):
            raise ValueError(f"Unknown provider {provider!r}")
        if not api_key:
            raise LLMError(f"No API key set for {provider}")
        self.provider, self.model, self.api_key, self.max_tokens = provider, model, api_key, max_tokens

    def complete(self, system: str, user: str, temperature: float = 0.0) -> str:
        if self.provider == "anthropic":
            out = _post(
                "https://api.anthropic.com/v1/messages",
                {"x-api-key": self.api_key, "anthropic-version": "2023-06-01"},
                {
                    "model": self.model,
                    "max_tokens": self.max_tokens,
                    "temperature": temperature,
                    "system": system,
                    "messages": [{"role": "user", "content": user}],
                },
            )
            return "".join(b.get("text", "") for b in out.get("content", []) if b.get("type") == "text")
        out = _post(
            "https://api.openai.com/v1/chat/completions",
            {"authorization": f"Bearer {self.api_key}"},
            {
                "model": self.model,
                "max_tokens": self.max_tokens,
                "temperature": temperature,
                "messages": [{"role": "system", "content": system}, {"role": "user", "content": user}],
            },
        )
        return out["choices"][0]["message"]["content"]


def parse_json(text: str) -> dict:
    """Parse the first JSON object in a model response (tolerates ```json fences)."""
    start, end = text.find("{"), text.rfind("}")
    if start == -1 or end <= start:
        raise LLMError(f"No JSON object in model output: {text[:200]!r}")
    return json.loads(text[start : end + 1])


def chat_model_from_settings(settings) -> ChatModel | None:
    provider = settings.resolved_provider()
    if provider == "anthropic":
        return ChatModel("anthropic", settings.anthropic_model, settings.anthropic_api_key)
    if provider == "openai":
        return ChatModel("openai", settings.openai_model, settings.openai_api_key)
    return None
