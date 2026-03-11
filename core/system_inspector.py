"""
Aegis v5.6 — System Inspector
==============================
Unified interface for system metrics and hardware awareness.
Ensures safe fallbacks for all metadata gathering.
"""

import logging
import psutil
from core.process_manager import get_running_app_names
from core.app_registry import get_installed_applications

logger = logging.getLogger(__name__)

def get_running_apps() -> list:
    """Safely retrieves running process names."""
    try:
        return get_running_app_names()
    except Exception as e:
        logger.error(f"Inspector: Failed to get running apps: {e}")
        return []

def get_installed_apps() -> list:
    """Safely retrieves installed application names from registry."""
    try:
        return get_installed_applications()
    except Exception as e:
        logger.error(f"Inspector: Failed to get installed apps: {e}")
        return []

def get_cpu_usage() -> float:
    """Safely retrieves CPU load percentage."""
    try:
        return psutil.cpu_percent(interval=0.1)
    except Exception:
        return 0.0

def get_memory_usage() -> dict:
    """Safely retrieves memory utilization metrics."""
    try:
        mem = psutil.virtual_memory()
        return {
            "total_GB": round(mem.total / (1024**3), 2),
            "available_GB": round(mem.available / (1024**3), 2),
            "percent": mem.percent
        }
    except Exception:
        return {"total_GB": 0, "available_GB": 0, "percent": 0}

def get_system_summary() -> dict:
    """Returns a comprehensive system health snapshot."""
    return {
        "cpu_percent": get_cpu_usage(),
        "memory": get_memory_usage(),
        "running_count": len(get_running_apps()),
        "installed_count": len(get_installed_apps())
    }
