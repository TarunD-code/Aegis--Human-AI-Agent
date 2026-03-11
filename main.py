"""
Aegis v2.0 — Main Entry Point
===============================
Initializes the Aegis system and launches the selected interface.

Usage:
    python main.py                  # Launch CLI (default)
    python main.py --mode cli
    python main.py --mode background  # Launch background daemon
"""

import argparse
import logging
import sys
import threading
from pathlib import Path

# Ensure the project root is on sys.path
PROJECT_ROOT = Path(__file__).resolve().parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from logs.logger import setup_logging
try:
    from colorama import Fore, Style, init as colorama_init
    COLORAMA_AVAILABLE = True
except ImportError:
    COLORAMA_AVAILABLE = False

def start_health_server():
    """Starts a simple health endpoint server in a background thread."""
    from http.server import HTTPServer, BaseHTTPRequestHandler
    import json
    
    class HealthHandler(BaseHTTPRequestHandler):
        def do_GET(self):
            if self.path == "/health":
                self.send_response(200)
                self.send_header("Content-Type", "application/json")
                self.end_headers()
                # Simplified status check
                try:
                    import os
                    from config import MEMORY_DB_PATH
                    # Verify DB path exists
                    db_ok = os.path.exists(MEMORY_DB_PATH)
                    # Check LLM Mode
                    offline = os.environ.get("AEGIS_OFFLINE_MODE", "false").lower() == "true"
                    llm_status = "offline_mock" if offline else "ready"
                    
                    status = {
                        "status": "ok",
                        "version": "v3.9.0",
                        "db_status": "connected" if db_ok else "not_found",
                        "llm_status": llm_status,
                        "adaptive_tone_enabled": True
                    }
                except Exception as e:
                    status = {"status": "error", "error": str(e)}
                    
                self.wfile.write(json.dumps(status).encode())
            else:
                self.send_response(404)
                self.end_headers()
        def log_message(self, format, *args):
            pass # Silence console logs for health checks

    def run_server():
        try:
            server = HTTPServer(("127.0.0.1", 17123), HealthHandler)
            server.serve_forever()
        except Exception:
            pass

    thread = threading.Thread(target=run_server, daemon=True)
    thread.start()

def main() -> None:
    """Parse arguments and launch Aegis."""
    parser = argparse.ArgumentParser(
        prog="aegis",
        description="Aegis v7.0.0 — Desktop Operating Intelligence",
    )
    parser.add_argument("--mode", choices=["cli", "background"], default="cli")
    parser.add_argument("-v", "--verbose", action="store_true")
    args = parser.parse_args()
    
    setup_logging(verbose=args.verbose)
    if COLORAMA_AVAILABLE:
        colorama_init(autoreset=True)

    logger.info(f"--- Aegis v7.0.0 Booting (Mode: {args.mode}) ---")
    
    from utils.env_check import check_dependencies
    ok, vision_enabled = check_dependencies()
    if not ok:
        logger.error("Aegis failed safe-boot dependency check.")
        sys.exit(1)
        
    if vision_enabled:
        logger.info("Vision Subsystem: ENABLED (YOLOv8 + OCR)")
    else:
        logger.info("Vision Subsystem: DISABLED (Missing optional dependencies)")

    start_health_server()

    if args.mode == "cli":
        from interfaces.cli import AegisCLI
        try:
            cli = AegisCLI()
            cli.run()
        except Exception as e:
            logging.exception("Unhandled error in Aegis REPL")
            err_msg = f"Critical Error: {e}"
            if COLORAMA_AVAILABLE:
                print(f"\n  {Fore.RED}✘ {err_msg}{Style.RESET_ALL}")
            else:
                print(f"\n  ✘ {err_msg}")
            sys.exit(1)
    # ... rest of mode logic ...


if __name__ == "__main__":
    main()
