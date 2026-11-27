"""Native Ollama chat provider for Qwen Thinking models."""

from __future__ import annotations

import json
from collections.abc import Callable
from urllib.error import HTTPError, URLError
from urllib.request import Request, urlopen

from aura.ai.provider import ChatMessage


class OllamaThinkingProvider:
    """Call Ollama's native chat API and expose only final assistant content."""

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

    def _request(self, messages: list[ChatMessage], *, stream: bool) -> Request:
        payload = {
            "model": self.model,
            "messages": messages,
            "think": True,
            "stream": stream,
            "options": {
                "temperature": self.temperature,
                "num_predict": self.max_tokens,
            },
        }
        return Request(
            self.url,
            data=json.dumps(payload, ensure_ascii=False).encode("utf-8"),
            headers={"Content-Type": "application/json"},
            method="POST",
        )

    def generate(self, messages: list[ChatMessage]) -> str:
        """Generate a response with thinking enabled, excluding internal reasoning."""
        try:
            with urlopen(self._request(messages, stream=False), timeout=self.timeout) as response:
                result = json.loads(response.read().decode("utf-8"))
        except HTTPError as exc:
            details = exc.read().decode("utf-8", errors="replace")
            raise RuntimeError(f"Ollama returned HTTP {exc.code}: {details or exc.reason}") from exc
        except URLError as exc:
            raise RuntimeError(f"Could not connect to Ollama: {exc.reason}") from exc
        except (UnicodeDecodeError, json.JSONDecodeError) as exc:
            raise RuntimeError("Ollama returned an invalid JSON response.") from exc

        message = result.get("message")
        content = message.get("content") if isinstance(message, dict) else None
        if not isinstance(content, str) or not content.strip():
            raise RuntimeError("Ollama Thinking model returned an empty response.")
        return content.strip()

    def generate_stream(
        self,
        messages: list[ChatMessage],
        on_chunk: Callable[[str], None],
    ) -> str:
        """Stream final answer tokens; never forward the model's private reasoning."""
        parts: list[str] = []
        try:
            with urlopen(self._request(messages, stream=True), timeout=self.timeout) as response:
                for raw_line in response:
                    line = raw_line.decode("utf-8").strip()
                    if not line:
                        continue
                    try:
                        event = json.loads(line)
                    except json.JSONDecodeError as exc:
                        raise RuntimeError("Ollama returned an invalid streaming response.") from exc

                    if event.get("error"):
                        raise RuntimeError(f"Ollama error: {event['error']}")

                    message = event.get("message")
                    content = message.get("content") if isinstance(message, dict) else None
                    if isinstance(content, str) and content:
                        parts.append(content)
                        on_chunk(content)

                    if event.get("done"):
                        break
        except HTTPError as exc:
            details = exc.read().decode("utf-8", errors="replace")
            raise RuntimeError(f"Ollama returned HTTP {exc.code}: {details or exc.reason}") from exc
        except URLError as exc:
            raise RuntimeError(f"Could not connect to Ollama: {exc.reason}") from exc
        except UnicodeDecodeError as exc:
            raise RuntimeError("Ollama returned an invalid UTF-8 streaming response.") from exc

        result = "".join(parts).strip()
        if not result:
            raise RuntimeError("Ollama Thinking model returned an empty response.")
        return result
