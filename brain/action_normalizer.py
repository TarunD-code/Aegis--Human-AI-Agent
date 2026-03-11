"""
Aegis v3.6 — Action Normalizer
==============================
Maps legacy parameter names to canonical ones.
"""

from typing import Any
from config import CANONICAL_PARAM_FALLBACKS

def normalize_parameters(action_type: str, params: dict[str, Any], raw_action: dict[str, Any]) -> dict[str, Any]:
    """
    Applies fallbacks for legacy parameters.
    e.g., if a plan action has `value: "calc"` but the action schema expects `application_name`.
    """
    normalized = params.copy()
    for old_key, new_key in CANONICAL_PARAM_FALLBACKS.items():
        if new_key not in normalized:
            if old_key in raw_action:
                normalized[new_key] = raw_action[old_key]
            elif old_key in normalized:
                normalized[new_key] = normalized.pop(old_key)
    return normalized
