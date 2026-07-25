from PySide6.QtWidgets import (
    QWidget,
    QVBoxLayout,
    QLabel,
    QComboBox,
    QPushButton,
    QGroupBox,
    QFormLayout
)


class SettingsPage(QWidget):

    def __init__(self, engine):
        super().__init__()

        self.engine = engine

        self.setup_ui()

    def setup_ui(self):

        main_layout = QVBoxLayout(self)

        main_layout.setContentsMargins(30, 25, 30, 25)
        main_layout.setSpacing(20)

        title = QLabel("⚙ Settings")
        title.setObjectName("title")

        subtitle = QLabel(
            "Configure your JARVIS experience."
        )
        subtitle.setObjectName("subtitle")

        main_layout.addWidget(title)
        main_layout.addWidget(subtitle)

        # ---------------- AI Settings ---------------- #

        ai_group = QGroupBox("AI Configuration")

        ai_layout = QFormLayout(ai_group)

        self.model_combo = QComboBox()
        self.model_combo.addItems([
            "llama3.2:latest"
        ])

        ai_layout.addRow("Model:", self.model_combo)

        # ---------------- Theme ---------------- #

        theme_group = QGroupBox("Appearance")

        theme_layout = QFormLayout(theme_group)

        self.theme_combo = QComboBox()

        self.theme_combo.addItems([
            "Dark"
        ])

        theme_layout.addRow("Theme:", self.theme_combo)

        # ---------------- Info ---------------- #

        info_group = QGroupBox("Application")

        info_layout = QFormLayout(info_group)

        version = QLabel("JARVIS v2")

        info_layout.addRow("Version:", version)

        # ---------------- Save ---------------- #

        self.save_button = QPushButton(
            "Save Settings"
        )

        main_layout.addSpacing(10)
        main_layout.addWidget(ai_group)
        main_layout.addWidget(theme_group)
        main_layout.addWidget(info_group)

        main_layout.addStretch()

        main_layout.addWidget(self.save_button)