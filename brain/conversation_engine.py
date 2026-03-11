"""
Aegis v5.2 — Conversation Intelligence Engine
===============================================
Resolves pronouns, contextual references, and follow-up commands
to enable multi-turn continuity.
"""

from __future__ import annotations
import logging
import re
from typing import Any

logger = logging.getLogger(__name__)

class ConversationEngine:
    """
    Handles reference resolution and query expansion for follow-up commands.
    """

    def __init__(self, memory: Any = None):
        self._memory = memory

    def expand_query(self, user_input: str, session_state: dict[str, Any]) -> str:
        """
        Orchestrates reference resolution and continuity expansion.
        """
        expanded = user_input.strip()
        
        # 1. Resolve Continuity (e.g., "again", "continue")
        expanded = self._resolve_continuity(expanded, session_state)
        
        # 2. Resolve References (e.g., "it", "that", "previous result")
        expanded = self._resolve_references(expanded, session_state)
        
        if expanded != user_input:
            logger.info(f"Query expanded: '{user_input}' -> '{expanded}'")
            
        return expanded

    def _resolve_references(self, text: str, state: dict[str, Any]) -> str:
        """
        Resolves pronouns like 'it', 'that', 'result' into values.
        """
        # v5.3: Pull from WorkingMemory if available
        try:
            from core.state import working_memory
            last_result = working_memory.get("last_result")
        except (ImportError, AttributeError):
            last_result = state.get("last_result")

        if last_result is None:
            return text

        # Patterns for "it", "that", "the result", "previous result"
        patterns = [
            (r"\b(the\s+)?(it|that|result|previous result)\b", str(last_result)),
        ]

        resolved = text
        for pattern, replacement in patterns:
            # Only replace if it makes sense (e.g., not inside other words)
            resolved = re.sub(pattern, replacement, resolved, flags=re.IGNORECASE)
            
        return resolved

    def _resolve_continuity(self, text: str, state: dict[str, Any]) -> str:
        """
        Resolves 'again', 'repeat', 'continue' based on last action.
        """
        # "do it again", "write again", "repeat that"
        text_lower = text.lower()
        
        # v5.3 + v5.4: Formal Working Memory & Task Context
        try:
            from core.state import working_memory, task_manager
            active_app = working_memory.get("active_application")
            last_typed = working_memory.get("last_text_written")
            last_search = working_memory.get("last_search_query")
            active_task = task_manager.active_task
        except (ImportError, AttributeError):
            active_app = state.get("active_application") or state.get("last_app")
            last_typed = state.get("last_typed")
            last_search = state.get("browser", {}).get("last_search")
            active_task = None

        # 1. Action Continuity: "write again", "type it again"
        if any(w in text_lower for w in ["again", "repeat", "redo"]):
            if last_typed and ("write" in text_lower or "type" in text_lower):
                return f"type text '{last_typed}' in the active application"
            
            # search it again
            if "search" in text_lower and last_search:
                return f"search the web for '{last_search}'"

            # Generic "do it again" for last result/command if possible
            last_input = state.get("last_input") or ""
            if "do it again" in text_lower or text_lower == "again":
                if active_task == "Writing" and last_typed:
                    return f"type text '{last_typed}'"
                return last_input

        # 2. Process Continuity: "continue"
        if text_lower == "continue":
            if active_task:
                return f"continue with the {active_task} task"
            if active_app:
                return f"continue working in {active_app}"
            return "continue with the previous task"

        return text
