"""
Aegis v3.0 — Session & Context Upgrade Tests
=============================================
Verifies result chaining, rejection feedback, and context-aware automation.
"""

import sys
from pathlib import Path
from unittest.mock import MagicMock, patch

import pytest

# Ensure project root is importable
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from memory.session_memory import SessionMemory
from security.approval_gate import request_approval
from execution.actions.ui_actions import type_text
from brain.planner import Action

class TestSessionContext:
    """Tests for session persistence and Feedback."""

    def test_session_state_persistence(self):
        """Verify result and app tracking in SessionMemory."""
        session = SessionMemory()
        session.add_entry("test", "plan", result="Calculated: 42")
        
        state = session.get_session_state()
        assert state["command_count"] == 1
        # Result chaining logic in CLI (captured here via mock integration)
        session.last_result = "42" 
        assert session.get_session_state()["last_result"] == "42"

    @patch("builtins.input")
    def test_rejection_feedback_capture(self, mock_input):
        """Verify approval gate captures feedback on 'no'."""
        # 1. Reject with reason
        mock_input.side_effect = ["no", "use chrome instead"]
        approved, feedback = request_approval()
        assert approved is False
        assert feedback == "use chrome instead"

    @patch("core.environment_scanner.get_foreground_app")
    @patch("automation.ui_controller.press_key")
    @patch("automation.ui_controller.type_text")
    def test_calculator_continuity(self, mock_type, mock_press, mock_fg):
        """Verify Calculator skips ESC when chaining."""
        mock_fg.return_value = "Calculator"
        mock_type.return_value = {"success": True, "message": "Typed"}
        
        # Fresh calculation (starts with number)
        action_fresh = Action(type="type_text", value="100")
        type_text(action_fresh)
        mock_press.assert_called_with("esc")
        
        mock_press.reset_mock()
        
        # Chained calculation (starts with operator)
        action_chain = Action(type="type_text", value="+50")
        type_text(action_chain)
        mock_press.assert_not_called()

    @patch("core.environment_scanner.get_foreground_app")
    @patch("automation.ui_controller.type_text")
    def test_browser_typing_context(self, mock_type, mock_fg):
        """Verify browser detection logic."""
        mock_fg.return_value = "Google Chrome"
        mock_type.return_value = {"success": True, "message": "Typed"}
        
        action = Action(type="type_text", value="https://google.com")
        res = type_text(action)
        assert res.success is True
