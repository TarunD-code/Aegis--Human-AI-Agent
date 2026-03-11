"""
Aegis v5.6 — Application Registry Scanner
==========================================
Scans Windows Registry for installed software inventory.
"""

import winreg
import logging
from typing import List

logger = logging.getLogger(__name__)

def scan_installed_applications() -> List[str]:
    """
    Scans HKLM and HKCU Uninstall keys for application names.
    Note: Returns display names from the registry.
    """
    found_apps = set()
    
    reg_paths = [
        (winreg.HKEY_LOCAL_MACHINE, r"SOFTWARE\Microsoft\Windows\CurrentVersion\Uninstall"),
        (winreg.HKEY_LOCAL_MACHINE, r"SOFTWARE\WOW6432Node\Microsoft\Windows\CurrentVersion\Uninstall"),
        (winreg.HKEY_CURRENT_USER, r"SOFTWARE\Microsoft\Windows\CurrentVersion\Uninstall")
    ]
    
    for hive, path in reg_paths:
        try:
            with winreg.OpenKey(hive, path) as key:
                for i in range(winreg.QueryInfoKey(key)[0]):
                    try:
                        subkey_name = winreg.EnumKey(key, i)
                        with winreg.OpenKey(key, subkey_name) as subkey:
                            try:
                                name, _ = winreg.QueryValueEx(subkey, "DisplayName")
                                if name:
                                    found_apps.add(str(name).strip())
                            except OSError:
                                continue
                    except OSError:
                        continue
        except OSError:
            continue
            
    return sorted(list(found_apps))
