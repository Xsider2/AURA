"""Provider implementation for OpenAI and OpenAI-compatible APIs."""

from __future__ import annotations

from openai import OpenAI

from aura.ai.provider import ChatMessage


class OpenAICompatibleProvider:
    """Send chat requests to OpenAI-compatible chat completion endpoints."""

    def __init__(
        self,
        *,
        api_key: str,
        model: str,
        base_url: str | None = None,
        timeout: float = 300.0,
        temperature: float = 0.7,
        max_tokens: int = 800,
        thinking: bool | None = None,
        client: OpenAI | None = None,
    ) -> None:
        self.model = model
        self.temperature = temperature
        self.max_tokens = max_tokens
        self.thinking = thinking
        self._client = client or OpenAI(
            api_key=api_key,
            base_url=base_url,
            timeout=timeout,
        )

    def generate(self, messages: list[ChatMessage]) -> str:
        """Return the assistant's text response or raise a provider error."""
        request_options: dict[str, object] = {
            "model": self.model,
            "messages": messages,
            "temperature": self.temperature,
            "max_tokens": self.max_tokens,
        }
        if self.thinking is not None:
            request_options["extra_body"] = {
                "reasoning_effort": "medium" if self.thinking else "none"
            }

        response = self._client.chat.completions.create(**request_options)
        content = response.choices[0].message.content
        if not content:
            raise RuntimeError("AI provider returned an empty response.")
        return content.strip()
