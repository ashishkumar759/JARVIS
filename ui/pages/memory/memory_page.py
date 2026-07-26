from PySide6.QtCore import Qt
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
        self.load_memories()

    def setup_ui(self):

        layout = QVBoxLayout(self)
        layout.setSpacing(15)

        # -----------------------------
        # Title
        # -----------------------------

        title = QLabel("Memory Browser")
        title.setAlignment(Qt.AlignCenter)
        title.setStyleSheet("""
            font-size:24px;
            font-weight:bold;
        """)

        # -----------------------------
        # Search
        # -----------------------------

        self.search_box = QLineEdit()
        self.search_box.setPlaceholderText(
            "Search memories..."
        )

        self.search_box.returnPressed.connect(
            self.search_memories
        )

        # -----------------------------
        # Memory List
        # -----------------------------

        self.memory_list = QListWidget()

        # -----------------------------
        # Layout
        # -----------------------------

        layout.addWidget(title)
        layout.addWidget(self.search_box)
        layout.addWidget(self.memory_list)

    # ==========================================================
    # Load All Memories
    # ==========================================================

    def load_memories(self):

        self.memory_list.clear()

        memories = self.engine.get_all_memories()

        if not memories:

            self.memory_list.addItem(
                "No memories stored."
            )

            return

        for memory in memories:

            memory_id = memory[0]
            content = memory[1]
            category = memory[2]

            self.memory_list.addItem(
                f"[{category}] {content}"
            )

    # ==========================================================
    # Search Memories
    # ==========================================================

    def search_memories(self):

        query = self.search_box.text().strip()

        if not query:

            self.load_memories()
            return

        self.memory_list.clear()

        memories = self.engine.search_memories(query)

        if not memories:

            self.memory_list.addItem(
                "No matching memories."
            )

            return

        for memory in memories:

            self.memory_list.addItem(
                f"[{memory['category']}] {memory['content']}"
            )