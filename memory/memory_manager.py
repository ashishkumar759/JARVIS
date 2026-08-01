from datetime import datetime

from memory.sqlite_store import SQLiteStore
from memory.chroma_store import ChromaStore
from memory.storage_policy import StoragePolicy
from memory.embedding_service import EmbeddingService


# Below this Chroma distance, two texts are treated as the same fact
# already stored (catches paraphrases, not just exact strings).
# Tuned for all-MiniLM-L6-v2 cosine distance; re-check if the embedding
# model changes.
DUPLICATE_DISTANCE_THRESHOLD = 0.08

# Below this distance, a fact marked is_correction=True is considered
# to be updating THIS existing memory (same topic), not an unrelated
# new fact that merely happens to be a correction of something else.
CORRECTION_DISTANCE_THRESHOLD = 0.35


class MemoryManager:
    """
    Coordinates all memory operations.

    Responsibilities:
    - Decide whether a message holds zero, one, or several storable facts.
    - Detect duplicate memories, both exact and near-paraphrase.
    - Apply corrections by updating the existing memory instead of
      appending a contradictory new one.
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

    def _is_semantic_duplicate(self, text: str) -> bool:
        """
        Catches near-duplicates an exact string match would miss, e.g.
        "I like black coffee" vs "I love black coffee" vs re-phrasings
        the classifier itself produces across separate turns.
        """
        results = self.chroma_store.search(text, top_k=1)

        if not results:
            return False

        return results[0]["distance"] < DUPLICATE_DISTANCE_THRESHOLD

    def _apply_correction(self, fact: str, category: str) -> bool:
        """
        For facts marked is_correction=True: find the closest existing
        memory and overwrite it in place, rather than inserting a new
        row that contradicts the old one (e.g. two different birthdays
        both sitting in memory and both being fed to the model as
        "authoritative facts").

        Returns True if an existing memory was found and updated,
        False if nothing close enough existed (caller should then
        fall through to a normal insert).
        """
        results = self.chroma_store.search(fact, top_k=1)

        if not results or results[0]["distance"] > CORRECTION_DISTANCE_THRESHOLD:
            return False

        old_id = results[0]["memory_id"]

        # created_at is intentionally left as-is by update_memory --
        # a correction changes what is known, not when it was first learned.
        self.sqlite_store.update_memory(
            int(old_id),
            content=fact,
            category=category
        )

        self.chroma_store.update_memory(
            memory_id=old_id,
            text=fact,
            metadata={"category": category}
        )

        return True

    def store_memory(self, content: str, history: str = ""):
        """
        Classifies the message and stores every fact that passes both
        the LLM's judgement and the code-level validation in
        StoragePolicy. A single message can contain zero, one, or
        multiple storable facts.

        Args:
            content: the current user message.
            history: recent conversation turns as plain text, passed
                through to the classifier to help it resolve pronouns
                like "you"/"your" (e.g. a fact about the assistant vs.
                a fact about the user). Never mined for facts itself.

        Returns a list of memory_ids that were newly stored or updated
        (empty list if nothing in the message was worth storing).
        """

        classification = self.storage_policy.classify(content, history=history)
        facts = classification.get("facts", [])

        if not facts:
            print("No storable facts in message:", content)
            return []

        stored_ids = []

        for fact_data in facts:
            fact = fact_data["content"]
            category = fact_data["category"]
            is_correction = fact_data["is_correction"]

            if is_correction and self._apply_correction(fact, category):
                print("Updated existing memory via correction:", fact)
                continue

            # Prevent exact duplicate memories
            if self.sqlite_store.memory_exists(fact):
                print("Memory already exists. Skipping storage:", fact)
                continue

            # Prevent near-duplicate (paraphrase) memories
            if self._is_semantic_duplicate(fact):
                print("Semantic duplicate detected. Skipping storage:", fact)
                continue

            # Compute once, pass to both stores, so SQLite's created_at
            # and Chroma's metadata created_at refer to the exact same
            # instant instead of two independent datetime.now() calls
            # a few milliseconds apart.
            created_at = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

            memory_id = self.sqlite_store.add_memory(
                content=fact,
                category=category,
                created_at=created_at
            )

            self.chroma_store.add_memory(
                memory_id=str(memory_id),
                text=fact,
                metadata={
                    "category": category,
                    "created_at": created_at
                }
            )

            stored_ids.append(memory_id)

        return stored_ids

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

            created_at = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

        # Store in SQLite
            memory_id = self.sqlite_store.add_memory(
                content=content,
                category="journal",
                created_at=created_at
            )

        # Store embedding in Chroma
            self.chroma_store.add_memory(
                memory_id=str(memory_id),
                text=content,
                metadata={
                    "category": "journal",
                    "created_at": created_at
                }
            )

            return memory_id
