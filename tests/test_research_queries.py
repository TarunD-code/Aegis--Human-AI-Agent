"""
Aegis v4.0 — Research Query Tests
====================================
Validates Wikipedia and DuckDuckGo engine integration.
"""

import sys
from pathlib import Path
import pytest
from unittest.mock import patch, MagicMock

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from execution.actions.research_actions import knowledge_lookup
from brain.planner import Action

class TestResearchQueries:

    @patch("wikipediaapi.Wikipedia.page")
    def test_wiki_lookup_success(self, mock_page):
        """Verify Wikipedia page summary is retrieved."""
        mock_page_obj = MagicMock()
        mock_page_obj.exists.return_value = True
        mock_page_obj.summary = "Albert Einstein was a physicist."
        mock_page.return_value = mock_page_obj
        
        action = Action(type="knowledge_lookup", params={"query": "Einstein"})
        res = knowledge_lookup(action)
        
        assert res.success is True
        assert "Einstein" in res.data["result"]
        assert "physicist" in res.data["result"]

    @patch("requests.get")
    def test_ddg_fallback(self, mock_get):
        """Verify DuckDuckGo is called if Wikipedia fails or is missing."""
        # 1. Wiki page doesn't exist
        with patch("wikipediaapi.Wikipedia.page") as mock_wiki:
            mock_wiki.return_value.exists.return_value = False
            
            # 2. DDG provides answer
            mock_response = MagicMock()
            mock_response.json.return_value = {"AbstractText": "Linux is a kernel."}
            mock_get.return_value = mock_response
            
            action = Action(type="knowledge_lookup", params={"query": "Linux"})
            res = knowledge_lookup(action)
            
            assert res.success is True
            assert "Linux" in res.data["result"]
