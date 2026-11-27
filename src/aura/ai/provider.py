"""Shared contracts for AURA AI providers."""

from __future__ import annotations

from collections.abc import Callable
from typing import Literal, Protocol, TypedDict


class ChatMessage(TypedDict):
    """A message in the provider-neutral conversation format."""

    role: Literal["system", "user", "assistant"]
    content: str


class AIProvider(Protocol):
    """Interface implemented by every conversational AI provider."""

    def generate(self, messages: list[ChatMessage]) -> str:
        """Generate an assistant response for the supplied conversation."""

    def generate_stream(
        self,
        messages: list[ChatMessage],
        on_chunk: Callable[[str], None],
    ) -> str:
        """Stream response fragments and return the complete assistant response."""
