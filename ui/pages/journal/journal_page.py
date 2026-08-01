from PySide6.QtCore import Qt
from PySide6.QtWidgets import (
    QWidget,
    QVBoxLayout,
    QLabel,
    QTextEdit,
    QPushButton,
    QMessageBox
)

from ui.workers.plan_worker import PlanWorker


class JournalPage(QWidget):

    def __init__(self, engine):
        super().__init__()

        self.engine = engine
        self.plan_worker = None

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
        # Tomorrow's Plan Section
        # ==========================================================

        plan_title = QLabel("Tomorrow's Plan")
        plan_title.setAlignment(Qt.AlignCenter)
        plan_title.setStyleSheet("""
            font-size:18px;
            font-weight:bold;
        """)

        self.generate_plan_button = QPushButton(
            "Generate Tomorrow's Plan"
        )

        self.generate_plan_button.clicked.connect(
            self.generate_plan
        )

        self.plan_output = QTextEdit()
        self.plan_output.setReadOnly(True)
        self.plan_output.setPlaceholderText(
            "Your plan for tomorrow will appear here..."
        )

        self.save_plan_button = QPushButton(
            "Save Plan"
        )
        self.save_plan_button.setEnabled(False)

        self.save_plan_button.clicked.connect(
            self.save_plan
        )

        layout.addSpacing(10)
        layout.addWidget(plan_title)
        layout.addWidget(self.generate_plan_button)
        layout.addWidget(self.plan_output)
        layout.addWidget(self.save_plan_button)

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

    # ==========================================================
    # Generate Tomorrow's Plan
    # ==========================================================

    def generate_plan(self):

        if self.plan_worker is not None:
            # A generation is already running; ignore the extra click
            # instead of starting a second overlapping worker.
            return

        draft_text = (
            self.journal_editor
            .toPlainText()
            .strip()
        )

        self.generate_plan_button.setEnabled(False)
        self.generate_plan_button.setText("Generating...")
        self.save_plan_button.setEnabled(False)

        self.plan_worker = PlanWorker(
            self.engine,
            draft_text
        )

        self.plan_worker.finished.connect(
            self.on_plan_ready
        )

        self.plan_worker.error.connect(
            self.on_plan_error
        )

        self.plan_worker.start()

    def on_plan_ready(self, plan_text):

        self.plan_output.setPlainText(plan_text)

        self.generate_plan_button.setEnabled(True)
        self.generate_plan_button.setText("Generate Tomorrow's Plan")
        self.save_plan_button.setEnabled(True)

        self.plan_worker = None

    def on_plan_error(self, error):

        QMessageBox.critical(
            self,
            "Error",
            error
        )

        self.generate_plan_button.setEnabled(True)
        self.generate_plan_button.setText("Generate Tomorrow's Plan")

        self.plan_worker = None

    # ==========================================================
    # Save Plan
    # ==========================================================

    def save_plan(self):

        plan_text = (
            self.plan_output
            .toPlainText()
            .strip()
        )

        if not plan_text:
            return

        try:

            success = self.engine.save_plan(
                plan_text
            )

            if success:

                QMessageBox.information(
                    self,
                    "Plan Saved",
                    "Tomorrow's plan has been saved."
                )

            else:

                QMessageBox.information(
                    self,
                    "Already Saved",
                    "This plan is already stored."
                )

        except Exception as e:

            QMessageBox.critical(
                self,
                "Error",
                str(e)
            )