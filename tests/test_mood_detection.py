"""
Aegis v3.9 — Mood Detection Tests
"""

import sys
from pathlib import Path
import pytest

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from brain.mood_detector import detect_mood, NEUTRAL, URGENT, FRUSTRATED, ANALYTICAL, LATE_NIGHT, POSITIVE


class TestMoodDetection:

    def test_neutral_default(self):
        """Short neutral command during daytime should be NEUTRAL or URGENT."""
        profile = detect_mood("open notepad", current_hour=14)
        assert profile.mood_type in (NEUTRAL, URGENT)

    def test_urgent_keywords(self):
        """Urgent keywords with exclamation should detect URGENT."""
        profile = detect_mood("open calculator NOW hurry!", current_hour=14)
        assert profile.mood_type == URGENT
        assert profile.urgency_score > 0.2

    def test_frustrated_keywords(self):
        profile = detect_mood("why did this fail again???", current_hour=14)
        assert profile.mood_type == FRUSTRATED

    def test_positive_keywords(self):
        profile = detect_mood("Thanks, that was perfect!", current_hour=14)
        assert profile.mood_type == POSITIVE

    def test_analytical_keywords(self):
        profile = detect_mood("Explain the detailed breakdown of the file organization statistics", current_hour=14)
        assert profile.mood_type == ANALYTICAL

    def test_all_caps_urgent(self):
        profile = detect_mood("OPEN CALCULATOR RIGHT NOW", current_hour=14)
        assert profile.mood_type == URGENT

    def test_late_night_detection(self):
        profile = detect_mood("open notepad", current_hour=23)
        assert profile.mood_type == LATE_NIGHT

    def test_early_morning_late_night(self):
        profile = detect_mood("open notepad", current_hour=3)
        assert profile.mood_type == LATE_NIGHT

    def test_daytime_not_late_night(self):
        profile = detect_mood("open notepad", current_hour=14)
        assert profile.mood_type != LATE_NIGHT

    def test_empty_input_returns_neutral(self):
        profile = detect_mood("")
        assert profile.mood_type == NEUTRAL

    def test_confidence_in_range(self):
        profile = detect_mood("open notepad", current_hour=14)
        assert 0.0 <= profile.confidence <= 1.0

    def test_urgency_in_range(self):
        profile = detect_mood("do it now!", current_hour=14)
        assert 0.0 <= profile.urgency_score <= 1.0
