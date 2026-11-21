"""Tests for the provider-neutral AI integration."""

import json
from types import SimpleNamespace
from unittest.mock import Mock, patch

import pytest

from aura.ai.factory import create_provider
from aura.ai.ollama import OllamaThinkingProvider
from aura.ai.openai_compatible import OpenAICompatibleProvider


def test_openai_compatible_provider_returns_assistant_content():
    client = Mock()
    client.chat.completions.create.return_value = SimpleNamespace(
        choices=[SimpleNamespace(message=SimpleNamespace(content="  Привет!  "))]
    )
    provider = OpenAICompatibleProvider(api_key="test-key", model="test-model", client=client)

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
    provider = OpenAICompatibleProvider(api_key="test-key", model="test-model", client=client)

    with pytest.raises(RuntimeError, match="empty response"):
        provider.generate([{"role": "user", "content": "Привет"}])


def test_ollama_thinking_provider_returns_content_not_reasoning():
    response = Mock()
    response.__enter__ = Mock(return_value=response)
    response.__exit__ = Mock(return_value=False)
    response.read.return_value = json.dumps(
        {
            "message": {
                "content": "  Final answer  ",
                "thinking": "This private reasoning must not be returned.",
            }
        }
    ).encode("utf-8")
    messages = [{"role": "user", "content": "Привет"}]
    provider = OllamaThinkingProvider(
        base_url="http://localhost:11434/",
        model="qwen3:4b",
        timeout=42,
        temperature=0.4,
        max_tokens=512,
    )

    with patch("aura.ai.ollama.urlopen", return_value=response) as urlopen:
        result = provider.generate(messages)

    assert result == "Final answer"
    request = urlopen.call_args.args[0]
    assert request.full_url == "http://localhost:11434/api/chat"
    payload = json.loads(request.data.decode("utf-8"))
    assert payload == {
        "model": "qwen3:4b",
        "messages": messages,
        "think": True,
        "stream": False,
        "options": {"temperature": 0.4, "num_predict": 512},
    }
    assert urlopen.call_args.kwargs["timeout"] == 42


def test_ollama_thinking_provider_rejects_empty_content_even_with_reasoning():
    response = Mock()
    response.__enter__ = Mock(return_value=response)
    response.__exit__ = Mock(return_value=False)
    response.read.return_value = b'{"message":{"content":"","thinking":"not a response"}}'
    provider = OllamaThinkingProvider(base_url="http://localhost:11434", model="qwen3:4b")

    with (
        patch("aura.ai.ollama.urlopen", return_value=response),
        pytest.raises(RuntimeError, match="empty response"),
    ):
        provider.generate([{"role": "user", "content": "Hello"}])


@pytest.mark.parametrize(
    ("thinking", "expected_model"),
    [(False, "qwen3:4b-instruct"), (True, "qwen3:4b")],
)
def test_factory_selects_local_model_for_thinking_mode(monkeypatch, thinking, expected_model):
    monkeypatch.setattr("aura.ai.factory.load_dotenv", lambda: None)
    monkeypatch.setenv("AI_PROVIDER", "ollama")
    monkeypatch.setenv("OLLAMA_BASE_URL", "http://localhost:11434/")
    monkeypatch.delenv("OLLAMA_MODEL", raising=False)
    monkeypatch.delenv("OLLAMA_THINKING_MODEL", raising=False)
    monkeypatch.setenv("AI_TIMEOUT", "300")
    monkeypatch.setenv("AI_TEMPERATURE", "0.3")
    monkeypatch.delenv("AI_MAX_TOKENS", raising=False)
    monkeypatch.delenv("AI_THINKING_MAX_TOKENS", raising=False)

    if thinking:
        with patch("aura.ai.factory.OllamaThinkingProvider") as provider_class:
            provider = create_provider(thinking=True)
        provider_class.assert_called_once_with(
            base_url="http://localhost:11434",
            model=expected_model,
            timeout=300.0,
            temperature=0.3,
            max_tokens=1600,
        )
    else:
        with patch("aura.ai.factory.OpenAICompatibleProvider") as provider_class:
            provider = create_provider(thinking=False)
        provider_class.assert_called_once_with(
            api_key="ollama",
            base_url="http://localhost:11434/v1",
            model=expected_model,
            timeout=300.0,
            temperature=0.3,
            max_tokens=800,
        )
    assert provider is provider_class.return_value


def test_factory_uses_configured_local_model_names(monkeypatch):
    monkeypatch.setenv("AI_PROVIDER", "ollama")
    monkeypatch.setenv("OLLAMA_MODEL", "custom-instruct")
    monkeypatch.setenv("OLLAMA_THINKING_MODEL", "custom-thinking")

    with patch("aura.ai.factory.OpenAICompatibleProvider") as instruct_class:
        create_provider(thinking=False)
    with patch("aura.ai.factory.OllamaThinkingProvider") as thinking_class:
        create_provider(thinking=True)

    assert instruct_class.call_args.kwargs["model"] == "custom-instruct"
    assert thinking_class.call_args.kwargs["model"] == "custom-thinking"


def test_factory_requires_api_key_for_openai(monkeypatch):
    monkeypatch.setenv("AI_PROVIDER", "openai")
    monkeypatch.delenv("OPENAI_API_KEY", raising=False)

    with pytest.raises(ValueError, match="OPENAI_API_KEY"):
        create_provider()


def test_factory_creates_openai_provider(monkeypatch):
    monkeypatch.setattr("aura.ai.factory.load_dotenv", lambda: None)
    monkeypatch.setenv("AI_PROVIDER", "openai")
    monkeypatch.setenv("OPENAI_API_KEY", "test-key")
    monkeypatch.setenv("OPENAI_MODEL", "gpt-test")
    monkeypatch.setenv("AI_TIMEOUT", "300")
    monkeypatch.setenv("AI_TEMPERATURE", "0.3")
    monkeypatch.delenv("AI_MAX_TOKENS", raising=False)

    with patch("aura.ai.factory.OpenAICompatibleProvider") as provider_class:
        create_provider()

    provider_class.assert_called_once_with(
        api_key="test-key",
        model="gpt-test",
        timeout=300.0,
        temperature=0.3,
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


def test_factory_uses_configured_thinking_token_budget(monkeypatch):
    monkeypatch.setenv("AI_PROVIDER", "ollama")
    monkeypatch.setenv("AI_THINKING_MAX_TOKENS", "2048")

    with patch("aura.ai.factory.OllamaThinkingProvider") as provider_class:
        create_provider(thinking=True)

    assert provider_class.call_args.kwargs["max_tokens"] == 2048


def test_factory_rejects_invalid_thinking_token_budget(monkeypatch):
    monkeypatch.setenv("AI_PROVIDER", "ollama")
    monkeypatch.setenv("AI_THINKING_MAX_TOKENS", "0")

    with pytest.raises(ValueError, match="AI_THINKING_MAX_TOKENS"):
        create_provider(thinking=True)


def test_factory_does_not_require_thinking_budget_for_normal_mode(monkeypatch):
    monkeypatch.setenv("AI_PROVIDER", "ollama")
    monkeypatch.setenv("AI_MAX_TOKENS", "800")
    monkeypatch.setenv("AI_THINKING_MAX_TOKENS", "invalid")

    with patch("aura.ai.factory.OpenAICompatibleProvider") as provider_class:
        create_provider(thinking=False)

    assert provider_class.call_args.kwargs["max_tokens"] == 800
