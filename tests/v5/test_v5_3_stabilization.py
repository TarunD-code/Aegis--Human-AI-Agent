import pytest
import os
import json
from unittest.mock import MagicMock, patch
from memory.memory_manager import MemoryManager
from brain.execution_router import ExecutionRouter
from brain.intent_engine import IntentMetadata
from brain.planner import ActionPlan
from interfaces.cli import AegisCLI

class TestStabilizationV5_3:
    
    def test_memory_manager_singleton(self):
        """Verify MemoryManager follows the Singleton pattern."""
        m1 = MemoryManager()
        m2 = MemoryManager()
        assert m1 is m2
        assert m1._initialized is True

    def test_execution_router_math(self):
        """Verify math queries bypass the planner."""
        planner = MagicMock()
        router = ExecutionRouter(planner=planner)
        intent = IntentMetadata(intent_types=["MATH"])
        
        plan = router.route("2 + 2", intent, {})
        
        assert plan.summary.startswith("Calculated")
        assert plan.actions[0].type == "compute_result"
        planner.generate_plan.assert_not_called()

    def test_execution_router_fallback(self):
        """Verify unknown intents fall back to the planner."""
        planner = MagicMock()
        router = ExecutionRouter(planner=planner)
        intent = IntentMetadata(intent_types=["EXECUTE"])
        
        router.route("do something complicated", intent, {})
        
        planner.generate_plan.assert_called_once()

    def test_app_registry_static_lookup(self):
        """Verify that open_application uses the static registry."""
        from execution.actions.app_actions import open_application
        action = MagicMock()
        action.params = {"application_name": "notepad"}
        action.value = "notepad"
        
        from unittest.mock import mock_open
        with patch("os.path.exists", return_value=True), \
             patch("builtins.open", mock_open(read_data=json.dumps({"notepad": "C:\\fake\\notepad.exe"}))), \
             patch("subprocess.Popen") as mock_popen:
            
            res = open_application(action)
            assert res.success is True
            # Verify it used the path from registry
            assert "C:\\fake\\notepad.exe" in mock_popen.call_args[0][0][0]

    def test_cli_resilience(self):
        """Verify the REPL loop survives exceptions in _process_command."""
        cli = AegisCLI()
        with patch.object(cli, "_process_command", side_effect=Exception("Simulated Failure")), \
             patch("builtins.input", side_effect=["test command", "exit"]), \
             patch("builtins.print") as mock_print:
            
            cli.run()
            # Verify the error message was printed but the loop continued to 'exit'
            failed_call = any("encountered an issue" in str(call) for call in mock_print.call_args_list)
            assert failed_call is True

    def test_window_tracker_integration(self):
        """Verify CLI gathers window context."""
        cli = AegisCLI()
        with patch("core.window_tracker.tracker.get_context", return_value={"active_window_title": "Test Title", "active_window_process": "test.exe"}):
            context = cli._gather_context()
            assert context["foreground_app"] == "Test Title"
            assert context["foreground_process"] == "test.exe"
