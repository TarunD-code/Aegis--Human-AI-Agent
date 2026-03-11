"""
Aegis v3.6.1 — User Profile Tests
====================================
Tests for the user_profile and preferences API in MemoryManager.
"""

import sys
import json
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from memory.memory_manager import MemoryManager


@pytest.fixture
def temp_db(tmp_path):
    return str(tmp_path / "test_profile.db")


class TestUserProfile:
    """Tests for get_user_profile / set_user_profile / update_user_profile."""

    def test_get_user_profile_returns_dict_when_empty(self, temp_db):
        mm = MemoryManager(db_path=temp_db)
        profile = mm.get_user_profile()
        assert isinstance(profile, dict)
        assert profile == {}

    def test_set_and_get_profile(self, temp_db):
        mm = MemoryManager(db_path=temp_db)
        profile = {
            "organization_preference": "alphabetical",
            "email_tone_preference": "formal",
            "risk_tolerance": "low",
        }
        mm.set_user_profile(profile)
        loaded = mm.get_user_profile()
        assert loaded["organization_preference"] == "alphabetical"
        assert loaded["email_tone_preference"] == "formal"
        assert loaded["risk_tolerance"] == "low"

    def test_update_profile_merges(self, temp_db):
        mm = MemoryManager(db_path=temp_db)
        mm.set_user_profile({"name": "Alice", "risk_tolerance": "low"})
        mm.update_user_profile({"risk_tolerance": "high", "theme": "dark"})
        loaded = mm.get_user_profile()
        assert loaded["name"] == "Alice"
        assert loaded["risk_tolerance"] == "high"
        assert loaded["theme"] == "dark"

    def test_migration_from_json(self, tmp_path):
        """Verify legacy user_profile.json is imported during migration."""
        db_file = tmp_path / "test_legacy.db"
        legacy_json = tmp_path / "user_profile.json"
        legacy_data = {"organization_preference": "by_date", "risk_tolerance": "medium"}
        legacy_json.write_text(json.dumps(legacy_data), encoding="utf-8")

        mm = MemoryManager(db_path=str(db_file))
        profile = mm.get_user_profile()
        assert profile.get("organization_preference") == "by_date"
        assert profile.get("risk_tolerance") == "medium"
        # Legacy file should be deleted after import
        assert not legacy_json.exists()

    def test_profile_persists_across_instances(self, temp_db):
        mm1 = MemoryManager(db_path=temp_db)
        mm1.set_user_profile({"name": "TestUser"})
        del mm1

        mm2 = MemoryManager(db_path=temp_db)
        assert mm2.get_user_profile()["name"] == "TestUser"


class TestPreferences:
    """Tests for get_preference / set_preference."""

    def test_get_missing_returns_default(self, temp_db):
        mm = MemoryManager(db_path=temp_db)
        assert mm.get_preference("missing_key", "fallback") == "fallback"

    def test_set_and_get(self, temp_db):
        mm = MemoryManager(db_path=temp_db)
        mm.set_preference("theme", "dark")
        assert mm.get_preference("theme") == "dark"

    def test_upsert_overwrites(self, temp_db):
        mm = MemoryManager(db_path=temp_db)
        mm.set_preference("lang", "en")
        mm.set_preference("lang", "fr")
        assert mm.get_preference("lang") == "fr"

    def test_preference_store_integration(self, temp_db):
        """Verify PreferenceStore works with MemoryManager."""
        from memory.preference_store import PreferenceStore
        mm = MemoryManager(db_path=temp_db)
        store = PreferenceStore(mm)
        store.set_bool("auto_approve", True)
        assert store.get_bool("auto_approve") is True
        store.set_int("retries", 5)
        assert store.get_int("retries") == 5
