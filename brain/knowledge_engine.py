"""
Aegis v4.0 — Knowledge Engine
================================
Performs Wikipedia lookups, DuckDuckGo searches, and LLM-based summarization.
"""

from __future__ import annotations

import logging
import requests
from typing import Any

logger = logging.getLogger(__name__)

class KnowledgeEngine:
    """
    Retrieves information from external and internal sources.
    """

    def __init__(self, user_agent: str = "Aegis/4.0 (AI Assistant)"):
        self.wiki = None
        try:
            import wikipediaapi
            self.wiki = wikipediaapi.Wikipedia(
                user_agent=user_agent,
                language='en',
                extract_format=wikipediaapi.ExtractFormat.WIKI
            )
        except ImportError:
            logger.warning("wikipediaapi not installed. Wikipedia searches will fail gracefully.")

    def search_wikipedia(self, query: str) -> str:
        """Fetch summary from Wikipedia."""
        try:
            page = self.wiki.page(query)
            if page.exists():
                return page.summary[:1000] # Limit to 1000 chars
            return f"No Wikipedia page found for '{query}'."
        except Exception as e:
            logger.error(f"Wikipedia search error: {e}")
            return f"Error searching Wikipedia: {e}"

    def search_duckduckgo(self, query: str) -> str:
        """Fetch instant answer from DuckDuckGo."""
        try:
            url = f"https://api.duckduckgo.com/?q={query}&format=json&no_html=1"
            response = requests.get(url, timeout=10)
            data = response.json()
            
            abstract = data.get("AbstractText", "")
            if abstract:
                return abstract
            
            related = data.get("RelatedTopics", [])
            if related and "Text" in related[0]:
                return related[0]["Text"]
                
            return f"No instant answer found on DuckDuckGo for '{query}'."
        except Exception as e:
            logger.error(f"DuckDuckGo search error: {e}")
            return f"Error searching DuckDuckGo: {e}"

    def get_knowledge(self, query: str) -> str:
        """Combined search strategy."""
        # 1. Try Wikipedia
        res = self.search_wikipedia(query)
        if "No Wikipedia page found" not in res and not res.startswith("Error"):
            return res
            
        # 2. Try DuckDuckGo
        return self.search_duckduckgo(query)
