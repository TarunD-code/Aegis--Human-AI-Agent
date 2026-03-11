import pytest
from unittest.mock import MagicMock, patch
from brain.contextual_planner import ContextualPlanner
from brain.planner import ActionPlan, Action

class TestConversationalFlowsV5_2:
    @patch("brain.llm.llm_client.LLMClient.generate_plan")
    def test_multi_turn_calculation_flow(self, mock_llm):
        """Test 'add 5 with it' flow."""
        memory = MagicMock()
        # Mocking session state in context
        context = {
            "session_state": {
                "last_result": 15,
                "last_input": "calculate 10 + 5"
            }
        }
        
        planner = ContextualPlanner(memory=memory)
        
        # We expect the prompt to contain '15' instead of 'it'
        mock_llm.return_value = {
            "summary": "Adding 5 to 15",
            "reasoning": "User asked to add 5 to the previous result.",
            "actions": [{"type": "compute_result", "params": {"expression": "15 + 5"}, "description": "calculating", "risk_level": "LOW"}],
            "requires_approval": False
        }
        
        plan = planner.generate_plan("add 5 with it", context=context)
        
        # Check if the LLM was called with the EXPANDED query
        assert "add 5 with 15" in str(mock_llm.call_args)
        assert plan.summary == "Adding 5 to 15"

    @patch("brain.llm.llm_client.LLMClient.generate_plan")
    def test_write_again_flow(self, mock_llm):
        """Test 'write again' flow."""
        memory = MagicMock()
        context = {
            "session_state": {
                "last_typed": "Aegis is stable",
                "active_application": "Notepad"
            }
        }
        
        planner = ContextualPlanner(memory=memory)
        
        mock_llm.return_value = {
            "summary": "Typing previous text again",
            "reasoning": "User asked to repeat the previous typing action.",
            "actions": [{"type": "type_text", "params": {"text": "Aegis is stable", "application_name": "Notepad"}}],
            "requires_approval": False
        }
        
        plan = planner.generate_plan("write again", context=context)
        
        assert "Aegis is stable" in str(mock_llm.call_args)
        assert plan.actions[0].params["application_name"] == "Notepad"
