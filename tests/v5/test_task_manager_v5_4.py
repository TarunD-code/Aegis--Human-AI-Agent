import pytest
from core.task_manager import TaskManager

class TestTaskManagerV5_4:
    def test_update_task_mechanics(self):
        tm = TaskManager()
        tm.update_task("Writing", state="typing", app="Notepad")
        assert tm.active_task == "Writing"
        assert tm.task_state == "typing"
        assert tm.associated_app == "Notepad"
        assert tm.last_update is not None

    def test_get_context(self):
        tm = TaskManager()
        tm.update_task("Calculation", state="result=15")
        context = tm.get_context()
        assert context["active_task"] == "Calculation"
        assert context["task_state"] == "result=15"

    def test_reset_task(self):
        tm = TaskManager()
        tm.update_task("Research", state="searching")
        tm.reset_task()
        assert tm.active_task is None
        assert tm.task_state is None
