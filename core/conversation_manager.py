class ConversationManager:
    """
    Handles the active conversation history.

    Responsibilities:
    - Store user messages
    - Store assistant messages
    - Return conversation history
    - Clear conversation
    """

    def __init__(self):
        self.history = []

    # ==========================================================
    # Add Messages
    # ==========================================================

    def add_user_message(self, message):

        self.history.append(
            {
                "role": "user",
                "content": message
            }
        )

    def add_assistant_message(self, message):

        self.history.append(
            {
                "role": "assistant",
                "content": message
            }
        )

    # ==========================================================
    # Get Conversation
    # ==========================================================

    def get_history(self):

        return self.history

    def get_last_message(self):

        if not self.history:
            return None

        return self.history[-1]

    def get_message_count(self):

        return len(self.history)

    # ==========================================================
    # Conversation Management
    # ==========================================================

    def clear_history(self):

        self.history.clear()