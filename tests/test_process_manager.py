"""
Aegis v2.0 — Process Manager Tests
====================================
Tests for the read-only process manager module.
"""

import sys
from pathlib import Path
from unittest.mock import MagicMock, patch

import pytest

# Ensure project root is importable
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from core.process_manager import (
    get_running_processes,
    is_process_running,
    is_app_running,
    get_running_app_names,
)


class TestProcessManager:
    """Tests for process detection."""

    @patch("psutil.process_iter")
    def test_get_running_processes(self, mock_iter):
        # Mock process data
        proc1 = MagicMock()
        proc1.info = {"pid": 123, "name": "notepad.exe", "memory_percent": 1.5}
        proc2 = MagicMock()
        proc2.info = {"pid": 456, "name": "chrome.exe", "memory_percent": 10.2}
        
        mock_iter.return_value = [proc1, proc2]

        procs = get_running_processes()
        assert len(procs) == 2
        # Should be sorted by memory percent desc
        assert procs[0]["name"] == "chrome.exe"
        assert procs[1]["name"] == "notepad.exe"

    @patch("psutil.process_iter")
    @patch("core.process_manager.get_running_windows")
    def test_is_process_running(self, mock_wins, mock_iter):
        # Mock window check
        mock_wins.return_value = []
        
        # Mock process check
        proc = MagicMock()
        proc.info = {"name": "notepad.exe"}
        mock_iter.return_value = [proc]

        assert is_process_running("notepad") is True
        assert is_app_running("notepad")[0] is True
        assert is_process_running("calc") is False

    @patch("psutil.process_iter")
    def test_get_running_app_names(self, mock_iter):
        proc1 = MagicMock()
        proc1.info = {"name": "Notepad.exe"}
        proc2 = MagicMock()
        proc2.info = {"name": "chrome.exe"}
        proc3 = MagicMock()
        proc3.info = {"name": "notEPAD.EXE"} # Duplicate
        
        mock_iter.return_value = [proc1, proc2, proc3]

        names = get_running_app_names()
        assert "notepad.exe" in names
        assert "chrome.exe" in names
        assert len(names) == 2 # Deduplicated
