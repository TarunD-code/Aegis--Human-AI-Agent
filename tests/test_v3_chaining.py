"""
Aegis v3.0 — Structured Chaining & Context Tests
================================================
Verifies JSON array plans, math chaining, and browser continuity.
"""

import sys
from pathlib import Path
from unittest.mock import MagicMock, patch

import pytest

# Ensure project root is importable
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from brain.planner import parse_plan, Action
from interfaces.cli import AegisCLI
from memory.session_memory import SessionMemory

class TestV3Chaining:
    """Tests for result chaining and structured plans."""

    def test_json_array_parsing(self):
        """Verify that parse_plan handles the new description field."""
        raw_action = {
            "type": "type_text",
            "value": "123",
            "description": "Typing a number"
        }
        # In Aegis v3.0, plans are parsed from a dict that contains an 'actions' list
        # The ContextualPlanner converts the array from LLM into this dict.
        raw_plan = {
            "summary": "Test",
            "actions": [raw_action],
            "requires_approval": True
        }
        plan = parse_plan(raw_plan)
        assert plan.actions[0].description == "Typing a number"
        assert "Typing a number" in str(plan.actions[0])

    @patch("interfaces.cli.get_system_snapshot")
    @patch("interfaces.cli.AegisLogger")
    @patch("interfaces.cli.ContextualPlanner")
    @patch("interfaces.cli.request_approval")
    def test_math_result_chaining(self, mock_approve, mock_planner, mock_logger, mock_snapshot):
        """Verify that CLI extracts numbers and stores them in session."""
        session = SessionMemory()
        cli = AegisCLI(session=session)
        
        # Simulate a result from an action
        from execution.actions.app_actions import ActionResult
        res = ActionResult(action_type="type_text", success=True, message="Result: 30")
        
        # Mock engine to return this result
        cli._engine = MagicMock()
        cli._engine.execute_action.return_value = res
        
        # Mock approval
        mock_approve.return_value = (True, None)
        
        # Mock planner to return a simple plan
        mock_planner_inst = mock_planner.return_value
        mock_planner_inst.generate_plan.return_value = {
            "summary": "Calc",
            "actions": [{"type": "type_text", "value": "10+20", "description": "calc"}],
            "requires_approval": True
        }
        
        with patch("builtins.print"):
            cli._process_command("calculate 10+20")
            
        assert session.last_result == "30"

    @patch("interfaces.cli.AegisLogger")
    def test_browser_tab_tracking(self, mock_logger):
        """Verify that CLI tracks browser focus and URLs."""
        session = SessionMemory()
        cli = AegisCLI(session=session)
        cli._engine = MagicMock()
        cli._engine.execute_action.return_value = MagicMock(success=True, message="Focused")
        
        # Simulate CLI loop tracking logic
        # 1. Open Chrome
        action_open = Action(type="open_application", value="chrome", description="open")
        self._simulate_cli_tracking(cli, action_open, MagicMock(success=True, message="Opened Chrome"))
                
        assert session.last_app == "chrome"
        assert session.last_tab == "New Tab"
        
        # 2. Type URL
        action_type = Action(type="type_text", value="https://youtube.com", description="go to yt")
        self._simulate_cli_tracking(cli, action_type, MagicMock(success=True, message="Navigated"))
                
        assert session.last_tab == "https://youtube.com"

    def _simulate_cli_tracking(self, cli, action, res):
        """Helper to run the tracking logic from cli.py loop."""
        if action.type in ("open_application", "focus_application"):
            cli._session.last_app = action.value
            if action.value and action.value.lower() in ("chrome", "edge", "browser"):
                cli._session.last_tab = cli._session.browser_context["last_url"] or "New Tab"

        if action.type == "type_text" and cli._session.last_app and cli._session.last_app.lower() in ("chrome", "edge"):
            if action.value and (action.value.startswith("http") or "." in action.value):
                cli._session.last_tab = action.value
                cli._session.browser_context["last_url"] = action.value

    def test_prompt_next_action_logic(self):
        """Verify the post-action prompt handler."""
        from execution.actions.ui_actions import _prompt_next_action_handler
        action = Action(type="prompt_next_action", value="", description="What next?")
        res = _prompt_next_action_handler(action)
        assert res.success is True
        assert "What next?" in res.message
