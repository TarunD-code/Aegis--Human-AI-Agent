import pytest
from unittest.mock import MagicMock, patch
from execution.ui_automation.window_focus import focus_window_v5

class TestWindowFocusV5:
    """Tests for the v5 Robust Window Focus Engine."""

    @patch("pywinauto.findwindows.find_elements")
    @patch("win32gui.GetForegroundWindow")
    @patch("execution.ui_automation.window_focus._activate_window")
    def test_focus_exact_match(self, mock_activate, mock_fg, mock_find):
        """Verify that an exact title match is prioritized and focused."""
        # Create mock elements
        m1 = MagicMock()
        m1.handle = 101
        m1.name = "Notepad"
        m1.rectangle.return_value.width.return_value = 100
        m1.rectangle.return_value.height.return_value = 100
        m1.process_id = 1234
        
        mock_find.return_value = [m1]
        mock_fg.return_value = 999 # Some other window
        mock_activate.return_value = True
        
        assert focus_window_v5("Notepad") is True
        mock_activate.assert_called_with(101)

    @patch("pywinauto.findwindows.find_elements")
    @patch("win32gui.GetForegroundWindow")
    @patch("win32gui.IsWindowVisible")
    @patch("execution.ui_automation.window_focus._activate_window")
    def test_focus_multiple_windows_priority(self, mock_activate, mock_visible, mock_fg, mock_find):
        """Verify priority sorting: Exact > Visible > Largest."""
        # m1: Fuzzy match, Visible, Small
        m1 = MagicMock()
        m1.handle = 101
        m1.name = "My Notepad++"
        m1.rectangle.return_value.width.return_value = 50
        m1.rectangle.return_value.height.return_value = 50
        
        # m2: Exact match, Visible, Small
        m2 = MagicMock()
        m2.handle = 102
        m2.name = "Notepad"
        m2.rectangle.return_value.width.return_value = 40
        m2.rectangle.return_value.height.return_value = 40
        
        # m3: Fuzzy match, Visible, Large
        m3 = MagicMock()
        m3.handle = 103
        m3.name = "Untitled - Notepad"
        m3.rectangle.return_value.width.return_value = 200
        m3.rectangle.return_value.height.return_value = 200
        
        mock_find.return_value = [m1, m2, m3]
        mock_fg.return_value = 999
        mock_visible.return_value = True
        mock_activate.side_effect = [True] # Succeed on first attempt of sorted list
        
        focus_window_v5("Notepad")
        
        # Priority should be m2 (Exact) -> m3 (Largest) -> m1 (Smallest)
        # So mock_activate should be called with m2's handle (102) first
        mock_activate.assert_called_with(102)

    @patch("pywinauto.findwindows.find_elements")
    @patch("execution.ui_automation.window_focus._activate_window")
    @patch("execution.ui_automation.window_focus._alt_tab_fallback")
    def test_focus_fallback_triggered(self, mock_fallback, mock_activate, mock_find):
        """Verify that fallback strategies are triggered if direct activation fails."""
        m1 = MagicMock(handle=101, name="Notepad")
        mock_find.return_value = [m1]
        mock_activate.return_value = False # Fail direct activation
        mock_fallback.return_value = True
        
        assert focus_window_v5("Notepad") is True
        mock_fallback.assert_called_once()
