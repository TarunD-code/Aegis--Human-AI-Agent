"""
Aegis v1.0 — Application Actions
==================================
Handler for opening applications on Windows.
"""

from __future__ import annotations

import logging
import os
import subprocess
import shutil
from dataclasses import dataclass, field
from typing import Any

logger = logging.getLogger(__name__)


@dataclass
class ExecutionResult:
    """Result of executing a single action."""
    success: bool
    message: str | None = None
    data: dict[str, Any] = field(default_factory=dict)
    
    @property
    def details(self) -> dict[str, Any]:
        """Backward compatibility for legacy code."""
        return self.data

    @property
    def action_type(self) -> str:
        """Heuristic for legacy code that expected action_type in result."""
        return self.data.get("action_type", "unknown")

    def to_dict(self) -> dict[str, Any]:
        """Convert ExecutionResult to dictionary."""
        return {
            "success": self.success,
            "message": self.message,
            "data": self.data
        }


# ── Well-known application mappings ─────────────────────────────────────

APP_ALIASES: dict[str, str] = {
    "notepad": "notepad.exe",
    "calculator": "calc.exe",
    "calc": "calc.exe",
    "paint": "mspaint.exe",
    "wordpad": "wordpad.exe",
    "cmd": "cmd.exe",
    "command prompt": "cmd.exe",
    "powershell": "powershell.exe",
    "explorer": "explorer.exe",
    "file explorer": "explorer.exe",
    "task manager": "taskmgr.exe",
    "control panel": "control.exe",
    "snipping tool": "snippingtool.exe",
    "settings": "ms-settings:",
    "edge": "msedge.exe",
    "microsoft edge": "msedge.exe",
    "chrome": "chrome.exe",
    "google chrome": "chrome.exe",
    "firefox": "firefox.exe",
    "code": "code",
    "vscode": "code",
    "visual studio code": "code",
}


def open_application(action) -> ExecutionResult:
    """
    Open an application by name on Windows.

    Supports common aliases (notepad, calculator, etc.) and falls back
    to ``os.startfile`` for arbitrary executables or paths.
    """
    app_name = (action.params.get("application_name") or action.value or "").strip()
    if not app_name:
        return ExecutionResult(
            success=False,
            message="No application name provided.",
            data={"action_type": "open_application"}
        )

    # Aegis v5.3: Static Registry Priority
    import json
    registry_path = "d:\\Aegis\\config\\app_registry.json"
    resolved = None
    if os.path.exists(registry_path):
        try:
            with open(registry_path, "r") as f:
                registry = json.load(f)
                resolved = registry.get(app_name.lower())
                if resolved:
                    logger.info(f"Resolved '{app_name}' via static registry: {resolved}")
        except Exception as e:
            logger.debug(f"Static registry lookup failed: {e}")

    if not resolved:
        # Aegis v5.7: Resolve via AppRegistry class (Fuzzy)
        from core.app_registry import registry as dynamic_registry
        resolved = dynamic_registry.resolve(app_name)
    
    # --- Strict Open-or-Focus Enforcement (Stabilization Phase) ---
    from core.process_manager import is_app_running, get_running_windows, focus_window
    is_running, _ = is_app_running(resolved)
    
    if is_running:
        windows = get_running_windows(resolved)
        if windows and focus_window(windows[0]):
            logger.info(f"Target '{app_name}' is already running. Focused existing window.")
            return ExecutionResult(
                success=True,
                message=f"Focused existing window for '{app_name}'.",
                data={"action_type": "focus_application"}
            )
        else:
            logger.warning(f"Target '{app_name}' is running, but focus failed. Proceeding with new launch.")
    
    logger.info("Opening application: %s (resolved: %s)", app_name, resolved)

    try:
        # Special handling for ms-settings: URIs
        if resolved.startswith("ms-"):
            os.startfile(resolved)
            return ExecutionResult(
                success=True,
                message=f"Opened '{app_name}' via URI: {resolved}",
                data={"action_type": "open_application"}
            )

        # Try to find executable on PATH
        exe_path = shutil.which(resolved)
        if exe_path:
            subprocess.Popen(  # noqa: S603
                [exe_path],
                stdout=subprocess.DEVNULL,
                stderr=subprocess.DEVNULL,
            )
            return ExecutionResult(
                success=True,
                message=f"Launched '{app_name}' ({exe_path}).",
                data={"action_type": "open_application"}
            )

        # v5.6: Office Bypass - try direct launch even if path validation is strict
        office_apps = ["winword", "excel", "powerpnt", "outlook", "onenote"]
        if any(app in resolved.lower() for app in office_apps) or any(app in app_name.lower() for app in office_apps):
            try:
                subprocess.Popen([resolved] if os.path.isabs(resolved) else [resolved + ".exe"], 
                               stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
                return ExecutionResult(
                    success=True,
                    message=f"Attempted direct launch of {app_name}.",
                    data={"action_type": "open_application"}
                )
            except Exception:
                pass

        # Fallback: os.startfile (works for many Windows apps)
        os.startfile(resolved)  # noqa: S606
        return ExecutionResult(
            success=True,
            message=f"Opened '{app_name}' via startfile.",
            data={"action_type": "open_application"}
        )

    except (FileNotFoundError, OSError):
        # Aegis v7.0: Explicit Browser Fallback Consent
        logger.warning(f"Target '{app_name}' not found locally. Requesting browser fallback consent.")
        from security.approval_gate import ask_inline_confirmation
        if ask_inline_confirmation(f"I couldn't find '{app_name}' installed on your PC. Should I search for it in your browser instead?"):
            from browser_automation.browser_controller import browser_controller
            browser_controller.search_web(f"download {app_name}")
            return ExecutionResult(
                success=True,
                message=f"I couldn't find '{app_name}' locally, so I've opened a browser search for you, Sir.",
                data={"action_type": "open_browser_fallback"}
            )
        
        return ExecutionResult(
            success=False,
            message=f"Application '{app_name}' not found, and browser fallback was declined.",
            data={"action_type": "open_application"}
        )
