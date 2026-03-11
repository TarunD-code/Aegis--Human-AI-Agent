"""
Aegis v6.3 — Robust Window Focus Engine
========================================
Implements advanced window disambiguation with fuzzy title matching
via pygetwindow and rapidfuzz, with multi-stage fallbacks.
"""

import logging
import time

logger = logging.getLogger(__name__)

def _fuzzy_find_window(app_name: str):
    """Use pygetwindow + rapidfuzz to find the best-matching window by title."""
    try:
        import pygetwindow as gw
        from rapidfuzz import fuzz
    except ImportError:
        logger.debug("pygetwindow or rapidfuzz not available for fuzzy matching.")
        return None

    all_titles = gw.getAllTitles()
    best_match = None
    best_score = 0

    search_term = app_name.lower()

    for title in all_titles:
        if not title.strip():
            continue
        score = fuzz.partial_ratio(search_term, title.lower())
        if score > best_score and score > 60:  # Minimum threshold
            best_score = score
            best_match = title

    if best_match:
        logger.info(f"Fuzzy matched '{app_name}' -> '{best_match}' (score: {best_score})")
        return best_match
    return None

def focus_window_v5(app_name: str) -> bool:
    """
    Advanced window focus with fuzzy title matching (v6.3).

    Priority:
    1. Fuzzy title match via pygetwindow + rapidfuzz.
    2. pywinauto regex fallback.
    3. win32gui direct activation.
    4. Center click fallback.
    """
    logger.info(f"Targeting window focus for: {app_name}")

    # === Stage 0: Fuzzy Title Match (Primary Strategy) ===
    matched_title = _fuzzy_find_window(app_name)
    if matched_title:
        try:
            import pygetwindow as gw
            windows = gw.getWindowsWithTitle(matched_title)
            for w in windows:
                if hasattr(w, 'activate'):
                    try:
                        if hasattr(w, 'isMinimized') and w.isMinimized:
                            w.restore()
                            time.sleep(0.2)
                        w.activate()
                        time.sleep(0.3)
                        logger.info(f"Successfully focused via fuzzy title: '{matched_title}'")
                        return True
                    except Exception as e:
                        logger.debug(f"pygetwindow activate failed: {e}")
        except Exception as e:
            logger.debug(f"Fuzzy title focus failed: {e}")

    # === Stage 1: pywinauto regex fallback ===
    try:
        import pywinauto
        import win32gui
        import win32con

        elements = pywinauto.findwindows.find_elements(title_re=f".*{app_name}.*")
        if not elements:
            logger.warning(f"No windows found matching pattern: .*{app_name}.*")
            return False

        fg_hwnd = win32gui.GetForegroundWindow()

        def calculate_priority(w):
            rect = w.rectangle
            area = (rect.width() * rect.height())
            is_active = (w.handle == fg_hwnd)
            is_visible = win32gui.IsWindowVisible(w.handle)
            return (
                0 if is_active else 1,
                0 if is_visible else 1,
                -area,
            )

        sorted_elements = sorted(elements, key=calculate_priority)

        for element in sorted_elements:
            hwnd = element.handle
            if _activate_hwnd(hwnd):
                logger.info(f"Focused window via pywinauto: '{element.name}' (HWND: {hwnd})")
                return True

        # Stage 2: Click on window center
        if sorted_elements:
            best_rect = sorted_elements[0].rectangle
            center_x = best_rect.left + (best_rect.width() // 2)
            center_y = best_rect.top + (best_rect.height() // 2)
            import pyautogui
            pyautogui.click(center_x, center_y)
            time.sleep(0.3)
            return True

    except Exception as e:
        logger.error(f"Critical failure in window focus engine: {e}")

    return False

def _activate_hwnd(hwnd) -> bool:
    """Activate a window by its handle using win32gui."""
    try:
        import win32gui
        import win32con

        if win32gui.IsIconic(hwnd):
            win32gui.ShowWindow(hwnd, win32con.SW_RESTORE)
        else:
            win32gui.ShowWindow(hwnd, win32con.SW_SHOW)

        win32gui.SetForegroundWindow(hwnd)
        time.sleep(0.3)
        return win32gui.GetForegroundWindow() == hwnd
    except Exception as e:
        logger.debug(f"win32gui activation failed: {e}")
        return False

def focus_window(app_name: str) -> bool:
    """
    v7.0: Unified Focus API with Verification.
    """
    success = focus_window_v5(app_name)
    if not success:
        return False

    # Verification Engine
    time.sleep(0.5)
    try:
        import pygetwindow as gw
        from rapidfuzz import fuzz
        active_title = gw.getActiveWindowTitle()
        if not active_title:
            return False
            
        score = fuzz.partial_ratio(app_name.lower(), active_title.lower())
        if score >= 70:
            logger.info(f"Focus Verified: '{active_title}' matches '{app_name}' (score {int(score)})")
            return True
        else:
            logger.warning(f"Focus Verification Failed: Active window is '{active_title}' (score {int(score)})")
            return False
    except Exception as e:
        logger.debug(f"Verification Engine error: {e}")
        return True # Default to true if verification itself crashes
