"""
Aegis v2.0 — Contextual Planner Tests
=======================================
Tests for the enhanced contextual planner.
"""

import sys
import json
import os
from pathlib import Path
from unittest.mock import MagicMock, patch

# Ensure project root is importable
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

# Set dummy env var for config to find
os.environ["GROQ_API_KEY"] = "gsk_FAKE_KEY"

from brain.contextual_planner import ContextualPlanner

class TestContextualPlanner:
    """Tests for prompt enrichment and AI interaction."""

    # Patch GroqClient where it is used (inside contextual_planner.py)
    @patch("brain.contextual_planner.GroqClient")
    def test_generate_plan_enriched(self, mock_client_class):
        # 1. Setup mocks
        mock_client = MagicMock()
        mock_client.generate_plan.return_value = {
            "summary": "Context accepted",
            "actions": [],
            "requires_approval": False
        }
        mock_client_class.return_value = mock_client

        # 2. Run test
        planner = ContextualPlanner()
        context = {
            "system_snapshot": {"cpu_percent": 10},
            "running_apps": ["notepad.exe"],
            "foreground_app": "VS Code",
            "open_windows": ["Aegis", "Code"],
            "recent_approved": [],
            "recent_rejected": [],
            "frequent_apps": []
        }
        
        plan_dict = planner.generate_plan("hello", context=context)
        assert plan_dict["summary"] == "Context accepted"
        
        # 3. Verify interaction
        # GroqClient initialization
        mock_client_class.assert_called_once()
        # generate_plan should be called
        mock_client.generate_plan.assert_called_once()
        
        sent_prompt = mock_client.generate_plan.call_args[0][0]
        assert "CURRENT CONTEXT" in sent_prompt
        assert "notepad.exe" in sent_prompt

    def test_format_bytes(self):
        planner = ContextualPlanner()
        assert planner._format_bytes(1024) == "1.0 KB"
        assert planner._format_bytes(1024 * 1024) == "1.0 MB"
        assert planner._format_bytes(1024 * 1024 * 1024) == "1.0 GB"
