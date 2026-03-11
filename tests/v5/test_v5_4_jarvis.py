import pytest
import os
import json
from unittest.mock import MagicMock, patch
from brain.command_normalizer import normalizer
from memory.user_memory import user_memory
from brain.execution_router import ExecutionRouter
from brain.intent_engine import IntentClassifier, IntentMetadata
from brain.planner import ActionPlan
from core.window_tracker import tracker
from config import ACTION_WHITELIST

class TestJarvisV5_4:
    
    def test_fuzzy_normalization(self):
        """Verify fuzzy typo correction works."""
        assert normalizer.normalize("opne notepd") == "open notepad"
        assert normalizer.normalize("claculate 10+5") == "calculate" # Router handles the rest

    def test_user_memory_persistence(self):
        """Verify facts can be remembered and recalled."""
        user_memory.remember("favorite color", "blue")
        assert user_memory.recall("favorite color") == "blue"
        user_memory.forget("favorite color")
        assert user_memory.recall("favorite color") is None

    def test_intent_priority_open(self):
        """Verify 'open calculator' is EXECUTE, not MATH."""
        classifier = IntentClassifier()
        metadata = classifier.classify("open calculator")
        assert "EXECUTE" in metadata.intent_types
        assert "MATH" not in metadata.intent_types

    def test_security_whitelist(self):
        """Verify new actions are whitelisted."""
        assert "browse_to" in ACTION_WHITELIST
        assert "list_running_apps" in ACTION_WHITELIST
        assert "close_application" in ACTION_WHITELIST

    def test_router_app_registry_bypass(self):
        """Verify app registry bypass in router."""
        router = ExecutionRouter(planner=MagicMock())
        with patch("core.app_registry.registry.resolve", return_value="C:\\Windows\\notepad.exe"):
            intent = IntentMetadata(intent_types=["EXECUTE"])
            plan = router.route("open notepad", intent, {})
            assert plan.summary == "Launching notepad"
            assert plan.actions[0].type == "open_application"
            assert plan.actions[0].value == "C:\\Windows\\notepad.exe"

    def test_router_browser_routing(self):
        """Verify browser routing returns valid plan."""
        router = ExecutionRouter(planner=MagicMock())
        intent = IntentMetadata(intent_types=["BROWSER"])
        plan = router.route("open youtube", intent, {})
        assert plan.actions[0].type == "browse_to"
        assert plan.actions[0].params["query"] == "youtube"

    def test_window_tracker_visible_windows(self):
        """Verify window tracker lists visible windows."""
        context = tracker.get_context()
        assert "visible_windows" in context
        assert isinstance(context["visible_windows"], list)

    def test_system_config_retries(self):
        """Verify SystemConfig is accessible."""
        from config import SystemConfig
        assert SystemConfig.MAX_RETRIES == 3
        assert SystemConfig.RETRY_DELAY == 1.0
