from pathlib import Path
import chromadb

from memory.embedding_service import EmbeddingService


# Anchored to this file's location for the same reason as sqlite_store.py:
# a relative default path depends on the process's cwd at launch time,
# which can silently point different app sessions at different DBs.
BASE_DIR = Path(__file__).resolve().parent


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
        db_path=None
    ):
        db_path = Path(db_path) if db_path else BASE_DIR / "chroma_db"
        db_path.mkdir(parents=True, exist_ok=True)

        self.client = chromadb.PersistentClient(
            path=str(db_path)
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

    def update_memory(self, memory_id: str, text: str, metadata=None):
        """
        Overwrites an existing memory's embedding and text in place.
        Used together with SQLiteStore.update_memory when the classifier
        marks a fact as is_correction=True.
        """

        if metadata is None:
            metadata = {}

        embedding = self.embedding_service.embed(text)

        self.collection.update(
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