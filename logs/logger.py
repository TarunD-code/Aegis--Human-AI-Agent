"""
Aegis v1.0 — Logger
=====================
Structured JSON logging for all Aegis operations: requests, AI plans,
approvals, and execution results.
"""

from __future__ import annotations

import json
import logging
import sys
import os
from datetime import datetime, timezone
from pathlib import Path
from logging.handlers import RotatingFileHandler
from typing import Any
from config import LOG_DIR, BASE_DIR

# Global logger registry
_loggers: dict[str, logging.Logger] = {}

def get_logger(name: str) -> logging.Logger:
    """Standardized logger factory for Aegis."""
    if name in _loggers:
        return _loggers[name]
    
    logger = logging.getLogger(name)
    _loggers[name] = logger
    return logger

def setup_logging(verbose: bool = False) -> None:
    """Aegis v3.5.4 — Production-Ready Logging Setup."""
    level = logging.DEBUG if verbose else logging.INFO
    log_format = "%(asctime)s │ %(name)-25s │ %(levelname)-7s │ %(message)s"
    date_fmt = "%H:%M:%S"

    # Force UTF-8 on Windows Console
    for stream in [sys.stdout, sys.stderr]:
        if hasattr(stream, "reconfigure"):
            try:
                stream.reconfigure(encoding="utf-8")
            except Exception:
                pass

    root_logger = logging.getLogger()
    root_logger.setLevel(level)
    for h in root_logger.handlers[:]:
        root_logger.removeHandler(h)

    # Console Handler
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setFormatter(logging.Formatter(log_format, datefmt=date_fmt))
    root_logger.addHandler(console_handler)

    # Rotating File Handler
    try:
        log_root = BASE_DIR / "logs"
        log_root.mkdir(exist_ok=True)
        file_handler = RotatingFileHandler(
            log_root / "aegis.log", 
            maxBytes=10*1024*1024, # 10MB
            backupCount=5,
            encoding="utf-8"
        )
        file_handler.setFormatter(logging.Formatter(log_format, datefmt=date_fmt))
        root_logger.addHandler(file_handler)
    except Exception as exc:
        print(f"Warning: Could not initialize file logging: {exc}")

    # Silence noisy dependencies
    for mod in ["urllib3", "google", "groq", "httpx"]:
        logging.getLogger(mod).setLevel(logging.WARNING)

class AegisLogger:
    """Structured JSON audit logger for Aegis v3.5.4."""

    def __init__(self) -> None:
        self._log_dir = Path(LOG_DIR)
        self._log_dir.mkdir(parents=True, exist_ok=True)
        self._audit_logger = get_logger("aegis.audit")

    def _write_audit(self, event_type: str, data: dict[str, Any]) -> None:
        """Writes a structured JSON event to the audit stream and file."""
        entry = {
            "timestamp": datetime.now(tz=timezone.utc).isoformat(),
            "event_type": event_type,
            **data
        }
        
        # 1. Log to standard logger (captured by file/console)
        self._audit_logger.info(f"AUDIT_EVENT: {event_type} | {json.dumps(data)}")

        # 2. Append to daily persistent JSON file
        today = datetime.now(tz=timezone.utc).strftime("%Y-%m-%d")
        log_file = self._log_dir / f"aegis_{today}.json"
        
        try:
            entries = []
            if log_file.exists():
                with open(log_file, "r", encoding="utf-8") as f:
                    content = f.read().strip()
                    if content:
                        entries = json.loads(content)
            
            entries.append(entry)
            
            with open(log_file, "w", encoding="utf-8") as f:
                json.dump(entries, f, indent=2, ensure_ascii=False)
                f.flush()
                os.fsync(f.fileno()) # Durability guarantee
        except Exception as e:
            get_logger(__name__).error(f"Failed to write audit entry: {e}")

    def log_ai_plan(self, plan: dict, retry_count: int = 0, validation_errors: list = None) -> None:
        self._write_audit("ai_plan", {
            "plan": plan,
            "retry_count": retry_count,
            "errors": validation_errors or []
        })

    def log_approval(self, plan_id: str, approved: bool, user: str = "cli") -> None:
        self._write_audit("approval_event", {
            "plan_id": plan_id,
            "approved": approved,
            "user": user
        })

    def log_execution(self, action: dict, result: Any, success: bool) -> None:
        self._write_audit("execution_event", {
            "action_type": action.get("type") or action.get("action_type"),
            "action_id": action.get("id"),
            "success": success,
            "result": str(result)
        })

    def log_error(self, error: str, context: str = "") -> None:
        self._write_audit("error_event", {"error": error, "context": context})

# Global for legacy usage
_global_aegis_logger = None
def get_audit_logger():
    global _global_aegis_logger
    if _global_aegis_logger is None:
        _global_aegis_logger = AegisLogger()
    return _global_aegis_logger
