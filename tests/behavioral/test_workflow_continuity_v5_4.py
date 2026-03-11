import pytest
from unittest.mock import MagicMock, patch
from execution.engine import ExecutionEngine
from brain.planner import Action
from execution.actions.app_actions import ExecutionResult
from brain.contextual_planner import ContextualPlanner

class TestWorkflowContinuityV5_4:
    @patch("execution.engine.ACTION_REGISTRY")
    def test_writing_workflow_updates_task_manager(self, mock_registry):
        """Verify that type_text updates TaskManager to 'Writing'."""
        from core.state import task_manager
        task_manager.reset_task()
        
        mock_handler = MagicMock(return_value=ExecutionResult(success=True, message="Typed"))
        mock_registry.get.return_value = mock_handler
        
        engine = ExecutionEngine()
        action = Action(type="type_text", params={"text": "hello", "application_name": "Notepad"})
        engine.execute(action)
        
        assert task_manager.active_task == "Writing"
        assert task_manager.associated_app == "Notepad"

    @patch("brain.llm.llm_client.LLMClient.generate_plan")
    def test_planner_anchors_to_active_task(self, mock_llm):
        """Verify that planner prompt contains the active task context."""
        from core.state import task_manager
        task_manager.reset_task()
        task_manager.update_task("Writing", state="typing", app="Notepad")
        
        planner = ContextualPlanner()
        mock_llm.return_value = {"summary": "test", "actions": [], "reasoning": "test", "requires_approval": False}
        
        planner.generate_plan("write again", context={"session_state": {}})
        
        prompt = str(mock_llm.call_args)
        assert "ACTIVE WORKFLOW: Writing" in prompt
        assert "Primary App: Notepad" in prompt

    def test_conversation_engine_task_aware_expansion(self):
        """Verify that ConversationEngine uses active task for expansion."""
        from brain.conversation_engine import ConversationEngine
        from core.state import task_manager, working_memory
        
        task_manager.reset_task()
        working_memory.reset()
        
        task_manager.update_task("Writing", app="Notepad")
        working_memory.set("last_text_written", "hello world")
        
        engine = ConversationEngine()
        # "again" should resolve to typing the last written text because task is "Writing"
        expanded = engine.expand_query("again", {"last_input": "write hello world"})
        assert "type text 'hello world'" in expanded.lower()
