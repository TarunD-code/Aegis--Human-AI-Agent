import sqlite3
import logging
from datetime import datetime, timezone
from pathlib import Path

logger = logging.getLogger(__name__)

class UserMemory:
    """
    Persistent key-value store for user-specific facts and information.
    """
    def __init__(self, db_path: str = "memory/user_facts.db"):
        self.db_path = Path(db_path)
        self.db_path.parent.mkdir(parents=True, exist_ok=True)
        self._init_db()

    def _get_connection(self):
        return sqlite3.connect(self.db_path)

    def _init_db(self):
        with self._get_connection() as conn:
            conn.execute("""
                CREATE TABLE IF NOT EXISTS facts (
                    key TEXT PRIMARY KEY,
                    value TEXT,
                    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """)
            conn.commit()

    def remember(self, key: str, value: str):
        """Store or update a fact."""
        with self._get_connection() as conn:
            conn.execute(
                "INSERT OR REPLACE INTO facts (key, value, updated_at) VALUES (?, ?, ?)",
                (key.lower(), value, datetime.now(tz=timezone.utc).isoformat())
            )
            conn.commit()
        logger.info(f"UserMemory: Remembered {key} = {value}")

    def recall(self, key: str) -> str | None:
        """Retrieve a stored fact."""
        with self._get_connection() as conn:
            row = conn.execute("SELECT value FROM facts WHERE key = ?", (key.lower(),)).fetchone()
            return row[0] if row else None

    def forget(self, key: str):
        """Remove a stored fact."""
        with self._get_connection() as conn:
            conn.execute("DELETE FROM facts WHERE key = ?", (key.lower(),))
            conn.commit()
        logger.info(f"UserMemory: Forgot {key}")

    def list_all(self) -> dict:
        """Return all stored facts as a dictionary."""
        with self._get_connection() as conn:
            rows = conn.execute("SELECT key, value FROM facts").fetchall()
            return {row[0]: row[1] for row in rows}

# Global instance
user_memory = UserMemory()
