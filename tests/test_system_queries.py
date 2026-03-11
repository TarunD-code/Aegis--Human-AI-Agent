"""
Aegis v4.0 — System Query Tests
==================================
Validates psutil integration and metric reporting.
"""

import sys
from pathlib import Path
import pytest
from unittest.mock import patch

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from execution.actions.system_actions import get_system_metrics
from brain.planner import Action

class TestSystemQueries:

    @patch("psutil.cpu_percent")
    @patch("psutil.virtual_memory")
    def test_metrics_collection(self, mock_mem, mock_cpu):
        """Verify metrics are polled and formatted correctly."""
        mock_cpu.return_value = 15.5
        mock_mem.return_value.percent = 45.0
        mock_mem.return_value.total = 16000000000
        mock_mem.return_value.available = 8000000000
        mock_mem.return_value.used = 8000000000
        
        action = Action(type="system_stats", params={})
        res = get_system_metrics(action)
        
        assert res.success is True
        assert "CPU 15.5%" in res.message
        assert "RAM 45.0%" in res.message
