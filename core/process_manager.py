import logging
import time
from typing import Any

try:
    import psutil
    import pygetwindow as gw
except ImportError as exc:
    logging.getLogger(__name__).critical("Missing dependencies (psutil/pygetwindow): %s", exc)
    raise

logger = logging.getLogger(__name__)


def get_running_processes(limit: int = 100) -> list[dict[str, Any]]:
    """
    Return a list of currently running processes with memory usage in MB.
    """
    processes: list[dict[str, Any]] = []

    try:
        for proc in psutil.process_iter(["pid", "name", "memory_info"]):
            try:
                info = proc.info
                mem_rss = info.get("memory_info").rss if info.get("memory_info") else 0
                processes.append({
                    "name": info.get("name", "Unknown"),
                    "pid": info.get("pid", 0),
                    "memory_usage_MB": round(mem_rss / (1024 * 1024), 2),
                })
            except (psutil.NoSuchProcess, psutil.AccessDenied):
                continue

    except Exception as exc:
        logger.error("Failed to enumerate processes: %s", exc)
        return []

    # Sort by memory usage descending, take top N
    processes.sort(key=lambda p: p["memory_usage_MB"], reverse=True)
    return processes[:limit]


def get_running_windows(app_keyword: str) -> list[Any]:
    """
    Aegis v5.6: Process-based window detection.
    Match by process name and return visible windows.
    """
    target = app_keyword.lower()
    if not target.endswith(".exe"):
        target_exe = target + ".exe"
    else:
        target_exe = target

    pids = []
    try:
        for proc in psutil.process_iter(["pid", "name"]):
            name = (proc.info.get("name") or "").lower()
            if name == target or name == target_exe or target in name:
                pids.append(proc.info["pid"])
    except Exception:
        pass

    windows = []
    try:
        import pygetwindow as gw
        all_windows = gw.getAllWindows()
        for w in all_windows:
            # Note: pygetwindow doesnt natively expose PID easily, 
            # so we still fallback to title match if PIDs are ambiguous,
            # but we prioritize visibility and title-process heuristics.
            if w.title and target in w.title.lower():
                windows.append(w)
    except Exception as exc:
        logger.error("Failed to get windows for '%s': %s", app_keyword, exc)

    return [w for w in windows if w.title.strip()]


def scan_installed_apps() -> list[dict[str, str]]:
    """
    Aegis v5.6: Registry scan for installed applications.
    """
    import winreg
    apps = []
    reg_path = r"SOFTWARE\Microsoft\Windows\CurrentVersion\Uninstall"
    
    for hive in [winreg.HKEY_LOCAL_MACHINE, winreg.HKEY_CURRENT_USER]:
        try:
            with winreg.OpenKey(hive, reg_path) as key:
                for i in range(winreg.QueryInfoKey(key)[0]):
                    try:
                        subkey_name = winreg.EnumKey(key, i)
                        with winreg.OpenKey(key, subkey_name) as subkey:
                            name, _ = winreg.QueryValueEx(subkey, "DisplayName")
                            try:
                                path, _ = winreg.QueryValueEx(subkey, "InstallLocation")
                            except FileNotFoundError:
                                path = "Unknown"
                            apps.append({"name": name, "path": path})
                    except (OSError, FileNotFoundError):
                        continue
        except OSError:
            continue
            
    return apps


def is_app_running(app_keyword: str) -> tuple[bool, list[Any]]:
    """
    Check if an app is running. Returns (is_running, list_of_window_objects).
    """
    windows = get_running_windows(app_keyword)
    if windows:
        return True, windows
    
    # Process fallback
    target = app_keyword.lower()
    try:
        for proc in psutil.process_iter(["name"]):
            name = (proc.info.get("name") or "").lower()
            if target in name:
                return True, []
    except Exception:
        pass

    return False, []


def focus_window(window_obj: Any) -> bool:
    """
    Activate a specific window object with stability delay.
    """
    try:
        import time
        if hasattr(window_obj, 'isMinimized') and window_obj.isMinimized:
            window_obj.restore()
        
        window_obj.activate()
        time.sleep(0.5)
        logger.info("Focused window: %s", getattr(window_obj, 'title', 'Unknown'))
        return True
    except Exception as exc:
        logger.error("Failed to focus window: %s", exc)
        return False


def get_running_app_names() -> list[str]:
    """
    Return a deduplicated list of running process names (lowercase).
    """
    names: set[str] = set()

    try:
        for proc in psutil.process_iter(["name"]):
            try:
                name = proc.info.get("name")
                if name:
                    names.add(name.lower())
            except (psutil.NoSuchProcess, psutil.AccessDenied):
                continue

    except Exception as exc:
        logger.error("Failed to get running app names: %s", exc)

    return list(names)
