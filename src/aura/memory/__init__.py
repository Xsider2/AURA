"""Local SQLite storage for AURA conversation history."""

from __future__ import annotations

import os
import sqlite3
from pathlib import Path

from aura.ai.provider import ChatMessage


def default_database_path() -> Path:
    """Return the per-user application data path without requiring extra packages."""
    local_app_data = os.getenv("LOCALAPPDATA")
    if local_app_data:
        return Path(local_app_data) / "AURA" / "memory.sqlite3"
    return Path.home() / ".local" / "share" / "AURA" / "memory.sqlite3"


class ConversationStore:
    """Persist user and assistant messages in a private local SQLite database."""

    def __init__(self, database_path: Path | str | None = None) -> None:
        self.database_path = Path(database_path) if database_path else default_database_path()
        self.database_path.parent.mkdir(parents=True, exist_ok=True)
        self._initialize()

    def _connect(self) -> sqlite3.Connection:
        connection = sqlite3.connect(self.database_path, timeout=10)
        connection.execute("PRAGMA journal_mode = WAL")
        connection.execute("PRAGMA foreign_keys = ON")
        return connection

    def _initialize(self) -> None:
        with self._connect() as connection:
            connection.execute(
                """
                CREATE TABLE IF NOT EXISTS conversation_messages (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    role TEXT NOT NULL CHECK (role IN ('user', 'assistant')),
                    content TEXT NOT NULL CHECK (length(trim(content)) > 0),
                    created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP
                )
                """
            )
            connection.execute(
                "CREATE INDEX IF NOT EXISTS idx_conversation_messages_id "
                "ON conversation_messages(id)"
            )

    def add_message(self, role: str, content: str) -> None:
        """Save one non-empty user or assistant message."""
        if role not in {"user", "assistant"}:
            raise ValueError("Only user and assistant messages can be stored.")
        if not isinstance(content, str) or not content.strip():
            raise ValueError("Message content must not be empty.")
        with self._connect() as connection:
            connection.execute(
                "INSERT INTO conversation_messages (role, content) VALUES (?, ?)",
                (role, content),
            )

    def load_messages(self, *, limit: int | None = None) -> list[ChatMessage]:
        """Load messages in chronological order, optionally keeping the newest entries."""
        if limit is not None and limit < 1:
            raise ValueError("Message limit must be at least 1.")
        query = "SELECT role, content FROM conversation_messages ORDER BY id"
        parameters: tuple[int, ...] = ()
        if limit is not None:
            query = (
                "SELECT role, content FROM ("
                "SELECT id, role, content FROM conversation_messages "
                "ORDER BY id DESC LIMIT ?"
                ") ORDER BY id"
            )
            parameters = (limit,)
        with self._connect() as connection:
            rows = connection.execute(query, parameters).fetchall()
        return [{"role": role, "content": content} for role, content in rows]

    def clear(self) -> None:
        """Delete all saved conversation messages."""
        with self._connect() as connection:
            connection.execute("DELETE FROM conversation_messages")
