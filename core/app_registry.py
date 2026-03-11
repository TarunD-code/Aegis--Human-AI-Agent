"""
Aegis v5.6 — Application Registry
===================================
Scans the Windows Registry to discover installed applications.
"""

import winreg
import logging
from typing import List

logger = logging.getLogger(__name__)

class ApplicationRegistry:
    """
    Aegis v5.6 — Centralized Application Registry.
    Manages lookup and resolution of application names to execution paths.
    """
    def __init__(self):
        self._cache = {}
        self._aliases = {
            "notepad": "notepad.exe",
            "chrome": "chrome.exe",
            "calculator": "calc.exe",
            "calc": "calc.exe",
            "word": "winword.exe",
            "excel": "excel.exe",
            "powerpoint": "powerpnt.exe",
            "outlook": "outlook.exe"
        }

    def search(self, query: str) -> List[dict]:
        """
        v7.0: Fuzzy search for installed applications.
        Returns [{'name': str, 'path': str, 'score': float}]
        """
        from rapidfuzz import process, fuzz
        
        # 1. Gather all unique names from cache/aliases/scans
        all_apps = {} # name -> path
        
        # Add aliases
        for alias, exe in self._aliases.items():
            all_apps[alias] = exe
            
        # Scan Registry & Shortcuts (via existing Scanner)
        try:
            from core.app_registry_scanner import scan_installed_applications
            scanned = scan_installed_applications() # Returns paths or names
            for path in scanned:
                name = path.split("\\")[-1].replace(".exe", "").replace(".lnk", "").lower()
                all_apps[name] = path
        except Exception as e:
            logger.warning(f"AppRegistry: Scanner failed: {e}")

        # 2. Extract best matches
        names = list(all_apps.keys())
        matches = process.extract(query.lower(), names, scorer=fuzz.WRatio, limit=5)
        
        results = []
        for match_name, score, _ in matches:
            results.append({
                "name": match_name,
                "path": all_apps[match_name],
                "score": score
            })
            
        return sorted(results, key=lambda x: x['score'], reverse=True)

    def resolve(self, app_name: str) -> str:
        """
        Aegis v7.0: Enhanced resolution using fuzzy search.
        """
        name_lower = app_name.lower().strip()
        
        # 1. Exact Alias Match
        if name_lower in self._aliases:
            return self._aliases[name_lower]
            
        # 2. Fuzzy Match
        matches = self.search(name_lower)
        if matches and matches[0]['score'] >= 90:
            return matches[0]['path']
                
        # 3. Fallback
        return app_name

# Singleton instance for system-wide use
registry = ApplicationRegistry()

def get_installed_applications() -> List[str]:
    """Compatibility wrapper for Aegis v5.5 logic."""
    from core.app_registry_scanner import scan_installed_applications
    return scan_installed_applications()

if __name__ == "__main__":
    # Quick test
    print(f"Discovered {len(get_installed_applications())} applications.")
