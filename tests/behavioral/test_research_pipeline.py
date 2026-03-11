import pytest
from unittest.mock import MagicMock, patch
from execution.engine import ExecutionEngine
from brain.planner import Action, ActionPlan
from execution.actions.research_handlers import store_knowledge, summarize_page, extract_page_text
from execution.actions.app_actions import ExecutionResult

class TestJarvisResearchPipelineV5:
    """Full behavioral tests for the v5 Research & Memory pipeline."""

    @patch("execution.actions.research_handlers.knowledge")
    def test_research_to_memory_flow(self, mock_knowledge):
        """Verify the flow: Scrape -> Summarize -> Store."""
        mock_knowledge.store_fact.return_value = True
        
        # 1. Mock Extraction
        with patch("execution.actions.research_handlers.browser") as mock_browser:
            mock_browser.extract_content.return_value = "Quantum computing is a type of computation that uses quantum-mechanical phenomena..."
            
            # Action 1: Extract
            action_extract = Action(type="extract_page_text", params={})
            res_extract = extract_page_text(action_extract)
            assert res_extract.success is True
            content = res_extract.data["content"]
            
            # Action 2: Summarize
            with patch("execution.actions.research_handlers.LLMClient") as mock_llm:
                mock_llm.return_value.generate_plan.return_value = "Quantum computing uses qubits for processing."
                action_sum = Action(type="summarize_page", params={"content": content})
                res_sum = summarize_page(action_sum)
                assert res_sum.success is True
                summary = res_sum.data["summary"]
                
                # Action 3: Store
                action_store = Action(type="store_knowledge", params={
                    "topic": "Quantum Computing",
                    "summary": summary,
                    "source_url": "https://example.com"
                })
                res_store = store_knowledge(action_store)
                
                assert res_store.success is True
                assert mock_knowledge.store_fact.called
                args, _ = mock_knowledge.store_fact.call_args
                assert args[0] == "Quantum Computing"
                assert "qubits" in args[1]
