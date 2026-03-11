import pytest
from unittest.mock import MagicMock, patch
from execution.engine import ExecutionEngine
from brain.planner import Action
from execution.actions.app_actions import ExecutionResult

class TestExecutionResilienceV5:
    """Tests for the v5 Execution Resilience layer."""

    @patch("execution.engine.ACTION_REGISTRY")
    def test_global_retry_logic(self, mock_registry):
        """Verify that the engine retries a failed action once."""
        mock_handler = MagicMock()
        # Fail first, succeed second
        mock_handler.side_effect = [
            ExecutionResult(success=False, message="Transient error"),
            ExecutionResult(success=True, message="Success on retry")
        ]
        mock_registry.get.return_value = mock_handler
        
        engine = ExecutionEngine()
        action = Action(type="press_key", value="enter")
        
        result = engine.execute(action)
        
        assert result.success is True
        assert result.message == "Success on retry"
        assert mock_handler.call_count == 2

    @patch("execution.engine.ACTION_REGISTRY")
    def test_focus_to_open_fallback(self, mock_registry):
        """Verify that failing focus_application triggers open_application."""
        mock_focus_handler = MagicMock(return_value=ExecutionResult(success=False, message="Window not found"))
        mock_open_handler = MagicMock(return_value=ExecutionResult(success=True, message="App opened successfully"))
        
        def registry_get(action_type):
            if action_type == "focus_application": return mock_focus_handler
            if action_type == "open_application": return mock_open_handler
            return None
            
        mock_registry.get.side_effect = registry_get
        
        engine = ExecutionEngine()
        action = Action(type="focus_application", value="Chrome")
        
        result = engine.execute(action)
        
        assert result.success is True
        assert "App opened successfully" in result.message
        assert mock_focus_handler.call_count == 1
        assert mock_open_handler.call_count == 1

    def test_optional_action_resilience(self):
        """Verify that a failed optional action doesn't stop the plan."""
        engine = ExecutionEngine()
        
        # Mock execute to fail
        engine.execute = MagicMock(return_value=ExecutionResult(success=False, message="Fail"))
        
        from brain.planner import ActionPlan
        plan = ActionPlan(
            summary="Test Plan",
            actions=[
                Action(type="print", params={"optional": True}),
                Action(type="print")
            ]
        )
        
        results = engine.execute_plan(plan)
        
        assert len(results) == 2
        # Plan should continue despite first action failure because it's optional
        assert engine.execute.call_count == 2
