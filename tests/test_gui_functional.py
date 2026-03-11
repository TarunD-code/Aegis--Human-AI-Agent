"""
Aegis v3.0 — GUI Functional Test (Calculator)
==============================================
Tests the full GUI automation chain: mock opening, focusing, and math.
"""

import sys
from pathlib import Path
from unittest.mock import MagicMock, patch

import pytest

# Ensure project root is importable
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from brain.planner import Action
from execution.actions.ui_actions import type_text, press_key

class TestGUICalculatorSequence:
    """Verify Calculator automation logic (ESC -> formula -> ENTER)."""

    @patch("automation.ui_controller.UI_AVAILABLE", True)
    @patch("automation.ui_controller.type_text")
    @patch("automation.ui_controller.press_key")
    @patch("automation.ui_controller.wait")
    @patch("core.environment_scanner.get_foreground_app")
    def test_calculator_math_sequence(self, mock_fg, mock_wait, mock_press, mock_type):
        """Test: 2+5*10 sequence."""
        # Setup mocks
        mock_fg.return_value = "Calculator"
        mock_type.return_value = {"success": True, "message": "Typed"}
        mock_press.return_value = {"success": True, "message": "Pressed"}
        
        # 1. Type formula
        action_type = Action(type="type_text", value="2+5*10")
        res_type = type_text(action_type)
        
        assert res_type.success is True
        # Verify ESC was pressed because foreground is Calculator
        # First call to press_key should be 'esc', second (if any) is from direct press_key call
        mock_press.assert_any_call("esc")
        mock_type.assert_called_with("2+5*10")

        # 2. Press Enter
        action_enter = Action(type="press_key", value="enter")
        res_enter = press_key(action_enter)
        
        assert res_enter.success is True
        mock_press.assert_any_call("enter")

    @patch("automation.ui_controller.UI_AVAILABLE", False)
    def test_gui_unavailable_graceful_error(self):
        """Verify fallback when UI deps are missing."""
        action = Action(type="type_text", value="test")
        res = type_text(action)
        
        assert res.success is False
        assert "dependencies missing" in res.details["message"]
