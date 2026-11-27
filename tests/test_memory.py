"""Tests for local conversation persistence."""

import sqlite3

import pytest

from aura.memory import ConversationStore, default_database_path


def test_store_persists_messages_between_instances(tmp_path):
    database = tmp_path / "aura.sqlite3"
    first = ConversationStore(database)
    first.add_message("user", "Привет")
    first.add_message("assistant", "Здравствуйте!")

    reopened = ConversationStore(database)

    assert reopened.load_messages() == [
        {"role": "user", "content": "Привет"},
        {"role": "assistant", "content": "Здравствуйте!"},
    ]


def test_store_loads_only_newest_messages_in_chronological_order(tmp_path):
    store = ConversationStore(tmp_path / "aura.sqlite3")
    for index in range(5):
        store.add_message("user", f"Сообщение {index}")

    assert store.load_messages(limit=2) == [
        {"role": "user", "content": "Сообщение 3"},
        {"role": "user", "content": "Сообщение 4"},
    ]


@pytest.mark.parametrize(
    ("role", "content"),
    [
        ("system", "Не сохранять системный промпт"),
        ("user", ""),
        ("assistant", "  "),
    ],
)
def test_store_rejects_invalid_messages(tmp_path, role, content):
    store = ConversationStore(tmp_path / "aura.sqlite3")

    with pytest.raises(ValueError):
        store.add_message(role, content)


def test_store_clear_removes_saved_messages(tmp_path):
    store = ConversationStore(tmp_path / "aura.sqlite3")
    store.add_message("user", "Удалить меня")

    store.clear()

    assert store.load_messages() == []


def test_store_rejects_non_positive_history_limit(tmp_path):
    store = ConversationStore(tmp_path / "aura.sqlite3")

    with pytest.raises(ValueError, match="at least 1"):
        store.load_messages(limit=0)


def test_default_database_path_uses_local_app_data(monkeypatch, tmp_path):
    monkeypatch.setenv("LOCALAPPDATA", str(tmp_path))

    assert default_database_path() == tmp_path / "AURA" / "memory.sqlite3"


def test_database_does_not_accept_empty_content_at_sql_level(tmp_path):
    store = ConversationStore(tmp_path / "aura.sqlite3")

    with pytest.raises(sqlite3.IntegrityError):
        with sqlite3.connect(store.database_path) as connection:
            connection.execute(
                "INSERT INTO conversation_messages (role, content) VALUES (?, ?)",
                ("user", "   "),
            )
