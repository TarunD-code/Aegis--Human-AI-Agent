import pytest
from unittest.mock import MagicMock, patch
from vision.ui_inspector import UIInspector

class TestDigitalVisionV5:
    """Tests for the v5 Digital Vision Engine (UIA-based)."""

    @patch("vision.ui_inspector.Desktop")
    def test_find_elements_mock(self, mock_desktop_class):
        """Verify that find_elements calls descendants with correct params."""
        mock_desktop = mock_desktop_class.return_value
        mock_win = MagicMock()
        mock_desktop.window.return_value = mock_win
        mock_win.exists.return_value = True
        
        inspector = UIInspector()
        inspector.find_elements("Chrome", name="Login", control_type="Button")
        
        mock_win.descendants.assert_called_with(title="Login", control_type="Button")

    @patch("vision.ui_inspector.Desktop")
    def test_click_element_by_name_mock(self, mock_desktop_class):
        """Verify that click_element_by_name triggers a click on the correct element."""
        mock_desktop = mock_desktop_class.return_value
        mock_win = MagicMock()
        mock_desktop.window.return_value = mock_win
        mock_win.exists.return_value = True
        
        mock_el = MagicMock()
        mock_el.is_visible.return_value = True
        mock_win.descendants.return_value = [mock_el]
        
        inspector = UIInspector()
        success = inspector.click_element_by_name("Chrome", "Login")
        
        assert success is True
        mock_el.click_input.assert_called_once()
