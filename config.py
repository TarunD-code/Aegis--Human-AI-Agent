"""
Aegis v4.0 — Central Configuration Module
==========================================
Loads environment variables and defines system-wide constants
including blocked folders, action whitelist, log paths, memory
DB path, and AI prompts.
"""

import os
from pathlib import Path
from dotenv import load_dotenv

# ---------------------------------------------------------------------------
# Environment
# ---------------------------------------------------------------------------
load_dotenv()

GROQ_API_KEY: str = os.getenv("GROQ_API_KEY", "")
TELEGRAM_BOT_TOKEN: str = os.getenv("TELEGRAM_BOT_TOKEN", "")
TELEGRAM_AUTHORIZED_USER_ID: str = os.getenv("TELEGRAM_AUTHORIZED_USER_ID", "")

# ---------------------------------------------------------------------------
# Paths
# ---------------------------------------------------------------------------
BASE_DIR: Path = Path(__file__).resolve().parent
LOG_DIR: Path = BASE_DIR / "logs" / "data"
MEMORY_DB_PATH: Path = BASE_DIR / "memory" / "aegis_memory.db"
APP_REGISTRY_PATH: Path = BASE_DIR / "core" / "app_registry.json"

AEGIS_VERSION: str = "v7.0.0"

# ---------------------------------------------------------------------------
# Action Parameter Schemas (v4.0 Enforcement)
# ---------------------------------------------------------------------------
ACTION_PARAMETER_SCHEMAS: dict[str, list[str]] = {
    "open_application": ["application_name"],
    "focus_application": ["application_name"],
    "type_text": ["text"],
    "press_key": ["key"],
    "hotkey": ["keys"],
    "click": ["x", "y"],
    "scroll": ["amount"],
    "knowledge_lookup": ["query"],
    "search_online": ["query"],
    "search_web": ["query"],
    "open_url": ["url"],
    "browse_to": ["query"],
    "open_new_tab": ["url"],
    "navigate_tab": ["direction"],
    "store_knowledge": ["topic", "summary"],
    "summarize_page": [],
    "extract_page_text": [],
    "open_first_result": [],
    "list_running_apps": [],
    "switch_application": ["application_name"],
    "close_application": ["application_name"],
    "respond_text": ["text"],
    # v7.0 Cognitive Agent
    "vision_click": ["target"],
    "vision_scroll": ["direction"],
    "vision_read": [],
    "vision_locate": ["element"],
    "capture_screenshot": [],
    "ask_confirmation": ["summary"],
    "play_music": ["song"],
    "move_relative": ["direction", "pixels"],
    "compute_result": ["expression"],
}

# Legacy -> Canonical mapping
CANONICAL_PARAM_FALLBACKS: dict[str, str] = {
    "value": "application_name"
}

# ---------------------------------------------------------------------------
# Security — Action Whitelist
# ---------------------------------------------------------------------------
ACTION_WHITELIST: set[str] = {
    "ask_confirmation",
    "browse_to",
    "capture_screenshot",
    "click",
    "close_application",
    "compute_result",
    "create_file",
    "extract_page_text",
    "focus_application",
    "get_running_processes",
    "hotkey",
    "knowledge_lookup",
    "launch_application",
    "list_duplicates",
    "list_running_apps",
    "move_files",
    "move_mouse",
    "move_relative",
    "navigate_tab",
    "open_application",
    "open_first_result",
    "open_new_tab",
    "open_url",
    "organize_email",
    "organize_files",
    "play_music",
    "press_key",
    "prompt_next_action",
    "rename_file",
    "respond_text",
    "run_powershell",
    "scan_directory",
    "scroll",
    "search_online",
    "search_web",
    "store_knowledge",
    "summarize_page",
    "summarize_text",
    "switch_application",
    "system_stats",
    "type_text",
    "undo_last_action",
    "vision_click",
    "vision_locate",
    "vision_read",
    "vision_scroll",
    "wait",
}

# Aegis v5.5: Action Aliases for backward compatibility
ACTION_ALIASES: dict[str, str] = {
    "launch_application": "open_application",
    "start_application": "open_application",
    "run_application": "open_application",
    "execute_command": "run_powershell",
    "browse": "browse_to",
    # v7.0 Cognitive Agent aliases
    "screenshot": "capture_screenshot",
    "confirm": "ask_confirmation",
    "take_screenshot": "capture_screenshot",
    "screen_click": "vision_click",
    "screen_read": "vision_read",
}

ALLOWED_ACTIONS = ACTION_WHITELIST

def get_action_list() -> list[str]:
    """Returns a sorted list of allowed actions for the planner."""
    return sorted(list(ALLOWED_ACTIONS))

# ---------------------------------------------------------------------------
# Security — Blocked System Folders
# ---------------------------------------------------------------------------
BLOCKED_FOLDERS: list[str] = [
    r"C:\Windows",
    r"C:\Program Files",
    r"C:\Program Files (x86)",
    "System Volume Information",
]

