"""
Aegis v5.0 — Knowledge Store
=============================
Jarvis-style semantic memory for facts, research, and long-term learning.
"""

from __future__ import annotations
import logging
from typing import List, Dict, Optional
from memory.memory_manager import MemoryManager

logger = logging.getLogger(__name__)

class KnowledgeStore:
    """
    Manages long-term facts and research findings.
    """

    def __init__(self, memory_manager: Optional[MemoryManager] = None):
        self._manager = memory_manager or MemoryManager()

    def store_fact(self, topic: str, summary: str, source: str = "N/A", tags: str = "") -> bool:
        """Commits a fact to long-term memory."""
        try:
            with self._manager._get_connection() as conn:
                conn.execute(
                    "INSERT INTO knowledge (topic, summary, source_url, tags) VALUES (?, ?, ?, ?)",
                    (topic, summary, source, tags)
                )
                conn.commit()
            logger.info(f"Learned new fact about '{topic}'.")
            return True
        except Exception as e:
            logger.error(f"Failed to store fact: {e}")
            return False

    def query_knowledge(self, query: str) -> List[Dict]:
        """Simple keyword search for existing knowledge."""
        try:
            with self._manager._get_connection() as conn:
                # Basic LIKE search for now. Vector search planned for future.
                rows = conn.execute(
                    "SELECT * FROM knowledge WHERE topic LIKE ? OR summary LIKE ? ORDER BY timestamp DESC LIMIT 10",
                    (f"%{query}%", f"%{query}%")
                ).fetchall()
                return [dict(row) for row in rows]
        except Exception as e:
            logger.error(f"Knowledge query failed: {e}")
            return []

    def get_latest_research(self, limit: int = 5) -> List[Dict]:
        """Retrieve most recent research findings."""
        try:
            with self._manager._get_connection() as conn:
                rows = conn.execute(
                    "SELECT * FROM knowledge ORDER BY timestamp DESC LIMIT ?",
                    (limit,)
                ).fetchall()
                return [dict(row) for row in rows]
        except Exception as e:
            logger.error(f"Failed to get recent research: {e}")
            return []
