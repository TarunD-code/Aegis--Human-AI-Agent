"""
Aegis v2.0 — Sleep Service
============================
Thread-safe sleep state manager for the background daemon.
Manages transitions between sleep and awake states with full logging.

This module contains NO execution logic.
"""

from __future__ import annotations

import logging
import threading
from datetime import datetime, timezone

logger = logging.getLogger(__name__)


class SleepService:
    """
    Manages the sleep/awake state of the Aegis background daemon.

    Thread-safe — can be safely called from the event loop thread
    and the hotkey handler thread simultaneously.
    """

    def __init__(self) -> None:
        """Initialize in the sleeping state."""
        self._lock = threading.Lock()
        self._sleeping: bool = True
        self._last_transition: datetime = datetime.now(tz=timezone.utc)
        logger.info("SleepService initialized (state: SLEEPING).")

    def enter_sleep(self) -> None:
        """
        Transition to sleep mode.

        If already sleeping, this is a no-op (logged at debug level).
        """
        with self._lock:
            if self._sleeping:
                logger.debug("SleepService: already sleeping, no-op.")
                return

            self._sleeping = True
            self._last_transition = datetime.now(tz=timezone.utc)
            logger.info(
                "SleepService: entered SLEEP mode at %s.",
                self._last_transition.isoformat(),
            )

    def wake(self) -> None:
        """
        Transition to awake mode.

        If already awake, this is a no-op (logged at debug level).
        """
        with self._lock:
            if not self._sleeping:
                logger.debug("SleepService: already awake, no-op.")
                return

            self._sleeping = False
            self._last_transition = datetime.now(tz=timezone.utc)
            logger.info(
                "SleepService: WOKE UP at %s.",
                self._last_transition.isoformat(),
            )

    def is_sleeping(self) -> bool:
        """
        Check whether Aegis is currently in sleep mode.

        Returns
        -------
        bool
            True if sleeping, False if awake.
        """
        with self._lock:
            return self._sleeping

    @property
    def last_transition_time(self) -> datetime:
        """Return the timestamp of the last sleep/wake transition."""
        with self._lock:
            return self._last_transition

    def __str__(self) -> str:
        state = "SLEEPING" if self.is_sleeping() else "AWAKE"
        return f"SleepService(state={state}, last_transition={self.last_transition_time.isoformat()})"
