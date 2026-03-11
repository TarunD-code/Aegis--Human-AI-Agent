"""
Aegis v3.0 — Instance Conflict Resolver
=========================================
Detects if an application instance is already running and prepares
a conflict structure to request user decision.
"""

import logging
from typing import Any
from core.process_manager import is_app_running

logger = logging.getLogger(__name__)


def resolve_instance_conflict(app_name: str) -> dict[str, Any] | None:
    """
    Check for existing instances of app_name.
    Returns a conflict dict if found, else None.
    """
    is_running, windows = is_app_running(app_name)
    
    if not is_running:
        return None

    titles = [w.title for w in windows if hasattr(w, 'title')]
    
    return {
        "conflict": "application_already_running",
        "app_name": app_name,
        "windows": titles,
        "message": f"'{app_name}' is already running with {len(titles)} window(s).",
        "options": ["Reuse existing window", "Open new instance", "Cancel action"]
    }

def handle_conflict_decision(app_name: str, decision: str) -> bool:
    """
    Apply the conflict resolution decision.
    Returns True if execution should proceed (or was handled by reuse), 
    False if operation was cancelled.
    """
    if decision == "cancel":
        logger.info(f"Operation for '{app_name}' cancelled by user.")
        return False
        
    if decision == "reuse":
        from core.process_manager import get_running_windows, focus_window
        windows = get_running_windows(app_name)
        if windows and focus_window(windows[0]):
            logger.info(f"Successfully focused existing '{app_name}' window.")
            return True # Logic in app_actions will see this as 'handled'
    
    # decision == 'new' just falls through to normal opening logic
    return True
