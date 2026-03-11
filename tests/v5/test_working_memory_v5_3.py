import pytest
from memory.working_memory import WorkingMemory

class TestWorkingMemoryV5_3:
    def test_set_get_mechanics(self):
        wm = WorkingMemory()
        wm.set("last_result", 42)
        assert wm.get("last_result") == 42
        assert wm.get("unknown_key") is None

    def test_reset_mechanics(self):
        wm = WorkingMemory()
        wm.set("active_application", "Chrome")
        wm.reset()
        assert wm.get("active_application") is None

    def test_get_all(self):
        wm = WorkingMemory()
        wm.set("last_result", 100)
        data = wm.get_all()
        assert data["last_result"] == 100
        assert "active_application" in data
