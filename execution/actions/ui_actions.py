"""
Aegis v4.0 — UI Action Handlers
=================================
Robust handlers for UI automation using execution/ui_automation.py.
Each action includes verification logic via execution/verification_engine.py.
"""

from __future__ import annotations
import logging
from typing import Any
from execution import ui_automation as ui
from execution.ui_automation.window_focus import focus_window_v5
from vision.ui_inspector import UIInspector
from execution.verification_engine import VerificationEngine, verify_window_focus, verify_typing
from execution.actions.app_actions import ExecutionResult

logger = logging.getLogger(__name__)

verify_engine = VerificationEngine(retries=2)

def focus_application(action) -> ExecutionResult:
    """Focus an application window by title (v5 Robust Engine).."""
    app_name = (action.params.get("application_name") or action.value or "").strip()
    if not app_name:
        return ExecutionResult(success=False, message="No application name provided.", data={"action_type": action.type})

    success, msg = verify_engine.verify_and_retry(
        focus_window_v5,
        lambda: verify_window_focus(app_name),
        app_name
    )
    return ExecutionResult(success=success, message=msg, data={"action_type": action.type})

def type_text(action) -> ExecutionResult:
    """Type text into active window with verification and refocus (v5.1)."""
    text = (action.params.get("text") or action.value or "").strip()
    app_name = action.params.get("application_name") or ""
    
    if not text:
        return ExecutionResult(success=True, message="Nothing to type.", data={"action_type": action.type})

    # Step 1: Initial focus attempt if app_name provides
    if app_name:
        focus_window_v5(app_name)
    
    # Step 2: Verification with one refocus retry
    from execution.ui_automation.core import verify_active_window
    
    if app_name and not verify_active_window(app_name):
        logger.warning(f"Active window verification failed for '{app_name}'. Attempting refocus retry.")
        focus_window_v5(app_name)
        if not verify_active_window(app_name):
             return ExecutionResult(
                 success=False, 
                 message=f"Could not verify '{app_name}' is in focus. Typing aborted for safety.", 
                 data={"action_type": action.type}
             )

    # Aegis v5.0: Browser Shortcut (Ctrl+L) for address bar if in browser context
    app_context = app_name.lower() or "active"
    browsers = ["chrome", "firefox", "edge", "browser"]
    
    if any(b in app_context for b in browsers):
        logger.info(f"Detected browser context ({app_context}). Using address bar shortcut.")
        ui.hotkey(["ctrl", "l"])
        import time
        time.sleep(0.3)

    success, msg = verify_engine.verify_and_retry(
        ui.type_text,
        verify_typing,
        text
    )
    
    # Fallback: If verification failed, just try typing without focus assurance
    if not success:
        logger.warning(f"Typing verification failed. Attempting blind type fallback.")
        ui.type_text(text)
        return ExecutionResult(success=True, message=f"{msg} (Blind fallback applied)", data={"action_type": action.type})
        
    return ExecutionResult(success=success, message=msg, data={"action_type": action.type})

def press_key(action) -> ExecutionResult:
    """Press a single key."""
    key = (action.params.get("key") or action.value or "").strip().lower()
    success = ui.press_key(key)
    return ExecutionResult(success=success, message=f"Pressed '{key}'", data={"action_type": action.type})

def hotkey(action) -> ExecutionResult:
    """Press a key combination."""
    keys = action.params.get("keys", [])
    if not keys and action.value:
        keys = [k.strip().lower() for k in action.value.split("+")]
    
    success = ui.hotkey(keys)
    return ExecutionResult(success=success, message=f"Pressed hotkey: {'+'.join(keys)}", data={"action_type": action.type})

