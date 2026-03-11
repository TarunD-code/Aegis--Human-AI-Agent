import win32gui
import win32process
import psutil
import logging
from typing import Optional

logger = logging.getLogger(__name__)

def get_active_window_title() -> Optional[str]:
    """Retrieve the title of the currently focused window."""
    try:
        hwnd = win32gui.GetForegroundWindow()
        return win32gui.GetWindowText(hwnd)
    except Exception as e:
        logger.debug(f"Failed to get active window title: {e}")
        return None

def get_active_window_process_name() -> Optional[str]:
    """Retrieve the process name of the currently focused window."""
    try:
        hwnd = win32gui.GetForegroundWindow()
        _, pid = win32process.GetWindowThreadProcessId(hwnd)
        process = psutil.Process(pid)
        return process.name()
    except Exception as e:
        logger.debug(f"Failed to get active window process: {e}")
        return None

class WindowTracker:
    """
    Monitors and reports the state of the active window for context injection.
    """
    def __init__(self):
        self.last_title = None
        self.last_process = None

    def get_context(self) -> dict:
        """Get the current active window context."""
        title = get_active_window_title()
        process = get_active_window_process_name()
        
        # Update cache
        self.last_title = title
        self.last_process = process
        
        return {
            "active_window_title": title,
            "active_window_process": process,
            "visible_windows": self.list_visible_windows()[:15]
        }

    def list_visible_windows(self) -> list[str]:
        """Enumerate all currently visible window titles."""
        windows = []
        def enum_handler(hwnd, _):
            if win32gui.IsWindowVisible(hwnd):
                title = win32gui.GetWindowText(hwnd)
                if title:
                    windows.append(title)
        win32gui.EnumWindows(enum_handler, None)
        return windows

# Global instance
tracker = WindowTracker()
