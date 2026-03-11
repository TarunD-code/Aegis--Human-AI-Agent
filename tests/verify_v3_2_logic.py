import sys
from pathlib import Path
from datetime import datetime, timezone
import json

# Ensure project root is importable
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from memory.memory_manager import MemoryManager
from interfaces.cli import AegisCLI
from brain.planner import Action

def test_v3_2_undo_and_categories():
    print("Testing Aegis v3.2 Ultimate Core Logic...")
    
    # Setup
    mem = MemoryManager(db_path="tmp_v3_2_verify.db")
    cli = AegisCLI(memory=mem)
    
    # 1. Test Categorization
    print("\n[1] Testing Categorization...")
    cli._session.last_app = "Notepad"
    mem.store_action_event("Notepad", "type_text", "Hello", "Success")
    
    history = mem.get_daily_history(datetime.now().strftime("%Y-%m-%d"), app="Notepad")
    assert history[0]["app_category"] == "Editor"
    print("OK: Notepad auto-tagged as Editor.")

    # 2. Test Undo
    print("\n[2] Testing Undo...")
    cli._session.last_result = "100"
    
    # Simulate an action that changes state
    action1 = Action(type="compute_result", value="100 + 50", use_last_result=True)
    # We need to manually execute the resolution part to simulate CLI loop
    cli._session.record_execution({"type": "compute_result"}, {"last_result": "100"})
    cli._session.last_result = "150"
    
    print(f"Current result: {cli._session.last_result}")
    
    # Simulate Undo
    undo_action = Action(type="undo_last_action", value="", description="Undo")
    # Manually trigger the undo logic from CLI
    last_exec = cli._session.pop_last_execution()
    if last_exec:
        cli._session.last_result = last_exec["state_before"].get("last_result")
    
    print(f"Result after undo: {cli._session.last_result}")
    assert cli._session.last_result == "100"
    print("OK: Undo reverted last_result successfully.")

    print("\nAll core v3.2 Ultimate logic verified!")

if __name__ == "__main__":
    try:
        test_v3_2_undo_and_categories()
    except Exception as e:
        print(f"Test Failed: {e}")
        sys.exit(1)
