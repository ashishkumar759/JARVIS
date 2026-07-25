from PySide6.QtWidgets import (
    QWidget,
    QVBoxLayout,
    QLabel,
    QTextEdit,
    QPushButton
)


class JournalPage(QWidget):

    def __init__(self, engine):
        super().__init__()

        self.engine = engine

        self.setup_ui()

    def setup_ui(self):

        layout = QVBoxLayout(self)

        layout.setContentsMargins(30, 25, 30, 25)
        layout.setSpacing(15)

        title = QLabel("📓 Daily Journal")
        title.setObjectName("title")

        subtitle = QLabel(
            "Write about your day. JARVIS will remember what matters."
        )
        subtitle.setObjectName("subtitle")

        self.journal_editor = QTextEdit()

        self.journal_editor.setPlaceholderText(
            "What happened today?"
        )

        self.save_button = QPushButton(
            "Save Journal"
        )

        layout.addWidget(title)
        layout.addWidget(subtitle)
        layout.addSpacing(10)
        layout.addWidget(self.journal_editor)
        layout.addWidget(self.save_button)