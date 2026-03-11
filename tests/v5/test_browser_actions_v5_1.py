import pytest
from unittest.mock import MagicMock, patch
from execution.actions.browser_actions import search_web, navigate_tab
from brain.planner import Action

class TestBrowserActionsV5_1:
    """Tests for the v5.1 Browser Action Handlers."""

    @patch("webbrowser.open")
    def test_search_web_handler(self, mock_browser_open):
        """Verify that search_web calls webbrowser.open with correctly quoted query."""
        action = Action(type="search_web", params={"query": "quantum computing"})
        result = search_web(action)
        
        assert result.success is True
        mock_browser_open.assert_called_once_with("https://www.google.com/search?q=quantum%20computing")

    @patch("pyautogui.hotkey")
    def test_navigate_tab_handler(self, mock_hotkey):
        """Verify that navigate_tab triggers Ctrl+Tab."""
        action = Action(type="navigate_tab", params={"direction": "next"})
        result = navigate_tab(action)
        
        assert result.success is True
        mock_hotkey.assert_called_once_with("ctrl", "tab")
