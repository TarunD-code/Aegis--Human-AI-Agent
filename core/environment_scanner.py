"""
Aegis v2.0 — Environment Scanner
===================================
Detects the currently focused application and lists open windows
using pygetwindow (with win32gui fallback).

This module contains NO execution logic.
"""

from __future__ import annotations

import logging

logger = logging.getLogger(__name__)


def get_foreground_app() -> str:
    """
    Return the title of the currently focused (foreground) window.

    Returns
    -------
    str
        Window title of the foreground application, or empty string
        if detection fails.
    """
    # Try pygetwindow first
    try:
        import pygetwindow as gw

        active = gw.getActiveWindow()
        if active and active.title:
            logger.debug("Foreground app (pygetwindow): %s", active.title)
            return active.title
    except Exception as exc:  # noqa: BLE001
        logger.debug("pygetwindow failed, trying win32gui fallback: %s", exc)

    # Fallback to win32gui
    try:
        import win32gui

        hwnd = win32gui.GetForegroundWindow()
        title = win32gui.GetWindowText(hwnd)
        if title:
            logger.debug("Foreground app (win32gui): %s", title)
            return title
    except Exception as exc:  # noqa: BLE001
        logger.warning("Failed to detect foreground app: %s", exc)

    return ""


def get_open_windows() -> list[str]:
    """
    Return a list of titles of all visible open windows.

    Filters out empty titles and common system/invisible windows.

    Returns
    -------
    list[str]
        Sorted list of window titles. Empty list on failure.
    """
    # Try pygetwindow first
    try:
        import pygetwindow as gw

        windows = gw.getAllWindows()
        titles = _filter_window_titles([w.title for w in windows if w.title])
        if titles:
            logger.debug("Found %d open windows (pygetwindow).", len(titles))
            return titles
    except Exception as exc:  # noqa: BLE001
        logger.debug("pygetwindow failed for window list, trying win32gui: %s", exc)

    # Fallback to win32gui
    try:
        import win32gui

        titles_raw: list[str] = []

        def _enum_callback(hwnd: int, results: list[str]) -> None:
            if win32gui.IsWindowVisible(hwnd):
                title = win32gui.GetWindowText(hwnd)
                if title:
                    results.append(title)

        win32gui.EnumWindows(_enum_callback, titles_raw)
        titles = _filter_window_titles(titles_raw)
        logger.debug("Found %d open windows (win32gui).", len(titles))
        return titles

    except Exception as exc:  # noqa: BLE001
        logger.warning("Failed to enumerate open windows: %s", exc)
        return []


# ── Internal helpers ─────────────────────────────────────────────────────

# Window titles to exclude (common invisible/system windows)
_EXCLUDE_TITLES: set[str] = {
    "program manager",
    "windows input experience",
    "microsoft text input application",
    "settings",
    "msrdc",
    "",
}


def _filter_window_titles(raw_titles: list[str]) -> list[str]:
    """Filter and deduplicate window titles, removing system windows."""
    seen: set[str] = set()
    filtered: list[str] = []

    for title in raw_titles:
        title_clean = title.strip()
        if not title_clean:
            continue
        if title_clean.lower() in _EXCLUDE_TITLES:
            continue
        if title_clean in seen:
            continue
        seen.add(title_clean)
        filtered.append(title_clean)

    return sorted(filtered)
