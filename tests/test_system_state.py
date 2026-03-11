"""
Aegis v2.0 — System State Tests
=================================
Tests for the read-only system introspection module.
"""

import sys
from pathlib import Path
from unittest.mock import MagicMock, patch

import pytest

# Ensure project root is importable
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from core.system_state import (
    get_cpu_percent,
    get_memory_info,
    get_disk_info,
    get_system_snapshot,
)


class TestSystemState:
    """Tests for system state collection."""

    @patch("psutil.cpu_percent")
    def test_get_cpu_percent(self, mock_cpu):
        mock_cpu.return_value = 15.5
        val = get_cpu_percent(interval=0.1)
        assert val == 15.5
        mock_cpu.assert_called_once()

    @patch("psutil.cpu_percent")
    def test_get_cpu_percent_failure(self, mock_cpu):
        mock_cpu.side_effect = Exception("psutil error")
        val = get_cpu_percent()
        assert val == -1.0

    @patch("psutil.virtual_memory")
    def test_get_memory_info(self, mock_mem):
        mock_obj = MagicMock()
        mock_obj.total = 16000000000
        mock_obj.available = 8000000000
        mock_obj.percent = 50.0
        mock_mem.return_value = mock_obj

        info = get_memory_info()
        assert info["total"] == 16000000000
        assert info["percent"] == 50.0

    @patch("psutil.disk_usage")
    def test_get_disk_info(self, mock_disk):
        mock_obj = MagicMock()
        mock_obj.total = 500000000000
        mock_obj.used = 100000000000
        mock_obj.free = 400000000000
        mock_obj.percent = 20.0
        mock_disk.return_value = mock_obj

        info = get_disk_info("C:\\")
        assert info["total"] == 500000000000
        assert info["percent"] == 20.0

    @patch("core.system_state.get_cpu_percent")
    @patch("core.system_state.get_memory_info")
    @patch("core.system_state.get_disk_info")
    def test_get_system_snapshot(self, mock_disk, mock_mem, mock_cpu):
        mock_cpu.return_value = 10.0
        mock_mem.return_value = {"percent": 40.0}
        mock_disk.return_value = {"percent": 30.0}

        snapshot = get_system_snapshot()
        assert snapshot["cpu_percent"] == 10.0
        assert snapshot["memory"]["percent"] == 40.0
        assert snapshot["disk"]["percent"] == 30.0

    @patch("core.system_state.get_cpu_percent")
    @patch("core.system_state.get_memory_info")
    @patch("core.system_state.get_disk_info")
    def test_get_system_snapshot_partial_failure(self, mock_disk, mock_mem, mock_cpu):
        # Even if CPU fails, we want memory and disk
        mock_cpu.side_effect = Exception("CPU fail")
        mock_mem.return_value = {"percent": 40.0}
        mock_disk.return_value = {"percent": 30.0}

        snapshot = get_system_snapshot()
        assert snapshot["cpu_percent"] == -1.0
        assert snapshot["memory"]["percent"] == 40.0
        assert snapshot["disk"]["percent"] == 30.0
