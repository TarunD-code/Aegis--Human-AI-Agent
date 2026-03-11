import pytest
from unittest.mock import MagicMock, patch
from execution.actions.ui_actions import type_text
from brain.planner import Action

class TestTypingVerificationV5_1:
    """Tests for the v5.1 Active Window Verification logic."""

    @patch("execution.actions.ui_actions.focus_window_v5")
    @patch("execution.ui_automation.core.verify_active_window")
    @patch("execution.actions.ui_actions.ui.type_text")
    def test_type_text_verifies_window_pass(self, mock_type, mock_verify, mock_focus):
        """Verify that typing proceeds if verification passes."""
        mock_verify.return_value = True
        
        action = Action(type="type_text", params={"text": "hello", "application_name": "Notepad"})
        result = type_text(action)
        
        assert result.success is True
        mock_type.assert_called()
        mock_verify.assert_called_with("Notepad")

    @patch("execution.actions.ui_actions.focus_window_v5")
    @patch("execution.ui_automation.core.verify_active_window")
    def test_type_text_fails_after_retry(self, mock_verify, mock_focus):
        """Verify that typing aborts if verification fails even after refocus retry."""
        # Fail first, fail second
        mock_verify.side_effect = [False, False]
        
        action = Action(type="type_text", params={"text": "hello", "application_name": "Notepad"})
        result = type_text(action)
        
        assert result.success is False
        assert "Could not verify 'Notepad' is in focus" in result.message
        assert mock_focus.call_count == 2
