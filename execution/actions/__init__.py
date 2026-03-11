"""
Aegis v6.3 — Action Registry
==============================
Maps action type strings to their handler functions.
Central dispatch table for the Execution Engine.
All imports are wrapped safely to prevent cascade failures.
"""

import logging

logger = logging.getLogger(__name__)

# Safe import helper
def _safe_import(module_path, attr_name):
    try:
        mod = __import__(module_path, fromlist=[attr_name])
        return getattr(mod, attr_name)
    except (ImportError, AttributeError) as e:
        logger.warning(f"Registry: Could not import {module_path}.{attr_name}: {e}")
        return None

# --- Core Action Handlers ---
from execution.actions.app_actions import open_application
from execution.actions.powershell_actions import run_powershell
from execution.actions.file_actions import (
    create_file,
    list_duplicates,
    organize_files,
    rename_file,
)
from execution.actions import ui_actions
from execution.actions import research_actions
from execution.actions import research_handlers
from execution.actions import browser_actions
from execution.actions import org_actions
from execution.actions import system_actions
from execution.actions.respond_text import respond_text
from execution.actions.media_actions import play_music
from execution.actions.math_actions import compute_result

# --- Browser Controller (v6.3) ---
from browser_automation.browser_controller import browser_controller as _bc

def _bc_search_web(action):
    from execution.actions.app_actions import ExecutionResult
    query = action.params.get("query") or action.value or ""
    ok = _bc.search_web(query)
    return ExecutionResult(success=ok, message=f"Searched web for: {query}", data={"action_type": "search_web"})

def _bc_open_first_result(action):
    from execution.actions.app_actions import ExecutionResult
    query = action.params.get("query") or action.value or ""
    ok = _bc.open_first_result(query)
    return ExecutionResult(success=ok, message=f"Opened first result for: {query}", data={"action_type": "open_first_result"})

def _bc_extract_page_text(action):
    from execution.actions.app_actions import ExecutionResult
    url = action.params.get("url") or action.value or ""
    text = _bc.extract_page_text(url)
    return ExecutionResult(success=bool(text), message=f"Extracted {len(text)} chars.", data={"action_type": "extract_page_text", "content": text})

def _bc_summarize_page(action):
    from execution.actions.app_actions import ExecutionResult
    summary = _bc.summarize_page()
    return ExecutionResult(success=bool(summary), message=summary, data={"action_type": "summarize_page"})

def _bc_browse_to(action):
    from execution.actions.app_actions import ExecutionResult
    url = action.params.get("query") or action.params.get("url") or action.value or ""
    ok = _bc.browse_to(url)
    return ExecutionResult(success=ok, message=f"Navigated to: {url}", data={"action_type": "browse_to"})

def _bc_open_url(action):
    from execution.actions.app_actions import ExecutionResult
    url = action.params.get("url") or action.value or ""
    ok = _bc.open_url(url)
    return ExecutionResult(success=ok, message=f"Opened URL: {url}", data={"action_type": "open_url"})

# --- Vision Agent (safe lazy import) ---
def _vision_click(action):
    from execution.actions.app_actions import ExecutionResult
    try:
        from agents.vision_agent.vision_controller import vision_hub
        target = action.params.get("target") or action.value or ""
        ok = vision_hub.click_element_by_text(target)
        return ExecutionResult(success=ok, message=f"Vision clicked: {target}", data={"action_type": "vision_click"})
    except Exception as e:
        return ExecutionResult(success=False, message=f"Vision click failed: {e}", data={"action_type": "vision_click"})

def _vision_scroll(action):
    from execution.actions.app_actions import ExecutionResult
    try:
        from agents.vision_agent.vision_controller import vision_hub
        direction = action.params.get("direction") or action.value or "down"
        ok = vision_hub.scroll_direction(direction)
        return ExecutionResult(success=ok, message=f"Vision scrolled: {direction}", data={"action_type": "vision_scroll"})
    except Exception as e:
        return ExecutionResult(success=False, message=f"Vision scroll failed: {e}", data={"action_type": "vision_scroll"})

def _vision_read(action):
    from execution.actions.app_actions import ExecutionResult
    try:
        from agents.vision_agent.vision_controller import vision_hub
        region = action.params.get("region")
        text = vision_hub.vision_read(region)
        return ExecutionResult(success=bool(text), message=f"Read {len(text)} chars from screen.", data={"action_type": "vision_read", "content": text})
    except Exception as e:
        return ExecutionResult(success=False, message=f"Vision read failed: {e}", data={"action_type": "vision_read"})

def _vision_locate(action):
    from execution.actions.app_actions import ExecutionResult
    try:
        from agents.vision_agent.vision_controller import vision_hub
        element = action.params.get("element") or action.value or ""
        coords = vision_hub.vision_locate(element)
        if coords:
            return ExecutionResult(success=True, message=f"Located '{element}' at {coords}", data={"action_type": "vision_locate", "coordinates": coords})
        return ExecutionResult(success=False, message=f"Could not locate '{element}'", data={"action_type": "vision_locate"})
    except Exception as e:
        return ExecutionResult(success=False, message=f"Vision locate failed: {e}", data={"action_type": "vision_locate"})

