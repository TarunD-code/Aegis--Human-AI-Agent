"""
Aegis v7.0 — Vision Controller
==============================
Central orchestration hub for the Aegis Vision Agent.
Combines Screen Capturing, Object Detection, Text Detection, 
and UI Interacting into high-level automated functions.
"""

import os
import time
import logging
from typing import Optional, Dict, List, Tuple
from datetime import datetime

from agents.vision_agent.screen_capture import capturer
from agents.vision_agent.object_detector import detector
from agents.vision_agent.text_detector import text_detector
from agents.vision_agent.ui_interactor import interactor

logger = logging.getLogger(__name__)

class VisionHub:
    """Orchestrates the visual AI loops for GUI interaction."""
    
    def __init__(self):
        self.vision_enabled = True
        self.initialized = False

    def load(self) -> bool:
        """Lazy load heavy models."""
        if self.initialized: return True
        try:
            from agents.vision_agent.object_detector import detector
            if hasattr(detector, 'load_weights'):
                detector.load_weights()
            self.initialized = True
            return True
        except Exception as e:
            logger.error(f"VisionHub: Failed to load models: {e}")
            self.vision_enabled = False
            return False

    def find_on_screen(self, element: str) -> Optional[Tuple[int, int]]:
        """Implementation of user-requested find_on_screen."""
        if not self.load(): return None
        return self.vision_locate(element)

    def click_element_by_class(self, target_class: str, target_area: Optional[str] = None, max_retries: int = 3) -> bool:
        """Implementation of user-requested click_element_by_class."""
        if not self.load(): return False
        return self._click_by_class(target_class, target_area, max_retries)

    def _click_by_class(self, target_class: str, target_area: Optional[str] = None, max_retries: int = 3) -> bool:
        """Looks for a specific text string on the screen and clicks it."""
        logger.info(f"VisionController: Attempting to click text '{target_text}'")
        target_lower = target_text.lower()
        
        for attempt in range(max_retries):
            img = capturer.capture_full_screen()
            if img is None:
                logger.error("VisionController: Could not capture screen.")
                return False
                
            texts = text_detector.extract_text(img)
            
            for t in texts:
                if target_lower in t['text'].lower() or t['text'].lower() in target_lower:
                    cx, cy = t['center']
                    logger.info(f"VisionController: Found '{target_text}' at ({cx}, {cy}). Clicking.")
                    return interactor.click(cx, cy)
                    
            logger.debug(f"VisionController: '{target_text}' not found. Retry {attempt + 1}/{max_retries}")
            time.sleep(1.0)
            
        logger.warning(f"VisionController: Exhausted retries looking for '{target_text}'")
        return False

    @classmethod
    def click_element_by_class(cls, target_class: str, target_area: Optional[str] = None, max_retries: int = 3) -> bool:
        """Looks for a UI class (e.g., 'button', 'search bar') and clicks it."""
        logger.info(f"VisionController: Attempting to click object '{target_class}'")
        target_lower = target_class.lower()
        
        for attempt in range(max_retries):
            img = capturer.capture_full_screen()
            if img is None:
                return False
                
            elements = detector.detect_ui_elements(img)
            
            best_element = None
            highest_conf = 0.0
            
            for el in elements:
                if target_lower in el['label'].lower() and el['confidence'] > highest_conf:
                    if el['confidence'] > 0.4:
                        best_element = el
                        highest_conf = el['confidence']
                        
            if best_element:
                cx, cy = best_element['center']
                logger.info(f"VisionController: Found '{target_class}' at ({cx}, {cy}). Clicking.")
                return interactor.click(cx, cy)
                
            time.sleep(1.0)
            
        return False
        
    @classmethod
    def scroll_direction(cls, direction: str, amount: int = 500) -> bool:
        """Translates semantic scrolling instructions into actions."""
        if 'up' in direction.lower():
            return interactor.scroll(amount)
        else:
            return interactor.scroll(-amount)

    @classmethod
    def vision_read(cls, region: Optional[Dict] = None) -> str:
        """
        v7.0: Read text from the screen (full or region).
        Returns extracted text string. Stores in working memory.
        """
        logger.info("VisionController: Reading screen text")
        try:
            if region:
                img = capturer.capture_region(
                    region.get("x", 0), region.get("y", 0),
                    region.get("width", 800), region.get("height", 600)
                )
            else:
                img = capturer.capture_full_screen()
            
            if img is None:
                return ""
            
            texts = text_detector.extract_text(img)
            all_text = " ".join([t['text'] for t in texts if t['text'].strip()])
            
            # Store in working memory
            try:
                from core.state import working_memory
                working_memory.set("page_content", all_text[:3000])
            except Exception:
                pass
            
            logger.info(f"VisionController: Read {len(all_text)} chars from screen.")
            return all_text
        except Exception as e:
            logger.error(f"VisionController: vision_read failed: {e}")
            return ""

    @classmethod
    def vision_locate(cls, element: str, max_retries: int = 3) -> Optional[Tuple[int, int]]:
        """
        v7.0: Locate an element on screen by text or class name.
        Returns (x, y) center coordinates or None.
        """
        logger.info(f"VisionController: Locating element '{element}'")
        element_lower = element.lower()
        
        for attempt in range(max_retries):
            img = capturer.capture_full_screen()
            if img is None:
                return None
            
            # Try text detection first
            texts = text_detector.extract_text(img)
            for t in texts:
                if element_lower in t['text'].lower():
                    coords = t['center']
                    logger.info(f"VisionController: Located '{element}' via text at {coords}")
                    return coords
            
            # Try object detection
            elements = detector.detect_ui_elements(img)
            for el in elements:
                if element_lower in el['label'].lower() and el['confidence'] > 0.4:
                    coords = el['center']
                    logger.info(f"VisionController: Located '{element}' via object at {coords}")
                    return coords
            
            time.sleep(0.5)
        
        logger.warning(f"VisionController: Could not locate '{element}'")
        return None

    @classmethod
    def capture_screenshot(cls, filename: str = "") -> str:
        """
        v7.0: Capture a screenshot and save to disk.
        Returns the file path of the saved screenshot.
        """
        logger.info("VisionController: Capturing screenshot")
        try:
            img = capturer.capture_full_screen()
            if img is None:
                return ""
            
            import cv2
            screenshots_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), "logs", "screenshots")
            os.makedirs(screenshots_dir, exist_ok=True)
            
            if not filename:
                filename = f"screenshot_{datetime.now().strftime('%Y%m%d_%H%M%S')}.png"
            
            filepath = os.path.join(screenshots_dir, filename)
            cv2.imwrite(filepath, img)
            logger.info(f"VisionController: Screenshot saved to {filepath}")
            return filepath
        except Exception as e:
            logger.error(f"VisionController: Screenshot failed: {e}")
            return ""

vision_hub = VisionController()
