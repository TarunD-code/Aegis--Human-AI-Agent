"""
Aegis v2.0 — Session Memory
==============================
In-memory runtime context that tracks the current session's commands,
plans, and decisions. Resets on each session start.

This data is NEVER persisted automatically — it exists only for the
duration of the current Aegis session.
"""

from __future__ import annotations

import logging
from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import Any

logger = logging.getLogger(__name__)


@dataclass
class SessionEntry:
    """A single entry in the session history."""

    timestamp: str
    user_input: str
    plan_summary: str
    approved: bool | None = None  # None = no approval needed
    executed: bool = False


class SessionMemory:
    """
    Stores runtime context for the current Aegis session.

    This is purely in-memory and is reset when Aegis restarts.
    It helps the contextual planner understand what has already
    been done in the current session.
    """

    def __init__(self) -> None:
        """Initialize a fresh session."""
        self._history: list[SessionEntry] = []
        self._session_start: str = datetime.now(tz=timezone.utc).isoformat()
        self._metadata: dict[str, Any] = {}
        
        # Aegis v3.2 Ultimate: Focus Context & Undo History
        self.last_result: Any = None
        self.last_app: str | None = None
        self.last_typed: str | None = None
        self.last_tab: str | None = None  # Browser tab context
        self.active_application: str | None = None  # Aegis v5.1 Jarvis Context
        self.active_file: str | None = None  # Active document/file path
        self.last_download: str | None = None  # Path to last downloaded file
        
        self.browser_context: dict[str, Any] = {
            "last_url": None,
            "last_search": None,
            "active_tab_index": 0
        }
        self.last_rejection_reason: str | None = None
        self.last_error: dict | None = None  # v3.3+ Proactive Recovery context
        self.execution_history: list[dict] = []  # Stack of executed actions for Undo
        
        # Aegis v3.5: Context Memory Threading
        self.conversation_context_id: str | None = None
        self.knowledge_base: dict[str, Any] = {
            "summaries": [],
            "facts": {},
            "decisions": [],
            "tasks": []
        }
        self.last_activity: str = datetime.now(tz=timezone.utc).isoformat()

        logger.info("SessionMemory initialized (v3.5 Human-Like Intelligence).")

    def add_entry(
        self,
        user_input: str,
        plan_summary: str,
        approved: bool | None = None,
        executed: bool = False,
        result: Any = None,
    ) -> None:
        """Record a command interaction in session history."""
        entry = SessionEntry(
            timestamp=datetime.now(tz=timezone.utc).isoformat(),
            user_input=user_input,
            plan_summary=plan_summary,
            approved=approved,
            executed=executed,
        )
        self._history.append(entry)
        
        if result is not None:
            # Aegis v3.0: Smart numeric extraction for chaining
            import re
            if isinstance(result, str):
                numbers = re.findall(r"[-+]?\d*\.\d+|\d+", result)
                if numbers:
                    self.last_result = numbers[-1]
                    logger.debug("Session memory: last_result caught numeric: %s", self.last_result)
                else:
                    self.last_result = result
            else:
                self.last_result = result

        self.last_activity = datetime.now(tz=timezone.utc).isoformat()
        logger.debug(
            "Session entry added: input=%r, approved=%s, executed=%s, result=%s",
            user_input,
            approved,
            executed,
            result
        )

    def get_session_state(self) -> dict[str, Any]:
        """Return the current session state for prompt injection."""
        return {
            "last_result": self.last_result,
            "last_app": self.last_app,
            "active_application": self.active_application,
            "last_typed": self.last_typed,
            "last_tab": self.last_tab,
            "active_file": self.active_file,
            "last_download": self.last_download,
            "browser": self.browser_context,
            "last_rejection_reason": self.last_rejection_reason,
            "last_error": self.last_error,
            "last_input": self.get_last_input(),
            "conversation_id": self.conversation_context_id,
            "knowledge_base": self.knowledge_base,
            "command_count": self.command_count
        }

    def get_recent(self, limit: int = 5) -> list[dict[str, Any]]:
        """Return the most recent session entries as dicts."""
        entries = self._history[-limit:]
        return [
            {
                "timestamp": e.timestamp,
                "user_input": e.user_input,
                "plan_summary": e.plan_summary,
                "approved": e.approved,
                "executed": e.executed,
            }
            for e in entries
        ]

    def get_last_input(self) -> str:
        """Return the last user input, or empty string if none."""
        if self._history:
            return self._history[-1].user_input
        return ""

    def get_last_plan_summary(self) -> str:
        """Return the last plan summary, or empty string if none."""
        if self._history:
            return self._history[-1].plan_summary
        return ""

    @property
    def command_count(self) -> int:
        """Return the number of commands processed in this session."""
        return len(self._history)

    def record_execution(self, action_dict: dict, previous_state: dict) -> None:
        """Record an action execution for future undo potential."""
        self.execution_history.append({
            "action": action_dict,
            "state_before": previous_state,
            "timestamp": datetime.now(tz=timezone.utc).isoformat()
        })

    def pop_last_execution(self) -> dict | None:
        """Pop the last execution record for undo."""
        if self.execution_history:
            return self.execution_history.pop()
        return None

    @property
    def session_start(self) -> str:
        """Return the session start timestamp."""
        return self._session_start

    def set_metadata(self, key: str, value: Any) -> None:
        """Store arbitrary session metadata."""
        self._metadata[key] = value

    def get_metadata(self, key: str, default: Any = None) -> Any:
        """Retrieve session metadata."""
        return self._metadata.get(key, default)

    def reset(self) -> None:
        """Clear all session data and start fresh."""
        self._history.clear()
        self._metadata.clear()
        self._session_start = datetime.now(tz=timezone.utc).isoformat()
        
        # Reset context
        self.last_result = None
        self.last_app = None
        self.active_application = None
        self.last_typed = None
        self.last_tab = None
        self.active_file = None
        self.last_download = None
        self.browser_context = {
            "last_url": None,
            "last_search": None,
            "active_tab_index": 0
        }
        self.last_rejection_reason = None
        self.last_error = None
        # v3.5 Context
        self.conversation_context_id = None
        self.knowledge_base = {"summaries": [], "facts": {}, "decisions": [], "tasks": []}
        self.last_activity = datetime.now(tz=timezone.utc).isoformat()
        
        logger.info("SessionMemory reset.")

    def is_context_stale(self, threshold_minutes: int = 60) -> bool:
        """Check if the context has expired based on inactivity."""
        last = datetime.fromisoformat(self.last_activity)
        now = datetime.now(tz=timezone.utc)
        delta = (now - last).total_seconds() / 60
        return delta > threshold_minutes
