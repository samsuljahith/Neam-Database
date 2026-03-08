import sqlite3, json, os
from config import settings

class MetadataStore:
    """SQLite storage for chunk text and metadata."""

    def __init__(self):
        os.makedirs(settings.data_dir, exist_ok=True)
        db = os.path.join(settings.data_dir, "metadata.db")
        self.conn = sqlite3.connect(db, check_same_thread=False)
        self.conn.row_factory = sqlite3.Row
        self._init_db()

    def _init_db(self):
        self.conn.execute("""
            CREATE TABLE IF NOT EXISTS chunks (
                id INTEGER PRIMARY KEY,
                collection TEXT NOT NULL,
                vector_id INTEGER NOT NULL,
                text TEXT NOT NULL,
                source TEXT,
                metadata TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        self.conn.execute("""
            CREATE INDEX IF NOT EXISTS idx_coll
            ON chunks(collection)
        """)
        self.conn.commit()

    def add(self, collection, vector_id, text,
            source=None, metadata=None):
        self.conn.execute(
            """INSERT INTO chunks
               (collection, vector_id, text, source, metadata)
               VALUES (?,?,?,?,?)""",
            (collection, vector_id, text, source,
             json.dumps(metadata) if metadata else None))
        self.conn.commit()

    def get_by_vector_ids(self, collection, vector_ids):
        ph = ",".join("?" * len(vector_ids))
        rows = self.conn.execute(
            f"SELECT * FROM chunks WHERE collection=? AND vector_id IN ({ph})",
            [collection] + vector_ids).fetchall()
        return [dict(r) for r in rows]

    def list_collections(self):
        rows = self.conn.execute(
            "SELECT DISTINCT collection FROM chunks"
        ).fetchall()
        return [r["collection"] for r in rows]
