import sqlite3
from pathlib import Path


class SQLiteStore:

    def __init__(self, db_path="memory/memory.db"):

        self.db_path = Path(db_path)
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
        category="general"
    ):

        with self._get_connection() as conn:

            cursor = conn.cursor()

            cursor.execute("""
                INSERT INTO memories
                (content, category)
                VALUES (?, ?)
            """, (content, category))

            conn.commit()

            return cursor.lastrowid

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