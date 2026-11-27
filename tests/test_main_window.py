"""Smoke tests for the AURA desktop interface."""

import os
from unittest.mock import patch

os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")

import pytest
from PySide6.QtWidgets import QApplication, QMessageBox

from aura.ai.worker import AIWorker
from aura.memory import ConversationStore
from aura.ui.main_window import MainWindow


@pytest.fixture(scope="module")
def qapp():
    app = QApplication.instance() or QApplication([])
    yield app


def test_window_has_expected_controls(qapp, tmp_path):
    window = MainWindow(ConversationStore(tmp_path / "aura.sqlite3"))
    assert window.windowTitle() == "AURA — AI Assistant"
    assert window.message_input is not None
    assert window.send_button.text() == "Отправить"
    assert "Привет! Я AURA." in window.chat.toPlainText()
    window.close()


def test_send_message_starts_background_request_and_clears_input(qapp, tmp_path):
    store = ConversationStore(tmp_path / "aura.sqlite3")
    window = MainWindow(store)
    window.message_input.setText("Проверка AURA")

    with patch.object(AIWorker, "start") as start:
        window.send_message()

    transcript = window.chat.toPlainText()
    assert "Проверка AURA" in transcript
    assert "Сообщение получено." not in transcript
    assert window.message_input.text() == ""
    assert not window.message_input.isEnabled()
    assert store.load_messages() == [{"role": "user", "content": "Проверка AURA"}]
    start.assert_called_once()
    window.close()


def test_assistant_response_is_rendered_as_text(qapp, tmp_path):
    store = ConversationStore(tmp_path / "aura.sqlite3")
    window = MainWindow(store)
    response = "<script>alert('x')</script>"
    window._handle_response(response)

    assert "<script>" not in window.chat.toHtml()
    assert "&lt;script&gt;" in window.chat.toHtml()
    assert window._messages[-1]["role"] == "assistant"
    assert store.load_messages() == [{"role": "assistant", "content": response}]
    window.close()


def test_window_restores_saved_conversation(qapp, tmp_path):
    store = ConversationStore(tmp_path / "aura.sqlite3")
    store.add_message("user", "Запомни этот разговор")
    store.add_message("assistant", "Я сохранила его локально.")

    window = MainWindow(store)

    assert "Запомни этот разговор" in window.chat.toPlainText()
    assert "Я сохранила его локально." in window.chat.toPlainText()
    assert len(window._messages) == 3
    window.close()


def test_clear_history_requires_confirmation_and_deletes_messages(qapp, tmp_path):
    store = ConversationStore(tmp_path / "aura.sqlite3")
    store.add_message("user", "Секретная фраза")
    window = MainWindow(store)

    with patch(
        "aura.ui.main_window.QMessageBox.question",
        return_value=QMessageBox.StandardButton.No,
    ):
        window.clear_history()
    assert store.load_messages() == [{"role": "user", "content": "Секретная фраза"}]

    with patch(
        "aura.ui.main_window.QMessageBox.question",
        return_value=QMessageBox.StandardButton.Yes,
    ):
        window.clear_history()

    assert store.load_messages() == []
    assert len(window._messages) == 1
    assert "История очищена" in window.chat.toPlainText()
    window.close()
