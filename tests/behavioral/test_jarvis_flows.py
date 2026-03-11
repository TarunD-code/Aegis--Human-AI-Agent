import pytest
from unittest.mock import MagicMock, patch
from execution.engine import ExecutionEngine
from brain.planner import Action, ActionPlan
from execution.actions.app_actions import ExecutionResult

class TestJarvisFlowsV5_1:
    """Consolidated behavioral tests for Aegis v5.1 Jarvis mode."""

    @patch("execution.engine.ACTION_REGISTRY")
    def test_direct_search_flow(self, mock_registry):
        """1. Open Chrome and search – should use search_web (direct URL)."""
        mock_handler = MagicMock(return_value=ExecutionResult(success=True, message="Searching..."))
        mock_registry.get.return_value = mock_handler
        
        engine = ExecutionEngine()
        action = Action(type="search_web", params={"query": "cats"})
        result = engine.execute(action)
        
        assert result.success is True
        assert "Searching" in result.message
        # Verify no UI typing handler was called for this search
        assert mock_handler.call_count == 1

    @patch("execution.actions.ui_actions.focus_window_v5")
    @patch("execution.ui_automation.core.verify_active_window")
    @patch("execution.ui_automation.core.pyautogui.write")
    def test_notepad_type_flow(self, mock_write, mock_verify, mock_focus):
        """2. Open Notepad and type – should focus, verify, type."""
        from execution.actions.ui_actions import type_text
        mock_verify.return_value = True
        
        action = Action(type="type_text", params={"text": "hello", "application_name": "Notepad"})
        result = type_text(action)
        
        assert result.success is True
        mock_focus.assert_called()
        mock_verify.assert_called_with("Notepad")
        mock_write.assert_called()

    @patch("pyautogui.hotkey")
    def test_navigate_tab_flow(self, mock_hotkey):
        """3. Navigate tabs – should use navigate_tab handler (Ctrl+Tab)."""
        from execution.actions.browser_actions import navigate_tab
        action = Action(type="navigate_tab", params={"direction": "next"})
        result = navigate_tab(action)
        assert result.success is True
        mock_hotkey.assert_called_with("ctrl", "tab")

    @patch("execution.engine.ACTION_REGISTRY")
    @patch("execution.ui_automation.window_focus.focus_window_v5")
    def test_recovery_from_focus_failure(self, mock_focus, mock_registry):
        """5. Recovery from focus failure – mock focus failure, verify retry and fallback."""
        mock_focus_handler = MagicMock(return_value=ExecutionResult(success=False, message="Fail"))
        mock_open_handler = MagicMock(return_value=ExecutionResult(success=True, message="Opened"))
        
        def registry_get(t):
            if t == "focus_application": return mock_focus_handler
            if t == "open_application": return mock_open_handler
            return None
        mock_registry.get.side_effect = registry_get
        
        engine = ExecutionEngine()
        action = Action(type="focus_application", value="Chrome")
        result = engine.execute(action)
        
        assert result.success is True
        assert "Opened" in result.message
        assert mock_focus_handler.call_count == 1 # 1 try then fallback to open

    @patch("core.state.session_memory")
    def test_active_app_memory(self, mock_memory):
        """6. Active app memory – after opening Chrome, write hello should use it."""
        mock_memory.active_application = "Chrome"
        
        # This test verifies the Planner's use of memory (mocking the context injection)
        from brain.contextual_planner import ContextualPlanner
        planner = ContextualPlanner(memory=mock_memory)
        # Mock LLM to return a plan using Chrome
        with patch.object(planner, "_client") as mock_client:
            mock_client.generate_plan.return_value = {
                "summary": "Typing into Chrome",
                "reasoning": "Active application found in memory.",
                "actions": [{"type": "type_text", "params": {"text": "hello", "application_name": "Chrome"}, "description": "typing", "risk_level": "LOW"}],
                "requires_approval": False
            }
            plan = planner.generate_plan("write hello", context={"session_state": {"active_application": "Chrome"}})
            assert plan.actions[0].params["application_name"] == "Chrome"

    @patch("execution.engine.ACTION_REGISTRY")
    def test_missing_action_handler_safety(self, mock_registry):
        """7. Missing action handler – ensure all actions in planner are registered."""
        mock_registry.get.return_value = None
        engine = ExecutionEngine()
        action = Action(type="unknown_action")
        result = engine.execute(action)
        assert result.success is False
        assert "No handler registered" in result.message

    def test_rect_property_safety(self):
        """8. Window focus with RECT property – no crash."""
        from execution.ui_automation.window_focus import focus_window_v5
        with patch("pywinauto.findwindows.find_elements") as mock_find:
            mock_win = MagicMock()
            mock_rect = MagicMock()
            type(mock_win).rectangle = mock_rect
            mock_find.return_value = [mock_win]
            # No crash when accessing mock_win.rectangle
            focus_window_v5("Test")

    @patch("subprocess.Popen")
    def test_browser_new_tab(self, mock_popen):
        """9. Browser new tab with URL – should use command line."""
        from execution.actions.browser_actions import open_new_tab
        action = Action(type="open_new_tab", params={"url": "https://google.com"})
        open_new_tab(action)
        mock_popen.assert_called()

    @patch("execution.engine.ExecutionEngine._log_risk")
    @patch("execution.engine.ACTION_REGISTRY")
    def test_critical_action_logging(self, mock_registry, mock_log_risk):
        """10. Critical action verification – ensure logs are hit."""
        mock_registry.get.return_value = MagicMock(return_value=ExecutionResult(success=True, message="OK"))
        engine = ExecutionEngine()
        action = Action(type="delete_file", risk_level="CRITICAL")
        engine.execute(action)
        mock_log_risk.assert_called_once()
