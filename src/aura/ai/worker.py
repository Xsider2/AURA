"""Background worker for non-blocking AI requests."""

from __future__ import annotations

from openai import OpenAIError
from PySide6.QtCore import QThread, Signal

from aura.ai.factory import create_provider
from aura.ai.provider import ChatMessage


class AIWorker(QThread):
    """Run a provider request outside the GUI thread."""

    succeeded = Signal(str)
    failed = Signal(str)

    def __init__(self, messages: list[ChatMessage], *, thinking: bool = False) -> None:
        super().__init__()
        self.messages = messages
        self.thinking = thinking

    def run(self) -> None:
        try:
            response = create_provider(thinking=self.thinking).generate(self.messages)
        except (OpenAIError, OSError, RuntimeError, ValueError) as exc:
            self.failed.emit(str(exc) or exc.__class__.__name__)
        else:
            self.succeeded.emit(response)
