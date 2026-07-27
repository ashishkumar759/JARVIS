from PySide6.QtWidgets import (
    QWidget,
    QVBoxLayout,
    QHBoxLayout,
    QLabel,
    QTextEdit,
    QLineEdit,
    QPushButton
)

from ui.workers.chat_worker import ChatWorker


class ChatPage(QWidget):

    def __init__(self, engine):
        super().__init__()

        self.engine = engine
        self.worker = None

        self.setup_ui()

    def setup_ui(self):

        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(30, 25, 30, 25)
        main_layout.setSpacing(15)

        title = QLabel("💬 Chat")
        title.setObjectName("title")

        subtitle = QLabel(
            "Talk with your personal AI assistant."
        )
        subtitle.setObjectName("subtitle")

        self.chat_history = QTextEdit()
        self.chat_history.setReadOnly(True)
        self.chat_history.setPlaceholderText(
            "Conversation will appear here..."
        )

        bottom_layout = QHBoxLayout()

        self.message_input = QLineEdit()
        self.message_input.setPlaceholderText(
            "Type your message..."
        )

        self.send_button = QPushButton("Send")

        self.send_button.clicked.connect(
            self.send_message
        )

        self.message_input.returnPressed.connect(
            self.send_message
        )

        bottom_layout.addWidget(self.message_input)
        bottom_layout.addWidget(self.send_button)

        main_layout.addWidget(title)
        main_layout.addWidget(subtitle)
        main_layout.addSpacing(10)
        main_layout.addWidget(self.chat_history)
        main_layout.addLayout(bottom_layout)

    # ==========================================================
    # Send Message
    # ==========================================================

    def send_message(self):

        message = self.message_input.text().strip()

        if not message:
            return

        self.append_message(
            "You",
            message
        )

        self.message_input.clear()

        self.send_button.setEnabled(False)
        self.message_input.setEnabled(False)

        self.worker = ChatWorker(
            self.engine,
            message
        )

        self.worker.finished.connect(
            self.on_reply_received
        )

        self.worker.error.connect(
            self.on_error
        )

        self.worker.start()

    # ==========================================================
    # Worker Callbacks
    # ==========================================================

    def on_reply_received(self, reply):

        self.append_message(
            "JARVIS",
            reply
        )

        self.send_button.setEnabled(True)
        self.message_input.setEnabled(True)
        self.message_input.setFocus()

        self.worker = None

    def on_error(self, error):

        self.append_message(
            "System",
            f"ERROR: {error}"
        )

        self.send_button.setEnabled(True)
        self.message_input.setEnabled(True)
        self.message_input.setFocus()

        self.worker = None

    # ==========================================================
    # Chat Display
    # ==========================================================

    def append_message(self, sender, message):

        self.chat_history.append(
            f"<b>{sender}:</b> {message}"
        )

        scrollbar = self.chat_history.verticalScrollBar()

        scrollbar.setValue(
            scrollbar.maximum()
        )