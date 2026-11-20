"""Configuration and construction of the selected AI provider."""

from __future__ import annotations

import os

from dotenv import load_dotenv

from aura.ai.openai_compatible import OpenAICompatibleProvider
from aura.ai.provider import AIProvider


def _generation_settings() -> tuple[float, int]:
    """Read and validate response-generation settings from the environment."""
    try:
        temperature = float(os.getenv("AI_TEMPERATURE", "0.7"))
    except ValueError as exc:
        raise ValueError("AI_TEMPERATURE must be a number between 0 and 2.") from exc

    if not 0 <= temperature <= 2:
        raise ValueError("AI_TEMPERATURE must be between 0 and 2.")

    try:
        max_tokens = int(os.getenv("AI_MAX_TOKENS", "800"))
    except ValueError as exc:
        raise ValueError("AI_MAX_TOKENS must be an integer between 1 and 8192.") from exc

    if not 1 <= max_tokens <= 8192:
        raise ValueError("AI_MAX_TOKENS must be between 1 and 8192.")

    return temperature, max_tokens


def create_provider() -> AIProvider:
    """Create the provider selected through the environment configuration."""
    load_dotenv()

    provider_name = os.getenv("AI_PROVIDER", "ollama").strip().lower()

    if provider_name in {"ollama", "local"}:
        base_url = os.getenv("OLLAMA_BASE_URL", "http://localhost:11434").rstrip("/")
        temperature, max_tokens = _generation_settings()
        return OpenAICompatibleProvider(
            api_key="ollama",
            base_url=f"{base_url}/v1",
            model=os.getenv("OLLAMA_MODEL", "llama3.2"),
            temperature=temperature,
            max_tokens=max_tokens,
        )

    if provider_name == "openai":
        api_key = os.getenv("OPENAI_API_KEY", "").strip()
        if not api_key:
            raise ValueError(
                "AI_PROVIDER is set to 'openai', but OPENAI_API_KEY is not configured."
            )
        temperature, max_tokens = _generation_settings()
        return OpenAICompatibleProvider(
            api_key=api_key,
            model=os.getenv("OPENAI_MODEL", "gpt-4o-mini"),
            temperature=temperature,
            max_tokens=max_tokens,
        )

    raise ValueError("Unsupported AI_PROVIDER. Choose 'ollama' (or 'local') or 'openai'.")
