"""
Aegis v2.0 — System State Monitor
====================================
Read-only system introspection using psutil. Provides CPU, memory,
and disk metrics as structured dictionaries.

This module contains NO execution logic.
"""

from __future__ import annotations

import logging
from typing import Any

import psutil

logger = logging.getLogger(__name__)


def get_cpu_percent(interval: float = 1.0) -> float:
    """
    Return current CPU usage as a percentage.

    Parameters
    ----------
    interval : float
        Sampling interval in seconds (default 1.0).

    Returns
    -------
    float
        CPU usage percentage (0.0–100.0), or -1.0 on failure.
    """
    try:
        return psutil.cpu_percent(interval=interval)
    except Exception as exc:  # noqa: BLE001
        logger.error("Failed to read CPU percent: %s", exc)
        return -1.0


def get_memory_info() -> dict[str, Any]:
    """
    Return system memory information.

    Returns
    -------
    dict
        Keys: total, available, percent. Values in bytes (total/available)
        and percentage (percent). Returns partial dict on failure.
    """
    try:
        mem = psutil.virtual_memory()
        return {
            "total": mem.total,
            "available": mem.available,
            "percent": mem.percent,
        }
    except Exception as exc:  # noqa: BLE001
        logger.error("Failed to read memory info: %s", exc)
        return {"total": 0, "available": 0, "percent": 0.0}


def get_disk_info(path: str = "C:\\") -> dict[str, Any]:
    """
    Return disk usage information for the given mount point.

    Parameters
    ----------
    path : str
        Disk path to check (default ``C:\\``).

    Returns
    -------
    dict
        Keys: total, used, free, percent. Values in bytes
        (total/used/free) and percentage (percent).
    """
    try:
        disk = psutil.disk_usage(path)
        return {
            "total": disk.total,
            "used": disk.used,
            "free": disk.free,
            "percent": disk.percent,
        }
    except Exception as exc:  # noqa: BLE001
        logger.error("Failed to read disk info for '%s': %s", path, exc)
        return {"total": 0, "used": 0, "free": 0, "percent": 0.0}


def get_system_snapshot() -> dict[str, Any]:
    """
    Collect a full system snapshot combining CPU, memory, and disk data.

    Returns a structured dictionary that can be injected into the
    contextual planner prompt. Handles partial failures gracefully —
    if one metric fails, the others are still returned.

    Returns
    -------
    dict
        Complete system snapshot with cpu_percent, memory, and disk keys.
    """
    snapshot: dict[str, Any] = {}

    try:
        snapshot["cpu_percent"] = get_cpu_percent(interval=0.5)
    except Exception as exc:  # noqa: BLE001
        logger.error("Snapshot: CPU collection failed: %s", exc)
        snapshot["cpu_percent"] = -1.0

    try:
        snapshot["memory"] = get_memory_info()
    except Exception as exc:  # noqa: BLE001
        logger.error("Snapshot: Memory collection failed: %s", exc)
        snapshot["memory"] = {"total": 0, "available": 0, "percent": 0.0}

    try:
        snapshot["disk"] = get_disk_info()
    except Exception as exc:  # noqa: BLE001
        logger.error("Snapshot: Disk collection failed: %s", exc)
        snapshot["disk"] = {"total": 0, "used": 0, "free": 0, "percent": 0.0}

    logger.info(
        "System snapshot collected: CPU=%.1f%%, Mem=%.1f%%, Disk=%.1f%%",
        snapshot["cpu_percent"],
        snapshot["memory"]["percent"],
        snapshot["disk"]["percent"],
    )

    return snapshot
