"""
Aegis v3.9 — Risk Tone Amplification Tests
"""

import sys
from pathlib import Path
import pytest

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from brain.tone_controller import ToneController
from brain.mood_detector import MoodProfile, NEUTRAL, URGENT, FRUSTRATED


class TestRiskToneAmplification:

    def setup_method(self):
        self.tone = ToneController()

    def test_critical_risk_overrides_mood(self):
        """CRITICAL risk should produce formal tone regardless of mood."""
        mood = MoodProfile(mood_type=URGENT)
        result = self.tone.format_response(
            action_type="delete_files",
            message="All data will be erased.",
            success=True,
            risk_level="CRITICAL",
            mood=mood,
        )
        assert "CRITICAL" in result
        assert "Sir" in result
        assert "CONFIRM" in result

    def test_critical_no_followup_question(self):
        """CRITICAL should not ask casual follow-up questions."""
        result = self.tone.format_response(
            action_type="delete_files",
            message="Permanent deletion.",
            success=True,
            risk_level="CRITICAL",
        )
        assert "What's next?" not in result
        assert "anything else" not in result.lower()

    def test_high_risk_success(self):
        """HIGH risk success should be formal with verification request."""
        result = self.tone.format_response(
            action_type="run_powershell",
            message="Script completed.",
            success=True,
            risk_level="HIGH",
        )
        assert "Sir" in result
        assert "verify" in result.lower() or "convenience" in result.lower()

    def test_high_risk_failure(self):
        """HIGH risk failure should recommend review."""
        result = self.tone.format_response(
            action_type="run_powershell",
            message="Script failed.",
            success=False,
            risk_level="HIGH",
        )
        assert "Sir" in result
        assert "review" in result.lower()

    def test_low_risk_uses_mood(self):
        """LOW risk should use mood-based tone, not risk override."""
        mood = MoodProfile(mood_type=URGENT)
        result = self.tone.format_response(
            action_type="open_application",
            message="Notepad opened.",
            success=True,
            risk_level="LOW",
            mood=mood,
        )
        assert "Next task?" in result  # Urgent tone, not risk tone

    def test_frustrated_failure_empathetic(self):
        """Failure during FRUSTRATED mood should be empathetic."""
        mood = MoodProfile(mood_type=FRUSTRATED)
        result = self.tone.format_response(
            action_type="open_application",
            message="Application not found.",
            success=False,
            risk_level="LOW",
            mood=mood,
        )
        assert "understand" in result.lower() or "concern" in result.lower()
        assert "Sir" in result
