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
            print("Memory rejected:", content)
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





    def store_journal(self, content: str):
            """
            Stores a journal entry explicitly.

            Unlike normal conversation memories, journal entries are
            intentionally saved by the user, so they bypass the
            StoragePolicy classifier.

            Returns:
            memory_id if stored successfully.
            None if the journal already exists.
            """

            content = content.strip()

            if not content:
                return None

        # Prevent duplicate journal entries
            if self.sqlite_store.memory_exists(content):
                print("Journal already exists. Skipping storage.")
                return None

        # Store in SQLite
            memory_id = self.sqlite_store.add_memory(
                content=content,
                category="journal"
            )

        # Store embedding in Chroma
            self.chroma_store.add_memory(
                memory_id=str(memory_id),
                text=content,
                metadata={
                    "category": "journal"
                }
            )

            return memory_id
