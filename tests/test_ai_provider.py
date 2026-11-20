"""Tests for the provider-neutral AI integration."""

from types import SimpleNamespace
from unittest.mock import Mock, patch

import pytest

from aura.ai.factory import create_provider
from aura.ai.openai_compatible import OpenAICompatibleProvider


def test_openai_compatible_provider_returns_assistant_content():
    client = Mock()
    client.chat.completions.create.return_value = SimpleNamespace(
        choices=[
            SimpleNamespace(
                message=SimpleNamespace(content="  Привет!  "),
            )
        ]
    )
    provider = OpenAICompatibleProvider(
        api_key="test-key",
        model="test-model",
        client=client,
    )

    result = provider.generate([{"role": "user", "content": "Привет"}])

    assert result == "Привет!"
    client.chat.completions.create.assert_called_once_with(
        model="test-model",
        messages=[{"role": "user", "content": "Привет"}],
    )


def test_openai_compatible_provider_rejects_empty_response():
    client = Mock()
    client.chat.completions.create.return_value = SimpleNamespace(
        choices=[SimpleNamespace(message=SimpleNamespace(content=None))]
    )
    provider = OpenAICompatibleProvider(
        api_key="test-key",
        model="test-model",
        client=client,
    )

    with pytest.raises(RuntimeError, match="empty response"):
        provider.generate([{"role": "user", "content": "Привет"}])


def test_factory_creates_local_ollama_provider(monkeypatch):
    monkeypatch.setenv("AI_PROVIDER", "ollama")
    monkeypatch.setenv("OLLAMA_BASE_URL", "http://localhost:11434/")
    monkeypatch.setenv("OLLAMA_MODEL", "qwen2.5")

    with patch("aura.ai.factory.OpenAICompatibleProvider") as provider_class:
        provider = create_provider()

    provider_class.assert_called_once_with(
        api_key="ollama",
        base_url="http://localhost:11434/v1",
        model="qwen2.5",
    )
    assert provider is provider_class.return_value


def test_factory_requires_api_key_for_openai(monkeypatch):
    monkeypatch.setenv("AI_PROVIDER", "openai")
    monkeypatch.delenv("OPENAI_API_KEY", raising=False)

    with pytest.raises(ValueError, match="OPENAI_API_KEY"):
        create_provider()


def test_factory_creates_openai_provider(monkeypatch):
    monkeypatch.setenv("AI_PROVIDER", "openai")
    monkeypatch.setenv("OPENAI_API_KEY", "test-key")
    monkeypatch.setenv("OPENAI_MODEL", "gpt-test")

    with patch("aura.ai.factory.OpenAICompatibleProvider") as provider_class:
        create_provider()

    provider_class.assert_called_once_with(
        api_key="test-key",
        model="gpt-test",
    )


def test_factory_rejects_unknown_provider(monkeypatch):
    monkeypatch.setenv("AI_PROVIDER", "unknown")

    with pytest.raises(ValueError, match="Unsupported AI_PROVIDER"):
        create_provider()
