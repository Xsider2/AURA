"""Shared contracts for AURA AI providers."""

from __future__ import annotations

from typing import Literal, Protocol, TypedDict


class ChatMessage(TypedDict):
    """A message in the provider-neutral conversation format."""

    role: Literal["system", "user", "assistant"]
    content: str


class AIProvider(Protocol):
    """Interface implemented by every conversational AI provider."""

    def generate(self, messages: list[ChatMessage]) -> str:
        """Generate an assistant response for the supplied conversation."""
