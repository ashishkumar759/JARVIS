from core.jarvis_engine import JarvisEngine
from PySide6.QtCore import Qt
from PySide6.QtWidgets import (
    QLabel,
    QHBoxLayout,
    QMainWindow,
    QPushButton,
    QSizePolicy,
    QStackedWidget,
    QVBoxLayout,
    QWidget,
)

from ui.pages.chat.chat_page import ChatPage
from ui.pages.journal.journal_page import JournalPage
from ui.pages.memory.memory_page import MemoryPage
from ui.pages.settings.settings_page import SettingsPage


class MainWindow(QMainWindow):

    def __init__(self):
        super().__init__()

        self.setWindowTitle("JARVIS")
        self.resize(1200, 750)
        self.setMinimumSize(1000, 650)

        self.engine = JarvisEngine()

        self.setup_ui()

    def setup_ui(self):

        central_widget = QWidget()
        self.setCentralWidget(central_widget)

        root_layout = QHBoxLayout(central_widget)
        root_layout.setContentsMargins(0, 0, 0, 0)
        root_layout.setSpacing(0)

        # ================= Sidebar ================= #

        sidebar = QWidget()
        sidebar.setObjectName("sidebar")
        sidebar.setFixedWidth(220)

        sidebar_layout = QVBoxLayout(sidebar)
        sidebar_layout.setContentsMargins(15, 20, 15, 20)
        sidebar_layout.setSpacing(10)

        title = QLabel("JARVIS")
        title.setAlignment(Qt.AlignCenter)
        title.setStyleSheet(
            "font-size:24px;font-weight:bold;"
        )

        sidebar_layout.addWidget(title)
        sidebar_layout.addSpacing(20)

        self.chat_button = QPushButton("💬  Chat")
        self.journal_button = QPushButton("📓  Journal")
        self.memory_button = QPushButton("🧠  Memories")
        self.settings_button = QPushButton("⚙  Settings")

        sidebar_layout.addWidget(self.chat_button)
        sidebar_layout.addWidget(self.journal_button)
        sidebar_layout.addWidget(self.memory_button)
        sidebar_layout.addWidget(self.settings_button)

        sidebar_layout.addStretch()

        # ================= Pages ================= #

        self.pages = QStackedWidget()

        self.chat_page = ChatPage(self.engine)
        self.journal_page = JournalPage(self.engine)
        self.memory_page = MemoryPage(self.engine)
        self.settings_page = SettingsPage(self.engine)

        self.pages.addWidget(self.chat_page)
        self.pages.addWidget(self.journal_page)
        self.pages.addWidget(self.memory_page)
        self.pages.addWidget(self.settings_page)

        self.pages.setCurrentWidget(self.chat_page)

        # ================= Navigation ================= #

        self.chat_button.clicked.connect(
            lambda: self.show_page(self.chat_page)
        )

        self.journal_button.clicked.connect(
            lambda: self.show_page(self.journal_page)
        )

        self.memory_button.clicked.connect(
            lambda: self.show_page(self.memory_page)
        )

        self.settings_button.clicked.connect(
            lambda: self.show_page(self.settings_page)
        )

        # ================= Assemble ================= #

        root_layout.addWidget(sidebar)
        root_layout.addWidget(self.pages)

        self.pages.setSizePolicy(
            QSizePolicy.Expanding,
            QSizePolicy.Expanding
        )

    def show_page(self, page):

        self.pages.setCurrentWidget(page)