"""
Aegis v1.0 — Planner Tests
============================
Tests for ActionPlan parsing and validation.
"""

import sys
from pathlib import Path

import pytest

# Ensure project root is importable
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from brain.planner import Action, ActionPlan, parse_plan


class TestParseValidPlan:
    """Tests for successfully parsing valid plans."""

    def test_single_action_plan(self):
        raw = {
            "summary": "Open Notepad",
            "actions": [
                {"type": "open_application", "value": "notepad"}
            ],
            "requires_approval": True,
        }
        plan = parse_plan(raw)
        assert plan.summary == "Open Notepad"
        assert len(plan.actions) == 1
        assert plan.actions[0].type == "open_application"
        assert plan.actions[0].value == "notepad"
        assert plan.requires_approval is True

    def test_multi_action_plan(self):
        raw = {
            "summary": "Organize and list duplicates",
            "actions": [
                {"type": "organize_files", "target": "D:\\Downloads"},
                {"type": "list_duplicates", "target": "D:\\Downloads"},
            ],
            "requires_approval": True,
        }
        plan = parse_plan(raw)
        assert len(plan.actions) == 2
        assert plan.actions[0].type == "organize_files"
        assert plan.actions[1].type == "list_duplicates"

    def test_conversational_plan(self):
        raw = {
            "summary": "Hello! I'm Aegis, your AI assistant.",
            "actions": [],
            "requires_approval": False,
        }
        plan = parse_plan(raw)
        assert plan.is_conversational is True
        assert plan.requires_approval is False

    def test_action_with_params(self):
        raw = {
            "summary": "Create a file",
            "actions": [
                {
                    "type": "create_file",
                    "target": "D:\\test.txt",
                    "value": "Hello World",
                    "params": {"encoding": "utf-8"},
                }
            ],
            "requires_approval": True,
        }
        plan = parse_plan(raw)
        assert plan.actions[0].params == {"encoding": "utf-8"}


class TestParseInvalidPlan:
    """Tests for rejecting invalid plan structures."""

    def test_missing_summary(self):
        raw = {"actions": [], "requires_approval": True}
        with pytest.raises(ValueError, match="summary"):
            parse_plan(raw)

    def test_non_dict_input(self):
        with pytest.raises(ValueError, match="JSON object"):
            parse_plan("not a dict")

    def test_action_missing_type(self):
        raw = {
            "summary": "Bad plan",
            "actions": [{"value": "something"}],
            "requires_approval": True,
        }
        with pytest.raises(ValueError, match="missing 'type'"):
            parse_plan(raw)

    def test_unknown_action_type(self):
        raw = {
            "summary": "Evil plan",
            "actions": [{"type": "delete_everything"}],
            "requires_approval": True,
        }
        with pytest.raises(ValueError, match="unknown action type"):
            parse_plan(raw)

    def test_actions_not_a_list(self):
        raw = {
            "summary": "Bad structure",
            "actions": "not a list",
            "requires_approval": True,
        }
        with pytest.raises(ValueError, match="list"):
            parse_plan(raw)


class TestActionPlanProperties:
    """Tests for ActionPlan dataclass properties."""

    def test_is_conversational_true(self):
        plan = ActionPlan(summary="Hi", actions=[], requires_approval=False)
        assert plan.is_conversational is True

    def test_is_conversational_false(self):
        action = Action(type="open_application", value="notepad")
        plan = ActionPlan(summary="Open app", actions=[action])
        assert plan.is_conversational is False

    def test_str_representation(self):
        action = Action(type="open_application", value="notepad")
        plan = ActionPlan(summary="Open Notepad", actions=[action])
        text = str(plan)
        assert "Open Notepad" in text
        assert "open_application" in text
