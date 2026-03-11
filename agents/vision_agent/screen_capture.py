"""
Aegis v6.2 — Screen Capture Module
==================================
Captures real-time screenshots using MSS for visual AI analysis.
Limits capture intervals to prevent extreme CPU consumption.
"""

import time
import logging
import numpy as np
import cv2

try:
    import mss
except ImportError:
    mss = None
    logging.getLogger(__name__).warning("mss not installed. Screen capture disabled.")

logger = logging.getLogger(__name__)

class ScreenCapture:
    def __init__(self, capture_delay: float = 0.5):
        self.capture_delay = capture_delay
        self.last_capture_time = 0.0
        self.sct = mss.mss() if mss else None

    def capture_full_screen(self) -> np.ndarray | None:
        """Captures the primary monitor and returns an OpenCV image."""
        if not self.sct:
            logger.error("ScreenCapture: MSS is missing.")
            return None

        # Rate limiting logic
        current_time = time.time()
        if (current_time - self.last_capture_time) < self.capture_delay:
            time.sleep(self.capture_delay - (current_time - self.last_capture_time))

        try:
            # Monitor 1 is the primary monitor
            monitor = self.sct.monitors[1]
            sct_img = self.sct.grab(monitor)
            
            # Convert to numpy array
            img = np.array(sct_img)
            
            # MSS returns BGRA. Convert to BGR for OpenCV standard.
            img_bgr = cv2.cvtColor(img, cv2.COLOR_BGRA@BGR) if hasattr(cv2, 'COLOR_BGRA2BGR') else cv2.cvtColor(img, cv2.COLOR_BGRA2BGR)
            
            self.last_capture_time = time.time()
            return img_bgr

        except Exception as e:
            logger.error(f"Failed to capture full screen: {e}")
            return None

    def capture_region(self, x: int, y: int, width: int, height: int) -> np.ndarray | None:
        """Captures a specific quadrant of the screen."""
        if not self.sct:
            return None

        current_time = time.time()
        if (current_time - self.last_capture_time) < self.capture_delay:
            time.sleep(self.capture_delay - (current_time - self.last_capture_time))

        try:
            bbox = {'top': y, 'left': x, 'width': width, 'height': height}
            sct_img = self.sct.grab(bbox)
            
            img = np.array(sct_img)
            img_bgr = cv2.cvtColor(img, cv2.COLOR_BGRA2BGR)
            
            self.last_capture_time = time.time()
            return img_bgr
            
        except Exception as e:
            logger.error(f"Failed to capture region ({x},{y},{width},{height}): {e}")
            return None

# Singleton
capturer = ScreenCapture()
