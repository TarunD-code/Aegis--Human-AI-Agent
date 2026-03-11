"""
Aegis v7.0 — Working Memory
=============================
Stores and manages short-term conversational variables and
a ring buffer of recent action history for context-aware planning.
"""

from __future__ import annotations
import logging
from typing import Any
from collections import deque
from datetime import datetime

logger = logging.getLogger(__name__)

class WorkingMemory:
    """
    Manages temporary variables and action history during a conversation.
    v7.0: Includes a context buffer (ring buffer) of recent actions.
    """

    CONTEXT_BUFFER_SIZE = 10

    def __init__(self) -> None:
        self._data: dict[str, Any] = {
            "last_result": None,
            "result": None,
            "math_result_count": 0,
            "last_text_written": None,
            "active_application": None,
            "active_url": None,
            "page_content": None,
            "last_search_query": None,
            "current_task": None,
            "last_action_key": None,
        }
        self._action_history: deque[dict] = deque(maxlen=self.CONTEXT_BUFFER_SIZE)

    def set(self, key: str, value: Any) -> None:
        """Set a variable value. Auto-registers new keys."""
        self._data[key] = value
        logger.debug(f"WorkingMemory updated: {key} = {value}")

    def get(self, key: str, default: Any = None) -> Any:
        """Get a variable value."""
        return self._data.get(key, default)

    def get_all(self) -> dict[str, Any]:
        """Return all stored variables."""
        return self._data.copy()

    def push_action(self, action_type: str, params: dict, result: dict) -> None:
        """
        v7.0: Push an action and its outcome into the context buffer.
        """
        entry = {
            "action_type": action_type,
            "params": params,
            "success": result.get("success", False),
            "message": result.get("message", ""),
            "timestamp": datetime.now().isoformat(),
        }
        self._action_history.append(entry)
        logger.debug(f"Context buffer: pushed {action_type} (buffer size: {len(self._action_history)})")

    def get_recent_actions(self, n: int = 5) -> list[dict]:
        """v7.0: Return the last N actions from the context buffer."""
        return list(self._action_history)[-n:]

    def get_context_summary(self) -> str:
        """v7.0: Return a text summary of recent actions for the planner."""
        if not self._action_history:
            return "No recent actions."
        lines = []
        for entry in list(self._action_history)[-5:]:
            status = "✔" if entry["success"] else "✘"
            lines.append(f"  {status} {entry['action_type']}: {entry['message'][:80]}")
        return "Recent actions:\n" + "\n".join(lines)

    def reset(self) -> None:
        """Clear all temporary variables and history."""
        for key in self._data:
            if key == "math_result_count":
                self._data[key] = 0
            else:
                self._data[key] = None
        self._action_history.clear()
        logger.info("WorkingMemory reset.")
