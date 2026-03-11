"""
Aegis v1.0 — Plan Validator
============================
Validates an ActionPlan against security rules before it reaches
the approval gate or execution engine.
"""

from __future__ import annotations

from typing import TYPE_CHECKING
from security.whitelist import is_action_allowed, is_path_blocked, is_ps_command_allowed
from config import ACTION_PARAMETER_SCHEMAS
from logs.logger import get_logger

if TYPE_CHECKING:
    from brain.planner import ActionPlan

logger = get_logger(__name__)

def validate_plan(plan: ActionPlan) -> tuple[bool, list[str]]:
    """
    Validate every action in *plan* against security rules and parameter schemas.
    Never raises; returns (is_valid, errors).
    """
    warnings: list[str] = []
    
    try:
        PROTECTED_PROCESSES = {"cmd.exe", "powershell.exe", "python.exe", "aegis.exe", "terminal.exe", "conhost.exe"}
        
        for idx, action in enumerate(plan.actions, 1):
            prefix = f"Action {idx} [{action.type}]"

            # 1. Protect Core System Processes
            if action.type == "close_application":
                app_name = (action.params.get("application_name") or action.value or "").lower()
                if any(proc in app_name for proc in PROTECTED_PROCESSES):
                    warnings.append(
                        f"{prefix}: Termination of protected process '{app_name}' is FORBIDDEN."
                    )
                    continue

            # 2. Check action type whitelist
            if not is_action_allowed(action.type):
                warnings.append(
                    f"{prefix}: Action type '{action.type}' is NOT whitelisted."
                )
                continue  # no point checking further

            # 2. Check parameter schema
            required_params = ACTION_PARAMETER_SCHEMAS.get(action.type, [])
            for param in required_params:
                if param not in action.params:
                    # v3.5.3: Allow fallback to 'value' for application_name for transition
                    if param == "application_name" and action.value:
                        logger.warning("%s: 'application_name' missing in params, falling back to 'value'.", prefix)
                        action.params["application_name"] = action.value
                    else:
                        warnings.append(
                            f"{prefix}: Missing required parameter '{param}'."
                        )

            # 3. Check for blocked folder targets
            if action.target and is_path_blocked(action.target):
                warnings.append(
                    f"{prefix}: Target path '{action.target}' is inside a "
                    f"blocked system folder."
                )

            # 4. Validate PowerShell commands
            if action.type == "run_powershell" and action.value:
                if not is_ps_command_allowed(action.value):
                    warnings.append(
                        f"{prefix}: PowerShell command '{action.value}' is not allowed."
                    )

    except Exception as e:
        logger.exception("Unexpected error in validate_plan")
        return False, [f"validation_exception: {e}"]

    is_valid = len(warnings) == 0

    if is_valid:
        logger.info("Plan security validation passed.")
    else:
        logger.warning(
            "Plan security validation FAILED with %d error(s): %s",
            len(warnings),
            "; ".join(warnings),
        )

    return is_valid, warnings

def validate_action(action) -> tuple[bool, bool, str]:
    """
    v7.0: Single action security validation.
    Returns (is_allowed, needs_confirmation, error_message).
    """
    from security.whitelist import is_action_allowed
    from config import ACTION_WHITELIST
    
    # 1. Whitelist Check
    if action.type not in ACTION_WHITELIST and not is_action_allowed(action.type):
        return False, False, f"Action '{action.type}' is not whitelisted for execution."
    
    # 2. Risk Level Check (HIGH/CRITICAL require confirmation)
    needs_conf = False
    if getattr(action, 'risk_level', 'LOW') in ["HIGH", "CRITICAL"]:
        needs_conf = True
    
    if getattr(action, 'requires_confirmation', False):
        needs_conf = True
        
    return True, needs_conf, ""
