"""
Aegis v5.6 — Variable Resolution Layer
======================================
Resolves placeholders like {result}, {result1}, etc. in commands and expressions.
"""

import re
import logging
from typing import Dict, Any

logger = logging.getLogger(__name__)

def resolve_variables(text: str, context: Dict[str, Any]) -> str:
    """
    v7.0: Replaces {{variable}} placeholders with values from the context.
    Supports both legacy {result} and new {{variable}} formats.
    """
    if not isinstance(text, str):
        return text
        
    def replace_match_double(match):
        var_name = match.group(1).strip()
        val = context.get(var_name)
        if val is not None:
            logger.debug(f"Resolver: Replacing {{{{{var_name}}}}} with {val}")
            return str(val)
        return match.group(0)

    def replace_match_single(match):
        var_name = match.group(1).strip()
        val = context.get(var_name)
        if val is not None:
            logger.debug(f"Resolver: Replacing {{{var_name}}} with {val}")
            return str(val)
        return match.group(0)

    # 1. New v7.0 format: {{variable}}
    text = re.sub(r"\{\{(.*?)\}\}", replace_match_double, text)
    
    # 2. Legacy format: {variable} (incl. result, result1, etc.)
    text = re.sub(r"\{(.*?)\}", replace_match_single, text)
    
    return text
