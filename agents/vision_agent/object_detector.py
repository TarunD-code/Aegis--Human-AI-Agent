"""
Aegis v6.2 — Vision Object Detector
===================================
Uses YOLOv8 to detect UI elements on the screen.
Extracts bounding boxes, confidence scores, and class labels.
"""

import logging
import numpy as np

try:
    from ultralytics import YOLO
except ImportError:
    YOLO = None
    logging.getLogger(__name__).warning("ultralytics not installed. Vision Object Detector disabled.")

logger = logging.getLogger(__name__)

class UIObjectDetector:
    def __init__(self, model_path: str = "yolov8n.pt"):
        """
        Loads the YOLO detection model lazily.
        """
        self.model_path = model_path
        self.model = None
        self.loaded = False

    def load_weights(self) -> bool:
        """Actually load the YOLO model weights into memory."""
        if self.loaded: return True
        if YOLO is None:
            logger.error("ObjectDetector: ultralytics not installed. Cannot load weights.")
            return False
            
        try:
            logger.info(f"ObjectDetector: Loading model from {self.model_path}")
            self.model = YOLO(self.model_path)
            self.loaded = True
            return True
        except Exception as e:
            logger.error(f"ObjectDetector: Failed to load model: {e}")
            return False

    def detect_ui_elements(self, image: np.ndarray) -> list[dict]:
        """
        Analyzes an OpenCV image array and returns detected UI elements.
        Format: [{'label': 'button', 'confidence': 0.95, 'box': (x1, y1, x2, y2)}]
        """
        if not self.loaded:
            if not self.load_weights():
                return []

        if image is None:
            return []

        try:
            results = self.model(image, verbose=False)
            elements = []
            
            for r in results:
                boxes = r.boxes
                for box in boxes:
                    x1, y1, x2, y2 = box.xyxy[0].cpu().numpy()
                    conf = float(box.conf[0].cpu().numpy())
                    cls_id = int(box.cls[0].cpu().numpy())
                    label = self.model.names[cls_id]
                    
                    elements.append({
                        "label": label,
                        "confidence": conf,
                        "box": (int(x1), int(y1), int(x2), int(y2)),
                        "center": (int((x1+x2)/2), int((y1+y2)/2))
                    })
            
            return elements
        except Exception as e:
            logger.error(f"UI Object Detection failed: {e}")
            return []

# Singleton instance
detector = UIObjectDetector()
