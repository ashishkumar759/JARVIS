"""
retrieval.py

Semantic retrieval layer for JARVIS.

Flow:
User Query
    ↓
Chroma Semantic Search
    ↓
Matching Memory IDs
    ↓
SQLite Lookup
    ↓
Return Complete Memory Records
"""

from memory.chroma_store import ChromaStore
from memory.sqlite_store import SQLiteStore


class MemoryRetriever:
    """
    Handles semantic retrieval of memories.
    """

    def __init__(self):
        self.chroma_store = ChromaStore()
        self.sqlite_store = SQLiteStore()

    def search(self, query: str, top_k: int = 5):
        """
        Search for memories relevant to the query.

        Args:
            query (str): User query.
            top_k (int): Number of memories to retrieve.

        Returns:
            list[dict]: Retrieved memory records.
        """

        # Perform semantic search in Chroma
        search_results = self.chroma_store.search(
            query=query,
            top_k=top_k
        )

        if not search_results:
            return []

        retrieved_memories = []

        # search_results should be something like:
        # [
        #     {"memory_id": "1", "distance": 0.12},
        #     {"memory_id": "5", "distance": 0.20}
        # ]

        for result in search_results:

            memory = self.sqlite_store.get_memory(
                int(result["memory_id"])
            )

            if memory:
                retrieved_memories.append(memory)

        return retrieved_memories