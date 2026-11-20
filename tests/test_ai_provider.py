""""Tests for the provider-neutral AI integration.""""

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
        temperature=0.7,
        max_tokens=800,
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


@pytest.mark.parametrize("thinking", [False, True])
def test_openai_compatible_provider_adds_qwen_thinking_directive(thinking):
    client = Mock()
    client.chat.completions.create.return_value = SimpleNamespace(
        choices=[SimpleNamespace(message=SimpleNamespace(content="Ответ"))]
    )
    messages = [
        {"role": "system", "content": "Ты — AURA."},
        {"role": "user", "content": "Привет"},
    ]
    provider = OpenAICompatibleProvider(
        api_key="ollama",
        model="qwen3:4b",
        thinking=thinking,
        client=client,
    )

    provider.generate(messages)

    expected_directive = "/think" if thinking else "/no_think"
    client.chat.completions.create.assert_called_once_with(
        model="qwen3:4b",
        messages=[
            {"role": "system", "content": "Ты — AURA."},
            {"role": "user", "content": f"Привет {expected_directive}"},
        ],
        temperature=0.7,
        max_tokens=800,
    )
    assert messages[-1]["content"] == "Привет"


def test_factory_creates_local_ollama_provider(monkeypatch):
    monkeypatch.setenv("AI_PROVIDER", "ollama")
    monkeypatch.setenv("OLLAMA_BASE_URL", "http://localhost:11434/")
    monkeypatch.setenv("OLLAMA_MODEL", "qwen2.5")
    monkeypatch.setenv("AI_TEMPERATURE", "0.4")
    monkeypatch.setenv("AI_MAX_TOKENS", "1200")
    monkeypatch.setenv("AI_TIMEOUT", "300")

    with patch("aura.ai.factory.OpenAICompatibleProvider") as provider_class:
        provider = create_provider()

    provider_class.assert_called_once_with(
        api_key="ollama",
        base_url="http://localhost:11434/v1",
        model="qwen2.5",
        timeout=300.0,
        temperature=0.4,
        max_tokens=1200,
        thinking=False,
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
    monkeypatch.setenv("AI_TEMPERATURE", "0.7")
    monkeypatch.setenv("AI_MAX_TOKENS", "800")
    monkeypatch.setenv("AI_TIMEOUT", "300")

    with patch("aura.ai.factory.OpenAICompatibleProvider") as provider_class:
        create_provider()

    provider_class.assert_called_once_with(
        api_key="test-key",
        model="gpt-test",
        timeout=300.0,
        temperature=0.7,
        max_tokens=800,
    )


def test_factory_rejects_invalid_generation_settings(monkeypatch):
    monkeypatch.setenv("AI_PROVIDER", "ollama")
    monkeypatch.setenv("AI_TEMPERATURE", "2.5")

    with pytest.raises(ValueError, match="AI_TEMPERATURE"):
        create_provider()

    monkeypatch.setenv("AI_TEMPERATURE", "0.7")
    monkeypatch.setenv("AI_MAX_TOKENS", "0")

    with pytest.raises(ValueError, match="AI_MAX_TOKENS"):
        create_provider()


def test_factory_rejects_unknown_provider(monkeypatch):
    monkeypatch.setenv("AI_PROVIDER", "unknown")

    with pytest.raises(ValueError, match="Unsupported AI_PROVIDER"):
        create_provider()