def _capture_screenshot(action):
    from execution.actions.app_actions import ExecutionResult
    try:
        from agents.vision_agent.vision_controller import vision_hub
        filepath = vision_hub.capture_screenshot()
        return ExecutionResult(success=bool(filepath), message=f"Screenshot saved: {filepath}", data={"action_type": "capture_screenshot", "path": filepath})
    except Exception as e:
        return ExecutionResult(success=False, message=f"Screenshot failed: {e}", data={"action_type": "capture_screenshot"})

def _ask_confirmation(action):
    from execution.actions.app_actions import ExecutionResult
    summary = action.params.get("summary") or action.value or "Confirm this action?"
    try:
        from security.approval_gate import ask_inline_confirmation
        approved = ask_inline_confirmation(summary)
        if approved:
            return ExecutionResult(success=True, message="User confirmed.", data={"action_type": "ask_confirmation"})
        else:
            return ExecutionResult(success=False, message="User denied. Halting plan.", data={"action_type": "ask_confirmation", "halted": True})
    except Exception:
        # Fallback: auto-deny if confirmation system unavailable
        return ExecutionResult(success=False, message="Confirmation system unavailable. Action blocked.", data={"action_type": "ask_confirmation"})

def _move_relative(action):
    from execution.actions.app_actions import ExecutionResult
    try:
        import pyautogui
        direction = (action.params.get("direction") or "").lower()
        pixels = int(action.params.get("pixels", 100))
        dx, dy = 0, 0
        if "left" in direction: dx = -pixels
        elif "right" in direction: dx = pixels
        elif "up" in direction: dy = -pixels
        elif "down" in direction: dy = pixels
        pyautogui.moveRel(dx, dy, duration=0.3)
        return ExecutionResult(success=True, message=f"Moved cursor {direction} by {pixels}px", data={"action_type": "move_relative"})
    except Exception as e:
        return ExecutionResult(success=False, message=f"Move relative failed: {e}", data={"action_type": "move_relative"})

# Maps action_type (from ActionPlan) to the handler function
ACTION_REGISTRY = {
    # Application Management
    "open_application": open_application,
    "focus_application": ui_actions.focus_application,
    "switch_application": system_actions.switch_application,
    "close_application": system_actions.close_application,
    "list_running_apps": system_actions.list_running_apps,
    "get_running_processes": ui_actions.get_running_processes,
    # UI Automation
    "type_text": ui_actions.type_text,
    "press_key": ui_actions.press_key,
    "hotkey": ui_actions.hotkey,
    "click": ui_actions.click,
    "scroll": ui_actions.scroll,
    "move_mouse": ui_actions.move_mouse,
    "move_relative": _move_relative,
    "wait": ui_actions.wait,
    "prompt_next_action": ui_actions._prompt_next_action_handler,
    # Browser Actions
    "search_web": _bc_search_web,
    "open_first_result": _bc_open_first_result,
    "extract_page_text": _bc_extract_page_text,
    "summarize_page": _bc_summarize_page,
    "browse_to": _bc_browse_to,
    "open_url": _bc_open_url,
    "open_new_tab": browser_actions.open_new_tab,
    "navigate_tab": browser_actions.navigate_tab,
    "scrape_results": ui_actions.scrape_results,
    # File & System
    "run_powershell": run_powershell,
    "create_file": create_file,
    "list_duplicates": list_duplicates,
    "organize_files": organize_files,
    "rename_file": rename_file,
    "system_stats": system_actions.get_system_metrics,
    "scan_directory": org_actions.scan_directory,
    "move_files": org_actions.move_files,
    "organize_email": org_actions.organize_email,
    # Research
    "search_online": research_actions.search_online,
    "knowledge_lookup": research_actions.knowledge_lookup,
    "summarize_text": research_actions.summarize_text,
    "store_knowledge": research_handlers.store_knowledge,
    # Core Actions
    "respond_text": respond_text,
    "compute_result": compute_result,
    "play_music": play_music,
    "undo_last_action": lambda a: ExecutionResult(success=True, message="Last action undone (mock).", data={"action_type": "undo"}),
    # Vision Agent (v7.0)
    "vision_click": _vision_click,
    "vision_scroll": _vision_scroll,
    "vision_read": _vision_read,
    "vision_locate": _vision_locate,
    "capture_screenshot": _capture_screenshot,
    # Cognitive Agent (v7.0)
    "ask_confirmation": _ask_confirmation,
    "respond_text": lambda a: ExecutionResult(success=True, message=a.value or (a.params.get("text") if isinstance(a.params, dict) else ""))
}
