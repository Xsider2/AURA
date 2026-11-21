"""Native Ollama chat provider for Qwen Thinking models."""

from __future__ import annotations

import json
from urllib.error import HTTPError, URLError
from urllib.request import Request, urlopen

from aura.ai.provider import ChatMessage


class OllamaThinkingProvider:
    """Call Ollama's native chat API and return only the final assistant content."""

    def __init__(
        self,
        *,
        base_url: str,
        model: str,
        timeout: float = 300.0,
        temperature: float = 0.3,
        max_tokens: int = 800,
    ) -> None:
        self.url = f"{base_url.rstrip('/')}/api/chat"
        self.model = model
        self.timeout = timeout
        self.temperature = temperature
        self.max_tokens = max_tokens

    def generate(self, messages: list[ChatMessage]) -> str:
        """Generate a response with thinking enabled, excluding internal reasoning."""
        payload = {
            "model": self.model,
            "messages": messages,
            "think": True,
            "stream": False,
            "options": {
                "temperature": self.temperature,
                "num_predict": self.max_tokens,
            },
        }
        request = Request(
            self.url,
            data=json.dumps(payload, ensure_ascii=False).encode("utf-8"),
            headers={"Content-Type": "application/json"},
            method="POST",
        )

        try:
            with urlopen(request, timeout=self.timeout) as response:
                result = json.loads(response.read().decode("utf-8"))
        except HTTPError as exc:
            details = exc.read().decode("utf-8", errors="replace")
            raise RuntimeError(
                f"Ollama returned HTTP {exc.code}: {details or exc.reason}"
            ) from exc
        except URLError as exc:
            raise RuntimeError(f"Could not connect to Ollama: {exc.reason}") from exc
        except (UnicodeDecodeError, json.JSONDecodeError) as exc:
            raise RuntimeError("Ollama returned an invalid JSON response.") from exc

        message = result.get("message")
        content = message.get("content") if isinstance(message, dict) else None
        if not isinstance(content, str) or not content.strip():
            raise RuntimeError("Ollama Thinking model returned an empty response.")
        return content.strip()
