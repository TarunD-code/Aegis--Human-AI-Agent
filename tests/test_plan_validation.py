import unittest
from brain.plan_validator import normalize_and_validate

class TestPlanValidation(unittest.TestCase):
    def test_missing_summary(self):
        plan = {"actions": [{"type": "wait"}]}
        is_valid, errors = normalize_and_validate(plan)
        self.assertFalse(is_valid)
        self.assertIn("missing_summary", errors)

    def test_missing_action_params(self):
        plan = {
            "summary": "wait",
            "reasoning": "testing",
            "actions": [{"type": "open_application"}] # Missing application_name
        }
        is_valid, errors = normalize_and_validate(plan)
        self.assertFalse(is_valid)
        self.assertTrue(any("missing_parameter:open_application:application_name" in e for e in errors))

    def test_fallback_mapping(self):
        plan = {
            "summary": "open calc",
            "reasoning": "testing fallback",
            "actions": [{"type": "open_application", "value": "calc.exe"}]
        }
        is_valid, errors = normalize_and_validate(plan)
        self.assertTrue(is_valid)
        self.assertEqual(plan["actions"][0]["parameters"]["application_name"], "calc.exe")

if __name__ == "__main__":
    unittest.main()
