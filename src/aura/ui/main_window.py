"""Main desktop window for the AURA assistant."""

from __future__ import annotations

import html
import sys

from PySide6.QtCore import Qt
from PySide6.QtGui import QFont
from PySide6.QtWidgets import (
    QApplication,
    QFrame,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QMainWindow,
    QPushButton,
    QSizePolicy,
    QTextBrowser,
    QVBoxLayout,
    QWidget,
)

from aura.ai.provider import ChatMessage
from aura.ai.worker import AIWorker


class MainWindow(QMainWindow):
    """First usable AURA shell: avatar panel, conversation and message input."""

    def __init__(self) -> None:
        super().__init__()
        self.setWindowTitle("AURA — AI Assistant")
        self.resize(1100, 720)
        self.setMinimumSize(820, 560)
        self._messages: list[ChatMessage] = [
            {
                "role": "system",
                "content": (
                    "Ты — AURA, персональный AI-помощник. Отвечай на русском языке, "
                    "если пользователь не попросил другой язык. Будь точной и полезной."
                ),
            }
        ]
        self._worker: AIWorker | None = None
        self._build_ui()

    def _build_ui(self) -> None:
        root = QWidget()
        root.setObjectName("root")
        layout = QHBoxLayout(root)
        layout.setContentsMargins(22, 22, 22, 22)
        layout.setSpacing(18)

        sidebar = QFrame()
        sidebar.setObjectName("sidebar")
        sidebar.setFixedWidth(280)
        side_layout = QVBoxLayout(sidebar)
        side_layout.setContentsMargins(20, 24, 20, 20)
        side_layout.setSpacing(14)

        brand = QLabel("A U R A")
        brand.setObjectName("brand")
        brand.setAlignment(Qt.AlignmentFlag.AlignCenter)
        side_layout.addWidget(brand)

        avatar = QLabel("A")
        avatar.setObjectName("avatar")
        avatar.setAlignment(Qt.AlignmentFlag.AlignCenter)
        avatar.setFixedSize(150, 150)
        avatar.setFont(QFont("Segoe UI", 54, QFont.Weight.Light))
        side_layout.addWidget(avatar, alignment=Qt.AlignmentFlag.AlignHCenter)

        assistant_name = QLabel("AURA")
        assistant_name.setObjectName("assistantName")
        assistant_name.setAlignment(Qt.AlignmentFlag.AlignCenter)
        side_layout.addWidget(assistant_name)

        status = QLabel("●  Интерфейс готов к работе")
        status.setObjectName("status")
        status.setAlignment(Qt.AlignmentFlag.AlignCenter)
        side_layout.addWidget(status)
        side_layout.addStretch()

        hint = QLabel("Твой персональный\nAI-помощник")
        hint.setObjectName("hint")
        hint.setAlignment(Qt.AlignmentFlag.AlignCenter)
        side_layout.addWidget(hint)

        conversation = QFrame()
        conversation.setObjectName("conversation")
        conversation_layout = QVBoxLayout(conversation)
        conversation_layout.setContentsMargins(24, 22, 24, 22)
        conversation_layout.setSpacing(14)

        header = QHBoxLayout()
        title = QLabel("Диалог")
        title.setObjectName("sectionTitle")
        header.addWidget(title)
        header.addStretch()
        self.connection_label = QLabel("Локальный интерфейс")
        self.connection_label.setObjectName("connection")
        header.addWidget(self.connection_label)
        conversation_layout.addLayout(header)

        self.chat = QTextBrowser()
        self.chat.setObjectName("chat")
        self.chat.setOpenExternalLinks(False)
        self.chat.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)
        self.chat.setHtml(
            "<div><b>AURA</b><br>Привет! Я AURA. Сейчас мы настраиваем мой интерфейс. "
            "Напиши сообщение, чтобы проверить отправку.</div>"
        )
        conversation_layout.addWidget(self.chat)

        input_row = QHBoxLayout()
        input_row.setSpacing(10)
        self.message_input = QLineEdit()
        self.message_input.setObjectName("messageInput")
        self.message_input.setPlaceholderText("Напиши сообщение…")
        self.message_input.returnPressed.connect(self.send_message)
        input_row.addWidget(self.message_input)

        self.send_button = QPushButton("Отправить")
        self.send_button.setObjectName("sendButton")
        self.send_button.setCursor(Qt.CursorShape.PointingHandCursor)
        self.send_button.clicked.connect(self.send_message)
        input_row.addWidget(self.send_button)
        conversation_layout.addLayout(input_row)

        layout.addWidget(sidebar)
        layout.addWidget(conversation, 1)
        self.setCentralWidget(root)
        self.setStyleSheet(
            """
            QWidget#root { background: #0c101b; color: #e8ecf7; }
            QFrame#sidebar, QFrame#conversation {
                background: #151c2b; border: 1px solid #263149; border-radius: 18px;
            }
            QLabel#brand { color: #a8b8ff; font-size: 15px; font-weight: 700; letter-spacing: 5px; }
            QLabel#avatar {
                color: #dce4ff; background: #26365b; border: 2px solid #7589d8;
                border-radius: 75px;
            }
            QLabel#assistantName { font-size: 20px; font-weight: 700; }
            QLabel#status { color: #8fd9b5; font-size: 11px; }
            QLabel#hint { color: #8d9ab5; font-size: 13px; }
            QLabel#sectionTitle { font-size: 22px; font-weight: 650; }
            QLabel#connection { color: #8d9ab5; font-size: 11px; }
            QTextBrowser#chat {
                background: #101625; border: 1px solid #263149; border-radius: 12px;
                padding: 12px; color: #e8ecf7; font-size: 14px;
            }
            QLineEdit#messageInput {
                background: #101625; border: 1px solid #34415e; border-radius: 10px;
                padding: 13px; color: #f2f4fb; selection-background-color: #5369b4;
            }
            QLineEdit#messageInput:focus { border: 1px solid #8297ed; }
            QPushButton#sendButton {
                background: #687fe0; color: white; border: none; border-radius: 10px;
                padding: 0 20px; font-weight: 600; min-height: 42px;
            }
            QPushButton#sendButton:hover { background: #7b91ed; }
            QPushButton#sendButton:pressed { background: #5268c4; }
            """
        )

    def send_message(self) -> None:
        """Submit a chat request without blocking the GUI thread."""
        message = self.message_input.text().strip()
        if not message or (self._worker is not None and self._worker.isRunning()):
            return

        safe_message = html.escape(message).replace("\n", "<br>")
        self.chat.append(
            f'<div style="margin: 12px 0; padding: 10px; background: #202c45; '
            f'border-radius: 9px;"><b style="color: #aebeff;">Ты</b><br>{safe_message}</div>'
        )
        self.message_input.clear()
        self.message_input.setEnabled(False)
        self.send_button.setEnabled(False)
        self.connection_label.setText("ИИ обрабатывает запрос…")

        self._messages.append({"role": "user", "content": message})
        request_messages = [self._messages[0], *self._messages[1:][-20:]]
        self._worker = AIWorker(request_messages)
        self._worker.succeeded.connect(self._handle_response)
        self._worker.failed.connect(self._handle_error)
        self._worker.finished.connect(self._worker_finished)
        self._worker.start()

    def _handle_response(self, response: str) -> None:
        """Display and retain a successful assistant response."""
        safe_response = html.escape(response).replace("\n", "<br>")
        self.chat.append(
            f'<div style="margin: 12px 0; padding: 10px; background: #19283a; '
            f'border-radius: 9px;"><b style="color: #8fd9b5;">AURA</b><br>{safe_response}</div>'
        )
        self._messages.append({"role": "assistant", "content": response})

    def _handle_error(self, error: str) -> None:
        """Show a readable error without terminating the application."""
        safe_error = html.escape(error)
        self.chat.append(
            f'<div style="margin: 12px 0; padding: 10px; background: #3a2028; '
            f'border-radius: 9px;"><b style="color: #ff9eaa;">Ошибка ИИ</b><br>{safe_error}</div>'
        )
        self.connection_label.setText("Проверь настройки ИИ")

    def _worker_finished(self) -> None:
        """Restore the input controls after the background task ends."""
        self.message_input.setEnabled(True)
        self.send_button.setEnabled(True)
        if self.connection_label.text() != "Проверь настройки ИИ":
            self.connection_label.setText("ИИ готов")
        self.message_input.setFocus()
        self._worker = None


def main() -> int:
    """Create and run the Qt application."""
    app = QApplication.instance() or QApplication(sys.argv)
    window = MainWindow()
    window.show()
    return app.exec()
