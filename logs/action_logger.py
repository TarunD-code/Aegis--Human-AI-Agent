"""
Aegis v7.0 — Structured Action Logger
=======================================
Logs every action execution as JSON-lines for diagnostics,
performance analysis, and debugging.
"""

import json
import os
import logging
import time
from datetime import datetime
from pathlib import Path

logger = logging.getLogger(__name__)

class ActionLogger:
    """Writes structured JSON-lines logs for every action execution."""

    def __init__(self, log_dir: str = ""):
        if not log_dir:
            base = Path(__file__).resolve().parent.parent
            log_dir = str(base / "logs" / "data")
        self.log_dir = log_dir
        os.makedirs(self.log_dir, exist_ok=True)
        self.log_file = os.path.join(self.log_dir, "action_log.jsonl")

    def log_action(
        self,
        action_type: str,
        params: dict,
        success: bool,
        message: str,
        duration_ms: float = 0.0,
        window_title: str = "",
        cursor_position: tuple = (0, 0),
        error: str = "",
    ) -> None:
        """Log a single action execution as a JSON line."""
        entry = {
            "timestamp": datetime.now().isoformat(),
            "action_type": action_type,
            "params": params,
            "success": success,
            "message": message[:500],
            "duration_ms": round(duration_ms, 2),
            "window_title": window_title,
            "cursor_x": cursor_position[0],
            "cursor_y": cursor_position[1],
            "error": error[:300] if error else "",
        }
        try:
            with open(self.log_file, "a", encoding="utf-8") as f:
                f.write(json.dumps(entry, ensure_ascii=False) + "\n")
        except Exception as e:
            logger.error(f"ActionLogger write failed: {e}")

    def get_recent_logs(self, n: int = 20) -> list[dict]:
        """Read the last N log entries."""
        try:
            with open(self.log_file, "r", encoding="utf-8") as f:
                lines = f.readlines()
            return [json.loads(line) for line in lines[-n:]]
        except Exception:
            return []

# Singleton
action_logger = ActionLogger()
