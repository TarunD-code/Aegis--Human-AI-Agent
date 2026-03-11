"""
Aegis v3.6 — Plan Validator
=============================
Graceful validation of LLM-generated plans before parsing.
"""

from typing import Tuple, List
from logs.logger import get_logger
from config import get_action_list, ACTION_PARAMETER_SCHEMAS
from brain.action_normalizer import normalize_parameters

logger = get_logger(__name__)

def normalize_and_validate(plan_dict: dict) -> Tuple[bool, List[str]]:
    """
    Aegis v3.6 — Production-Ready structural validation and normalization.
    Returns (is_valid, errors). Never raises.
    """
    errors = []
    try:
        if not isinstance(plan_dict, dict):
            return False, ["invalid_json_structure"]

        # 1. Required Top-Level Fields
        if not plan_dict.get("summary"):
            errors.append("missing_summary")
        if not plan_dict.get("reasoning"):
            errors.append("missing_reasoning")
        
        actions = plan_dict.get("actions")
        if not isinstance(actions, list) or not actions:
            errors.append("no_actions")
            return False, errors

        # 2. Action Normalization & Validation
        allowed_actions = get_action_list()

        for i, action in enumerate(actions):
            prefix = f"action_{i}"
            
            # Canonical Type
            raw_type = action.get("type") or action.get("action_type") or action.get("action")
            if not raw_type:
                errors.append(f"{prefix}:missing_type")
                continue
            
            if raw_type not in allowed_actions:
                errors.append(f"{prefix}:unknown_action:{raw_type}")
                continue
            
            action["action_type"] = raw_type # Enforce canonical key
            
            # Parameter Normalization
            params = action.get("parameters") or action.get("params") or {}
            
            # Apply Fallbacks via normalizer
            params = normalize_parameters(raw_type, params, action)
            
            # Check Required Parameters
            required = ACTION_PARAMETER_SCHEMAS.get(raw_type, [])
            for req in required:
                if req not in params:
                    errors.append(f"{prefix}:missing_parameter:{raw_type}:{req}")
            
            action["parameters"] = params

        if errors:
            logger.warning(f"Plan structure validation failed: {errors}")
            return False, errors

        logger.info("Plan structure validation passed.")
        return True, []

    except Exception as e:
        logger.exception("Unexpected error in normalize_and_validate")
        return False, [f"validation_exception: {e}"]

