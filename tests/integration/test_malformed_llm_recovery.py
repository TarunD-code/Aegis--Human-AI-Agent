"""
Aegis v3.6.1 — Integration Test: Malformed LLM Recovery
=========================================================
Verify the validator rejects bad plans and provides actionable error hints.
"""

import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parent.parent.parent))


class TestMalformedLLMRecovery:
    """Test validation catches malformed LLM outputs."""

    def test_missing_summary_rejected(self):
        from brain.plan_validator import normalize_and_validate

        bad_plan = {
            "reasoning": "Something",
            "actions": [{"type": "open_application", "parameters": {"application_name": "notepad"}}],
        }
        is_valid, errors = normalize_and_validate(bad_plan)
        assert not is_valid
        assert "missing_summary" in errors

    def test_unknown_action_rejected(self):
        from brain.plan_validator import normalize_and_validate

        bad_plan = {
            "summary": "Do something",
            "reasoning": "Because",
            "actions": [{"type": "hack_the_planet", "parameters": {}}],
        }
        is_valid, errors = normalize_and_validate(bad_plan)
        assert not is_valid
        assert any("unknown_action" in e for e in errors)

    def test_missing_required_param_reported(self):
        from brain.plan_validator import normalize_and_validate

        bad_plan = {
            "summary": "Open app",
            "reasoning": "User wants it",
            "actions": [{"type": "open_application", "parameters": {}}],
        }
        is_valid, errors = normalize_and_validate(bad_plan)
        assert not is_valid
        assert any("missing_parameter" in e for e in errors)

    def test_valid_plan_passes(self):
        from brain.plan_validator import normalize_and_validate

        good_plan = {
            "summary": "Open Notepad",
            "reasoning": "User explicitly asked",
            "actions": [{
                "type": "open_application",
                "parameters": {"application_name": "notepad"},
            }],
        }
        is_valid, errors = normalize_and_validate(good_plan)
        assert is_valid
        assert errors == []
