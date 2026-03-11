"""
Aegis v6.2 — Vision Text Detector
=================================
Uses PyTesseract to extract visible text and their coordinates 
from screen captures.
"""

import logging
import numpy as np

try:
    import pytesseract
except ImportError:
    pytesseract = None
    logging.getLogger(__name__).warning("pytesseract not installed. Vision Text Detector disabled.")

logger = logging.getLogger(__name__)

class VisionTextDetector:
    def __init__(self):
        """
        Initializes OCR. 
        Note: Tesseract executable must be installed on the host system 
        and added to PATH, or configured explicitly.
        """
        self.available = pytesseract is not None
        
    def extract_text(self, image: np.ndarray) -> list[dict]:
        """
        Extracts words and their bounding boxes from an image.
        Returns: [{'text': 'Login', 'box': (x1, y1, x2, y2), 'center': (x, y)}]
        """
        if not self.available or image is None:
            return []

        try:
            # Pytesseract expects RGB
            import cv2
            img_rgb = cv2.cvtColor(image, cv2.COLOR_BGR2RGB) if hasattr(cv2, 'COLOR_BGR2RGB') else cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
            
            data = pytesseract.image_to_data(img_rgb, output_type=pytesseract.Output.DICT)
            
            texts = []
            n_boxes = len(data['level'])
            for i in range(n_boxes):
                text = data['text'][i].strip()
                if text: # Skip empty results
                    x, y, w, h = data['left'][i], data['top'][i], data['width'][i], data['height'][i]
                    texts.append({
                        "text": text,
                        "box": (x, y, x + w, y + h),
                        "center": (int(x + w/2), int(y + h/2))
                    })
            return texts
        except Exception as e:
            logger.error(f"Text detection failed: {e}")
            return []
            
# Singleton
text_detector = VisionTextDetector()
