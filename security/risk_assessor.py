"""
Aegis v6.0 — Risk Assessment System
====================================
Evaluates the risk level of user intents to ensure dangerous actions 
require explicit user approval.
"""

def requires_approval(intent_metadata) -> bool:
    """
    Evaluates if the proposed intent includes high-risk actions.
    """
    if not intent_metadata or not intent_metadata.intent_types:
        return False
        
    risky_intents = [
        "DELETE",
        "SYSTEM_CONTROL",
        "FILE_MODIFICATION",
        "SYSTEM_MODIFICATION",
        "UNINSTALL"
    ]
    
    # Check if any detected intent is in the high-risk list
    for intent_type in intent_metadata.intent_types:
        if intent_type in risky_intents:
            return True
            
    return False

def check_command_risk(command_text: str) -> bool:
    """Fallback manual check for explicitly dangerous keywords."""
    dangerous_keywords = ["delete", "remove", "format", "shutdown", "restart", "kill"]
    text = command_text.lower()
    return any(keyword in text for keyword in dangerous_keywords)
