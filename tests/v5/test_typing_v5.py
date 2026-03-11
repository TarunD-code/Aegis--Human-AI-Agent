import pytest
from unittest.mock import MagicMock, patch
from execution.actions.ui_actions import type_text
from brain.planner import Action

class TestTypingV5:
    """Tests for the v5 Context-Aware Typing Engine."""

    @patch("execution.ui_automation.hotkey")
    @patch("execution.ui_automation.type_text")
    @patch("execution.verification_engine.VerificationEngine.verify_and_retry")
    def test_type_text_browser_context(self, mock_verify, mock_type, mock_hotkey):
        """Verify that browser context triggers Ctrl+L."""
        mock_verify.return_value = (True, "Verified")
        
        # Action with browser context
        action = Action(
            type="type_text", 
            params={"text": "google.com", "application_name": "Chrome"}
        )
        
        type_text(action)
        
        # Check if Ctrl+L was pressed
        mock_hotkey.assert_called_with(["ctrl", "l"])
        # Check if type_text was called (via verify_and_retry)
        mock_verify.assert_called()

    @patch("execution.ui_automation.type_text")
    @patch("execution.verification_engine.VerificationEngine.verify_and_retry")
    def test_type_text_generic_context(self, mock_verify, mock_type):
        """Verify no Ctrl+L for non-browser apps."""
        mock_verify.return_value = (True, "Verified")
        
        with patch("execution.ui_automation.hotkey") as mock_hotkey:
            action = Action(
                type="type_text", 
                params={"text": "Hello", "application_name": "Notepad"}
            )
            type_text(action)
            
            mock_hotkey.assert_not_called()

    @patch("execution.ui_automation.type_text")
    @patch("execution.verification_engine.VerificationEngine.verify_and_retry")
    def test_type_text_blind_fallback(self, mock_verify, mock_type):
        """Verify that failure in verification triggers blind fallback."""
        # Verification fails
        mock_verify.return_value = (False, "Failed")
        
        action = Action(type="type_text", params={"text": "Hello", "application_name": "Notepad"})
        
        result = type_text(action)
        
        # Verification failed, but the result should be success=True because of fallback
        assert result.success is True
        assert "Blind fallback applied" in result.message
        # The underlying ui.type_text should have been called twice (once via verify, once via fallback)
        # However, mock_type is mocked directly, so we check if it was called.
        # Wait, mock_verify calls the function passed to it. In this case ui.type_text.
        # But we mocked the VerificationEngine.verify_and_retry which usually calls it.
        # Let's check mock_type calls.
        assert mock_type.called
