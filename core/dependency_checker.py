import importlib
import sys
import logging
from config import ENABLE_UI_AUTOMATION

logger = logging.getLogger(__name__)

REQUIRED_MODULES = [
    "pyautogui",
    "pygetwindow",
    "pywinauto",
    "psutil"
]

def check_dependencies() -> None:
    """
    Verify that all required UI automation dependencies are installed.
    Exits if any are missing when ENABLE_UI_AUTOMATION is True.
    """
    if not ENABLE_UI_AUTOMATION:
        logger.info("UI Automation is disabled. Skipping dependency check.")
        return

    missing = []
    for module in REQUIRED_MODULES:
        try:
            importlib.import_module(module)
        except ImportError:
            missing.append(module)

    if missing:
        print("\n" + "!" * 60)
        for mod in missing:
            print(f"  CRITICAL: Missing dependency: {mod}")
        print("  Please run: pip install -r requirements.txt")
        print("!" * 60 + "\n")
        sys.exit(1)

    logger.debug("All UI dependencies verified.")
