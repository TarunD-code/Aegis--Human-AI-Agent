"""
Aegis v3.6 — Startup Environment Diagnostics
============================================
Checks dependencies and environment variables before starting.
"""
import sys
import subprocess
import logging

logger = logging.getLogger(__name__)

CORE_PACKAGES = [
    "colorama", "pybreaker", "backoff", "groq", "psutil", "rapidfuzz"
]

OPTIONAL_PACKAGES = [
    "ultralytics", "torch", "numpy", "cv2", "pyautogui", "pygetwindow", "pywinauto", "mss"
]

def check_dependencies() -> bool:
    """Check if required pip packages are installed in the current environment."""
    missing_core = []
    for pkg in CORE_PACKAGES:
        try:
            __import__(pkg)
        except ImportError:
            missing_core.append(pkg)

    if missing_core:
        print(f"ERROR: Missing CORE dependencies: {', '.join(missing_core)}")
        print("Aegis cannot boot. Please run: pip install " + " ".join(missing_core))
        return False

    missing_opt = []
    for pkg in OPTIONAL_PACKAGES:
        # Import as name if different from package name
        test_pkg = "cv2" if pkg == "opencv-python" else pkg
        try:
            __import__(test_pkg)
        except ImportError:
            missing_opt.append(pkg)
    
    vision_enabled = len(missing_opt) == 0
    if not vision_enabled:
        logger.warning(f"Missing optional/vision dependencies: {', '.join(missing_opt)}")
        logger.warning("Some UI and Vision features will be disabled until these are installed.")
        
    return True, vision_enabled

if __name__ == "__main__":
    if check_dependencies():
        print("Dependency check passed.")
        sys.exit(0)
    else:
        sys.exit(1)
