"""Main desktop window for the AURA assistant."""

from __future__ import annotations

import html
import sys

from PySide6.QtCore import Qt
from PySide6.QtGui import QFont
from PySide6.QtWidgets import (
    QApplication, QFrame, QHBoxLayout, QLabel, QLineEdit, QMainWindow,
    QPushButton, QSizePolicy, QTextBrowser, QVBoxLayout, QWidget,
)


class MainWindow(QMainWindow):
    """First usable AURA shell: avatar panel, conversation and message input."""

    def __init__(self) -> None:
        super().__init__()
        self.setWindowTitle("AURA — AI Assistant")
        self.resize(1100, 720)
        self.setMinimumSize(820, 560)
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
            '<div><b>AURA</b><br>Привет! Я AURA. Сейчас мы настраиваем мой интерфейс. '
            'Напиши сообщение, чтобы проверить отправку.</div>'
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
        """Append a user message and a clearly marked placeholder response."""
        message = self.message_input.text().strip()
        if not message:
            return
        safe_message = html.escape(message).replace("\n", "<br>")
        self.chat.append(
            f'<div style="margin: 12px 0; padding: 10px; background: #202c45; '
            f'border-radius: 9px;"><b style="color: #aebeff;">Ты</b><br>{safe_message}</div>'
        )
        self.chat.append(
            '<div style="margin: 12px 0; padding: 10px; background: #19283a; '
            'border-radius: 9px;"><b style="color: #8fd9b5;">AURA</b><br>'
            'Сообщение получено. Подключение ИИ будет добавлено на следующем этапе.</div>'
        )
        self.message_input.clear()


def main() -> int:
    """Create and run the Qt application."""
    app = QApplication.instance() or QApplication(sys.argv)
    window = MainWindow()
    window.show()
    return app.exec()
