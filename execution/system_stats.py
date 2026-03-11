"""
Aegis v4.0 — System Intelligence
===================================
Retrieves real-time system performance metrics.
"""

from __future__ import annotations

import psutil
import logging

logger = logging.getLogger(__name__)

def get_cpu_usage() -> float:
    """Return CPU usage percentage."""
    return psutil.cpu_percent(interval=0.1)

def get_memory_usage() -> dict:
    """Return memory usage metrics."""
    mem = psutil.virtual_memory()
    return {
        "total": mem.total,
        "available": mem.available,
        "percent": mem.percent,
        "used": mem.used
    }

def get_disk_usage(path: str = "C:\\") -> dict:
    """Return disk usage for a specific path."""
    try:
        usage = psutil.disk_usage(path)
        return {
            "total": usage.total,
            "used": usage.used,
            "free": usage.free,
            "percent": usage.percent
        }
    except Exception:
        return {}

def get_network_stats() -> dict:
    """Return network I/O counters."""
    net = psutil.net_io_counters()
    return {
        "bytes_sent": net.bytes_sent,
        "bytes_recv": net.bytes_recv,
        "packets_sent": net.packets_sent,
        "packets_recv": net.packets_recv
    }

def get_system_snapshot() -> dict:
    """Aggregate snapshot of system health."""
    return {
        "cpu_percent": get_cpu_usage(),
        "memory": get_memory_usage(),
        "disk": get_disk_usage(),
        "network": get_network_stats()
    }