def click(action) -> ExecutionResult:
    """Perform mouse click (Semantic or Coordinate-based)."""
    element_name = action.params.get("element_name") or action.params.get("text")
    application_name = action.params.get("application_name")
    
    # Aegis v7.0: Semantic Click with Vision Fallback
    if element_name and application_name:
        logger.info(f"Attempting semantic click on '{element_name}' in '{application_name}'")
        inspector = UIInspector()
        if inspector.click_element_by_name(application_name, element_name):
            return ExecutionResult(success=True, message=f"Clicked element '{element_name}' via UI tree.", data={"action_type": action.type})
        
        # Vision Fallback
        logger.info(f"UI Tree click failed. Attempting vision click for '{element_name}'")
        from agents.vision_agent import vision_hub
        if vision_hub.click_element_by_text(element_name):
            return ExecutionResult(success=True, message=f"Clicked '{element_name}' via Vision (OCR).", data={"action_type": action.type})
        if vision_hub.click_element_by_class(element_name):
            return ExecutionResult(success=True, message=f"Clicked '{element_name}' via Vision (Object Detection).", data={"action_type": action.type})

    # Coordinate-based Click
    x = action.params.get("x")
    y = action.params.get("y")
    if x is not None and y is not None:
        success = ui.mouse_click(x, y)
        return ExecutionResult(success=success, message=f"Clicked at coordinates ({x}, {y})", data={"action_type": action.type})
    
    return ExecutionResult(
        success=False, 
        message=f"Could not perform click. Missing coordinates or element name '{element_name}' not found.", 
        data={"action_type": action.type}
    )

def move_mouse(action) -> ExecutionResult:
    """Move mouse to coordinates."""
    x = action.params.get("x")
    y = action.params.get("y")
    if x is None or y is None:
        return ExecutionResult(success=False, message="Missing x or y.", data={"action_type": action.type})
    import pyautogui
    pyautogui.moveTo(x, y)
    return ExecutionResult(success=True, message=f"Moved mouse to ({x}, {y})", data={"action_type": action.type})

def move_relative(action) -> ExecutionResult:
    """v7.0: Move mouse relative to screen or current pos."""
    direction = action.params.get("direction", "center").lower()
    percent = int(action.params.get("percent") or action.value or 10)
    
    from execution.ui_automation import move_mouse_relative
    success = move_mouse_relative(direction, percent)
    return ExecutionResult(success=success, message=f"Moved mouse {direction} by {percent}%", data={"action_type": action.type})

def move_relative(action) -> ExecutionResult:
    """v7.0: Move mouse relative to screen or current pos."""
    direction = action.params.get("direction", "center").lower()
    percent = int(action.params.get("percent") or action.value or 10)
    
    success = ui.move_mouse_relative(direction, percent)
    return ExecutionResult(success=success, message=f"Moved mouse {direction} by {percent}%", data={"action_type": action.type})

def wait(action) -> ExecutionResult:
    """Wait for seconds."""
    try:
        sec = float(action.value or action.params.get("seconds") or 1.0)
        import time
        time.sleep(sec)
        return ExecutionResult(success=True, message=f"Waited {sec}s", data={"action_type": action.type})
    except Exception:
        return ExecutionResult(success=False, message="Invalid wait time.")

def get_running_processes(action) -> ExecutionResult:
    """List processes."""
    from core.process_manager import get_running_processes as list_procs
    procs = list_procs(limit=10)
    return ExecutionResult(success=True, message="Retrieved process list.", data={"processes": procs})

def scroll(action) -> ExecutionResult:
    """Scroll mouse wheel."""
    amount = action.params.get("amount") or int(action.value or 0)
    success = ui.scroll(amount)
    return ExecutionResult(success=success, message=f"Scrolled {amount}", data={"action_type": action.type})

def open_new_tab(action) -> ExecutionResult:
    """Simulate Ctrl+T to open a new browser tab."""
    success = ui.hotkey(["ctrl", "t"])
    return ExecutionResult(success=success, message="Opened new tab, Sir.", data={"action_type": action.type})

def scrape_results(action) -> ExecutionResult:
    """Scrape text content from the active window (e.g. search results)."""
    content = ui.scrape_page()
    if content:
        # Limit to first 2000 chars for context safety
        preview = content[:200] + "..." if len(content) > 200 else content
        return ExecutionResult(
            success=True, 
            message=f"Captured page content. Preview: {preview}",
            data={"action_type": action.type, "content": content}
        )
    return ExecutionResult(success=False, message="Could not capture page content, Sir.", data={"action_type": action.type})

def _prompt_next_action_handler(action) -> ExecutionResult:
    return ExecutionResult(success=True, message=action.description or "Ready for next instruction.", data={"action_type": action.type})
