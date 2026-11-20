"""Smoke tests for the initial AURA desktop interface."""

import os

os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")

import pytest
from PySide6.QtWidgets import QApplication

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


def test_send_message_appends_message_and_clears_input(qapp):
    window = MainWindow()
    window.message_input.setText("Проверка AURA")
    window.send_message()
    transcript = window.chat.toPlainText()
    assert "Проверка AURA" in transcript
    assert "Сообщение получено." in transcript
    assert window.message_input.text() == ""
    window.close()
