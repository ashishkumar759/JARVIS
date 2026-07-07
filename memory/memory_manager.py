from memory.sqlite_store import SQLiteStore
from memory.chroma_store import ChromaStore
from memory.storage_policy import StoragePolicy


class MemoryManager:
    """
    Coordinates all memory operations.

    Responsibilities:
    - Decide whether a memory should be stored.
    - Categorize memories.
    - Store structured memory in SQLite.
    - Store semantic memory in Chroma.
    """

    def __init__(self):
        self.sqlite_store = SQLiteStore()
        self.chroma_store = ChromaStore()
        self.storage_policy = StoragePolicy()

    def store_memory(self, content: str):
        """
        Stores a memory if the storage policy approves it.
        Returns the memory ID if stored, otherwise None.
        """

        if not self.storage_policy.should_store(content):
            return None

        category = self.storage_policy.categorize(content)

        memory_id = self.sqlite_store.add_memory(
            content=content,
            category=category
        )

        self.chroma_store.add_memory(
            memory_id=str(memory_id),
            text=content,
            metadata={
                "category": category
            }
        )

        return memory_id