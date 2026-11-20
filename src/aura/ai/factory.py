"""Configuration and construction of the selected AI provider."""

from __future__ import annotations

import math
import os

from dotenv import load_dotenv

from aura.ai.openai_compatible import OpenAICompatibleProvider
from aura.ai.provider import AIProvider


def _generation_settings() -> tuple[float, int]:
    """Read and validate response-generation settings from the environment."""
    try:
        temperature = float(os.getenv("AI_TEMPERATURE", "0.3"))
    except ValueError as exc:
        raise ValueError("AI_TEMPERATURE must be a number between 0 and 2.") from exc

    if not math.isfinite(temperature) or not 0 <= temperature <= 2:
        raise ValueError("AI_TEMPERATURE must be between 0 and 2.")

    try:
        max_tokens = int(os.getenv("AI_MAX_TOKENS", "800"))
    except ValueError as exc:
        raise ValueError("AI_MAX_TOKENS must be an integer between 1 and 8192.") from exc

    if not 1 <= max_tokens <= 8192:
        raise ValueError("AI_MAX_TOKENS must be between 1 and 8192.")

    return temperature, max_tokens


def _request_timeout() -> float:
    """Read and validate the provider request timeout in seconds."""
    try:
        timeout = float(os.getenv("AI_TIMEOUT", "300"))
    except ValueError as exc:
        raise ValueError("AI_TIMEOUT must be a number between 1 and 900 seconds.") from exc

    if not math.isfinite(timeout) or not 1 <= timeout <= 900:
        raise ValueError("AI_TIMEOUT must be between 1 and 900 seconds.")
    return timeout


def create_provider(*, thinking: bool = False) -> AIProvider:
    """Create the provider selected through the environment configuration."""
    load_dotenv()

    provider_name = os.getenv("AI_PROVIDER", "ollama").strip().lower()
    timeout = _request_timeout()
    temperature, max_tokens = _generation_settings()

    if provider_name in {"ollama", "local"}:
        base_url = os.getenv("OLLAMA_BASE_URL", "http://localhost:11434").rstrip("/")
        return OpenAICompatibleProvider(
            api_key="ollama",
            base_url=f"{base_url}/v1",
            model=os.getenv("OLLAMA_MODEL", "llama3.2"),
            timeout=timeout,
            temperature=temperature,
            max_tokens=max_tokens,
            thinking=thinking,
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
            timeout=timeout,
            temperature=temperature,
            max_tokens=max_tokens,
        )

    raise ValueError("Unsupported AI_PROVIDER. Choose 'ollama' (or 'local') or 'openai'.")
