"""
Aegis v5.3 — respond_text Action
================================
Direct terminal communication action. Prints text to the CLI renderer.
"""

from execution.actions.app_actions import ExecutionResult
from interfaces.cli_renderer import renderer

def respond_text(action) -> ExecutionResult:
    """
    Directly renders AI text to the terminal.
    """
    text = action.params.get("text") or action.value
    if not text:
        return ExecutionResult(success=False, message="No text provided to respond.")
        
    renderer.display_message(text, type="ai")
    
    return ExecutionResult(
        success=True,
        message="Response rendered to CLI successfully.",
        data={"rendered_text": text}
    )
