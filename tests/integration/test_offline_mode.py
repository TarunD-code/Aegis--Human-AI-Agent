"""
Aegis v3.6.1 — Integration Test: Offline Mode
================================================
Verify AEGIS_OFFLINE_MODE returns deterministic mock responses.
"""

import sys
import os
from pathlib import Path
from unittest.mock import patch

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parent.parent.parent))


class TestOfflineMode:
    """Verify offline mode returns a valid mock plan without calling any real LLM."""

    @patch.dict(os.environ, {"AEGIS_OFFLINE_MODE": "true"})
    def test_offline_mode_returns_mock_plan(self):
        from brain.llm.llm_client import LLMClient

        client = LLMClient(system_prompt="Test prompt")
        assert client.offline_mode is True

        plan = client.generate_plan("open calculator")
        assert isinstance(plan, dict)
        assert "summary" in plan
        assert "actions" in plan
        assert isinstance(plan["actions"], list)
        assert len(plan["actions"]) > 0

    @patch.dict(os.environ, {"AEGIS_OFFLINE_MODE": "true"})
    def test_offline_mode_no_api_key_needed(self):
        from brain.llm.llm_client import LLMClient

        # Remove API key to prove offline doesn't need it
        with patch.dict(os.environ, {"GROQ_API_KEY": ""}, clear=False):
            client = LLMClient(system_prompt="Test")
            plan = client.generate_plan("search for cats")
            assert isinstance(plan, dict)
            assert plan.get("summary") is not None
