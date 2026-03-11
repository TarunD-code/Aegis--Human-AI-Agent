import pytest
import json
import os
from unittest.mock import MagicMock, patch
from execution.engine import ExecutionEngine
from brain.planner import Action

class TestV7Comprehensive:
    @pytest.fixture(autouse=True)
    def setup(self):
        self.engine = ExecutionEngine()
        # Mocking heavy deps
        self.mock_pyautogui = patch('pyautogui.moveTo').start()
        self.mock_pygetwindow = patch('pygetwindow.getAllTitles').start()
        self.mock_cv2 = patch('cv2.imwrite').start()
        
        yield
        patch.stopall()

    def load_matrix(self):
        matrix_path = os.path.join(os.path.dirname(__file__), "v7_test_matrix.json")
        if not os.path.exists(matrix_path):
            from tests.generate_test_matrix import generate_matrix
            generate_matrix()
        with open(matrix_path, "r") as f:
            return json.load(f)

    def test_run_matrix(self):
        matrix = self.load_matrix()
        for scenario in matrix:
            action_data = scenario.get("action")
            if not action_data: continue
            
            action = Action(
                type=action_data["type"],
                value=action_data.get("value", ""),
                params=action_data.get("params", {}),
                risk_level=action_data.get("risk_level", "LOW")
            )
            
            # Setup mocks based on scenario
            if "app_resolve" in scenario["name"]:
                with patch('core.app_registry.registry.search') as mock_search:
                    mock_search.return_value = [{"name": scenario["expected_best_match"], "path": "test.exe", "score": 99}]
                    result = self.engine.execute(action)
                    assert result.success is True
            
            elif "security_block" in scenario["name"]:
                result = self.engine.execute(action)
                assert result.success is False
                assert "not whitelisted" in result.message.lower() or "security" in result.message.lower()

            elif "wait" in action.type:
                result = self.engine.execute(action)
                assert result.success is True
                
            # Log progress for large matrix
            # print(f"Passed: {scenario['name']}")

    def generate_final_report(self):
        """v7.0: Archive diagnostics and package report."""
        import shutil
        from datetime import datetime
        ts = datetime.now().strftime("%Y%m%d_%H%M%S")
        logs_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), "logs")
        archive_path = os.path.join(logs_dir, f"diagnostics_{ts}")
        
        if os.path.exists(logs_dir):
            shutil.make_archive(archive_path, 'zip', logs_dir)
            print(f"Diagnostics archived to: {archive_path}.zip")
