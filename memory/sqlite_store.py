import sqlite3
from datetime import datetime
from pathlib import Path


# Anchored to this file's location rather than a relative path from the
# process's current working directory. A relative default here means the
# app creates (or reads) a different memory.db depending on where it was
# launched from, which is the most likely explanation for byte-identical
# "duplicate" rows silently appearing across sessions.
BASE_DIR = Path(__file__).resolve().parent


class SQLiteStore:

    def __init__(self, db_path=None):

        self.db_path = Path(db_path) if db_path else BASE_DIR / "memory.db"
        self.db_path.parent.mkdir(
            parents=True,
            exist_ok=True
        )

        self._create_tables()

    # ==========================================================
    # Internal Helper
    # ==========================================================

    def _get_connection(self):

        return sqlite3.connect(self.db_path)

    # ==========================================================
    # Database Setup
    # ==========================================================

    def _create_tables(self):

        with self._get_connection() as conn:

            cursor = conn.cursor()

            # NOTE: DEFAULT CURRENT_TIMESTAMP is kept as a safety net.
            # created_at is normally supplied explicitly by add_memory()
            # (in Python, so it matches the timestamp written to Chroma's
            # metadata for the same fact) -- the SQL default only kicks
            # in if a caller ever inserts a row without passing one.
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS memories (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    content TEXT NOT NULL,
                    category TEXT,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """)

            conn.commit()

    # ==========================================================
    # Store Memory
    # ==========================================================

    def add_memory(
        self,
        content,
        category="general",
        created_at=None
    ):
        """
        Args:
            created_at: optional pre-formatted timestamp string. Pass
                this explicitly when the same instant also needs to be
                written to Chroma's metadata, so both stores agree on
                exactly when the fact was learned. If omitted, this
                generates its own timestamp (kept for backward
                compatibility with any direct callers/tests).
        """

        if created_at is None:
            created_at = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

        with self._get_connection() as conn:

            cursor = conn.cursor()

            cursor.execute("""
                INSERT INTO memories
                (content, category, created_at)
                VALUES (?, ?, ?)
            """, (content, category, created_at))

            conn.commit()

            return cursor.lastrowid

    # ==========================================================
    # Update Memory (used for corrections)
    # ==========================================================

    def update_memory(self, memory_id, content, category=None):
        """
        Overwrites an existing memory's content (and optionally its
        category) in place. Used when the classifier marks a new fact
        as is_correction=True, so a corrected fact replaces the old
        one instead of both versions sitting in memory forever.

        created_at is deliberately left untouched here -- a correction
        updates what is known, not when it was first learned. If you'd
        rather track "last modified" separately, that's a follow-up
        (a new column), not something this method should silently do.
        """

        with self._get_connection() as conn:

            cursor = conn.cursor()

            if category is not None:
                cursor.execute("""
                    UPDATE memories
                    SET content = ?, category = ?
                    WHERE id = ?
                """, (content, category, memory_id))
            else:
                cursor.execute("""
                    UPDATE memories
                    SET content = ?
                    WHERE id = ?
                """, (content, memory_id))

            conn.commit()

    # ==========================================================
    # Duplicate Detection
    # ==========================================================

    def memory_exists(self, content):

        with self._get_connection() as conn:

            cursor = conn.cursor()

            cursor.execute("""
                SELECT 1
                FROM memories
                WHERE LOWER(content)=LOWER(?)
                LIMIT 1
            """, (content,))

            return cursor.fetchone() is not None

    # ==========================================================
    # Retrieval
    # ==========================================================

    def get_all_memories(self):

        with self._get_connection() as conn:

            cursor = conn.cursor()

            cursor.execute("""
                SELECT
                    id,
                    content,
                    category,
                    created_at
                FROM memories
                ORDER BY created_at DESC
            """)

            return cursor.fetchall()

    def get_memory(self, memory_id):

        with self._get_connection() as conn:

            cursor = conn.cursor()

            cursor.execute("""
                SELECT
                    id,
                    content,
                    category,
                    created_at
                FROM memories
                WHERE id=?
            """, (memory_id,))

            row = cursor.fetchone()

            if row is None:
                return None

            return {
                "id": row[0],
                "content": row[1],
                "category": row[2],
                "created_at": row[3]
            }

    # ==========================================================
    # Close
    # ==========================================================

    def close(self):
        """
        Kept for compatibility.
        Connections are now managed automatically.
        """
        pass
