"""
Aegis v5.0 — UI Automation API
==============================
Unified interface for window management and input simulation.
"""

from execution.ui_automation.core import (
    type_text,
    press_key,
    hotkey,
    mouse_click,
    scroll,
    get_active_window_title,
    scrape_page,
    move_mouse_relative
)
from execution.ui_automation.window_focus import focus_window_v5 as focus_window
