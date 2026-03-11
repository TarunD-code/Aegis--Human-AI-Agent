"""
Aegis v3.9 — Tone Controller Tests
"""

import sys
from pathlib import Path
import pytest

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from brain.tone_controller import ToneController
from brain.mood_detector import MoodProfile, NEUTRAL, URGENT, FRUSTRATED, ANALYTICAL, LATE_NIGHT, POSITIVE


class TestToneController:

    def setup_method(self):
        self.tone = ToneController()

    def test_always_includes_sir(self):
        for mood_type in [NEUTRAL, URGENT, FRUSTRATED, ANALYTICAL, LATE_NIGHT, POSITIVE]:
            mood = MoodProfile(mood_type=mood_type)
            result = self.tone.format_response(
                action_type="open_application",
                message="Notepad opened.",
                success=True,
                mood=mood,
            )
            assert "Sir" in result, f"Missing 'Sir' for mood {mood_type}"

    def test_neutral_has_followup(self):
        mood = MoodProfile(mood_type=NEUTRAL)
        result = self.tone.format_response("open_application", "Done.", True, mood=mood)
        assert "?" in result  # Should have a follow-up question

    def test_urgent_is_concise(self):
        mood = MoodProfile(mood_type=URGENT)
        result = self.tone.format_response("open_application", "Done.", True, mood=mood)
        assert "Next task?" in result

    def test_frustrated_has_reassurance(self):
        mood = MoodProfile(mood_type=FRUSTRATED)
        result = self.tone.format_response("open_application", "Done.", True, mood=mood)
        assert "right away" in result or "handle" in result

    def test_analytical_has_structure(self):
        mood = MoodProfile(mood_type=ANALYTICAL)
        result = self.tone.format_response("open_application", "Done.", True, mood=mood)
        assert "Details:" in result or "Result:" in result

    def test_late_night_soft(self):
        mood = MoodProfile(mood_type=LATE_NIGHT)
        result = self.tone.format_response("open_application", "Done.", True, mood=mood)
        assert "night" in result.lower()

    def test_positive_encouraging(self):
        mood = MoodProfile(mood_type=POSITIVE)
        result = self.tone.format_response("open_application", "Done.", True, mood=mood)
        assert "Glad" in result or "next" in result.lower()

    def test_failure_includes_sir(self):
        result = self.tone.format_response("open_application", "Error occurred.", False)
        assert "Sir" in result

    def test_format_social_response(self):
        result = self.tone.format_social_response()
        assert "Sir" in result

    def test_format_rejection(self):
        result = self.tone.format_rejection()
        assert "Sir" in result

    def test_format_completion(self):
        result = self.tone.format_completion()
        assert "Sir" in result
