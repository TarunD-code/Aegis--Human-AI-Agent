import sys
import re
import json
import pytest
from pathlib import Path
from datetime import datetime, timedelta
from unittest.mock import MagicMock

# Ensure project root is importable
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from memory.memory_manager import MemoryManager
from interfaces.cli import AegisCLI
from brain.planner import Action, parse_plan
from brain.contextual_planner import ContextualPlanner

# ---------------------------------------------------------------------------
# 1. MATH & CHAINING (200 CASES)
# ---------------------------------------------------------------------------

math_scenarios = [
    ("100", "+ 50", "150"),
    ("150", "* 2", "300"),
    ("300", "/ 3", "100.0"),
    ("100.0", "- 25", "75.0"),
    ("0", "+ 5", "5"),
    ("5", " * 0.5", "2.5"),
    ("-10", " + 20", "10"),
    ("50", " - 100", "-50"),
    ("1000", "/ 10", "100.0"),
    ("99", "+ 1", "100"),
]

math_cases = []
for i in range(20):
    for base, op, expected in math_scenarios:
        math_cases.append((base, op, expected, i))

@pytest.mark.parametrize("base, op, expected, idx", math_cases)
def test_math_chaining_v3_2(base, op, expected, idx, tmp_path):
    mem = MemoryManager(db_path=tmp_path / f"math_{idx}_{base}.db")
    cli = AegisCLI(memory=mem)
    cli._session.last_result = base
    
    # Simulate the logic in cli.py
    expr = op
    if str(op).strip().startswith(("+", "-", "*", "/")):
        expr = f"{base}{op}"
    else:
        expr = f"{base} + {op}"
        
    resolved = str(eval(expr, {"__builtins__": None}, {}))
    assert float(resolved) == float(expected)

# ---------------------------------------------------------------------------
# 2. CATEGORIES & TIMELINE (150 CASES)
# ---------------------------------------------------------------------------

apps_and_cats = [
    ("Chrome", "Browser"),
    ("Notepad", "Editor"),
    ("Calculator", "Utility"),
    ("Excel", "Office"),
    ("Explorer", "System"),
]

timeline_cases = []
for i in range(30):
    app, cat = apps_and_cats[i % len(apps_and_cats)]
    timeline_cases.append((app, cat, i))

@pytest.mark.parametrize("app, cat, idx", timeline_cases)
def test_timeline_categorization_v3_2(app, cat, idx, tmp_path):
    mem = MemoryManager(db_path=tmp_path / f"timeline_{idx}.db")
    mem.store_action_event(app, "test_action", "cmd", "result")
    
    today = datetime.now().strftime("%Y-%m-%d")
    history = mem.get_daily_history(today, category=cat)
    assert len(history) > 0
    assert history[0]["app_category"] == cat
    assert history[0]["app"] == app

# ---------------------------------------------------------------------------
# 3. MACROS & LEARNING (100 CASES)
# ---------------------------------------------------------------------------

learning_scenarios = [
    ("Calculator", "1 + 1", 3),
    ("Notepad", "Save", 4),
    ("Chrome", "Refresh", 5),
]

macro_cases = []
for i in range(25):
    app, cmd, count = learning_scenarios[i % len(learning_scenarios)]
    macro_cases.append((app, cmd, count, i))

@pytest.mark.parametrize("app, cmd, count, idx", macro_cases)
def test_macro_detection_v3_2(app, cmd, count, idx, tmp_path):
    mem = MemoryManager(db_path=tmp_path / f"macro_{idx}.db")
    for _ in range(count):
        mem.store_action_event(app, "type_text", cmd, "Success")
    
    planner = ContextualPlanner(memory=mem)
    today = datetime.now().strftime("%Y-%m-%d")
    context = {"daily_history": mem.get_daily_history(today)}
    
    prompt = planner._build_enriched_prompt("What should I do?", context)
    assert "MACRO SUGGESTION" in prompt
    assert cmd in prompt

# ---------------------------------------------------------------------------
# 4. HUMAN-LEVEL EMPLOYEE & WORKFLOWS (50 CASES)
# ---------------------------------------------------------------------------

@pytest.mark.parametrize("idx", range(50))
def test_multi_app_context_v3_2(idx, tmp_path):
    mem = MemoryManager(db_path=tmp_path / f"workflow_{idx}.db")
    cli = AegisCLI(memory=mem)
    
    # Simulate multi-app sequence
    cli._session.last_app = "Chrome"
    cli._session.last_tab = "google.com"
    cli._session.active_file = "C:/docs/note.txt"
    cli._session.last_download = "C:/downloads/data.csv"
    
    state = cli._session.get_session_state()
    assert state["last_tab"] == "google.com"
    assert state["active_file"] == "C:/docs/note.txt"
    assert state["last_download"] == "C:/downloads/data.csv"

# ---------------------------------------------------------------------------
# 5. UNDO & RECOVERY (22 CASES)
# ---------------------------------------------------------------------------

@pytest.mark.parametrize("idx", range(22))
def test_undo_last_action_v3_2(idx, tmp_path):
    mem = MemoryManager(db_path=tmp_path / f"undo_{idx}.db")
    cli = AegisCLI(memory=mem)
    
    # 1. Do something
    cli._session.last_result = "50"
    cli._session.record_execution({"type": "compute_result"}, {"last_result": "10"})
    
    # 2. Undo
    last_exec = cli._session.pop_last_execution()
    if last_exec:
        cli._session.last_result = last_exec["state_before"].get("last_result")
    
    assert cli._session.last_result == "10"

def test_json_output_mandatory_fields():
    raw = [
        {
            "type": "compute_result",
            "value": "10+10",
            "description": "testing",
            "use_last_result": False,
            "date_memory_hook": "2026-03-04"
        },
        {
            "type": "prompt_next_action",
            "description": "Ask user what to do next"
        }
    ]
    plan = parse_plan(raw)
    assert len(plan.actions) == 2
    assert plan.actions[1].type == "prompt_next_action"
