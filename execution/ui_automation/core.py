"""
Aegis v4.0 — UI Automation Core
==============================
Simulates mouse and keyboard input.
"""

from __future__ import annotations
import time
import logging
import pyautogui
import keyboard
import pywinauto

logger = logging.getLogger(__name__)

# Security: Failsafe so the user can stop automation by moving mouse to corner
pyautogui.FAILSAFE = True

def type_text(text: str, interval: float = 0.05) -> bool:
    """Types text at the current cursor position."""
    try:
        pyautogui.write(text, interval=interval)
        logger.info(f"Typed text into active window.")
        return True
    except Exception as e:
        logger.error(f"Failed to type text: {e}")
        return False

def press_key(key: str) -> bool:
    """Presses a single key."""
    try:
        keyboard.press_and_release(key)
        logger.info(f"Pressed key: {key}")
        return True
    except Exception as e:
        logger.error(f"Failed to press key '{key}': {e}")
        return False

def hotkey(keys: list[str]) -> bool:
    """Presses a combination of keys (e.g. ['ctrl', 's'])."""
    try:
        keyboard.press_and_release("+".join(keys))
        logger.info(f"Pressed hotkey: {'+'.join(keys)}")
        return True
    except Exception as e:
        logger.error(f"Failed to press hotkey '{'+'.join(keys)}': {e}")
        return False

def mouse_click(x: int, y: int, clicks: int = 1) -> bool:
    """Move to (x, y) and click."""
    try:
        pyautogui.click(x=x, y=y, clicks=clicks)
        logger.info(f"Clicked at ({x}, {y}) {clicks} times.")
        return True
    except Exception as e:
        logger.error(f"Failed to click at ({x}, {y}): {e}")
        return False

def scroll(amount: int) -> bool:
    """Vertical scroll."""
    try:
        pyautogui.scroll(amount)
        logger.info(f"Scrolled amount: {amount}")
        return True
    except Exception as e:
        logger.error(f"Failed to scroll: {e}")
        return False

def get_active_window_title() -> str:
    """Retrieve the title of the current foreground window."""
    try:
        # Use pywinauto for robust title retrieval
        return pywinauto.Desktop(backend="win32").get_active_window().window_text()
    except Exception:
        # Fallback to win32gui
        import win32gui
        return win32gui.GetWindowText(win32gui.GetForegroundWindow())

def verify_active_window(expected_app: str) -> bool:
    """Check if the expected application name is in the active window title."""
    active_title = get_active_window_title()
    logger.debug(f"Verifying active window. Expected: '{expected_app}', Active: '{active_title}'")
    return expected_app.lower() in active_title.lower()

def move_mouse_relative(direction: str, offset_percent: int = 10) -> bool:
    """
    v7.0: Move mouse relative to screen dimensions or current position.
    'direction': 'left', 'right', 'up', 'down', 'center'
    'offset_percent': 0-100
    """
    try:
        width, height = pyautogui.size()
        curr_x, curr_y = pyautogui.position()
        
        move_to_x, move_to_y = curr_x, curr_y
        
        if direction == 'center':
            move_to_x, move_to_y = width // 2, height // 2
        elif direction == 'right':
            move_to_x = min(width - 5, curr_x + (width * offset_percent // 100))
        elif direction == 'left':
            move_to_x = max(5, curr_x - (width * offset_percent // 100))
        elif direction == 'up':
            move_to_y = max(5, curr_y - (height * offset_percent // 100))
        elif direction == 'down':
            move_to_y = min(height - 5, curr_y + (height * offset_percent // 100))
            
        pyautogui.moveTo(move_to_x, move_to_y, duration=0.2)
        logger.info(f"Moved mouse {direction} ({offset_percent}%) to ({move_to_x}, {move_to_y})")
        return True
    except Exception as e:
        logger.error(f"Relative move failed: {e}")
        return False

def scrape_page() -> str | None:
    """
    Grabs text content from the active window using the clipboard.
    Aegis v4.1: Automated Scraper.
    """
    try:
        import pyperclip
        # Save current clipboard
        old = pyperclip.paste()
        
        # Select all and copy
        pyautogui.hotkey('ctrl', 'a')
        time.sleep(0.5)
        pyautogui.hotkey('ctrl', 'c')
        time.sleep(0.5)
        
        content = pyperclip.paste()
        
        # Restore old clipboard
        pyperclip.copy(old)
        
        if content and content != old:
            logger.info("Scraped page content via clipboard.")
            return content
        return None
    except Exception as e:
        logger.error(f"Scrape failed: {e}")
        return None
