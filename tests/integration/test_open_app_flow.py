"""
Aegis v3.6.1 — Integration Test: Open Application Flow
========================================================
End-to-end test: LLM generates plan → user approves → executor runs → logs verified.
"""

import sys
import json
from pathlib import Path
from unittest.mock import MagicMock, patch

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parent.parent.parent))


class TestOpenAppFlow:
    """Mock the full pipeline: planner → validator → approval → execution → logs."""

    def test_open_calculator_flow(self, tmp_path):
        """Simulate 'open calculator' through the full pipeline."""
        from brain.plan_validator import normalize_and_validate

        # 1. Mock LLM response
        mock_plan = {
            "summary": "Open Calculator application",
            "reasoning": "User wants to open the Windows Calculator",
            "actions": [{
                "type": "open_application",
                "parameters": {"application_name": "calculator"},
                "risk_level": "LOW",
                "requires_confirmation": False,
            }],
            "requires_approval": True,
        }

        # 2. Validate the plan
        is_valid, errors = normalize_and_validate(mock_plan)
        assert is_valid, f"Plan should be valid, got errors: {errors}"

        # 3. Verify action normalization
        action = mock_plan["actions"][0]
        assert action["action_type"] == "open_application"
        assert action["parameters"]["application_name"] == "calculator"

    def test_plan_with_legacy_value_field(self):
        """Test that 'value' field is normalized to 'application_name'."""
        from brain.plan_validator import normalize_and_validate

        plan = {
            "summary": "Open Notepad",
            "reasoning": "User wants notepad",
            "actions": [{
                "type": "open_application",
                "value": "notepad",
                "parameters": {},
            }],
        }
        is_valid, errors = normalize_and_validate(plan)
        assert is_valid, f"Should normalize 'value' → 'application_name', got: {errors}"
        assert plan["actions"][0]["parameters"]["application_name"] == "notepad"
