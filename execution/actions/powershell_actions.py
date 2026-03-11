"""
Aegis v1.0 — PowerShell Actions
=================================
Handler for executing whitelisted PowerShell commands safely.
"""

from __future__ import annotations

import logging
import subprocess

from execution.actions.app_actions import ExecutionResult
from security.whitelist import is_ps_command_allowed

logger = logging.getLogger(__name__)

# Maximum time (seconds) a PowerShell command is allowed to run
PS_TIMEOUT: int = 30


def run_powershell(action) -> ExecutionResult:
    """
    Execute a whitelisted PowerShell command and capture its output.

    Security measures:
    - Command must start with a whitelisted cmdlet.
    - Executed with ``shell=False`` to prevent injection.
    - Timeout enforced to prevent hanging.
    - stdout and stderr are captured.
    """
    command = (action.value or "").strip()

    if not command:
        return ExecutionResult(
            success=False,
            message="No PowerShell command provided.",
            data={"action_type": "run_powershell"}
        )

    # Security check
    if not is_ps_command_allowed(command):
        return ExecutionResult(
            success=False,
            message=(
                f"PowerShell command '{command}' is not in the allowed "
                f"command whitelist. Execution blocked."
            ),
            data={"action_type": "run_powershell"}
        )

    logger.info("Executing whitelisted PowerShell command: %s", command)

    try:
        result = subprocess.run(  # noqa: S603
            ["powershell.exe", "-NoProfile", "-Command", command],
            capture_output=True,
            text=True,
            timeout=PS_TIMEOUT,
            shell=False,
        )

        output = result.stdout.strip()
        errors = result.stderr.strip()

        if result.returncode == 0:
            return ExecutionResult(
                success=True,
                message=f"PowerShell command executed successfully.",
                data={
                    "action_type": "run_powershell",
                    "command": command,
                    "output": output[:2000],  # Truncate large output
                    "return_code": result.returncode,
                },
            )
        else:
            return ExecutionResult(
                success=False,
                message=f"PowerShell command failed (exit code {result.returncode}).",
                data={
                    "action_type": "run_powershell",
                    "command": command,
                    "output": output[:2000],
                    "errors": errors[:2000],
                    "return_code": result.returncode,
                },
            )

    except subprocess.TimeoutExpired:
        return ExecutionResult(
            success=False,
            message=f"PowerShell command timed out after {PS_TIMEOUT}s: {command}",
            data={"action_type": "run_powershell"}
        )
    except FileNotFoundError:
        return ExecutionResult(
            success=False,
            message="PowerShell executable not found on this system.",
            data={"action_type": "run_powershell"}
        )
    except OSError as exc:
        return ExecutionResult(
            success=False,
            message=f"Failed to run PowerShell command: {exc}",
            data={"action_type": "run_powershell"}
        )
