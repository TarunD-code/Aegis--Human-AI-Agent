"""
Aegis v7.0 — Vision Agent Entry Point
====================================
Implements lazy-loading pattern for the Vision Hub to prevent
heavy model initialization at system boot.
"""

import logging
from typing import Optional

logger = logging.getLogger(__name__)

class VisionAgentProxy:
    """Proxy that defers loading of heavy Vision modules."""
    
    def __init__(self):
        self._hub = None
        self._enabled = True
        self._model_loaded = False

    @property
    def hub(self):
        """Lazy-load the real vision_hub when accessed."""
        if self._hub is None:
            if not self._enabled:
                raise RuntimeError("Vision features are disabled due to missing dependencies.")
            try:
                from agents.vision_agent.vision_controller import vision_hub
                self._hub = vision_hub
                logger.info("VisionAgent: vision_hub successfully initialized.")
            except Exception as e:
                self._enabled = False
                logger.error(f"VisionAgent: Failed to initialize vision_hub: {e}")
                raise
        return self._hub

    def load(self) -> bool:
        """
        Explicitly trigger model loading (YOLO weights).
        Call this before vision-heavy tasks.
        """
        try:
            hub = self.hub
            # Assuming vision_controller or sub-modules have a load method
            # Example: from agents.vision_agent.object_detector import detector; detector.load()
            from agents.vision_agent.object_detector import detector
            if detector.load_weights():
                self._model_loaded = True
                logger.info("VisionAgent: YOLO model weights loaded successfully.")
                return True
        except Exception as e:
            logger.error(f"VisionAgent: Model loading failed: {e}")
            return False
        return False

    def status(self) -> dict:
        """Return the current state of the Vision Agent."""
        return {
            "enabled": self._enabled,
            "model_loaded": self._model_loaded,
            "initialized": self._hub is not None
        }

# Global Proxy
vision_agent = VisionAgentProxy()
