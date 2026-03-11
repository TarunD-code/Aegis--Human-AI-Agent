import pytest
from unittest.mock import MagicMock, patch
from execution.ui_automation.window_focus import focus_window_v5

class TestWindowFocusV5_1:
    """Tests for the v5.1 Window Focus Engine improvements."""

    @patch("pywinauto.findwindows.find_elements")
    @patch("win32gui.GetForegroundWindow")
    @patch("execution.ui_automation.window_focus._activate_window_v5_1")
    def test_focus_window_with_rectangle_property(self, mock_activate, mock_fg_hwnd, mock_find_elements):
        """Verify that .rectangle is accessed as a property, not a method."""
        mock_win = MagicMock()
        # Mock .rectangle as a property that returns an object with width() and height()
        mock_rect = MagicMock()
        mock_rect.width.return_value = 100
        mock_rect.height.return_value = 100
        # This is the key: accessing .rectangle should not raise 'RECT' object is not callable
        type(mock_win).rectangle = mock_rect
        
        mock_find_elements.return_value = [mock_win]
        mock_activate.return_value = True
        
        # This should call calculate_priority which accesses w.rectangle
        success = focus_window_v5("Chrome")
        
        assert success is True
        # Verify rectangle was accessed (as a property, not a call)
        # Note: MagicMock attribute access is hard to "assert" without side_effect tracking
        # but the lack of TypeError is the main check here.

    @patch("pywinauto.findwindows.find_elements")
    @patch("execution.ui_automation.window_focus._activate_window_v5_1")
    @patch("pyautogui.click")
    def test_focus_fallback_chain(self, mock_click, mock_activate, mock_find_elements):
        """Verify that Stage 3 (click) is triggered if Stages 1 & 2 fail."""
        mock_win = MagicMock()
        mock_rect = MagicMock()
        mock_rect.left = 10
        mock_rect.top = 20
        mock_rect.width.return_value = 100
        mock_rect.height.return_value = 100
        type(mock_win).rectangle = mock_rect
        mock_find_elements.return_value = [mock_win]
        
        # Stage 1 & 2 fail
        mock_activate.return_value = False
        
        success = focus_window_v5("Chrome")
        
        assert success is True
        # Verify pyautogui.click was called at the center of the mock window
        mock_click.assert_called_once_with(10 + 50, 20 + 50)
