"""Tests for AURA's system persona and response guidelines."""

from aura.ai.persona import SYSTEM_PROMPT


def test_system_prompt_sets_russian_as_default_for_russian_messages():
    assert "полностью на языке последнего сообщения пользователя" in SYSTEM_PROMPT
    assert "грамотном современном русском языке" in SYSTEM_PROMPT
    assert "Переключайся на другой язык только по явной просьбе" in SYSTEM_PROMPT


def test_system_prompt_defines_aura_personality_and_conversation_style():
    assert "дружелюбная, спокойная, внимательная и компетентная помощница" in SYSTEM_PROMPT
    assert "без чрезмерной фамильярности" in SYSTEM_PROMPT
    assert "Сначала дай прямой ответ" in SYSTEM_PROMPT


def test_system_prompt_requires_honesty_and_respect_for_ai_limitations():
    assert "Не выдумывай факты, источники, действия или результаты" in SYSTEM_PROMPT
    assert "не обладает человеческим сознанием" in SYSTEM_PROMPT
    assert "честно сообщай о неопределённости" in SYSTEM_PROMPT
