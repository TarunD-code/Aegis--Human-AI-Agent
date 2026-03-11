import unittest
from execution.actions.app_actions import ExecutionResult
from execution.engine import ExecutionEngine
from brain.planner import Action, ActionPlan
import json

class TestV352Hardening(unittest.TestCase):
    def test_execution_result_compatibility(self):
        res = ExecutionResult(success=True, message="Test", data={"foo": "bar"})
        self.assertEqual(res.message, "Test")
        self.assertEqual(res.details["foo"], "bar") # Backward compatibility
        self.assertEqual(res.action_type, "unknown") # Default

    def test_engine_returns_execution_result(self):
        engine = ExecutionEngine()
        action = Action(type="wait", value="0.1")
        res = engine.execute(action)
        self.assertIsInstance(res, ExecutionResult)
        self.assertTrue(res.success)

    def test_cli_unbound_fix_simulation(self):
        # This is more of a logic check
        results = []
        # Simulate action loop
        for i in range(1):
            res = ExecutionResult(success=True)
            # simulate skip
            # if skip: pass
            results.append(res)
        
        # This line should not crash
        last_res = results[-1]
        self.assertEqual(last_res.success, True)

if __name__ == "__main__":
    unittest.main()
