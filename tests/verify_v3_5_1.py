import unittest
from unittest.mock import MagicMock, patch
from brain.intent_engine import IntentClassifier
from brain.planner import ActionPlan, Action, parse_plan
from brain.plan_validator import validate_plan_structure
from logs.logger import AegisLogger
from config import ACTION_WHITELIST
import json

class TestV351Stability(unittest.TestCase):
    def test_intent_greeting(self):
        ic = IntentClassifier()
        intent = ic.classify("hello")
        self.assertIn("SOCIAL", intent.intent_types)
        
        intent = ic.classify("hey aegis")
        self.assertIn("SOCIAL", intent.intent_types)

    def test_serialization(self):
        action = Action(type="click", value="button", description="click it")
        plan = ActionPlan(summary="Test", reasoning="Reasoning", actions=[action])
        
        # Test to_dict
        d = plan.to_dict()
        self.assertEqual(d["summary"], "Test")
        self.assertEqual(d["reasoning"], "Reasoning")
        self.assertEqual(len(d["actions"]), 1)
        self.assertEqual(d["actions"][0]["action_type"], "click")
        
        # Test logger normalization
        logger = AegisLogger()
        norm = logger._normalize_plan(plan)
        self.assertEqual(norm["summary"], "Test")
        
    def test_validator(self):
        valid_plan = {
            "summary": "Everything is fine",
            "reasoning": "Because I said so",
            "actions": [{"type": "click", "description": "click"}]
        }
        is_valid, err = validate_plan_structure(valid_plan, ACTION_WHITELIST)
        self.assertTrue(is_valid, f"Should be valid: {err}")
        
        invalid_plan = {
            "reasoning": "Missing summary",
            "actions": [{"type": "click"}]
        }
        is_valid, err = validate_plan_structure(invalid_plan, ACTION_WHITELIST)
        self.assertFalse(is_valid)
        self.assertIn("summary", err)

    def test_parse_plan_robustness(self):
        # Test new format with action_type and parameters
        raw = {
            "summary": "Complex plan",
            "reasoning": "Logic",
            "actions": [
                {
                    "action_type": "open_application",
                    "parameters": {"value": "notepad"},
                    "description": "open it"
                }
            ]
        }
        plan = parse_plan(raw)
        self.assertEqual(plan.summary, "Complex plan")
        self.assertEqual(plan.reasoning, "Logic")
        self.assertEqual(plan.actions[0].type, "open_application")
        self.assertEqual(plan.actions[0].value, "notepad")

if __name__ == "__main__":
    unittest.main()
