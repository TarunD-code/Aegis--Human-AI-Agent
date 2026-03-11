"""
Aegis v5.4 — Task manager
=========================
Tracks and manages multi-step workflows to ensure continuity across
conversational follow-up commands.
"""

from __future__ import annotations
import logging
from typing import Any

logger = logging.getLogger(__name__)

class TaskManager:
    """
    Manages the lifecycle and state of high-level tasks/workflows.
    Ensures that Aegis understands when it is in the middle of a specific activity.
    """

    def __init__(self) -> None:
        self.active_task: str | None = None
        self.task_state: str | None = None
        self.associated_app: str | None = None
        self.last_update: str | None = None

    def update_task(self, task_type: str, state: str | None = None, app: str | None = None) -> None:
        """
        Update the current active task and its state.
        
        Example: update_task("Writing", "typing", "Notepad")
        """
        self.active_task = task_type
        if state is not None:
            self.task_state = state
        if app is not None:
            self.associated_app = app
        
        from datetime import datetime, timezone
        self.last_update = datetime.now(tz=timezone.utc).isoformat()
        
        logger.info(f"TaskManager: Active Task updated to '{task_type}' (State: {state}, App: {app})")

    def get_context(self) -> dict[str, Any]:
        """Return the current task context for planner injection."""
        return {
            "active_task": self.active_task,
            "task_state": self.task_state,
            "associated_app": self.associated_app
        }

    def reset_task(self) -> None:
        """Clear the current task state."""
        logger.info(f"TaskManager: Resetting active task '{self.active_task}'")
        self.active_task = None
        self.task_state = None
        self.associated_app = None
        self.last_update = None
