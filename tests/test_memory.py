"""
Aegis v3.6 — Memory Tests
===========================
Tests for persistent memory and session memory.
Updated to match v3.6 table schema and API.
"""

import sys
import os
from pathlib import Path
import sqlite3

import pytest

# Ensure project root is importable
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from memory.memory_manager import MemoryManager
from memory.session_memory import SessionMemory


@pytest.fixture
def temp_db(tmp_path):
    """Fixture to provide a clean temporary database path."""
    db_file = tmp_path / "test_memory.db"
    return str(db_file)


class TestMemoryManager:
    """Tests for SQLite persistence."""

    def test_db_initialization(self, temp_db):
        mm = MemoryManager(db_path=temp_db)
        # Check if file exists
        assert os.path.exists(temp_db)

        # Verify tables match the v3.6 schema
        conn = sqlite3.connect(temp_db)
        cursor = conn.cursor()
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
        tables = [row[0] for row in cursor.fetchall()]
        assert "approved_plans" in tables
        assert "rejected_plans" in tables
        assert "daily_history" in tables
        assert "app_usage" in tables
        assert "schema_version" in tables
        conn.close()

    def test_store_and_get_approved(self, temp_db):
        mm = MemoryManager(db_path=temp_db)
        plan = {"summary": "Test plan", "actions": []}
        mm.store_approved(plan)

        recent = mm.get_recent_approved(1)
        assert len(recent) == 1
        # v3.6: get_recent_approved returns deserialized plan dicts directly
        assert recent[0]["summary"] == "Test plan"

    def test_store_and_get_rejected(self, temp_db):
        mm = MemoryManager(db_path=temp_db)
        plan = {"summary": "Bad plan", "actions": []}
        mm.store_rejected(plan, reason="Safety violation")

        recent = mm.get_recent_rejected(1)
        assert len(recent) == 1
        assert recent[0]["plan"]["summary"] == "Bad plan"
        assert recent[0]["reason"] == "Safety violation"

    def test_app_usage_stats(self, temp_db):
        mm = MemoryManager(db_path=temp_db)
        mm.increment_app_usage("notepad")
        mm.increment_app_usage("notepad")
        mm.increment_app_usage("calc")

        freq = mm.get_app_frequency(5)
        # v3.6: get_app_frequency returns a dict {app_name: count}
        assert isinstance(freq, dict)
        assert freq["notepad"] == 2
        assert freq["calc"] == 1

    def test_store_action_event(self, temp_db):
        mm = MemoryManager(db_path=temp_db)
        mm.store_action_event("notepad", "open_application", "open notepad", "success")
        from datetime import datetime
        today = datetime.now().strftime("%Y-%m-%d")
        history = mm.get_daily_history(today)
        assert len(history) == 1
        assert history[0]["app"] == "notepad"


class TestSessionMemory:
    """Tests for in-memory session context."""

    def test_session_lifecycle(self):
        sm = SessionMemory()
        assert sm.command_count == 0

        sm.add_entry("hello", "Hi there")
        assert sm.command_count == 1
        assert sm.get_last_input() == "hello"

        sm.reset()
        assert sm.command_count == 0
