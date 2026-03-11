"""
Aegis v6.0 — Browser Automation Agent
======================================
Dedicated Selenium agent for task-specific browser automation,
such as playing music, interacting with pages, and scraping.
"""

import time
import logging
from typing import Optional

logger = logging.getLogger(__name__)

def play_music(song: Optional[str] = None) -> bool:
    """
    Automates opening Chrome and playing a song on YouTube.
    Requires selenium and webdriver-manager.
    """
    if not song:
        song = "top music"
        
    logger.info(f"BrowserAgent: Attempting to play music: {song}")
    
    try:
        from selenium import webdriver
        from selenium.webdriver.common.by import By
        from selenium.webdriver.chrome.service import Service as ChromeService
        from webdriver_manager.chrome import ChromeDriverManager
        from selenium.webdriver.common.keys import Keys
    except ImportError:
        logger.error("BrowserAgent: Selenium or webdriver_manager not installed.")
        return False

    try:
        # 1. Detect browser & Setup
        options = webdriver.ChromeOptions()
        
        # Explicit Chrome Path Detection to Prevent Failures
        import os
        chrome_paths = [
            r"C:\Program Files\Google\Chrome\Application\chrome.exe",
            r"C:\Program Files (x86)\Google\Chrome\Application\chrome.exe",
            os.path.expanduser(r"~\AppData\Local\Google\Chrome\Application\chrome.exe")
        ]
        for path in chrome_paths:
            if os.path.exists(path):
                options.binary_location = path
                logger.info(f"BrowserAgent: Found Chrome at {path}")
                break
                
        # 2. Open Chrome
        driver = webdriver.Chrome(service=ChromeService(ChromeDriverManager().install()), options=options)
        
        # 3. Go to YouTube
        driver.get("https://youtube.com")
        time.sleep(2) # Wait for load/consent
        
        # 4. Search Music
        search = driver.find_element(By.NAME, "search_query")
        search.send_keys(song)
        search.send_keys(Keys.RETURN)
        
        time.sleep(3) # Wait for results
        
        # 5. Play first suggestion
        # Use an xpath or ID that matches video titles in search results
        first_video = driver.find_element(By.CSS_SELECTOR, "a#video-title")
        first_video.click()
        
        logger.info("BrowserAgent: Playing music.")
        # We don't close the driver, we leave it running for the user
        return True
        
    except Exception as e:
        logger.error(f"BrowserAgent: Error playing music: {e}")
        return False

def open_first_result(query: str) -> bool:
    """
    Automates a web search for the query, clicks the very first organic link, 
    and handles specific domain autoplays (like YouTube).
    """
    logger.info(f"BrowserAgent: Searching and opening top result for: {query}")
    try:
        from selenium import webdriver
        from selenium.webdriver.common.by import By
        from selenium.webdriver.chrome.service import Service as ChromeService
        from webdriver_manager.chrome import ChromeDriverManager
        from selenium.webdriver.common.keys import Keys
        import os
    except ImportError:
        logger.error("BrowserAgent: Selenium or webdriver_manager not installed.")
        return False

    try:
        options = webdriver.ChromeOptions()
        chrome_paths = [
            r"C:\Program Files\Google\Chrome\Application\chrome.exe",
            r"C:\Program Files (x86)\Google\Chrome\Application\chrome.exe",
            os.path.expanduser(r"~\AppData\Local\Google\Chrome\Application\chrome.exe")
        ]
        for path in chrome_paths:
            if os.path.exists(path):
                options.binary_location = path
                break

        driver = webdriver.Chrome(service=ChromeService(ChromeDriverManager().install()), options=options)
        
        # We will use DuckDuckGo as it's cleaner to scrape quickly
        driver.get("https://html.duckduckgo.com/html/")
        time.sleep(1)
        
        search_box = driver.find_element(By.ID, "search_form_input_homepage")
        search_box.send_keys(query)
        search_box.send_keys(Keys.RETURN)
        time.sleep(2)
        
        # Grab first actual result link
        first_link = driver.find_element(By.CSS_SELECTOR, "a.result__url")
        target_url = first_link.get_attribute("href")
        
        logger.info(f"BrowserAgent: Navigating top result -> {target_url}")
        driver.get(target_url)
        time.sleep(2)
        
        # YouTube specific handling for autoplay
        if "youtube.com" in target_url:
            logger.info("BrowserAgent: YouTube detected. Triggering autoplay hook.")
            try:
                # Press 'k' (standard YT play shortcut) or wait for autoplay
                body = driver.find_element(By.TAG_NAME, "body")
                body.send_keys("k") 
            except Exception:
                pass
                
        return True
    except Exception as e:
        logger.error(f"BrowserAgent: Failed to open first result: {e}")
        return False
