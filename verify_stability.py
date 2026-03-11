import sqlite3
import os
from memory.memory_manager import MemoryManager
from config import ACTION_WHITELIST, CONTEXTUAL_SYSTEM_PROMPT

def verify_db_migration():
    print("--- Verifying DB Migration ---")
    # Initialize MemoryManager which triggers _ensure_db and migrations
    mm = MemoryManager()
    
    with mm._connect() as conn:
        cursor = conn.cursor()
        cursor.execute("PRAGMA table_info(daily_history)")
        columns = [row[1] for row in cursor.fetchall()]
        
        required = ["app", "app_category", "command", "result"]
        missing = [col for col in required if col not in columns]
        
        if not missing:
            print("✔ All required columns present in daily_history.")
        else:
            print(f"✘ Missing columns in daily_history: {missing}")
    print()

def verify_action_contract():
    print("--- Verifying Action Contract ---")
    expected_actions = {
        "click", "compute_result", "create_file", "focus_application", 
        "get_running_processes", "hotkey", "list_duplicates", "move_files", 
        "move_mouse", "navigate_tab", "open_application", "organize_email", 
        "organize_files", "press_key", "prompt_next_action", "rename_file", 
        "run_powershell", "scan_directory", "search_online", "summarize_text", 
        "type_text", "undo_last_action", "wait"
    }
    
    if ACTION_WHITELIST == expected_actions:
        print("✔ ACTION_WHITELIST matches the execution contract.")
    else:
        print("✘ ACTION_WHITELIST mismatch.")
        print(f"Missing: {expected_actions - ACTION_WHITELIST}")
        print(f"Extra: {ACTION_WHITELIST - expected_actions}")
        
    if "[STRICT EXECUTION CONTRACT]" in CONTEXTUAL_SYSTEM_PROMPT:
        print("✔ CONTEXTUAL_SYSTEM_PROMPT contains strict execution contract rules.")
    else:
        print("✘ CONTEXTUAL_SYSTEM_PROMPT is missing strict execution contract rules.")
    print()

if __name__ == "__main__":
    verify_db_migration()
    verify_action_contract()
