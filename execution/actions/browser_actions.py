"""
Aegis v5.1 — Browser Action Handlers
=====================================
Direct browser control handlers registered in ACTION_REGISTRY.
"""

from __future__ import annotations
import logging
from browser_automation.browser_controller import BrowserController
from execution.actions.app_actions import ExecutionResult

logger = logging.getLogger(__name__)
browser = BrowserController()

def search_web(action) -> ExecutionResult:
    """Perform direct Google search via browser."""
    query = action.params.get("query") or action.value
    if not query:
        return ExecutionResult(success=False, message="No search query provided.")
    
    browser.search_web(query)
    return ExecutionResult(success=True, message=f"Searching for '{query}', Sir.", data={"action_type": action.type})

def open_url(action) -> ExecutionResult:
    """Open a specific URL directly."""
    url = action.params.get("url") or action.value
    if not url:
        return ExecutionResult(success=False, message="No URL provided.")
    
    browser.open_url(url)
    return ExecutionResult(success=True, message=f"Opening {url} as requested.", data={"action_type": action.type})

def open_new_tab(action) -> ExecutionResult:
    """Open a new browser tab with optional URL."""
    url = action.params.get("url") or "https://www.google.com"
    browser.open_new_tab(url)
    return ExecutionResult(success=True, message="New tab opened, Sir.", data={"action_type": action.type})

def navigate_tab(action) -> ExecutionResult:
    """Switch to next or previous tab."""
    direction = action.params.get("direction", "next")
    browser.navigate_tab(direction)
    return ExecutionResult(success=True, message=f"Switched to {direction} tab.", data={"action_type": action.type})
