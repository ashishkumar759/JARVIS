def get_stylesheet():
    return """
    QWidget {
        background-color: #1e1e1e;
        color: white;
        font-family: Segoe UI;
        font-size: 14px;
    }

    QMainWindow {
        background-color: #1e1e1e;
    }

    #sidebar {
        background-color: #2b2b2b;
        border-right: 1px solid #3c3c3c;
    }

    QPushButton {
        background-color: transparent;
        border: none;
        padding: 12px;
        text-align: left;
        border-radius: 8px;
    }

    QPushButton:hover {
        background-color: #3a3a3a;
    }

    QPushButton:pressed {
        background-color: #4a4a4a;
    }

    QLabel#title {
        font-size: 32px;
        font-weight: bold;
    }

    QLabel#subtitle {
        font-size: 16px;
        color: #aaaaaa;
    }
    """