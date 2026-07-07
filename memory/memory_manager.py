from memory.sqlite_store import SQLiteStore
from memory.chroma_store import ChromaStore


class MemoryManager:
    """
    Coordinates all memory operations.

    Responsibilities:
    - Save structured memory to SQLite.
    - Save semantic memory to Chroma.
    - Keep both databases synchronized.
    """

    def __init__(self):
        self.sqlite_store = SQLiteStore()
        self.chroma_store = ChromaStore()

    def store_memory(self, content: str, category: str = "general") -> int:
        """
        Store a memory in both SQLite and Chroma.

        Flow:
            1. Save memory in SQLite.
            2. Get generated memory ID.
            3. Save the same memory in Chroma.
            4. Return memory ID.
        """

        # Step 1: Store in SQLite
        memory_id = self.sqlite_store.add_memory(
            content=content,
            category=category
        )

        # Step 2: Store in Chroma
        self.chroma_store.add_memory(
            memory_id=str(memory_id),
            text=content,
            metadata={
                "category": category
            }
        )

        return memory_id

    def get_all_memories(self):
        """
        Return every memory stored in SQLite.
        """

        return self.sqlite_store.get_all_memories()

    def close(self):
        """
        Close database connections.
        """

        self.sqlite_store.close()