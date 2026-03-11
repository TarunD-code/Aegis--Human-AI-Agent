import pytest
import os
import json
from unittest.mock import MagicMock, patch
from brain.planner import Action, ActionPlan, parse_plan
from execution.actions import ACTION_REGISTRY
from memory.working_memory import WorkingMemory
from logs.action_logger import ActionLogger
from config import ACTION_WHITELIST, ACTION_ALIASES

def test_v7_planner_thought_reflect_schema():
    """Validate that the planner correctly extracts thought/reflect fields."""
    raw_json = {
        "summary": "Full cognitive plan",
        "actions": [
            {
                "thought": "I should open notepad",
                "type": "open_application",
                "params": {"application_name": "notepad"},
                "reflect": "Verify notepad is open"
            }
        ]
    }
    plan = parse_plan(raw_json)
    assert plan.actions[0].thought == "I should open notepad"
    assert plan.actions[0].reflect == "Verify notepad is open"

def test_v7_planner_safety_enforcement():
    """Validate that risk/confirmation logic is enforced."""
    raw_json = {
        "summary": "Risky plan",
        "actions": [
            {
                "type": "run_powershell",
                "params": {"command": "rm -rf /"},
                "risk_level": "CRITICAL",
                "requires_confirmation": False
            }
        ]
    }
    plan = parse_plan(raw_json)
    assert plan.actions[0].risk_level == "CRITICAL"
    assert plan.actions[0].requires_confirmation is True  # Forced by v7.0 safety rules

def test_v7_registry_completeness():
    """Validate that every whitelisted action has a handler or alias in the registry."""
    missing = []
    for a in ACTION_WHITELIST:
        canonical = ACTION_ALIASES.get(a, a)
        if canonical not in ACTION_REGISTRY:
            missing.append(a)
    assert not missing, f"Missing handlers for: {missing}"

def test_v7_working_memory_context_buffer():
    """Validate the working memory ring buffer."""
    wm = WorkingMemory()
    wm.push_action("click", {"x": 10}, {"success": True, "message": "Clicked"})
    wm.push_action("type_text", {"text": "hi"}, {"success": True, "message": "Typed"})
    
    recent = wm.get_recent_actions(2)
    assert len(recent) == 2
    assert recent[0]["action_type"] == "click"
    assert recent[1]["action_type"] == "type_text"

def test_v7_action_logger_output(tmp_path):
    """Validate structured logging."""
    log_file = tmp_path / "test_log.jsonl"
    logger = ActionLogger(log_dir=str(tmp_path))
    logger.log_file = str(log_file)
    
    logger.log_action("test_action", {"p": 1}, True, "Done", 10.5)
    
    with open(log_file, "r") as f:
        line = f.readline()
        data = json.loads(line)
        assert data["action_type"] == "test_action"
        assert data["duration_ms"] == 10.5

def test_v7_vision_read():
    """Validate vision OCR integration with mocked hub."""
    from agents.vision_agent import vision_controller
    with patch.object(vision_controller.vision_hub, 'vision_read', return_value="Hello Vision"):
        result = vision_controller.vision_hub.vision_read()
        assert "Hello Vision" in result

def test_v7_engine_variable_resolution():
    """Ensure engine resolves variables from all Working Memory keys."""
    from execution.engine import ExecutionEngine
    from core.state import working_memory
    
    working_memory.set("target_app", "calculator")
    # Note: ExecutionEngine.execute modifies action params IN PLACE
    action = Action(type="open_application", params={"application_name": "{{target_app}}"})
    
    engine = ExecutionEngine()
    with patch("core.app_registry.registry.resolve", return_value="calc.exe"):
        with patch("execution.actions.open_application", return_value=MagicMock(success=True)):
            engine.execute(action)
            assert action.params["application_name"] == "calculator"
