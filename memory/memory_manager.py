from memory.sqlite_store import SQLiteStore
from memory.chroma_store import ChromaStore
from memory.storage_policy import StoragePolicy
from memory.embedding_service import EmbeddingService


class MemoryManager:
    """
    Coordinates all memory operations.

    Responsibilities:
    - Decide whether a memory should be stored.
    - Detect duplicate memories.
    - Categorize memories.
    - Store structured memory in SQLite.
    - Store semantic memory in Chroma.
    """

    def __init__(self, embedding_service, client):
        self.embedding_service = embedding_service

        self.sqlite_store = SQLiteStore()

        self.chroma_store = ChromaStore(
            embedding_service=self.embedding_service
        )

        self.storage_policy = StoragePolicy(client)

    def store_memory(self, content: str):
        """
        Stores a memory if the storage policy approves it.
        Returns the memory ID if stored, otherwise None.
        """

        classification = self.storage_policy.classify(content)

        if not classification["should_store"]:
            return None

        fact = classification["fact"]
        category = classification["category"]

        # Prevent duplicate memories
        if self.sqlite_store.memory_exists(fact):
            print("Memory already exists. Skipping storage.")
            return None

        memory_id = self.sqlite_store.add_memory(
            content=fact,
            category=category
        )

        self.chroma_store.add_memory(
            memory_id=str(memory_id),
            text=fact,
            metadata={
                "category": category
            }
        )

        return memory_id
    
