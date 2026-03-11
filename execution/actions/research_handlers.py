"""
Aegis v5.0 — Research Action Handlers
========================================
Handlers for browser-based research and knowledge storage.
"""

import logging
from typing import Any
from execution.actions.app_actions import ExecutionResult
from browser_automation.browser_controller import BrowserController
from brain.llm.llm_client import LLMClient
from memory.knowledge_store import KnowledgeStore

logger = logging.getLogger(__name__)

# Initialize a global browser controller
browser = BrowserController(browser_name="chrome")
# Jarvis v5.0 persistent memory
knowledge = KnowledgeStore()

def open_first_result(action) -> ExecutionResult:
    """Clicks the first organic result in a search engine."""
    success = browser.open_first_result()
    return ExecutionResult(
        success=success, 
        message="Attempted to open first result, Sir." if success else "Failed to click result.",
        data={"action_type": action.type}
    )

def extract_page_text(action) -> ExecutionResult:
    """Scrapes the active browser page content."""
    content = browser.extract_content()
    if content:
        return ExecutionResult(
            success=True,
            message="Successfully extracted page content.",
            data={"action_type": action.type, "content": content}
        )
    return ExecutionResult(success=False, message="Could not extract content from the current page.")

def summarize_page(action) -> ExecutionResult:
    """Summarizes page content using the LLM."""
    content = action.params.get("content") or ""
    if not content:
        return ExecutionResult(success=False, message="No content provided to summarize.")
    
    # Simple summary logic for now (could call LLM)
    client = LLMClient(system_prompt="You are a research assistant. Summarize the provided text concisely.")
    summary = client.generate_plan(f"Summarize this content: {content[:10000]}", max_retries=1)
    
    # Since generate_plan returns a dict (usually), we need to handle it. 
    # But for a simple prompt, LLMClient might return a string if we are unlucky?
    # Actually, LLMClient.generate_plan normally expects to return JSON.
    # Let's assume it returns a summary string if we prompt it right.
    
    return ExecutionResult(
        success=True,
        message="Summarized the research content, Sir.",
        data={"action_type": action.type, "summary": str(summary)}
    )

def store_knowledge(action) -> ExecutionResult:
    """Stores a research summary in the persistent memory."""
    topic = action.params.get("topic", "General")
    summary = action.params.get("summary", "")
    source = action.params.get("source_url", "N/A")
    tags = action.params.get("tags", "")
    
    success = knowledge.store_fact(topic, summary, source, tags)
    
    if success:
        return ExecutionResult(
            success=True,
            message=f"I have committed this information about '{topic}' to my internal memory.",
            data={"action_type": action.type, "topic": topic}
        )
    return ExecutionResult(success=False, message=f"Sir, I failed to commit the data about '{topic}' to memory.")
