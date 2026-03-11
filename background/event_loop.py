"""
Aegis v2.0 — Background Event Loop
=====================================
Threaded event loop that waits for a hotkey signal before routing
user input to the CLI pipeline.

This module contains NO execution logic.
No planner invocation occurs without explicit user input.
"""

from __future__ import annotations

import logging
import threading
from typing import Callable

logger = logging.getLogger(__name__)


class BackgroundEventLoop:
    """
    Event loop that blocks until a wake signal is received.

    Uses a threading.Event to coordinate between the hotkey
    handler thread and the main event loop thread. When the
    event is set, the loop invokes the registered callback.
    """

    def __init__(self, on_wake: Callable[[], None]) -> None:
        """
        Initialize the event loop.

        Parameters
        ----------
        on_wake : Callable
            Callback invoked when the wake signal is received.
            Typically prompts the user for input and routes it
            to the CLI pipeline.
        """
        self._on_wake = on_wake
        self._wake_event = threading.Event()
        self._stop_event = threading.Event()
        self._thread: threading.Thread | None = None
        logger.info("BackgroundEventLoop initialized.")

    def signal_wake(self) -> None:
        """Signal the event loop to wake up and process user input."""
        logger.info("Wake signal received.")
        self._wake_event.set()

    def start(self) -> None:
        """Start the event loop in a background thread."""
        if self._thread and self._thread.is_alive():
            logger.warning("Event loop already running.")
            return

        self._stop_event.clear()
        self._thread = threading.Thread(
            target=self._run,
            name="AegisEventLoop",
            daemon=True,
        )
        self._thread.start()
        logger.info("BackgroundEventLoop started.")

    def stop(self) -> None:
        """Stop the event loop gracefully."""
        logger.info("Stopping BackgroundEventLoop...")
        self._stop_event.set()
        self._wake_event.set()  # Unblock if waiting

        if self._thread and self._thread.is_alive():
            self._thread.join(timeout=5.0)

        logger.info("BackgroundEventLoop stopped.")

    def _run(self) -> None:
        """Internal loop: wait for wake signal, invoke callback, repeat."""
        logger.info("Event loop thread running.")

        while not self._stop_event.is_set():
            # Block until wake signal or stop
            self._wake_event.wait()

            if self._stop_event.is_set():
                break

            # Reset for next cycle
            self._wake_event.clear()

            try:
                logger.info("Event loop: invoking wake callback.")
                self._on_wake()
            except Exception as exc:  # noqa: BLE001
                logger.error("Event loop callback error: %s", exc)

        logger.info("Event loop thread exiting.")
