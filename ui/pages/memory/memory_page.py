from PySide6.QtCore import Qt
from PySide6.QtWidgets import (
    QWidget,
    QVBoxLayout,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QListWidget,
    QListWidgetItem,
    QPushButton,
    QMessageBox
)


class MemoryPage(QWidget):

    def __init__(self, engine):
        super().__init__()

        self.engine = engine

        self.setup_ui()
        self.load_memories()
        self.engine.memory_updated.connect(self.refresh_current_view)

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
    # Refresh Helper
    # ==========================================================

    def refresh_current_view(self):
        """
        Re-runs whichever view is currently active. Used both after
        a delete and whenever engine.memory_updated fires from
        elsewhere (e.g. a journal save), so an in-progress search
        isn't silently thrown away in favor of the full list.
        """

        if self.search_box.text().strip():
            self.search_memories()
        else:
            self.load_memories()

    # ==========================================================
    # Row Builder
    # ==========================================================

    def _add_memory_row(self, memory_id, category, content):
        """
        Adds one memory as a list row: its text on the left, and a
        small permanent-delete button on the right.
        """

        item = QListWidgetItem()
        self.memory_list.addItem(item)

        row_widget = QWidget()
        row_layout = QHBoxLayout(row_widget)
        row_layout.setContentsMargins(10, 6, 10, 6)
        row_layout.setSpacing(10)

        label = QLabel(f"[{category}] {content}")
        label.setWordWrap(True)

        delete_button = QPushButton("🗑")
        delete_button.setFixedWidth(36)
        delete_button.setToolTip("Delete this memory permanently")
        delete_button.setStyleSheet("""
            QPushButton {
                background-color: #3a1f1f;
                border: 1px solid #5a2a2a;
                border-radius: 6px;
                padding: 4px;
                text-align: center;
            }
            QPushButton:hover {
                background-color: #6e2b2b;
            }
            QPushButton:pressed {
                background-color: #8c3535;
            }
        """)

        delete_button.clicked.connect(
            lambda checked=False, mid=memory_id: self.delete_memory(mid)
        )

        row_layout.addWidget(label, 1)
        row_layout.addWidget(delete_button, 0)

        item.setSizeHint(row_widget.sizeHint())
        self.memory_list.setItemWidget(item, row_widget)

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

            self._add_memory_row(memory_id, category, content)

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

            self._add_memory_row(
                memory["id"],
                memory["category"],
                memory["content"]
            )

    # ==========================================================
    # Delete Memory
    # ==========================================================

    def delete_memory(self, memory_id):
        """
        Confirms with the user, then permanently deletes the memory
        from every store via the engine. The list refreshes itself
        through engine.memory_updated once the delete succeeds.
        """

        confirm = QMessageBox.question(
            self,
            "Delete Memory",
            "Delete this memory permanently?\n\n"
            "This cannot be undone.",
            QMessageBox.Yes | QMessageBox.No,
            QMessageBox.No
        )

        if confirm != QMessageBox.Yes:
            return

        try:

            self.engine.delete_memory(memory_id)

        except Exception as e:

            QMessageBox.critical(
                self,
                "Error",
                f"Could not delete memory:\n{e}"
            )