from PySide6.QtWidgets import (
    QWidget,
    QVBoxLayout,
    QLabel,
    QLineEdit,
    QListWidget
)


class MemoryPage(QWidget):

    def __init__(self, engine):
        super().__init__()

        self.engine = engine

        self.setup_ui()

    def setup_ui(self):

        layout = QVBoxLayout(self)

        layout.setContentsMargins(30, 25, 30, 25)
        layout.setSpacing(15)

        title = QLabel("🧠 Memory Explorer")
        title.setObjectName("title")

        subtitle = QLabel(
            "Browse everything JARVIS knows about you."
        )
        subtitle.setObjectName("subtitle")

        self.search_box = QLineEdit()

        self.search_box.setPlaceholderText(
            "Search memories..."
        )

        self.memory_list = QListWidget()

        self.memory_list.addItem(
            "No memories loaded yet."
        )

        layout.addWidget(title)
        layout.addWidget(subtitle)
        layout.addSpacing(10)
        layout.addWidget(self.search_box)
        layout.addWidget(self.memory_list)