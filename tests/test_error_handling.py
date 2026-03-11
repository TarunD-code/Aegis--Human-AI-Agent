"""
Aegis v4.0 — Error Handling Tests
====================================
Validates the 'Sir, the action did not complete successfully' reporting.
"""

import sys
from pathlib import Path
import pytest
from unittest.mock import MagicMock, patch

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from execution.engine import ExecutionEngine
from brain.planner import Action

class TestErrorHandling:

    def test_crashed_handler_reporting(self):
        """Verify that handler crashes are caught and reported with 'Sir' prefix."""
        engine = ExecutionEngine()
        mock_handler = MagicMock(side_effect=RuntimeError("OS Error"))
        
        from execution.actions import ACTION_REGISTRY
        with patch.dict(ACTION_REGISTRY, {"type_text": mock_handler}):
            action = Action(type="type_text", value="test")
            res = engine.execute(action)
            
            assert res.success is False
            assert "Sir, the action" in res.message
            assert "OS Error" in res.message
