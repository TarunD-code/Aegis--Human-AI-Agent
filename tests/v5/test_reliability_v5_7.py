import pytest
from unittest.mock import MagicMock, patch
from brain.contextual_planner import ContextualPlanner
from brain.command_normalizer import normalizer
from brain.math_engine import math_engine
from core.app_registry import registry
from execution.engine import ExecutionEngine
from brain.planner import Action

class TestReliabilityV5_7:
    @pytest.fixture
    def planner(self):
        return ContextualPlanner()

    def test_command_normalization(self):
        """Verify that typos are corrected."""
        assert normalizer.normalize("opne notepd") == "open notepad"
        assert normalizer.normalize("wright") == "write"

    def test_math_evaluation_direct(self):
        """Verify that math expressions are evaluated by MathEngine."""
        assert math_engine.evaluate("10 + 5 * 2") == 20.0
        assert math_engine.evaluate("safe_eval(1+1)") is None  # Security check

    def test_planner_math_routing(self, planner):
        """Verify that math queries return a compute_result action directly."""
        with patch("core.state.working_memory.set") as mock_set:
            plan = planner.generate_plan("calculate 100 / 4", context={})
            assert plan.actions[0].type == "compute_result"
            assert plan.actions[0].value == "25.0"
            mock_set.assert_called_with("last_result", 25.0)

    def test_app_registry_resolution(self):
        """Verify that registry resolves names to paths."""
        path = registry.resolve("notepad")
        assert "notepad.exe" in path.lower()

    @patch("execution.engine.ACTION_REGISTRY")
    def test_execution_retry_logic(self, mock_registry):
        """Verify that ExecutionEngine retries failed actions 3 times."""
        engine = ExecutionEngine()
        mock_handler = MagicMock()
        mock_handler.side_effect = [
            MagicMock(success=False, message="Failure 1"),
            MagicMock(success=False, message="Failure 2"),
            MagicMock(success=True, message="Success on 3rd")
        ]
        mock_registry.get.return_value = mock_handler
        
        action = Action(type="type_text", value="hello")
        result = engine.execute(action)
        
        assert result.success is True
        assert mock_handler.call_count == 3

    def test_planner_hardening_fallback(self, planner):
        """Verify that planner doesn't crash if prompt construction fails."""
        with patch.object(planner, "_proactive_engine") as mock_proactive:
            mock_proactive.generate_suggestions.side_effect = Exception("Crash!")
            # This should trigger the fallback logic in _build_enriched_prompt
            prompt = planner._build_enriched_prompt("test", "test", {})
            assert "[SYSTEM] Context construction failed" in prompt
