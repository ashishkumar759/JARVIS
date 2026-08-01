from PySide6.QtCore import QThread, Signal


class PlanWorker(QThread):
    """
    Runs "Generate Tomorrow's Plan" in a background thread, mirroring
    ChatWorker, so a slow LLM call never freezes the Journal page.

    Signals:
        finished(str): emitted with the generated plan text.
        error(str): emitted if generation fails (e.g. no journal
            entry available yet, or the LLM backend is unreachable).
    """

    finished = Signal(str)
    error = Signal(str)

    def __init__(self, engine, draft_text):
        super().__init__()

        self.engine = engine
        self.draft_text = draft_text

    def run(self):

        try:

            plan = self.engine.generate_next_day_plan(
                self.draft_text
            )

            self.finished.emit(plan)

        except Exception as e:

            self.error.emit(str(e))
