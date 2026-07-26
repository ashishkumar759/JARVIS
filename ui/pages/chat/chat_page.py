from PySide6.QtWidgets import (
    QWidget,
    QVBoxLayout,
    QHBoxLayout,
    QLabel,
    QTextEdit,
    QLineEdit,
    QPushButton
)


class ChatPage(QWidget):

    def __init__(self, engine):
        super().__init__()

        self.engine = engine

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

        # Connect signals
        self.send_button.clicked.connect(self.send_message)
        self.message_input.returnPressed.connect(self.send_message)

        bottom_layout.addWidget(self.message_input)
        bottom_layout.addWidget(self.send_button)

        main_layout.addWidget(title)
        main_layout.addWidget(subtitle)
        main_layout.addSpacing(10)
        main_layout.addWidget(self.chat_history)
        main_layout.addLayout(bottom_layout)

    def send_message(self):

        message = self.message_input.text().strip()

        if not message:
            return

        # Show user's message
        self.append_message("You", message)

        # Clear input immediately
        self.message_input.clear()

        self.send_button.setEnabled(False)
        self.message_input.setEnabled(False)

        try:
            # Get response from JARVIS
            reply = self.engine.send_message(message)

            # Show JARVIS response
            self.append_message("JARVIS", reply)

        except Exception as e:

            self.append_message(
                "System",
                f"ERROR: {str(e)}"
            )

        finally:
             # Re-enable UI
            self.send_button.setEnabled(True)
            self.message_input.setEnabled(True)

            # Put cursor back in input
            self.message_input.setFocus()

    def append_message(self, sender, message):

        self.chat_history.append(
            f"<b>{sender}:</b> {message}"
        )

        scrollbar = self.chat_history.verticalScrollBar()
        scrollbar.setValue(scrollbar.maximum())