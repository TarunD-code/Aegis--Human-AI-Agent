"""
Aegis v6.3 — Browser Controller
================================
High-level browser control with search result extraction,
YouTube detection, page text capture, and working memory integration.
"""

from __future__ import annotations
import logging
import webbrowser
import subprocess
import re
from urllib.parse import quote, urlparse

logger = logging.getLogger(__name__)

class BrowserController:
    """
    Manages browser-level operations: search, navigate, extract, summarize.
    """

    def __init__(self, browser_name: str = "chrome"):
        self.browser_name = browser_name
        self._last_url = None
        logger.debug(f"BrowserController initialized for: {browser_name}")

    def search_web(self, query: str) -> bool:
        """Search Google directly."""
        url = f"https://www.google.com/search?q={quote(query)}"
        logger.info(f"Searching web for: {query}")
        webbrowser.open(url)
        self._last_url = url
        self._store_url(url)
        return True

    def open_url(self, url: str) -> bool:
        """Open a specific URL in the default browser."""
        if not url.startswith("http"):
            url = "https://" + url
        logger.info(f"Opening URL: {url}")
        webbrowser.open(url)
        self._last_url = url
        self._store_url(url)
        return True

    def browse_to(self, url: str) -> bool:
        """Navigate browser to a URL (alias for open_url)."""
        return self.open_url(url)

    def open_new_tab(self, url: str = "https://www.google.com") -> bool:
        """Open a new tab with a specific URL."""
        logger.info(f"Attempting to open new tab for: {url}")
        try:
            subprocess.Popen(["chrome.exe", "--new-tab", url])
            return True
        except Exception as e:
            logger.debug(f"Chrome command failed: {e}. Falling back to webbrowser.")
            webbrowser.open_new_tab(url)
            return True

    def open_first_result(self, query: str = "") -> bool:
        """
        v7.0: Enhanced first-result extraction with YouTube prioritization.
        """
        logger.info(f"open_first_result called for query: {query}")
        
        # 1. Attempt Playwright (Future Deep Integration)
        try:
            # Placeholder for Playwright automation
            pass
        except Exception:
            pass

        # 2. Fallback to requests + BeautifulSoup
        try:
            import requests
            from bs4 import BeautifulSoup
        except ImportError:
            logger.warning("requests/bs4 not installed. Falling back to simple search.")
            return self.search_web(query)

        try:
            search_url = f"https://www.google.com/search?q={quote(query)}"
            headers = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"}
            resp = requests.get(search_url, headers=headers, timeout=10)
            soup = BeautifulSoup(resp.text, "html.parser")

            # Improved link extraction
            links = []
            for a in soup.select('div.g a'):
                href = a.get('href')
                if href and href.startswith('http') and 'google.com' not in href:
                    links.append(href)
            
            if not links:
                # Fallback for older Google layouts or different structures
                for a_tag in soup.select("a[href]"):
                    href = a_tag["href"]
                    if "/url?q=" in href:
                        extracted = href.split("/url?q=")[1].split("&")[0]
                        if extracted.startswith("http") and "google.com" not in extracted:
                            links.append(extracted)

            first_link = links[0] if links else None

            if not first_link:
                logger.warning("No direct link found. Falling back to YouTube results.")
                first_link = f"https://www.youtube.com/results?search_query={quote(query)}"

            # YouTube enhancement
            if "youtube.com/watch" in first_link:
                if "autoplay=1" not in first_link:
                    connector = "&" if "?" in first_link else "?"
                    first_link += f"{connector}autoplay=1"
                logger.info(f"Prioritizing YouTube video with autoplay: {first_link}")

            logger.info(f"Navigating to first search result: {first_link}")
            webbrowser.open(first_link)
            self._last_url = first_link
            self._store_url(first_link)
            return True
            
        except Exception as e:
            logger.error(f"open_first_result failed: {e}")
            return self.search_web(query)

    def extract_page_text(self, url: str = "") -> str:
        """
        Aegis v6.3: Extract visible text from a web page and store in working memory.
        """
        target_url = url or self._last_url
        if not target_url:
            logger.warning("No URL available for text extraction.")
            return ""

        try:
            import requests
            from bs4 import BeautifulSoup
            headers = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)"}
            resp = requests.get(target_url, headers=headers, timeout=10)
            soup = BeautifulSoup(resp.text, "html.parser")

            # Remove script/style tags
            for tag in soup(["script", "style", "nav", "footer", "header"]):
                tag.decompose()

            text = soup.get_text(separator="\n", strip=True)
            content = text[:5000]  # Cap at 5000 chars for memory safety

            # Store in working memory
            try:
                from core.state import working_memory
                working_memory.set("page_content", content)
                working_memory.set("active_url", target_url)
            except Exception:
                pass

            logger.info(f"Extracted {len(content)} chars from {target_url}")
            return content
        except Exception as e:
            logger.error(f"Page text extraction failed: {e}")
            return ""

    def summarize_page(self) -> str:
        """
        Aegis v6.3: Summarize the page content stored in working memory.
        Falls back to LLM if content is empty.
        """
        try:
            from core.state import working_memory
            content = working_memory.get("page_content", "")
        except Exception:
            content = ""

        if not content:
            logger.info("No page content in memory. Cannot summarize.")
            return "No page content available to summarize, Sir."

        # Simple extractive summary: first 500 chars
        summary = content[:500]
        if len(content) > 500:
            summary += "..."
        logger.info(f"Page summary generated: {len(summary)} chars")
        return summary

    def navigate_tab(self, direction: str = "next") -> bool:
        """Navigate between tabs using keyboard shortcuts."""
        import pyautogui
        if direction == "next":
            pyautogui.hotkey("ctrl", "tab")
        else:
            pyautogui.hotkey("ctrl", "shift", "tab")
        return True

    def _store_url(self, url: str):
        """Store URL in working memory."""
        try:
            from core.state import working_memory
            working_memory.set("active_url", url)
        except Exception:
            pass

# Singleton
browser_controller = BrowserController()
