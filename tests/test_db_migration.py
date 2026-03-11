"""
Aegis v3.6.1 — DB Migration Tests
====================================
Tests that MemoryManager migration logic correctly upgrades schema.
"""

import os
import unittest
import sqlite3
import tempfile
import pathlib
from memory.memory_manager import MemoryManager


class TestDBMigration(unittest.TestCase):
    def setUp(self):
        self.temp_db = tempfile.NamedTemporaryFile(delete=False)
        self.temp_path = pathlib.Path(self.temp_db.name)
        # Create a v1 schema
        with sqlite3.connect(self.temp_path) as conn:
            conn.execute("CREATE TABLE schema_version (version INTEGER PRIMARY KEY)")
            conn.execute("INSERT INTO schema_version (version) VALUES (1)")
            conn.execute("CREATE TABLE daily_history (id INTEGER PRIMARY KEY, date TEXT)")

    def tearDown(self):
        self.temp_db.close()
        try:
            os.remove(self.temp_path)
        except Exception:
            pass

    def test_migration_run(self):
        mm = MemoryManager(db_path=self.temp_path)
        with sqlite3.connect(self.temp_path) as conn:
            # Context column should be added (v2 migration)
            cursor = conn.execute("PRAGMA table_info(daily_history)")
            cols = [row[1] for row in cursor.fetchall()]
            self.assertIn("context", cols)

            # Version should be at latest (currently v3)
            version = conn.execute("SELECT version FROM schema_version").fetchone()[0]
            self.assertEqual(version, 3)

    def test_migration_creates_preferences_table(self):
        mm = MemoryManager(db_path=self.temp_path)
        with sqlite3.connect(self.temp_path) as conn:
            cursor = conn.execute("SELECT name FROM sqlite_master WHERE type='table'")
            tables = [row[0] for row in cursor.fetchall()]
            self.assertIn("preferences", tables)

    def test_migration_creates_user_profile_table(self):
        mm = MemoryManager(db_path=self.temp_path)
        with sqlite3.connect(self.temp_path) as conn:
            cursor = conn.execute("SELECT name FROM sqlite_master WHERE type='table'")
            tables = [row[0] for row in cursor.fetchall()]
            self.assertIn("user_profile", tables)


if __name__ == "__main__":
    unittest.main()
