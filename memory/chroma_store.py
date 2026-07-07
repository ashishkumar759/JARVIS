from pathlib import Path
import chromadb

from memory.embedding_service import EmbeddingService


class ChromaStore:
    """
    Handles all vector database operations.

    Responsibilities:
    - Store embeddings
    - Perform semantic search
    - Return clean search results
    """


    def __init__(
        self,
        embedding_service,
        db_path="memory/chroma_db"
    ):
        Path(db_path).mkdir(parents=True, exist_ok=True)

        self.client = chromadb.PersistentClient(
            path=db_path
        )

        self.embedding_service = embedding_service

        self.collection = self.client.get_or_create_collection(
            name="jarvis_memory"
        )

    def add_memory(self, memory_id: str, text: str, metadata=None):
        """
        Store a memory in ChromaDB.
        """

        if metadata is None:
            metadata = {}

        embedding = self.embedding_service.embed(text)

        self.collection.add(
            ids=[str(memory_id)],
            documents=[text],
            embeddings=[embedding],
            metadatas=[metadata]
        )

    def search(self, query: str, top_k: int = 5):
        """
        Perform semantic search.

        Returns:
            [
                {
                    "memory_id": "1",
                    "distance": 0.12
                },
                ...
            ]
        """

        embedding = self.embedding_service.embed(query)

        results = self.collection.query(
            query_embeddings=[embedding],
            n_results=top_k
        )

        ids = results.get("ids", [[]])[0]
        distances = results.get("distances", [[]])[0]

        formatted_results = []

        for memory_id, distance in zip(ids, distances):
            formatted_results.append({
                "memory_id": memory_id,
                "distance": distance
            })

        return formatted_results