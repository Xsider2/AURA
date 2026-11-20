"""Configuration and construction of the selected AI provider."""

from __future__ import annotations

import os

from dotenv import load_dotenv

from aura.ai.openai_compatible import OpenAICompatibleProvider
from aura.ai.provider import AIProvider


def create_provider() -> AIProvider:
    """Create the provider selected through the environment configuration."""
    load_dotenv()

    provider_name = os.getenv("AI_PROVIDER", "ollama").strip().lower()

    if provider_name in {"ollama", "local"}:
        base_url = os.getenv("OLLAMA_BASE_URL", "http://localhost:11434").rstrip("/")
        return OpenAICompatibleProvider(
            api_key="ollama",
            base_url=f"{base_url}/v1",
            model=os.getenv("OLLAMA_MODEL", "llama3.2"),
        )

    if provider_name == "openai":
        api_key = os.getenv("OPENAI_API_KEY", "").strip()
        if not api_key:
            raise ValueError(
                "AI_PROVIDER is set to 'openai', but OPENAI_API_KEY is not configured."
            )
        return OpenAICompatibleProvider(
            api_key=api_key,
            model=os.getenv("OPENAI_MODEL", "gpt-4o-mini"),
        )

    raise ValueError("Unsupported AI_PROVIDER. Choose 'ollama' (or 'local') or 'openai'.")
