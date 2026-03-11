"""
Aegis v6.1 — Mouse Automation Controller
========================================
Exposes system-level mouse interaction capabilities using pyautogui.
Handles moving, clicking, dragging, and scrolling.
"""

import logging
import time

try:
    import pyautogui
    pyautogui.FAILSAFE = True
    pyautogui.PAUSE = 0.5
except ImportError:
    pyautogui = None
    logging.getLogger(__name__).warning("pyautogui not installed. Mouse automation disabled.")

logger = logging.getLogger(__name__)

class MouseController:
    """Provides high-level mouse actions."""
    
    @classmethod
    def is_available(cls) -> bool:
        return pyautogui is not None

    @classmethod
    def move_to(cls, x: int, y: int, duration: float = 0.5) -> bool:
        """Moves the mouse to the absolute (x, y) coordinates."""
        if not cls.is_available(): return False
        try:
            pyautogui.moveTo(x, y, duration=duration)
            logger.info(f"Mouse moved to ({x}, {y})")
            return True
        except Exception as e:
            logger.error(f"Mouse move failed: {e}")
            return False

    @classmethod
    def click(cls, button: str = 'left') -> bool:
        """Performs a single click at the current location."""
        if not cls.is_available(): return False
        try:
            pyautogui.click(button=button)
            logger.info(f"Mouse clicked ({button})")
            return True
        except Exception as e:
            logger.error(f"Mouse click failed: {e}")
            return False

    @classmethod
    def double_click(cls) -> bool:
        """Performs a double left click."""
        if not cls.is_available(): return False
        try:
            pyautogui.doubleClick()
            logger.info("Mouse double-clicked")
            return True
        except Exception as e:
            logger.error(f"Mouse double-click failed: {e}")
            return False

    @classmethod
    def scroll(cls, clicks: int) -> bool:
        """Scrolls the mouse wheel. Positive=Up, Negative=Down."""
        if not cls.is_available(): return False
        try:
            pyautogui.scroll(clicks)
            logger.info(f"Mouse scrolled ({clicks})")
            return True
        except Exception as e:
            logger.error(f"Mouse scroll failed: {e}")
            return False

    @classmethod
    def drag_to(cls, x: int, y: int, duration: float = 0.5) -> bool:
        """Drags from current location to (x,y)."""
        if not cls.is_available(): return False
        try:
            pyautogui.dragTo(x, y, duration=duration)
            logger.info(f"Mouse dragged to ({x}, {y})")
            return True
        except pyautogui.FailSafeException:
            logger.warning("Mouse drag aborted (Failsafe triggered).")
            return False
        except Exception as e:
            logger.error(f"Mouse drag failed: {e}")
            return False
