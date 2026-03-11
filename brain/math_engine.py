import re
import logging
from typing import Optional

logger = logging.getLogger(__name__)

class MathEngine:
    """
    Evaluates mathematical expressions safely, supporting both raw
    formulas and common natural language phrases.
    """
    def _nl_to_expr(self, text: str) -> str:
        """Translates natural language math into a raw expression."""
        text = text.lower().strip()
        
        # Pattern: "add X and Y"
        match = re.search(r"add\s+([\d\.]+)\s+and\s+([\d\.]+)", text)
        if match: return f"{match.group(1)}+{match.group(2)}"
        
        # Pattern: "multiply X by Y"
        match = re.search(r"multiply\s+([\d\.]+)\s+by\s+([\d\.]+)", text)
        if match: return f"{match.group(1)}*{match.group(2)}"
        
        # Pattern: "X percent of Y"
        match = re.search(r"([\d\.]+)\s+percent\s+of\s+([\d\.]+)", text)
        if match:
            percent = float(match.group(1)) / 100
            return f"{match.group(2)}*{percent}"

        # Clean common garbage words
        text = text.replace("what is", "").replace("calculate", "").strip()
        return text

    def evaluate(self, expression: str) -> Optional[float]:
        # Step 1: Handle natural language
        expr = self._nl_to_expr(expression)
        
        # Step 2: Clean and normalize
        expr = expr.replace(" ", "").replace("x", "*").replace("^", "**")
        
        # Security: Only allow numbers and basic operators
        if not re.match(r"^[0-9\+\-\*\/\.\(\)\*]+$", expr):
            logger.warning(f"Rejected unsafe math expression: {expression} (normalized: {expr})")
            return None
            
        try:
            # Safe eval with restricted globals
            result = eval(expr, {"__builtins__": None}, {})
            return float(result)
        except Exception as e:
            logger.error(f"Math evaluation failed for '{expr}': {e}")
            return None

# Global instance
math_engine = MathEngine()
