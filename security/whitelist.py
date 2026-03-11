"""
Aegis v1.0 — Security Whitelist
================================
Centralized whitelist definitions for action types, blocked system
folders, and safe PowerShell commands.
"""

from config import ACTION_WHITELIST, BLOCKED_FOLDERS, WHITELISTED_PS_COMMANDS

__all__ = [
    "ACTION_WHITELIST",
    "BLOCKED_FOLDERS",
    "WHITELISTED_PS_COMMANDS",
    "is_action_allowed",
    "is_path_blocked",
    "is_ps_command_allowed",
]


def is_action_allowed(action_type: str) -> bool:
    """Check whether a given action type is in the whitelist."""
    return action_type in ACTION_WHITELIST


def is_path_blocked(path: str) -> bool:
    """
    Check whether a given path falls under a blocked system folder.

    Uses case-insensitive prefix matching so that sub-paths of blocked
    folders (e.g. ``C:\\Windows\\System32``) are also caught.
    """
    if not path:
        return False

    normalized = path.replace("/", "\\").rstrip("\\").lower()

    for blocked in BLOCKED_FOLDERS:
        blocked_norm = blocked.replace("/", "\\").rstrip("\\").lower()
        if normalized == blocked_norm or normalized.startswith(blocked_norm + "\\"):
            return True

    return False


def is_ps_command_allowed(command: str) -> bool:
    """
    Check whether a PowerShell command string starts with a whitelisted
    cmdlet.  Only the first token (the cmdlet name) is checked.
    """
    if not command:
        return False

    first_token = command.strip().split()[0]

    for allowed in WHITELISTED_PS_COMMANDS:
        if first_token.lower() == allowed.lower():
            return True

    return False
