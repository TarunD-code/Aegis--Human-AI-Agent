"""
Aegis v6.3 — Application Scanner
=================================
Scans common Windows installation directories and registry
to discover installed applications and resolve executable paths.
"""

import os
import logging
from typing import Optional

logger = logging.getLogger(__name__)

class ApplicationScanner:
    """Discovers installed applications by scanning known directories."""

    SEARCH_DIRS = [
        os.environ.get("ProgramFiles", r"C:\Program Files"),
        os.environ.get("ProgramFiles(x86)", r"C:\Program Files (x86)"),
        os.path.join(os.environ.get("LOCALAPPDATA", ""), "Programs"),
        os.path.join(os.environ.get("APPDATA", ""), "Microsoft", "Windows", "Start Menu", "Programs"),
    ]

    # Well-known application mappings
    KNOWN_APPS = {
        "calculator": "calc.exe",
        "calc": "calc.exe",
        "notepad": "notepad.exe",
        "paint": "mspaint.exe",
        "explorer": "explorer.exe",
        "file explorer": "explorer.exe",
        "cmd": "cmd.exe",
        "command prompt": "cmd.exe",
        "powershell": "powershell.exe",
        "task manager": "taskmgr.exe",
        "control panel": "control.exe",
        "settings": "ms-settings:",
        "edge": "msedge.exe",
        "microsoft edge": "msedge.exe",
        "chrome": r"C:\Program Files\Google\Chrome\Application\chrome.exe",
        "google chrome": r"C:\Program Files\Google\Chrome\Application\chrome.exe",
        "firefox": "firefox.exe",
        "word": "WINWORD.EXE",
        "microsoft word": "WINWORD.EXE",
        "excel": "EXCEL.EXE",
        "powerpoint": "POWERPNT.EXE",
        "outlook": "OUTLOOK.EXE",
        "onenote": "ONENOTE.EXE",
        "code": "code",
        "vscode": "code",
        "visual studio code": "code",
        "vlc": "vlc.exe",
        "figma": "Figma.exe",
        "spotify": "Spotify.exe",
    }

    def __init__(self):
        self._cache: dict[str, str] = {}

    def scan_installed_apps(self) -> list[str]:
        """Scan directories for .exe files and return discovered app names."""
        found = []
        for search_dir in self.SEARCH_DIRS:
            if not os.path.exists(search_dir):
                continue
            try:
                for root, dirs, files in os.walk(search_dir):
                    for f in files:
                        if f.lower().endswith(".exe"):
                            full = os.path.join(root, f)
                            name = f.replace(".exe", "").lower()
                            self._cache[name] = full
                            found.append(f)
                    # Limit depth to 3 for speed
                    depth = root.replace(search_dir, "").count(os.sep)
                    if depth >= 3:
                        dirs.clear()
            except PermissionError:
                continue
        logger.info(f"ApplicationScanner: Discovered {len(found)} executables.")
        return found

    def resolve_application_path(self, name: str) -> Optional[str]:
        """Resolve a logical application name to its executable path."""
        name_lower = name.lower().strip()

        # 1. Check known apps first
        if name_lower in self.KNOWN_APPS:
            return self.KNOWN_APPS[name_lower]

        # 2. Check scan cache
        if name_lower in self._cache:
            return self._cache[name_lower]

        # 3. Fuzzy match against cache
        try:
            from rapidfuzz import fuzz
            best_match = None
            best_score = 0
            for cached_name, cached_path in self._cache.items():
                score = fuzz.ratio(name_lower, cached_name)
                if score > best_score and score > 70:
                    best_score = score
                    best_match = cached_path
            if best_match:
                return best_match
        except ImportError:
            pass

        # 4. Return the name itself as fallback
        return name

# Singleton
app_scanner = ApplicationScanner()
