"""
Aegis v5.3 — compute_result Action
==================================
Wrapper for the Math Engine to allow the Execution Engine to handle calculations.
"""

from brain.math_engine import math_engine
from execution.actions.app_actions import ExecutionResult

def compute_result(action) -> ExecutionResult:
    """
    Evaluates a math expression and returns an ExecutionResult.
    """
    expression = action.params.get("expression") or action.value
    if not expression:
        return ExecutionResult(success=False, message="No expression provided for computation.")
        
    result = math_engine.evaluate(expression)
    if result is None:
        return ExecutionResult(
            success=False, 
            message=f"Failed to evaluate expression: {expression}"
        )
        
    # Store in working memory with indexing for daisy-chaining
    from core.state import working_memory
    
    # Simple increment logic
    current_count = working_memory.get("math_result_count", 0) + 1
    working_memory.set("math_result_count", current_count)
    
    # Store as {result1}, {result2}, and the general {result}
    idx_key = f"result{current_count}"
    working_memory.set(idx_key, result)
    working_memory.set("result", result)
    
    # Also update session_memory for legacy compatibility
    from core.state import session_memory
    session_memory.last_result = result
        
    return ExecutionResult(
        success=True,
        message=f"Calculation successful: {result}",
        data={"result": result, "expression": expression, "key": idx_key}
    )
