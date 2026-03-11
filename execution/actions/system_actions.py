"""
Aegis v4.0 — System Actions
==============================
Retrieve system performance metrics via execution/system_stats.py.
"""

from __future__ import annotations
from execution import system_stats
from execution.actions.app_actions import ExecutionResult
from execution.verification_engine import VerificationEngine, verify_system_stats

verify_engine = VerificationEngine(retries=1)

def get_system_metrics(action) -> ExecutionResult:
    """Retrieve full system snapshot."""
    success, res = verify_engine.verify_and_retry(
        system_stats.get_system_snapshot,
        lambda: verify_system_stats(system_stats.get_system_snapshot()),
    )
    
    if success:
        snapshot = system_stats.get_system_snapshot()
        msg = (
            f"System Health: CPU {snapshot['cpu_percent']}%, "
            f"RAM {snapshot['memory']['percent']}% used, "
            f"Disk {snapshot['disk'].get('percent', 'N/A')}% used."
        )
        return ExecutionResult(success=True, message=msg, data=snapshot)
    
    return ExecutionResult(success=False, message="Failed to retrieve system metrics.")

def switch_application(action) -> ExecutionResult:
    """Switch focus to an application."""
    from core.system_inspector import switch_application as switch_func
    app_name = action.params.get("application_name") or action.value
    if switch_func(app_name):
        return ExecutionResult(success=True, message=f"Switched to {app_name}.")
    return ExecutionResult(success=False, message=f"Failed to switch to {app_name}.")

def close_application(action) -> ExecutionResult:
    """Close an application."""
    from core.system_inspector import close_application as close_func
    app_name = action.params.get("application_name") or action.value
    if close_func(app_name):
        return ExecutionResult(success=True, message=f"Closed {app_name}.")
    return ExecutionResult(success=False, message=f"Failed to close {app_name}.")

def list_running_apps(action) -> ExecutionResult:
    """List all running user applications."""
    from core.system_inspector import get_running_app_names
    apps = get_running_app_names()
    return ExecutionResult(success=True, message=f"Running apps: {', '.join(apps)}", data={"apps": apps})

def browse_to(action) -> ExecutionResult:
    """Route browser to a specific destination."""
    from browser_automation.browser_router import route_browser
    query = action.params.get("query") or action.value
    if route_browser(query):
        return ExecutionResult(success=True, message=f"Routed browser for: {query}")
    return ExecutionResult(success=False, message=f"Could not route browser for: {query}")
