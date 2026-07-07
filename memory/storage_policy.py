class StoragePolicy:
    """
    Decides whether a message should become long-term memory
    and assigns a category.
    """

    def __init__(self):
        self.store_keywords = [
            "i like",
            "i love",
            "i prefer",
            "my birthday",
            "my name",
            "i am",
            "i work",
            "i live",
            "my favourite",
            "remember that",
            "remember this",
            "i have"
        ]

    def should_store(self, message: str) -> bool:
        """
        Returns True if the message should be stored.
        """

        message = message.lower()

        for keyword in self.store_keywords:
            if keyword in message:
                return True

        return False

    def categorize(self, message: str) -> str:
        """
        Returns a category for the memory.
        """

        message = message.lower()

        if "birthday" in message:
            return "personal"

        if any(word in message for word in ["like", "love", "prefer", "favourite"]):
            return "preference"

        if any(word in message for word in ["work", "company", "job"]):
            return "work"

        if any(word in message for word in ["laptop", "pc", "computer", "rtx"]):
            return "device"

        if "remember" in message:
            return "reminder"

        return "general"