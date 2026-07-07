import sqlite3
from pathlib import Path


class SQLiteStore:
    def __init__(self, db_path="memory/memory.db"):
        self.db_path = Path(db_path)
        self.db_path.parent.mkdir(parents=True, exist_ok=True)

        self.conn = sqlite3.connect(self.db_path)
        self.cursor = self.conn.cursor()

        self._create_tables()

    def _create_tables(self):
        self.cursor.execute("""
        CREATE TABLE IF NOT EXISTS memories (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            content TEXT NOT NULL,
            category TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
        """)
        self.conn.commit()

    def add_memory(self, content, category="general"):
        self.cursor.execute("""
        INSERT INTO memories (content, category)
        VALUES (?, ?)
        """, (content, category))
        self.conn.commit()

        return self.cursor.lastrowid 

    def get_all_memories(self):
        self.cursor.execute("""
        SELECT id, content, category, created_at
        FROM memories
        ORDER BY created_at DESC
        """)
        return self.cursor.fetchall()
    
    def get_memory(self, memory_id):
        self.cursor.execute("""
            SELECT id, content, category, created_at
            FROM memories
            WHERE id = ?
        """, (memory_id,))

        row = self.cursor.fetchone()

        if row is None:
            return None

        return {
            "id": row[0],
            "content": row[1],
            "category": row[2],
            "created_at": row[3]
        }

    def close(self):
        self.conn.close()