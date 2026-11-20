"""Provider implementation for OpenAI and OpenAI-compatible APIs."""

from __future__ import annotations

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
        request_messages = [dict(message) for message in messages]
        if self.thinking is not None:
            # Ollama's Qwen3 template switches modes through these prompt tokens.
            for message in reversed(request_messages):
                if message["role"] == "user":
                    directive = "/think" if self.thinking else "/no_think"
                    message["content"] = f"{message['content']} {directive}"
                    break

        response = self._client.chat.completions.create(
            model=self.model,
            messages=request_messages,
            temperature=self.temperature,
            max_tokens=self.max_tokens,
        )
        content = response.choices[0].message.content
        if not content:
            raise RuntimeError("AI provider returned an empty response.")
        return content.strip()
