from PySide6.QtCore import QThread, Signal


class ChatWorker(QThread):
    """
    Runs a chat request in a background thread.

    Signals:
        finished(str): emitted when a reply is received.
        error(str): emitted if an exception occurs.
    """

    finished = Signal(str)
    error = Signal(str)

    def __init__(self, engine, message):
        super().__init__()

        self.engine = engine
        self.message = message

    def run(self):

        try:

            reply = self.engine.send_message(
                self.message
            )

            self.finished.emit(reply)

        except Exception as e:

            self.error.emit(str(e))