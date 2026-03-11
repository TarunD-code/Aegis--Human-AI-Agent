"""
Aegis v3.6.1 — Memory Manager
=============================
Persistent memory management with SQLite, migrations, and durable writes.
"""

import sqlite3
import json
import uuid
from pathlib import Path
from typing import Any, List, Dict
from datetime import datetime, timezone
from config import MEMORY_DB_PATH
from logs.logger import get_logger

logger = get_logger(__name__)

class MemoryManager:
    """
    Manages Aegis v3.6.1 persistent memory.
    Ensures a single instance exists (Singleton).
    """
    _instance = None
    _initialized = False

    def __new__(cls, *args, **kwargs):
        if cls._instance is None:
            cls._instance = super(MemoryManager, cls).__new__(cls)
        return cls._instance

    def __init__(self, db_path: Path | str = None) -> None:
        if self._initialized:
            return
        self._initialized = True
        self.db_path = Path(db_path) if db_path else Path(MEMORY_DB_PATH)
        self.db_path.parent.mkdir(parents=True, exist_ok=True)
        self._init_db()
        self.run_migrations()
        logger.info("MemoryManager v3.6.1 ready.")

    def _get_connection(self) -> sqlite3.Connection:
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        conn.execute("PRAGMA synchronous = FULL")
        conn.execute("PRAGMA journal_mode = WAL")
        return conn

    def _init_db(self) -> None:
        """Initialize core tables."""
        with self._get_connection() as conn:
            conn.execute("""
                CREATE TABLE IF NOT EXISTS approved_plans (
                    id TEXT PRIMARY KEY,
                    plan_json TEXT,
                    timestamp TEXT
                )
            """)
            conn.execute("""
                CREATE TABLE IF NOT EXISTS rejected_plans (
                    id TEXT PRIMARY KEY,
                    plan_json TEXT,
                    reason TEXT,
                    timestamp TEXT
                )
            """)
            conn.execute("""
                CREATE TABLE IF NOT EXISTS daily_history (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    date TEXT,
                    app TEXT,
                    action_type TEXT,
                    command TEXT,
                    result TEXT,
                    app_category TEXT
                )
            """)
            conn.execute("""
                CREATE TABLE IF NOT EXISTS app_usage (
                    app_name TEXT PRIMARY KEY,
                    usage_count INTEGER DEFAULT 0
                )
            """)
            conn.execute("""
                CREATE TABLE IF NOT EXISTS schema_version (
                    version INTEGER PRIMARY KEY
                )
            """)
            conn.execute("""
                CREATE TABLE IF NOT EXISTS preferences (
                    key TEXT PRIMARY KEY,
                    value TEXT NOT NULL
                )
            """)
            conn.execute("""
                CREATE TABLE IF NOT EXISTS user_profile (
                    id INTEGER PRIMARY KEY CHECK (id = 1),
                    profile TEXT NOT NULL,
                    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """)
            
            # Seed version 1
            if not conn.execute("SELECT version FROM schema_version").fetchone():
                conn.execute("INSERT INTO schema_version (version) VALUES (1)")
            conn.commit()

    def run_migrations(self) -> None:
        """Automated schema migration logic."""
        log_file = Path("logs/migration.log")
        log_file.parent.mkdir(parents=True, exist_ok=True)
        
        with self._get_connection() as conn:
            cursor = conn.cursor()
            version = cursor.execute("SELECT version FROM schema_version").fetchone()[0]
            
            if version < 2:
                msg = "Migrating DB to v2: Adding context column."
                logger.info(msg)
                with open(log_file, "a") as f:
                    f.write(f"[{datetime.now().isoformat()}] {msg}\n")
                try:
                    cursor.execute("ALTER TABLE daily_history ADD COLUMN context TEXT")
                    cursor.execute("UPDATE schema_version SET version = 2")
                    conn.commit()
                except sqlite3.OperationalError:
                    cursor.execute("UPDATE schema_version SET version = 2")
                    conn.commit()

            if version < 3:
                msg = "Migrating DB to v3: Adding preferences and user_profile tables."
                logger.info(msg)
                with open(log_file, "a") as f:
                    f.write(f"[{datetime.now().isoformat()}] {msg}\n")
                try:
                    cursor.execute("""
                        CREATE TABLE IF NOT EXISTS preferences (
                            key TEXT PRIMARY KEY,
                            value TEXT NOT NULL
                        )
                    """)
                    cursor.execute("""
                        CREATE TABLE IF NOT EXISTS user_profile (
                            id INTEGER PRIMARY KEY CHECK (id = 1),
                            profile TEXT NOT NULL,
                            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                        )
                    """)
                    # Import legacy profile JSON if it exists
                    legacy_path = self.db_path.parent / "user_profile.json"
                    if legacy_path.exists():
                        try:
                            legacy_data = json.loads(legacy_path.read_text(encoding="utf-8"))
                            cursor.execute(
                                "INSERT OR REPLACE INTO user_profile (id, profile, updated_at) VALUES (1, ?, ?)",
                                (json.dumps(legacy_data), datetime.now(tz=timezone.utc).isoformat())
                            )
                            legacy_path.unlink()
                            logger.info("Imported legacy user_profile.json into DB.")
                        except Exception as e:
                            logger.warning(f"Could not import legacy profile: {e}")
                    
                    cursor.execute("UPDATE schema_version SET version = 3")
                    conn.commit()
                except sqlite3.OperationalError as e:
                    logger.warning(f"Migration v3 partial: {e}")
                    cursor.execute("UPDATE schema_version SET version = 3")
                    conn.commit()

            if version < 5:
                msg = "Migrating DB to v5: Adding behavioral_patterns table for proactive intelligence."
                logger.info(msg)
                with open(log_file, "a") as f:
                    f.write(f"[{datetime.now().isoformat()}] {msg}\n")
                try:
                    cursor.execute("""
                        CREATE TABLE IF NOT EXISTS behavioral_patterns (
                            trigger_action TEXT,
                            suggested_action TEXT,
                            count INTEGER DEFAULT 1,
                            PRIMARY KEY(trigger_action, suggested_action)
                        )
                    """)
                    cursor.execute("UPDATE schema_version SET version = 5")
                    conn.commit()
                except sqlite3.OperationalError as e:
                    logger.warning(f"Migration v5 failed: {e}")
                    cursor.execute("UPDATE schema_version SET version = 5")
                    conn.commit()
            
        logger.info("DB Migrations completed.")

    # ── Approved / Rejected Plans ─────────────────────────────────────────

    def store_approved(self, plan: dict) -> None:
        plan_id = str(uuid.uuid4())
        with self._get_connection() as conn:
            conn.execute(
                "INSERT INTO approved_plans (id, plan_json, timestamp) VALUES (?, ?, ?)",
                (plan_id, json.dumps(plan), datetime.now(tz=timezone.utc).isoformat())
            )
            conn.commit()

    def store_rejected(self, plan: dict, reason: str) -> None:
        plan_id = str(uuid.uuid4())
        with self._get_connection() as conn:
            conn.execute(
                "INSERT INTO rejected_plans (id, plan_json, reason, timestamp) VALUES (?, ?, ?, ?)",
                (plan_id, json.dumps(plan), reason, datetime.now(tz=timezone.utc).isoformat())
            )

    # ── Daily History & App Usage ─────────────────────────────────────────

    def store_action_event(self, app: str, action_type: str, command: str, result: str, category: str = "general") -> None:
        today = datetime.now().strftime("%Y-%m-%d")
        with self._get_connection() as conn:
            conn.execute(
                "INSERT INTO daily_history (date, app, action_type, command, result, app_category) VALUES (?, ?, ?, ?, ?, ?)",
                (today, app or "System", action_type, command, result, category)
            )

    def get_daily_history(self, date_str: str) -> List[dict]:
        with self._get_connection() as conn:
            rows = conn.execute("SELECT * FROM daily_history WHERE date = ? ORDER BY id ASC", (date_str,)).fetchall()
            return [dict(row) for row in rows]

    def increment_app_usage(self, app_name: str) -> None:
        if not app_name: return
        with self._get_connection() as conn:
            conn.execute("""
                INSERT INTO app_usage (app_name, usage_count) 
                VALUES (?, 1) 
                ON CONFLICT(app_name) DO UPDATE SET usage_count = usage_count + 1
            """, (app_name,))

    def get_recent_approved(self, limit: int = 5) -> List[dict]:
        with self._get_connection() as conn:
            rows = conn.execute("SELECT plan_json FROM approved_plans ORDER BY timestamp DESC LIMIT ?", (limit,)).fetchall()
            return [json.loads(row['plan_json']) for row in rows]

    def get_recent_rejected(self, limit: int = 5) -> List[dict]:
        with self._get_connection() as conn:
            rows = conn.execute("SELECT plan_json, reason FROM rejected_plans ORDER BY timestamp DESC LIMIT ?", (limit,)).fetchall()
            return [{"plan": json.loads(row['plan_json']), "reason": row['reason']} for row in rows]

    def get_app_frequency(self, limit: int = 5) -> Dict[str, int]:
        with self._get_connection() as conn:
            rows = conn.execute("SELECT app_name, usage_count FROM app_usage ORDER BY usage_count DESC LIMIT ?", (limit,)).fetchall()
            return {row['app_name']: row['usage_count'] for row in rows}

    def get_latest_numeric_result(self) -> str | None:
        with self._get_connection() as conn:
            row = conn.execute(
                "SELECT result FROM daily_history WHERE result GLOB '*[0-9]*' ORDER BY id DESC LIMIT 1"
            ).fetchone()
            return row['result'] if row else None

    # ── Behavioral Patterns (v5.6) ─────────────────────────────────────────

    def record_transition(self, trigger: str, suggestion: str) -> None:
        """Record a transition between two actions for behavioral learning."""
        if not trigger or not suggestion: return
        with self._get_connection() as conn:
            conn.execute("""
                INSERT INTO behavioral_patterns (trigger_action, suggested_action, count)
                VALUES (?, ?, 1)
                ON CONFLICT(trigger_action, suggested_action) 
                DO UPDATE SET count = count + 1
            """, (trigger, suggestion))
            conn.commit()

    def get_top_patterns(self, trigger: str, limit: int = 3) -> List[dict]:
        """Retrieve the most frequent follow-up actions for a given trigger."""
        if not trigger: return []
        with self._get_connection() as conn:
            rows = conn.execute(
                "SELECT suggested_action, count FROM behavioral_patterns WHERE trigger_action = ? ORDER BY count DESC LIMIT ?",
                (trigger, limit)
            ).fetchall()
            return [dict(row) for row in rows]

    # ── Preferences (v3.6.1) ─────────────────────────────────────────────

    def get_preference(self, key: str, default: str = "") -> str:
        """Get a user preference by key. Returns default if not found. Never raises."""
        try:
            with self._get_connection() as conn:
                row = conn.execute("SELECT value FROM preferences WHERE key = ?", (key,)).fetchone()
                return row['value'] if row else default
        except Exception as e:
            logger.exception(f"get_preference failed for key '{key}'")
            return default

    def set_preference(self, key: str, value: str) -> None:
        """Set a user preference. Upserts the key-value pair."""
        try:
            with self._get_connection() as conn:
                conn.execute(
                    "INSERT OR REPLACE INTO preferences (key, value) VALUES (?, ?)",
                    (key, value)
                )
                conn.commit()
        except Exception as e:
            logger.exception(f"set_preference failed for key '{key}'")

    def save_preference(self, category: str, value: str) -> None:
        """Alias for set_preference, used for categorized preferences like music."""
        self.set_preference(category, value)

    # ── User Profile (v3.6.1) ────────────────────────────────────────────

    def get_user_profile(self) -> dict:
        """
        Return the user's persistent profile as a dict.
        Always returns a dict (empty if none) and never raises.
        """
        try:
            profile = self._load_user_profile_from_db()
            if profile is None:
                profile = self._load_legacy_profile_json()
            return profile or {}
        except Exception as e:
            logger.exception("get_user_profile failed; returning empty dict")
            return {}

    def _load_user_profile_from_db(self) -> dict | None:
        """Load user profile from the user_profile table."""
        try:
            with self._get_connection() as conn:
                row = conn.execute("SELECT profile FROM user_profile WHERE id = 1").fetchone()
                if row:
                    return json.loads(row['profile'])
                return None
        except Exception:
            return None

    def _load_legacy_profile_json(self) -> dict | None:
        """Read user_profile.json if present (legacy fallback)."""
        try:
            legacy_path = self.db_path.parent / "user_profile.json"
            if legacy_path.exists():
                return json.loads(legacy_path.read_text(encoding="utf-8"))
            return None
        except Exception:
            return None

    def set_user_profile(self, profile: dict) -> None:
        """Upsert the full user profile to DB."""
        try:
            with self._get_connection() as conn:
                conn.execute(
                    "INSERT OR REPLACE INTO user_profile (id, profile, updated_at) VALUES (1, ?, ?)",
                    (json.dumps(profile), datetime.now(tz=timezone.utc).isoformat())
                )
                conn.commit()
        except Exception as e:
            logger.exception("set_user_profile failed")

    def update_user_profile(self, patch: dict) -> None:
        """Merge patch into the existing profile and save."""
        current = self.get_user_profile()
        current.update(patch)
        self.set_user_profile(current)
