"""Smoke tests for the AURA desktop interface."""

import os
from unittest.mock import patch

os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")

import pytest
from PySide6.QtWidgets import QApplication

from aura.ai.worker import AIWorker
from aura.ui.main_window import MainWindow


@pytest.fixture(scope="module")
def qapp():
    app = QApplication.instance() or QApplication([])
    yield app


def test_window_has_expected_controls(qapp):
    window = MainWindow()
    assert window.windowTitle() == "AURA — AI Assistant"
    assert window.message_input is not None
    assert window.send_button.text() == "Отправить"
    assert "Привет! Я AURA." in window.chat.toPlainText()
    window.close()


def test_send_message_starts_background_request_and_clears_input(qapp):
    window = MainWindow()
    window.message_input.setText("Проверка AURA")

    with patch.object(AIWorker, "start") as start:
        window.send_message()

    transcript = window.chat.toPlainText()
    assert "Проверка AURA" in transcript
    assert "Сообщение получено." not in transcript
    assert window.message_input.text() == ""
    assert not window.message_input.isEnabled()
    start.assert_called_once()
    window.close()


def test_assistant_response_is_rendered_as_text(qapp):
    window = MainWindow()
    window._handle_response("<script>alert('x')</script>")

    assert "<script>" not in window.chat.toHtml()
    assert "&lt;script&gt;" in window.chat.toHtml()
    assert window._messages[-1]["role"] == "assistant"
    window.close()
