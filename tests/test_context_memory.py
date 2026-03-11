"""
Aegis v4.0 — Context Memory Tests
====================================
Validates that Aegis remembers the foreground app and uses it for context.
"""

import sys
from pathlib import Path
import pytest
from unittest.mock import MagicMock, patch

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from interfaces.cli import AegisCLI

class TestContextMemory:

    @patch("execution.ui_automation.get_active_window_title")
    def test_foreground_context_gathering(self, mock_title):
        """Verify that the CLI gathers the real active window title for the planner."""
        mock_title.return_value = "Chrome - Google Search"
        
        cli = AegisCLI()
        context = cli._gather_context()
        
        assert context["foreground_app"] == "Chrome - Google Search"

    @patch("interfaces.cli.detect_mood")
    @patch("interfaces.cli.request_approval")
    def test_session_state_mood_persistence(self, mock_approval, mock_mood):
        """Verify that mood is stored in session metadata."""
        mock_approval.return_value = (True, "")
        cli = AegisCLI()
        # Mock mood
        m_obj = MagicMock()
        m_obj.mood_type = "URGENT"
        mock_mood.return_value = m_obj
        
        cli._process_command("Help me now!")
        assert cli._session.get_metadata("current_mood") == "URGENT"
