"""
Aegis v2.0 — Preference Store
================================
Thin wrapper around MemoryManager for user preferences.

This module does NOT bypass any validation logic.
It is purely a convenience layer for reading/writing preferences.
"""

from __future__ import annotations

import logging
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from memory.memory_manager import MemoryManager

logger = logging.getLogger(__name__)


class PreferenceStore:
    """
    Convenient interface for managing user preferences.

    Wraps the MemoryManager's preference methods with type-aware
    getters and setters.
    """

    def __init__(self, memory: MemoryManager) -> None:
        """
        Initialize with a MemoryManager instance.

        Parameters
        ----------
        memory : MemoryManager
            The backing persistent memory manager.
        """
        self._memory = memory

    def get(self, key: str, default: str = "") -> str:
        """Get a preference value."""
        return self._memory.get_preference(key, default)

    def set(self, key: str, value: str) -> None:
        """Set a preference value."""
        self._memory.set_preference(key, value)
        logger.debug("Preference set: %s = %s", key, value)

    def get_bool(self, key: str, default: bool = False) -> bool:
        """Get a boolean preference."""
        val = self._memory.get_preference(key, "")
        if not val:
            return default
        return val.lower() in ("true", "1", "yes")

    def set_bool(self, key: str, value: bool) -> None:
        """Set a boolean preference."""
        self._memory.set_preference(key, "true" if value else "false")

    def get_int(self, key: str, default: int = 0) -> int:
        """Get an integer preference."""
        val = self._memory.get_preference(key, "")
        if not val:
            return default
        try:
            return int(val)
        except ValueError:
            return default

    def set_int(self, key: str, value: int) -> None:
        """Set an integer preference."""
        self._memory.set_preference(key, str(value))
