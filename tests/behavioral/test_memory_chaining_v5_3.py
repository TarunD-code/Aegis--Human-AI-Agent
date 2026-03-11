import pytest
from unittest.mock import MagicMock, patch
from execution.engine import ExecutionEngine
from brain.planner import Action
from execution.actions.app_actions import ExecutionResult

class TestMemoryChainingV5_3:
    @patch("execution.engine.ACTION_REGISTRY")
    def test_compute_result_updates_working_memory(self, mock_registry):
        """Verify that compute_result action updates WorkingMemory.last_result."""
        from core.state import working_memory
        working_memory.reset()
        
        # Mock compute_result handler
        mock_handler = MagicMock(return_value=ExecutionResult(
            success=True, 
            message="15", 
            data={"result": 15}
        ))
        mock_registry.get.return_value = mock_handler
        
        engine = ExecutionEngine()
        action = Action(type="compute_result", params={"expression": "10 + 5"})
        engine.execute(action)
        
        assert working_memory.get("last_result") == 15

    @patch("execution.engine.ACTION_REGISTRY")
    def test_type_text_updates_working_memory(self, mock_registry):
        """Verify that type_text updates WorkingMemory.last_text_written."""
        from core.state import working_memory
        working_memory.reset()
        
        mock_handler = MagicMock(return_value=ExecutionResult(success=True, message="Typed"))
        mock_registry.get.return_value = mock_handler
        
        engine = ExecutionEngine()
        action = Action(type="type_text", params={"text": "hello world", "application_name": "Notepad"})
        engine.execute(action)
        
        assert working_memory.get("last_text_written") == "hello world"
        assert working_memory.get("active_application") == "Notepad"

    @patch("brain.llm.llm_client.LLMClient.generate_plan")
    def test_planner_receives_working_memory(self, mock_llm):
        """Verify that ContextualPlanner injects WorkingMemory into the prompt."""
        from core.state import working_memory
        from brain.contextual_planner import ContextualPlanner
        
        working_memory.reset()
        working_memory.set("last_result", 999)
        
        planner = ContextualPlanner()
        mock_llm.return_value = {"summary": "test", "actions": [], "reasoning": "test", "requires_approval": False}
        
        planner.generate_plan("what was the result?", context={"session_state": {}})
        
        # Verify prompt content
        prompt = str(mock_llm.call_args)
        assert "last_result: 999" in prompt
