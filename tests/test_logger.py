"""
Aegis v3.6 — Logger Tests
===========================
Tests for the structured JSON logging system.
Updated to match v3.6 AegisLogger API.
"""

import json
import sys
import tempfile
from pathlib import Path
from unittest.mock import patch

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))


class TestAegisLogger:
    """Tests for AegisLogger functionality."""

    def setup_method(self):
        """Create a temporary log directory for each test."""
        self._temp_dir = tempfile.mkdtemp()
        # Patch LOG_DIR so logger writes to our temp dir
        self._patcher = patch("logs.logger.LOG_DIR", self._temp_dir)
        self._patcher.start()

        from logs.logger import AegisLogger
        self.logger = AegisLogger()

    def teardown_method(self):
        self._patcher.stop()

    def _read_log(self) -> list[dict]:
        """Read the latest log file from the temp directory."""
        log_files = list(Path(self._temp_dir).glob("aegis_*.json"))
        assert len(log_files) > 0, "No log file was created."
        content = log_files[0].read_text(encoding="utf-8")
        return json.loads(content)

    def test_log_ai_plan(self):
        """v3.6: log_ai_plan replaces log_plan."""
        plan = {"summary": "Test", "actions": [], "requires_approval": True}
        self.logger.log_ai_plan(plan)
        entries = self._read_log()
        assert len(entries) == 1
        assert entries[0]["event_type"] == "ai_plan"
        assert entries[0]["plan"] == plan

    def test_log_approval(self):
        """v3.6: log_approval uses plan_id, approved, user."""
        self.logger.log_approval("plan-001", approved=True, user="cli")
        entries = self._read_log()
        assert entries[0]["event_type"] == "approval_event"
        assert entries[0]["approved"] is True
        assert entries[0]["plan_id"] == "plan-001"

    def test_log_execution(self):
        """v3.6: log_execution takes action dict, result, and success bool."""
        action = {"type": "open_application", "id": "a1"}
        self.logger.log_execution(action, result="OK", success=True)
        entries = self._read_log()
        assert entries[0]["event_type"] == "execution_event"
        assert entries[0]["success"] is True

    def test_log_error(self):
        """v3.6: event_type is 'error_event'."""
        self.logger.log_error("Something broke", context="test")
        entries = self._read_log()
        assert entries[0]["event_type"] == "error_event"
        assert entries[0]["error"] == "Something broke"

    def test_multiple_entries_appended(self):
        """Multiple log calls should append to the same daily file."""
        self.logger.log_error("First")
        self.logger.log_error("Second")
        self.logger.log_error("Third")
        entries = self._read_log()
        assert len(entries) == 3

    def test_log_ai_plan_with_errors(self):
        """v3.6: log_ai_plan can include validation_errors."""
        plan = {"summary": "Bad plan", "actions": []}
        warnings = ["Action type blocked", "Path is restricted"]
        self.logger.log_ai_plan(plan, validation_errors=warnings)
        entries = self._read_log()
        assert entries[0]["event_type"] == "ai_plan"
        assert entries[0]["errors"] == warnings
