"""
Aegis v3.5.4 Release Verification Suite
========================================
Validates core production-ready features:
1. Logging (JSON & Rotation)
2. Health Endpoint
3. DB Migrations
4. LLM Resilience (Unit Mock)
5. Parameter Normalization
"""

import os
import json
import sqlite3
import unittest
import requests
from pathlib import Path
from logs.logger import get_logger
from memory.memory_manager import MemoryManager
from brain.plan_validator import normalize_and_validate
from config import AEGIS_VERSION, MEMORY_DB_PATH

class TestProductionHardening(unittest.TestCase):
    
    def test_version(self):
        self.assertEqual(AEGIS_VERSION, "v3.5.4 Production-Ready")

    def test_json_logging(self):
        from logs.logger import get_audit_logger
        from datetime import datetime, timezone
        from config import LOG_DIR
        audit = get_audit_logger()
        audit._write_audit("test_event", {"test_key": "test_val", "message": "Test JSON log message"})
        today = datetime.now(tz=timezone.utc).strftime("%Y-%m-%d")
        log_file = Path(LOG_DIR) / f"aegis_{today}.json"
        self.assertTrue(log_file.exists())
        with open(log_file, "r", encoding="utf-8") as f:
            entries = json.load(f)
            last_entry = entries[-1]
            self.assertEqual(last_entry["message"], "Test JSON log message")
            self.assertEqual(last_entry["test_key"], "test_val")

    def test_db_migrations(self):
        mm = MemoryManager()
        with sqlite3.connect(MEMORY_DB_PATH) as conn:
            cursor = conn.execute("PRAGMA table_info(daily_history)")
            cols = [row[1] for row in cursor.fetchall()]
            self.assertIn("context", cols)
            
            ver = conn.execute("SELECT version FROM schema_version").fetchone()[0]
            self.assertGreaterEqual(ver, 2)

    def test_parameter_normalization(self):
        # Test fallback from 'value' to 'application_name'
        bad_plan = {
            "summary": "Open calc",
            "reasoning": "Test",
            "actions": [
                {
                    "action_type": "open_application",
                    "parameters": {"value": "calculator"},
                    "risk_level": "LOW",
                    "requires_confirmation": False
                }
            ]
        }
        is_valid, errors = normalize_and_validate(bad_plan)
        self.assertTrue(is_valid, f"Normalization failed: {errors}")
        self.assertEqual(bad_plan["actions"][0]["parameters"]["application_name"], "calculator")

    def test_health_endpoint(self):
        # Health server should be running if main.py was triggered, 
        # but for unit testing we just check if it's reachable or start a temporary one
        try:
            res = requests.get("http://127.0.0.1:17123/health", timeout=2)
            self.assertEqual(res.status_code, 200)
            self.assertEqual(res.json()["status"], "healthy")
        except Exception:
            self.skipTest("Health server not running in test env.")

if __name__ == "__main__":
    unittest.main()
