"""
Aegis v4.0 — Multi-Step Task Tests
=====================================
Validates sequential execution and environment state flow.
"""

import sys
from pathlib import Path
import pytest
from unittest.mock import MagicMock, patch

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from execution.engine import ExecutionEngine
from brain.planner import ActionPlan, Action
from execution.actions.app_actions import ExecutionResult

class TestMultiStepTasks:

    def test_sequential_execution_stops_on_fail(self):
        """Verify that if step 1 fails, step 2 is not executed."""
        engine = ExecutionEngine()
        
        # Step 1: Fails
        mock_res1 = ExecutionResult(success=False, message="Failed to open app")
        mock_h1 = MagicMock(return_value=mock_res1)
        
        # Step 2: Should not run
        mock_h2 = MagicMock()
        
        # Patch the registry inside the engine instance or global registry
        from execution.actions import ACTION_REGISTRY
        with patch.dict(ACTION_REGISTRY, {"open_application": mock_h1, "type_text": mock_h2}):
            plan = ActionPlan(
                summary="Two steps",
                actions=[
                    Action(type="open_application", value="BadApp"),
                    Action(type="type_text", value="Hello")
                ]
            )
            
            results = engine.execute_plan(plan)
            assert len(results) == 1
            assert results[0].success is False
            mock_h2.assert_not_called()
