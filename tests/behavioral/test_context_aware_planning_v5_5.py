import pytest
from unittest.mock import MagicMock, patch
from brain.contextual_planner import ContextualPlanner
from brain.planner import ActionPlan, Action

class TestContextAwarePlanningV5_5:
    @patch("brain.llm.llm_client.LLMClient.generate_plan")
    def test_add_5_with_it_flow(self, mock_llm):
        """Verify that the planner uses working memory for 'it' resolution."""
        from core.state import working_memory
        working_memory.reset()
        working_memory.set("last_result", 15)
        
        planner = ContextualPlanner()
        
        # Mock LLM to expect the expanded query in the prompt
        mock_llm.return_value = {
            "summary": "Calculating 15 + 5",
            "reasoning": "User asked to add 5 to 'it' (15).",
            "actions": [{"type": "compute_result", "params": {"expression": "15 + 5"}, "description": "calc", "risk_level": "LOW"}],
            "requires_approval": False
        }
        
        # We pass an empty session_state in context because WorkingMemory is global
        plan = planner.generate_plan("add 5 with it", context={"session_state": {}})
        
        # Verify the prompt structure
        prompt_str = str(mock_llm.call_args)
        assert "[USER MESSAGE]" in prompt_str
        assert "Original: add 5 with it" in prompt_str
        assert "Expanded (Contextual): add 5 with 15" in prompt_str
        assert "[WORKING MEMORY]" in prompt_str
        assert "last_result: 15" in prompt_str
        
        # Verify result
        assert "15 + 5" in plan.actions[0].params["expression"]

    @patch("brain.llm.llm_client.LLMClient.generate_plan")
    def test_write_again_flow_context_aware(self, mock_llm):
        """Verify that 'write again' uses working memory and task state."""
        from core.state import working_memory, task_manager
        working_memory.reset()
        task_manager.reset_task()
        
        working_memory.set("last_text_written", "Greetings from Aegis")
        working_memory.set("active_application", "Notepad")
        task_manager.update_task("Writing", state="typing", app="Notepad")
        
        planner = ContextualPlanner()
        mock_llm.return_value = {
            "summary": "Typing greetings again",
            "reasoning": "User asked to repeat the previous text.",
            "actions": [{"type": "type_text", "params": {"text": "Greetings from Aegis", "application_name": "Notepad"}, "description": "typing", "risk_level": "LOW"}],
            "requires_approval": False
        }
        
        plan = planner.generate_plan("write again", context={"session_state": {}})
        
        prompt_str = str(mock_llm.call_args)
        assert "Expanded (Contextual): type text 'Greetings from Aegis' in the active application" in prompt_str
        assert "[ACTIVE TASK]" in prompt_str
        assert "ACTIVE WORKFLOW: Writing" in prompt_str
        assert "Primary App: Notepad" in prompt_str
