"""
Aegis v3.9 — Late Night Greeting Tests
"""

import sys
from pathlib import Path
import pytest

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from brain.greeting_engine import generate_greeting


class TestLateNightGreeting:

    def test_morning_greeting(self):
        greeting = generate_greeting(current_hour=8)
        assert "Good Morning" in greeting
        assert "Sir" in greeting

    def test_afternoon_greeting(self):
        greeting = generate_greeting(current_hour=14)
        assert "Good Afternoon" in greeting
        assert "Sir" in greeting

    def test_evening_greeting(self):
        greeting = generate_greeting(current_hour=19)
        assert "Good Evening" in greeting
        assert "Sir" in greeting

    def test_late_night_greeting(self):
        greeting = generate_greeting(current_hour=23)
        assert "Working late" in greeting
        assert "Sir" in greeting

    def test_early_morning_late_night(self):
        greeting = generate_greeting(current_hour=2)
        assert "Working late" in greeting

    def test_returning_session(self):
        greeting = generate_greeting(is_returning_session=True)
        assert "Welcome back" in greeting
        assert "Sir" in greeting

    def test_returning_overrides_time(self):
        greeting = generate_greeting(current_hour=23, is_returning_session=True)
        assert "Welcome back" in greeting  # Returning takes priority
