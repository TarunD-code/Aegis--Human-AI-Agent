import pytest
from unittest.mock import MagicMock, patch
from brain.contextual_planner import ContextualPlanner
from brain.planner import ActionPlan, Action

class TestPlannerV5:
    """Tests for the v5 Planner Engine Hardening."""

    @patch("brain.llm.llm_client.LLMClient.generate_plan")
    @patch("brain.intent_engine.IntentClassifier.classify")
    def test_planner_regenerates_once(self, mock_classify, mock_llm):
        """Verify that the planner retries once if validation fails."""
        # Setup intent
        intent = MagicMock()
        intent.requires_clarification = False
        intent.ambiguity_score = 0.1
        intent.intent_confidence = 0.95
        intent.intent_types = ["EXECUTE"]
        mock_classify.return_value = intent
        
        # 1st response: Missing 'application_name' for 'open_application'
        invalid_plan = {
            "summary": "Opening Notepad",
            "reasoning": "User asked to open notepad",
            "actions": [{"type": "open_application", "params": {}}] 
        }
        # 2nd response: Correct plan
        valid_plan = {
            "summary": "Opening Notepad",
            "reasoning": "User asked to open notepad",
            "actions": [{"type": "open_application", "params": {"application_name": "notepad"}}]
        }
        
        mock_llm.side_effect = [invalid_plan, valid_plan]
        
        planner = ContextualPlanner()
        plan = planner.generate_plan("open notepad")
        
        # Verify LLM was called twice
        assert mock_llm.call_count == 2
        assert plan.summary == "Opening Notepad"
        assert plan.actions[0].params["application_name"] == "notepad"

    @patch("brain.llm.llm_client.LLMClient.generate_plan")
    @patch("brain.intent_engine.IntentClassifier.classify")
    def test_planner_never_regenerates_twice(self, mock_classify, mock_llm):
        """Verify that the planner gives up and returns fallback after 1 retry."""
        intent = MagicMock()
        intent.requires_clarification = False
        intent.ambiguity_score = 0.1
        intent.intent_confidence = 0.95
        intent.intent_types = ["EXECUTE"]
        mock_classify.return_value = intent
        
        # Both responses are invalid
        invalid_plan = {
            "summary": "Opening Notepad",
            "reasoning": "User asked to open notepad",
            "actions": [{"type": "open_application", "params": {}}] 
        }
        
        mock_llm.side_effect = [invalid_plan, invalid_plan]
        
        planner = ContextualPlanner()
        plan = planner.generate_plan("open notepad")
        
        # Verify LLM was called exactly twice (initial + 1 retry)
        assert mock_llm.call_count == 2
        assert plan.summary == "Execution Strategy Error"
        assert "structural error" in plan.actions[0].description

    @patch("brain.llm.llm_client.LLMClient.generate_plan")
    @patch("brain.intent_engine.IntentClassifier.classify")
    def test_planner_accepts_valid_immediately(self, mock_classify, mock_llm):
        """Verify no regeneration if first attempt is valid."""
        intent = MagicMock()
        intent.requires_clarification = False
        intent.ambiguity_score = 0.1
        intent.intent_confidence = 0.95
        intent.intent_types = ["EXECUTE"]
        mock_classify.return_value = intent
        
        valid_plan = {
            "summary": "Opening Notepad",
            "reasoning": "User asked to open notepad",
            "actions": [{"type": "open_application", "params": {"application_name": "notepad"}}]
        }
        
        mock_llm.return_value = valid_plan
        
        planner = ContextualPlanner()
        planner.generate_plan("open notepad")
        
        assert mock_llm.call_count == 1
