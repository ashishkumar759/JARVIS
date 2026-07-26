from PySide6.QtCore import Qt
from PySide6.QtWidgets import (
    QWidget,
    QVBoxLayout,
    QLabel,
    QTextEdit,
    QPushButton,
    QMessageBox
)


class JournalPage(QWidget):

    def __init__(self, engine):
        super().__init__()

        self.engine = engine

        self.setup_ui()

    def setup_ui(self):

        layout = QVBoxLayout(self)
        layout.setSpacing(15)

        title = QLabel("Daily Journal")
        title.setAlignment(Qt.AlignCenter)
        title.setStyleSheet("""
            font-size:24px;
            font-weight:bold;
        """)

        self.journal_editor = QTextEdit()
        self.journal_editor.setPlaceholderText(
            "Write today's journal here..."
        )

        self.save_button = QPushButton(
            "Save Journal"
        )

        self.save_button.clicked.connect(
            self.save_journal
        )

        layout.addWidget(title)
        layout.addWidget(self.journal_editor)
        layout.addWidget(self.save_button)

    # ==========================================================
    # Save Journal
    # ==========================================================

    def save_journal(self):

        journal_text = (
            self.journal_editor
            .toPlainText()
            .strip()
        )

        if not journal_text:

            QMessageBox.information(
                self,
                "Empty Journal",
                "Please write something first."
            )

            return

        try:

            success = self.engine.save_journal(
                journal_text
            )

            if success:

                QMessageBox.information(
                    self,
                    "Journal Saved",
                    "Your journal has been saved successfully."
                )

                self.journal_editor.clear()

        except Exception as e:

            QMessageBox.critical(
                self,
                "Error",
                str(e)
            )