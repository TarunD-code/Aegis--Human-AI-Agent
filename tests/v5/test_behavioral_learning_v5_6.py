import pytest
import sqlite3
from unittest.mock import MagicMock, patch
from memory.memory_manager import MemoryManager
from brain.proactive_engine import ProactiveEngine

class TestBehavioralLearningV5_6:
    @pytest.fixture
    def memory(self, tmp_path):
        db = tmp_path / "test_aegis.db"
        return MemoryManager(db_path=db)

    def test_record_transition_increments_count(self, memory):
        """Verify that multiple transitions between same actions increment the count."""
        memory.record_transition("chrome:open", "youtube:search")
        memory.record_transition("chrome:open", "youtube:search")
        
        patterns = memory.get_top_patterns("chrome:open")
        assert len(patterns) == 1
        assert patterns[0]["suggested_action"] == "youtube:search"
        assert patterns[0]["count"] == 2

    def test_get_top_patterns_ordering(self, memory):
        """Verify that patterns are returned in descending order of frequency."""
        memory.record_transition("chrome:open", "youtube:search")
        memory.record_transition("chrome:open", "youtube:search")
        memory.record_transition("chrome:open", "google:search")
        
        patterns = memory.get_top_patterns("chrome:open")
        assert patterns[0]["suggested_action"] == "youtube:search"
        assert patterns[1]["suggested_action"] == "google:search"

    @patch("core.state.working_memory")
    @patch("core.state.memory_manager")
    def test_proactive_suggestion_confidence_threshold(self, mock_memory, mock_working):
        """Verify that suggestions are only generated after the confidence threshold (3) is met."""
        engine = ProactiveEngine()
        mock_working.get.return_value = "chrome:open"
        
        # Scenario 1: Count is 2 (below threshold)
        mock_memory.get_top_patterns.return_value = [{"suggested_action": "youtube:search_web", "count": 2}]
        suggestions = engine.generate_suggestions({})
        assert not any(s.type == "PROACTIVE" for s in suggestions)
        
        # Scenario 2: Count is 3 (at threshold)
        mock_memory.get_top_patterns.return_value = [{"suggested_action": "youtube:search_web", "count": 3}]
        suggestions = engine.generate_suggestions({})
        proactive = [s for s in suggestions if s.type == "PROACTIVE"]
        assert len(proactive) == 1
        assert "Search Web In Youtube" in proactive[0].content
