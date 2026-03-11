"""
Aegis v4.0 — Research Actions
================================
Implemented knowledge lookup and online search using the KnowledgeEngine.
"""

from __future__ import annotations
import logging
from brain.knowledge_engine import KnowledgeEngine
from execution.actions.app_actions import ExecutionResult

logger = logging.getLogger(__name__)
k_engine = KnowledgeEngine()

def search_online(action) -> ExecutionResult:
    """Perform DuckDuckGo search."""
    query = action.params.get("query") or action.value
    if not query:
        return ExecutionResult(success=False, message="No query provided.")
    
    res = k_engine.search_duckduckgo(query)
    return ExecutionResult(
        success=True,
        message=f"Found information for '{query}'",
        data={"action_type": action.type, "result": res}
    )

def knowledge_lookup(action) -> ExecutionResult:
    """Perform Wikipedia + DuckDuckGo combined lookup."""
    query = action.params.get("query") or action.value
    if not query:
        return ExecutionResult(success=False, message="No query provided.")

    res = k_engine.get_knowledge(query)
    return ExecutionResult(
        success=True,
        message=f"Retrieved knowledge for '{query}'",
        data={"action_type": action.type, "result": res}
    )

def summarize_text(action) -> ExecutionResult:
    """LLM usually handles this, but here we provide a basic fallback."""
    text = action.params.get("text") or action.value
    if not text:
        return ExecutionResult(success=False, message="No text to summarize.")
    
    summary = text[:200] + "..." if len(text) > 200 else text
    return ExecutionResult(success=True, message="Summarized text.", data={"summary": summary})
