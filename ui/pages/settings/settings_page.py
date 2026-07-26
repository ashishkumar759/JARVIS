from PySide6.QtCore import Qt
from PySide6.QtWidgets import (
    QWidget,
    QVBoxLayout,
    QLabel,
    QFormLayout
)


class SettingsPage(QWidget):

    def __init__(self, engine):
        super().__init__()

        self.engine = engine

        self.setup_ui()
        self.load_settings()

    def setup_ui(self):

        layout = QVBoxLayout(self)
        layout.setSpacing(20)

        title = QLabel("Settings")
        title.setAlignment(Qt.AlignCenter)
        title.setStyleSheet("""
            font-size:24px;
            font-weight:bold;
        """)

        layout.addWidget(title)

        self.form = QFormLayout()

        self.model_label = QLabel()
        self.embedding_label = QLabel()
        self.memory_label = QLabel()
        self.backend_label = QLabel()
        self.status_label = QLabel()

        self.form.addRow("Model:", self.model_label)
        self.form.addRow("Embedding Model:", self.embedding_label)
        self.form.addRow("Memory Backend:", self.memory_label)
        self.form.addRow("LLM Backend:", self.backend_label)
        self.form.addRow("Status:", self.status_label)

        layout.addLayout(self.form)
        layout.addStretch()

    def load_settings(self):

        settings = self.engine.get_settings()

        self.model_label.setText(
            settings["model"]
        )

        self.embedding_label.setText(
            settings["embedding_model"]
        )

        self.memory_label.setText(
            settings["memory_backend"]
        )

        self.backend_label.setText(
            settings["llm_backend"]
        )

        self.status_label.setText(
            "🟢 " + settings["status"]
        )