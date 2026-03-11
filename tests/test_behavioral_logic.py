import pytest
from unittest.mock import MagicMock, patch
from interfaces.cli import AegisCLI
from execution.engine import ExecutionEngine
from brain.planner import Action, ActionPlan, Action
from execution.actions.app_actions import ExecutionResult

class TestBehavioralRestoration:
    """Test suite for Aegis v4.1 Behavioral Restoration."""

    @patch("interfaces.cli.input")
    @patch("interfaces.cli.detect_mood")
    def test_conversational_loop_ends_with_followup(self, mock_mood, mock_input):
        """Verify that CLI output ends with the professional follow-up question."""
        mock_input.return_value = "exit" # To break loop after one run if needed, but we call _process_command directly
        mock_mood.return_value = MagicMock(mood_type="NEUTRAL")
        
        cli = AegisCLI()
        # Mock planner to return a simple conversational plan (no actions)
        plan = ActionPlan(summary="Hello", actions=[], requires_approval=False)
        cli._planner.generate_plan = MagicMock(return_value=plan)
        
        with patch("builtins.print") as mock_print:
            cli._process_command("Hi")
            # Check if any print call contains the follow-up question
            found = any("What would you like me to do next, Sir?" in str(call) for call in mock_print.call_args_list)
            assert found, "Follow-up question missing from output."

    @patch("interfaces.cli.input")
    @patch("interfaces.cli.detect_mood")
    def test_conflict_resolution_interaction(self, mock_mood, mock_input):
        """Verify that CONFLICT_REQUIRED triggers interactive prompt and decision update."""
        from unittest.mock import ANY
        mock_mood.return_value = MagicMock(mood_type="NEUTRAL")
        # User chooses to 'reuse'
        mock_input.return_value = "reuse"
        
        cli = AegisCLI()
        # Plan with one open_application action
        action = Action(type="open_application", params={"application_name": "chrome"})
        plan = ActionPlan(summary="Open Chrome", actions=[action], requires_approval=False)
        cli._planner.generate_plan = MagicMock(return_value=plan)
        
        # Engine first returns conflict, then success
        res_conflict = ExecutionResult(success=False, message="CONFLICT_REQUIRED", data={"app_name": "chrome"})
        res_success = ExecutionResult(success=True, message="Reused window")
        
        cli._engine.execute = MagicMock(side_effect=[res_conflict, res_success])
        
        with patch("builtins.print") as mock_print:
            cli._process_command("Search something")
            
            # Verify input was called for conflict decision
            mock_input.assert_called_with(ANY) # The decision prompt
            # Verify action was updated with decision
            assert action.params["decision"] == "reuse"
            # Verify success was reported
            assert any("✅" in str(call) for call in mock_print.call_args_list)

    def test_optional_action_resilience(self):
        """Verify that optional actions don't stop the plan on failure."""
        engine = ExecutionEngine()
        
        # Action 1: Optional, fails
        a1 = Action(type="focus_application", params={"application_name": "bad_app", "optional": True})
        # Action 2: Required, succeeds
        a2 = Action(type="type_text", params={"text": "hello"})
        
        plan = ActionPlan(summary="Resilient Plan", actions=[a1, a2])
        
        # Mock handlers
        mock_fail = MagicMock(return_value=ExecutionResult(success=False, message="Failed focus"))
        mock_ok = MagicMock(return_value=ExecutionResult(success=True, message="Typed"))
        
        with patch("execution.engine.ACTION_REGISTRY", {"focus_application": mock_fail, "type_text": mock_ok}):
            results = engine.execute_plan(plan)
            
            assert len(results) == 2
            assert results[0].success == False
            assert results[1].success == True
            assert results[1].message == "Typed"

    @patch("execution.ui_automation.pyautogui.hotkey")
    @patch("pyperclip.paste")
    @patch("pyperclip.copy")
    def test_scrape_results_logic(self, mock_copy, mock_paste, mock_hotkey):
        """Verify scrape_results captures content via clipboard."""
        from execution.actions.ui_actions import scrape_results
        
        # First call gets 'old' content, second gets 'new'
        mock_paste.side_effect = ["old clipboard", "Search Results: AI is cool"]
        action = Action(type="scrape_results", params={})
        
        result = scrape_results(action)
        
        assert result.success == True
        assert "AI is cool" in result.data["content"]
        assert mock_hotkey.called
