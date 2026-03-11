"""
Aegis v3.0 — UI Controller
===========================
Wrapper for PyAutoGUI and PyWinAuto to perform safe OS automation
(typing, clicking, navigating). Includes failsafes and stabilizers.
"""

import logging
import time
from typing import Any

UI_AVAILABLE = True

try:
    import pyautogui
    import pygetwindow as gw
    # Configure PyAutoGUI settings if available
    pyautogui.FAILSAFE = True
    pyautogui.PAUSE = 0.5
except ImportError:
    UI_AVAILABLE = False
    pyautogui = None
    gw = None

logger = logging.getLogger(__name__)


def type_text(text: str) -> dict[str, Any]:
    """Simulate natural keyboard typing."""
    try:
        logger.debug("Typing text: %s", text)
        pyautogui.write(text, interval=0.05)
        return {"success": True, "message": f"Typed: {text}"}
    except Exception as exc:
        logger.error("UI: Type failed: %s", exc)
        return {"success": False, "message": str(exc)}


def press_key(key: str) -> dict[str, Any]:
    """Press a single key."""
    try:
        logger.debug("Pressing key: %s", key)
        pyautogui.press(key)
        return {"success": True, "message": f"Pressed: {key}"}
    except Exception as exc:
        logger.error("UI: Press failed: %s", exc)
        return {"success": False, "message": str(exc)}


def hotkey(*keys: str) -> dict[str, Any]:
    """Perform a keyboard shortcut (e.g. ctrl, c)."""
    try:
        logger.debug("Hotkey combo: %s", keys)
        pyautogui.hotkey(*keys)
        return {"success": True, "message": f"Hotkey: {'+'.join(keys)}"}
    except Exception as exc:
        logger.error("UI: Hotkey failed: %s", exc)
        return {"success": False, "message": str(exc)}


def click(x: int | None = None, y: int | None = None) -> dict[str, Any]:
    """Perform a mouse click at (x, y) or current position."""
    try:
        pyautogui.click(x, y)
        return {"success": True, "message": f"Clicked at ({x or 'current'}, {y or 'current'})"}
    except Exception as exc:
        logger.error("UI: Click failed: %s", exc)
        return {"success": False, "message": str(exc)}


def move_mouse(x: int, y: int) -> dict[str, Any]:
    """Move mouse cursor to (x, y)."""
    try:
        pyautogui.moveTo(x, y, duration=0.2)
        return {"success": True, "message": f"Moved to ({x}, {y})"}
    except Exception as exc:
        logger.error("UI: Move failed: %s", exc)
        return {"success": False, "message": str(exc)}


def wait(seconds: float) -> dict[str, Any]:
    """Pause execution for a specific duration."""
    time.sleep(seconds)
    return {"success": True, "message": f"Waited {seconds}s"}
