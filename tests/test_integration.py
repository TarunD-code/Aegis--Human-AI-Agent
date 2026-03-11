"""
Aegis v2.0 — Integration Tests
================================
End-to-end tests for the v2.0 pipeline (CLI + Planner + Memory + Actions).
"""

import sys
import json
import os
from pathlib import Path
from unittest.mock import MagicMock, patch

# Ensure project root is importable
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

# Set dummy env var for config
os.environ["GEMINI_API_KEY"] = "AIza_FAKE_KEY"

from interfaces.cli import AegisCLI

class TestIntegration:
    """End-to-end pipeline validation using dependency injection."""

    @patch("interfaces.cli.get_system_snapshot")
    # PATCH the function in the module where it is USED
    @patch("interfaces.cli.request_approval")
    def test_full_pipeline_success(self, mock_approve, mock_snapshot):
        # 1. Setup mocks
        mock_snapshot.return_value = {"cpu_percent": 5}
        mock_approve.return_value = (True, None)
        
        mock_planner = MagicMock()
        mock_planner.generate_plan.return_value = {
            "summary": "Opening calculator",
            "actions": [{"type": "open_application", "value": "calc"}],
            "requires_approval": True
        }
        
        from execution.actions.app_actions import ActionResult
        mock_res = ActionResult(action_type="open_application", success=True, message="Success")
        mock_engine = MagicMock()
        mock_engine.execute_action.return_value = mock_res
        
        mock_memory = MagicMock()
        mock_session = MagicMock()

        # 2. Initialize CLI with injected mocks
        cli = AegisCLI(
            engine=mock_engine,
            memory=mock_memory,
            session=mock_session,
            planner=mock_planner
        )
        
        # 3. Inject command
        with patch("builtins.print"), patch("builtins.input", return_value="y"):
            cli._process_command("open calculator")

        # 4. Verify pipeline steps
        mock_snapshot.assert_called()
        mock_planner.generate_plan.assert_called()
        mock_approve.assert_called_once()
        mock_memory.store_approved.assert_called_once()
        mock_engine.execute_action.assert_called_once()

    @patch("interfaces.cli.get_system_snapshot")
    @patch("interfaces.cli.request_approval")
    def test_pipeline_rejection_storage(self, mock_approve, mock_snapshot):
        # 1. Setup mocks
        mock_snapshot.return_value = {}
        mock_approve.return_value = (False, "Dangerous action rejected by test")
        
        mock_planner = MagicMock()
        mock_planner.generate_plan.return_value = {
            "summary": "Dangerous action",
            "actions": [{"type": "open_application", "value": "secret"}],
            "requires_approval": True
        }
        
        mock_memory = MagicMock()
        mock_session = MagicMock()

        # 2. Run
        cli = AegisCLI(memory=mock_memory, planner=mock_planner, session=mock_session)
        with patch("builtins.print"), patch("builtins.input", return_value="n"):
            cli._process_command("do something risky")

        # 3. Verify rejection was stored
        mock_memory.store_rejected.assert_called_once()
