import sys

from PySide6.QtWidgets import QApplication

from ui.main_window import MainWindow
from ui.styles import get_stylesheet


def main():

    app = QApplication(sys.argv)

    app.setStyleSheet(get_stylesheet())

    window = MainWindow()
    window.show()

    sys.exit(app.exec())


if __name__ == "__main__":
    main()