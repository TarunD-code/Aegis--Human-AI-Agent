import webbrowser
import logging

logger = logging.getLogger(__name__)

URL_MAP = {
    "youtube": "https://www.youtube.com",
    "github": "https://www.github.com",
    "chatgpt": "https://chat.openai.com",
    "google": "https://www.google.com",
    "gmail": "https://mail.google.com",
    "stack overflow": "https://stackoverflow.com",
    "reddit": "https://www.reddit.com"
}

def route_browser(query: str) -> bool:
    """
    Routes a natural language query to a specific URL or performs a search.
    """
    clean_query = query.lower().strip()
    
    # Check for direct keyword matches
    for keyword, url in URL_MAP.items():
        if keyword in clean_query:
            logger.info(f"Routing browser to known site: {keyword}")
            webbrowser.open(url)
            return True
    
    # Fallback to search if query contains search-like intent
    if any(k in clean_query for k in ["search", "find", "who", "what", "how"]):
        query_param = clean_query.replace("search", "").strip()
        search_url = f"https://www.google.com/search?q={query_param}"
        logger.info(f"Routing browser to search: {query_param}")
        webbrowser.open(search_url)
        return True

    # If it looks like a URL, open it directly
    if "." in clean_query and " " not in clean_query:
        url = clean_query if clean_query.startswith("http") else f"https://{clean_query}"
        webbrowser.open(url)
        return True

    return False
