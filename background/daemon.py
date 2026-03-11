"""
Aegis v2.0 — Background Daemon
=================================
Hotkey-activated system tray daemon. Registers a global hotkey
(Ctrl+Alt+A) and creates a system tray icon.

On wake the daemon prompts the user for a command and routes it
through the standard CLI pipeline (Planner → Validator → Approval
→ Executor). It NEVER auto-executes.
"""

from __future__ import annotations

import logging
import sys
import threading
from pathlib import Path

logger = logging.getLogger(__name__)


def _create_tray_image():
    """Create a simple tray icon image (blue shield)."""
    try:
        from PIL import Image, ImageDraw

        img = Image.new("RGBA", (64, 64), (0, 0, 0, 0))
        draw = ImageDraw.Draw(img)
        # Draw a simple shield shape
        draw.polygon(
            [(32, 4), (58, 16), (54, 48), (32, 60), (10, 48), (6, 16)],
            fill=(0, 150, 255, 230),
            outline=(255, 255, 255, 255),
        )
        draw.text((22, 22), "A", fill=(255, 255, 255, 255))
        return img
    except ImportError:
        # Fallback: create a minimal icon without Pillow
        try:
            from PIL import Image

            return Image.new("RGB", (64, 64), (0, 120, 215))
        except ImportError:
            logger.warning("Pillow not available for tray icon. Using minimal fallback.")
            return None


class AegisDaemon:
    """
    System tray daemon with global hotkey support.

    - Registers Ctrl+Alt+A as wake hotkey via the ``keyboard`` library.
    - Creates a system tray icon via ``pystray``.
    - On wake, prompts for user input and routes it through AegisCLI.
    - Never auto-executes any actions.
    """

    def __init__(self) -> None:
        """Initialize the daemon components."""
        from background.event_loop import BackgroundEventLoop
        from core.sleep_service import SleepService
        from config import WAKE_HOTKEY

        self._sleep_service = SleepService()
        self._event_loop = BackgroundEventLoop(on_wake=self._handle_wake)
        self._hotkey = WAKE_HOTKEY
        self._tray_icon = None
        self._cli = None  # Lazy-initialized

        logger.info(
            "AegisDaemon initialized (hotkey: %s).",
            self._hotkey,
        )

    def _get_cli(self):
        """Lazy-initialize the CLI controller."""
        if self._cli is None:
            from interfaces.cli import AegisCLI

            self._cli = AegisCLI()
        return self._cli

    def start(self) -> None:
        """Start the background daemon."""
        print(f"\n  🛡️  Aegis v2.0 — Background Mode")
        print(f"  ─────────────────────────────────")
        print(f"  Hotkey: {self._hotkey.upper()}")
        print(f"  Status: Sleeping (waiting for wake signal)")
        print(f"  Tray:   System tray icon active")
        print(f"\n  Press {self._hotkey.upper()} to wake Aegis.")
        print(f"  Right-click tray icon to exit.\n")

        # Register global hotkey
        self._register_hotkey()

        # Start event loop
        self._event_loop.start()

        # Start system tray (blocks main thread)
        self._start_tray()

    def _register_hotkey(self) -> None:
        """Register the global wake hotkey."""
        try:
            import keyboard

            keyboard.add_hotkey(
                self._hotkey,
                self._on_hotkey_pressed,
                suppress=False,
            )
            logger.info("Global hotkey '%s' registered.", self._hotkey)
        except ImportError:
            logger.error("keyboard library not available. Hotkey disabled.")
            print("  ⚠ Warning: keyboard library not installed. Hotkey disabled.")
        except Exception as exc:  # noqa: BLE001
            logger.error("Failed to register hotkey: %s", exc)
            print(f"  ⚠ Warning: Could not register hotkey ({exc}).")
            print("    Try running as Administrator.")

    def _on_hotkey_pressed(self) -> None:
        """Called when the wake hotkey is pressed."""
        logger.info("Hotkey pressed — signaling wake.")
        self._sleep_service.wake()
        self._event_loop.signal_wake()

    def _handle_wake(self) -> None:
        """Handle a wake event — prompt user and process command."""
        print(f"\n  🔔 Aegis woke up! (Press {self._hotkey.upper()} again after processing)")

        try:
            user_input = input("  Aegis ❯ ").strip()

            if not user_input:
                print("  (No input — going back to sleep)")
                self._sleep_service.enter_sleep()
                return

            if user_input.lower() in ("exit", "quit"):
                print("  👋 Shutting down daemon...")
                self._shutdown()
                return

            # Route through the standard CLI pipeline
            cli = self._get_cli()
            cli._process_command(user_input)

        except (EOFError, KeyboardInterrupt):
            pass
        finally:
            self._sleep_service.enter_sleep()
            print(f"\n  💤 Aegis is sleeping. Press {self._hotkey.upper()} to wake.\n")

    def _start_tray(self) -> None:
        """Create and run the system tray icon (blocks)."""
        try:
            import pystray

            icon_image = _create_tray_image()
            if icon_image is None:
                logger.error("Cannot create tray icon — no image backend.")
                print("  ⚠ Tray icon unavailable. Running in console-only mode.")
                self._console_fallback()
                return

            menu = pystray.Menu(
                pystray.MenuItem("Wake Aegis", self._tray_wake),
                pystray.MenuItem("Exit", self._tray_exit),
            )

            self._tray_icon = pystray.Icon(
                name="Aegis",
                icon=icon_image,
                title="Aegis v2.0 — Sleeping",
                menu=menu,
            )

            logger.info("Starting system tray icon.")
            self._tray_icon.run()

        except ImportError:
            logger.warning("pystray not available. Running in console-only mode.")
            print("  ⚠ pystray not installed. Running in console-only mode.")
            self._console_fallback()

        except Exception as exc:  # noqa: BLE001
            logger.error("Tray icon error: %s", exc)
            print(f"  ⚠ Tray error: {exc}. Running in console-only mode.")
            self._console_fallback()

    def _tray_wake(self, icon=None, item=None) -> None:
        """Tray menu: Wake Aegis."""
        self._on_hotkey_pressed()

    def _tray_exit(self, icon=None, item=None) -> None:
        """Tray menu: Exit daemon."""
        logger.info("Exit requested via tray menu.")
        self._shutdown()

    def _shutdown(self) -> None:
        """Clean shutdown of all daemon components."""
        try:
            import keyboard
            keyboard.unhook_all()
        except Exception:  # noqa: BLE001
            pass

        self._event_loop.stop()

        if self._tray_icon:
            try:
                self._tray_icon.stop()
            except Exception:  # noqa: BLE001
                pass

        logger.info("AegisDaemon shut down.")

    def _console_fallback(self) -> None:
        """Fallback when tray is unavailable — wait for keyboard input."""
        print("  Running in console fallback mode. Press Ctrl+C to exit.\n")
        try:
            while True:
                import time
                time.sleep(1)
        except KeyboardInterrupt:
            print("\n  👋 Aegis daemon shutting down.")
            self._shutdown()
