"""
Aegis v6.2 — Vision UI Interactor
=================================
Safely controls the mouse based on vision system coordinates.
Incorporates safety delays to prevent erratic UI actions.
"""

import time
import logging

try:
    import pyautogui
    pyautogui.FAILSAFE = True
    pyautogui.PAUSE = 0.5
except ImportError:
    pyautogui = None
    logging.getLogger(__name__).warning("pyautogui not installed. UI Interactor disabled.")

logger = logging.getLogger(__name__)

class UIInteractor:
    def __init__(self, default_delay: float = 0.5):
        self.default_delay = default_delay
        self.available = pyautogui is not None

    def move_mouse(self, x: int, y: int) -> bool:
        if not self.available: return False
        try:
            logger.info(f"Vision UI: Moving to ({x}, {y})")
            pyautogui.moveTo(x, y, duration=self.default_delay)
            return True
        except pyautogui.FailSafeException:
            logger.warning("Failsafe triggered during move_mouse at boundaries.")
            return False

    def click(self, x: int, y: int) -> bool:
        if not self.available: return False
        try:
            self.move_mouse(x, y)
            time.sleep(0.1)
            pyautogui.click()
            logger.info(f"Vision UI: Clicked ({x}, {y})")
            return True
        except Exception as e:
            logger.error(f"Vision UI: Click failed: {e}")
            return False

    def double_click(self, x: int, y: int) -> bool:
        if not self.available: return False
        try:
            self.move_mouse(x, y)
            time.sleep(0.1)
            pyautogui.doubleClick()
            logger.info(f"Vision UI: Double Clicked ({x}, {y})")
            return True
        except Exception as e:
            logger.error(f"Vision UI: Double click failed: {e}")
            return False

    def drag(self, x1: int, y1: int, x2: int, y2: int) -> bool:
        if not self.available: return False
        try:
            self.move_mouse(x1, y1)
            time.sleep(0.1)
            pyautogui.dragTo(x2, y2, duration=self.default_delay)
            logger.info(f"Vision UI: Dragged from ({x1}, {y1}) to ({x2}, {y2})")
            return True
        except Exception as e:
            logger.error(f"Vision UI: Drag failed: {e}")
            return False

    def scroll(self, amount: int) -> bool:
        if not self.available: return False
        try:
            pyautogui.scroll(amount)
            logger.info(f"Vision UI: Scrolled by {amount}")
            return True
        except Exception as e:
            logger.error(f"Vision UI: Scroll failed: {e}")
            return False

# Singleton
interactor = UIInteractor()
