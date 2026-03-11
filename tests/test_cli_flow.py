import unittest
from unittest.mock import MagicMock, patch
from interfaces.cli import AegisCLI
from brain.planner import ActionPlan, Action
from execution.engine import ExecutionEngine

class TestCLIFlow(unittest.TestCase):
    @patch('interfaces.cli.request_approval')
    @patch('interfaces.cli.display_plan')
    def test_display_approval_execute_flow(self, mock_display, mock_approval):
        mock_approval.return_value = (True, "")
        mock_engine = MagicMock(spec=ExecutionEngine)
        
        mock_action = Action(type="wait", params={"time": 1})
        mock_plan = ActionPlan(
            summary="Test summary",
            reasoning="Test reasoning",
            actions=[mock_action],
            requires_approval=True
        )
        
        mock_planner = MagicMock()
        mock_planner._intent_engine.classify.return_value = MagicMock(intent_types=["GENERAL"])
        mock_planner.generate_plan.return_value = mock_plan
        
        mock_memory = MagicMock()
        mock_session = MagicMock()
        mock_session.conversation_context_id = "test_id"
        
        cli = AegisCLI(engine=mock_engine, memory=mock_memory, session=mock_session, planner=mock_planner)
        
        cli._process_command("Wait for 1 second")
        
        # Verify flow
        mock_checker = cli._planner.generate_plan
        mock_checker.assert_called_once()
        mock_display.assert_called_once_with(mock_plan)
        mock_approval.assert_called_once()
        mock_engine.execute_action.assert_called_once_with(mock_action)

if __name__ == "__main__":
    unittest.main()