# ---------------------------------------------------------------------------
# Security — Whitelisted PowerShell Commands
# ---------------------------------------------------------------------------
WHITELISTED_PS_COMMANDS: list[str] = [
    "Get-Process",
    "Get-ChildItem",
    "Get-Service",
    "Get-Date",
    "Get-ComputerInfo",
    "Get-Disk",
    "Get-Volume",
    "Get-NetIPAddress",
    "Get-EventLog",
    "Test-Connection",
    "Get-Content",
    "Measure-Object",
    "Select-Object",
    "Where-Object",
    "Sort-Object",
    "Format-Table",
    "Format-List",
    "Out-String",
]

# ---------------------------------------------------------------------------
# Background Mode — Hotkey
# ---------------------------------------------------------------------------
WAKE_HOTKEY: str = "ctrl+alt+a"

MAGIC_KEYBOARD_MODE: bool = True
ENABLE_UI_AUTOMATION: bool = True

# ---------------------------------------------------------------------------
# AI — Propmts
# ---------------------------------------------------------------------------
GROQ_MODEL: str = os.getenv("GROQ_MODEL", "llama-3.3-70b-versatile")
LLM_URL: str = os.getenv("LLM_URL", "")

SYSTEM_PROMPT: str = """You are Aegis v7.0, a cognitive AI agent for Windows.
You must return only JSON representing an action plan with thought/reflect reasoning.
"""

# AI — Contextual System Prompt for Groq (v7.0 Cognitive Agent)
_ACTIONS_STR = "\n".join([f"- {a}" for a in get_action_list()])

CONTEXTUAL_SYSTEM_PROMPT: str = f"""You are the Cognitive Planning Engine of Aegis v7.0 Desktop Operating Intelligence.
You have direct control over a Windows system with perception (vision), memory, reasoning, and action subsystems.

[STRICT EXECUTION CONTRACT]
Registered actions:
{_ACTIONS_STR}

STRICT RULES:
1. Return valid JSON with EXACTLY this structure:
{{
  "summary": "...",
  "reasoning": "...",
  "actions": [
    {{
      "thought": "I need to open the application first before typing.",
      "type": "open_application",
      "params": {{"application_name": "notepad"}},
      "description": "Launch Notepad",
      "risk_level": "LOW"
    }},
    {{
      "thought": "Now I will type the requested text into the open application.",
      "type": "type_text",
      "params": {{"text": "Hello World"}},
      "description": "Type greeting",
      "risk_level": "LOW",
      "reflect": "Verify the text appears in the window."
    }}
  ],
  "requires_approval": true
}}

2. COGNITIVE FIELDS (mandatory for complex tasks):
   - `thought`: Your reasoning BEFORE executing the action. Why is this action needed?
   - `reflect`: Your verification AFTER execution. How to confirm success?
   - Both fields help the execution engine make intelligent retry decisions.

3. MANDATORY PARAMETERS:
   - `open_application`: {{"application_name": "..."}}
   - `focus_application`: {{"application_name": "..."}}
   - `type_text`: {{"text": "...", "application_name": "..."}}
   - `press_key`: {{"key": "..."}}
   - `search_web` / `search_online`: {{"query": "..."}}
   - `store_knowledge`: {{"topic": "...", "summary": "..."}}
   - `respond_text`: {{"text": "..."}}  <-- USE THIS FOR ALL DIRECT REPLIES
   - `compute_result`: {{"expression": "..."}}
   - `vision_click`: {{"target": "..."}}  <-- Click a visual UI element by text or class
   - `vision_read`: {{}}  <-- Read text from the screen region
   - `vision_locate`: {{"element": "..."}}  <-- Find element coordinates
   - `capture_screenshot`: {{}}  <-- Save a screenshot to disk
   - `ask_confirmation`: {{"summary": "..."}}  <-- Pause for user approval

4. REAL-WORLD AUTOMATION PATTERNS:
   - Direct Communication: ALWAYS use `respond_text` for user replies.
   - TERMINAL SAFETY: NEVER target terminals with `type_text`.
   - Direct Browser Search: Use `search_web` ({{"query": "..."}}).
   - RESEARCH FLOW: `search_web` -> `extract_page_text` -> `summarize_page`.
   - Opening URLs: Use `open_url` or `browse_to`.
   - Vision UI: Use `vision_click` to click buttons/icons by their visible text.

5. SAFETY & CONFIRMATION:
   - "delete", "format", "shutdown" -> HIGH/CRITICAL risk.
   - ALL HIGH/CRITICAL actions MUST include `ask_confirmation` BEFORE the dangerous action.
   - Never report success yourself; the Execution Engine verifies it.

6. MULTI-STEP AUTONOMOUS PLANNING:
   - Break complex objectives into logical sequences.
   - Use `browse_to` -> `wait` -> `vision_click` for web interactions.
   - For file management, chain `scan_directory` -> `move_files`.
   - For music: `search_web` -> `open_first_result` -> `vision_click` play button.
   - Maximize autonomy while maintaining security.
"""

# ---------------------------------------------------------------------------
# Jarvis v5.4 — System Configuration
# ---------------------------------------------------------------------------
class SystemConfig:
    MAX_RETRIES = 3
    RETRY_DELAY = 1.0
    WINDOW_TRACKING_ENABLED = True
    FUZZY_NORMALIZER_ENABLED = True
    USER_MEMORY_ENABLED = True
    CONTEXT_BUFFER_SIZE = 10  # Last N actions kept in working memory
    VERSION = "7.0.0"
