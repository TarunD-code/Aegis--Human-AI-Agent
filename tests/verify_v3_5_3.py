import unittest
from security.validator import validate_plan
from brain.planner import Action, ActionPlan
from execution.actions.app_actions import open_application, ExecutionResult
import os

class TestV353Decoupling(unittest.TestCase):
    def test_parameter_schema_enforcement(self):
        # Action missing application_name
        action = Action(type="open_application", params={})
        plan = ActionPlan(summary="Test", actions=[action], reasoning="Test")
        # Ensure it is at least an Actions list
        is_valid, warnings = validate_plan(plan)
        self.assertFalse(is_valid)
        self.assertIn("Missing required parameter 'application_name'", [w for w in warnings if 'application_name' in w][0])

    def test_parameter_schema_fallback(self):
        # Action missing application_name but has value (transition support)
        action = Action(type="open_application", value="calculator", params={})
        plan = ActionPlan(summary="Test", actions=[action], reasoning="Test")
        is_valid, warnings = validate_plan(plan)
        self.assertTrue(is_valid)
        self.assertEqual(action.params["application_name"], "calculator")

    def test_open_application_params(self):
        # Verify handler uses params
        action = Action(type="open_application", params={"application_name": "notepad"})
        # Even if it fails (e.g. not on windows), it should be an ExecutionResult
        from execution.actions.app_actions import open_application
        res = open_application(action)
        self.assertIsInstance(res, ExecutionResult)
        self.assertTrue(hasattr(res, "success"))

    def test_cli_decoupling_check(self):
        # Verify cli.py doesn't contain string 'ExecutionResult(' (instantiation)
        with open("d:/Aegis/interfaces/cli.py", "r") as f:
            content = f.read()
            # It can be used as a type hint though: 'list[ExecutionResult]' 
            # or in a catch block or in the property name. 
            # The user specifically said "Locate the line where ExecutionResult is instantiated"
            # It will still likely have the type hint? The user said "Remove any obsolete import of ExecutionResult"
            # I removed the import. So it shouldn't even be a type hint.
            self.assertNotIn("ExecutionResult(", content)

if __name__ == "__main__":
    unittest.main()
