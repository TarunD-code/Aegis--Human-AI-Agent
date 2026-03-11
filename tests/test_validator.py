"""
Aegis v1.0 — Validator Tests
==============================
Tests for security validation of action plans.
"""

import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from brain.planner import Action, ActionPlan
from security.validator import validate_plan
from security.whitelist import is_action_allowed, is_path_blocked, is_ps_command_allowed


# ═══════════════════════════════════════════════════════════════════════
# Whitelist helper tests
# ═══════════════════════════════════════════════════════════════════════

class TestIsActionAllowed:

    def test_allowed_actions(self):
        for action_type in [
            "open_application", "organize_files", "list_duplicates",
            "create_file", "rename_file", "run_powershell",
        ]:
            assert is_action_allowed(action_type) is True

    def test_disallowed_actions(self):
        for action_type in [
            "delete_file", "format_disk", "shutdown", "unknown",
        ]:
            assert is_action_allowed(action_type) is False


class TestIsPathBlocked:

    def test_blocked_windows_folder(self):
        assert is_path_blocked(r"C:\Windows") is True

    def test_blocked_subfolder(self):
        assert is_path_blocked(r"C:\Windows\System32") is True

    def test_blocked_program_files(self):
        assert is_path_blocked(r"C:\Program Files") is True
        assert is_path_blocked(r"C:\Program Files (x86)") is True

    def test_blocked_system_volume(self):
        assert is_path_blocked("System Volume Information") is True

    def test_safe_path(self):
        assert is_path_blocked(r"D:\Downloads") is False
        assert is_path_blocked(r"C:\Users\Test\Documents") is False

    def test_empty_path(self):
        assert is_path_blocked("") is False

    def test_case_insensitive(self):
        assert is_path_blocked(r"c:\windows\system32") is True
        assert is_path_blocked(r"C:\WINDOWS") is True

    def test_forward_slashes(self):
        assert is_path_blocked("C:/Windows/System32") is True


class TestIsPsCommandAllowed:

    def test_allowed_commands(self):
        assert is_ps_command_allowed("Get-Process") is True
        assert is_ps_command_allowed("Get-ChildItem C:\\") is True
        assert is_ps_command_allowed("Get-Service | Where-Object {$_.Status -eq 'Running'}") is True

    def test_disallowed_commands(self):
        assert is_ps_command_allowed("Remove-Item") is False
        assert is_ps_command_allowed("Invoke-Expression") is False
        assert is_ps_command_allowed("Start-Process") is False
        assert is_ps_command_allowed("Set-ExecutionPolicy") is False

    def test_empty_command(self):
        assert is_ps_command_allowed("") is False

    def test_case_insensitive(self):
        assert is_ps_command_allowed("get-process") is True


# ═══════════════════════════════════════════════════════════════════════
# Plan validation tests
# ═══════════════════════════════════════════════════════════════════════

class TestValidatePlan:

    def test_valid_plan(self):
        plan = ActionPlan(
            summary="Open Notepad",
            actions=[Action(type="open_application", value="notepad")],
        )
        is_valid, warnings = validate_plan(plan)
        assert is_valid is True
        assert warnings == []

    def test_blocked_path(self):
        plan = ActionPlan(
            summary="Organize Windows folder",
            actions=[
                Action(type="organize_files", target=r"C:\Windows\System32")
            ],
        )
        is_valid, warnings = validate_plan(plan)
        assert is_valid is False
        assert len(warnings) == 1
        assert "blocked" in warnings[0].lower()

    def test_unknown_action_type(self):
        plan = ActionPlan(
            summary="Delete everything",
            actions=[Action(type="delete_all")],
        )
        is_valid, warnings = validate_plan(plan)
        assert is_valid is False
        assert "whitelisted" in warnings[0].lower() or "NOT" in warnings[0]

    def test_blocked_powershell_command(self):
        plan = ActionPlan(
            summary="Run dangerous command",
            actions=[
                Action(type="run_powershell", value="Remove-Item C:\\important")
            ],
        )
        is_valid, warnings = validate_plan(plan)
        assert is_valid is False
        assert len(warnings) == 1

    def test_allowed_powershell_command(self):
        plan = ActionPlan(
            summary="List processes",
            actions=[
                Action(type="run_powershell", value="Get-Process")
            ],
        )
        is_valid, warnings = validate_plan(plan)
        assert is_valid is True

    def test_multiple_violations(self):
        plan = ActionPlan(
            summary="Multiple bad actions",
            actions=[
                Action(type="organize_files", target=r"C:\Windows"),
                Action(type="run_powershell", value="Remove-Item C:\\"),
            ],
        )
        is_valid, warnings = validate_plan(plan)
        assert is_valid is False
        assert len(warnings) == 2

    def test_empty_plan(self):
        plan = ActionPlan(summary="Nothing to do", actions=[])
        is_valid, warnings = validate_plan(plan)
        assert is_valid is True
        assert warnings == []
