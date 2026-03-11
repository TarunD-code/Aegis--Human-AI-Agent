"""
Aegis v5.0 — Digital Vision Engine
===================================
Inspects the Windows UI tree using the UIA (User Interface Automation) backend.
Provides a native way to "see" and interact with UI elements without OCR.
"""

from __future__ import annotations
import logging
import time
from typing import List, Dict, Optional, Any
import pywinauto
from pywinauto import Desktop

logger = logging.getLogger(__name__)

class UIInspector:
    """
    Analyzes the UI structure of windows to locate and interact with elements.
    """

    def __init__(self, backend: str = "uia"):
        self.backend = backend
        self.desktop = Desktop(backend=backend)

    def find_elements(self, window_title: str, name: Optional[str] = None, control_type: Optional[str] = None) -> List[Any]:
        """
        Locates elements within a specific window matching the criteria.
        """
        try:
            window = self.desktop.window(title_re=f".*{window_title}.*", found_index=0)
            if not window.exists():
                logger.warning(f"Window matching '{window_title}' not found.")
                return []

            search_params = {}
            if name:
                search_params["title"] = name
            if control_type:
                search_params["control_type"] = control_type

            # descendant selection is powerful but can be slow
            elements = window.descendants(**search_params)
            return elements
        except Exception as e:
            logger.error(f"Error finding elements in '{window_title}': {e}")
            return []

    def get_ui_tree(self, window_title: str, depth: int = 2) -> Dict[str, Any]:
        """
        Dumps a simplified representation of the UI tree for the given window.
        Useful for the Planner to understand what's on screen.
        """
        try:
            window = self.desktop.window(title_re=f".*{window_title}.*", found_index=0)
            if not window.exists():
                return {"error": "Window not found"}

            def _parse_element(element, current_depth):
                if current_depth > depth:
                    return None
                
                data = {
                    "name": element.window_text(),
                    "type": element.control_type(),
                    "rectangle": element.rectangle(),
                    "children": []
                }
                
                try:
                    for child in element.children():
                        child_data = _parse_element(child, current_depth + 1)
                        if child_data:
                            data["children"].append(child_data)
                except Exception:
                    pass
                    
                return data

            return _parse_element(window, 0)
        except Exception as e:
            return {"error": str(e)}

    def click_element_by_name(self, window_title: str, element_name: str) -> bool:
        """
        Finds and clicks an element (e.g., a button) by its name.
        """
        elements = self.find_elements(window_title, name=element_name)
        if not elements:
            logger.warning(f"Element '{element_name}' not found in '{window_title}'.")
            return False

        try:
            # Prefer visible elements
            for el in elements:
                if el.is_visible():
                    el.click_input()
                    logger.info(f"Clicked element '{element_name}' in '{window_title}'.")
                    return True
            
            # Fallback to first found
            elements[0].click_input()
            logger.info(f"Clicked first found element '{element_name}' in '{window_title}'.")
            return True
        except Exception as e:
            logger.error(f"Failed to click element '{element_name}': {e}")
            return False

    def get_element_text(self, window_title: str, element_name: str) -> Optional[str]:
        """
        Retrieves the text/value of a specific UI element.
        """
        elements = self.find_elements(window_title, name=element_name)
        if not elements:
            return None

        try:
            return elements[0].window_text()
        except Exception:
            return None
