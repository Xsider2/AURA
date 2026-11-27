"""Provider implementation for OpenAI and OpenAI-compatible APIs."""

from __future__ import annotations

from collections.abc import Callable

from openai import OpenAI

from aura.ai.provider import ChatMessage


class OpenAICompatibleProvider:
    """Send chat requests to OpenAI and OpenAI-compatible endpoints."""

    def __init__(
        self,
        *,
        api_key: str,
        model: str,
        base_url: str | None = None,
        timeout: float = 300.0,
        temperature: float = 0.7,
        max_tokens: int = 800,
        client: OpenAI | None = None,
    ) -> None:
        self.model = model
        self.temperature = temperature
        self.max_tokens = max_tokens
        self._client = client or OpenAI(
            api_key=api_key,
            base_url=base_url,
            timeout=timeout,
        )

    def generate(self, messages: list[ChatMessage]) -> str:
        """Return the assistant's text response or raise a provider error."""
        response = self._client.chat.completions.create(
            model=self.model,
            messages=messages,
            temperature=self.temperature,
            max_tokens=self.max_tokens,
        )
        choices = getattr(response, "choices", None)
        if not choices:
            raise RuntimeError("AI provider returned an empty response.")

        message = getattr(choices[0], "message", None)
        content = getattr(message, "content", None)
        if not isinstance(content, str) or not content.strip():
            raise RuntimeError("AI provider returned an empty response.")
        return content.strip()

    def generate_stream(
        self,
        messages: list[ChatMessage],
        on_chunk: Callable[[str], None],
    ) -> str:
        """Stream assistant text chunks and return the complete response."""
        stream = self._client.chat.completions.create(
            model=self.model,
            messages=messages,
            temperature=self.temperature,
            max_tokens=self.max_tokens,
            stream=True,
        )
        parts: list[str] = []
        for event in stream:
            choices = getattr(event, "choices", None)
            if not choices:
                continue
            delta = getattr(choices[0], "delta", None)
            content = getattr(delta, "content", None)
            if isinstance(content, str) and content:
                parts.append(content)
                on_chunk(content)

        response = "".join(parts).strip()
        if not response:
            raise RuntimeError("AI provider returned an empty response.")
        return response
