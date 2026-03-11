"""
Aegis v3.9 — Tone Controller Engine
======================================
Wraps all outgoing responses with adaptive executive professional tone.
Always addresses the user as "Sir". Adjusts phrasing based on mood, urgency, and risk.

Every response follows the structure:
  [ Acknowledgement ] → [ Action / Result ] → [ Confirmation ] → [ Follow-up ]
"""

from __future__ import annotations

import logging
from typing import Any

from brain.mood_detector import MoodProfile, NEUTRAL, URGENT, FRUSTRATED, ANALYTICAL, LATE_NIGHT, POSITIVE

logger = logging.getLogger(__name__)


class ToneController:
    """
    Aegis v3.9 — Adaptive Executive Professional Tone Controller.
    
    Wraps raw execution results into conversational, professional responses
    that always address the user as "Sir".
    """

    def format_response(
        self,
        action_type: str,
        message: str,
        success: bool,
        risk_level: str = "LOW",
        mood: MoodProfile | None = None,
        action_description: str = "",
    ) -> str:
        """
        Format an execution result into a toned response.

        Parameters
        ----------
        action_type : str
            The canonical action type (e.g., 'open_application').
        message : str
            Raw result message from the execution engine.
        success : bool
            Whether the action succeeded.
        risk_level : str
            Risk level: LOW, MEDIUM, HIGH, CRITICAL.
        mood : MoodProfile | None
            Current detected mood profile.
        action_description : str
            Human-readable description of the action.
        """
        if mood is None:
            mood = MoodProfile()

        # Risk overrides mood tone
        if risk_level == "CRITICAL":
            return self._critical_tone(action_type, message, action_description)
        if risk_level == "HIGH":
            return self._high_risk_tone(action_type, message, success, action_description)

        # Mood-based tone
        if not success:
            return self._failure_tone(action_type, message, mood, action_description)

        tone_map = {
            NEUTRAL: self._neutral_tone,
            URGENT: self._urgent_tone,
            FRUSTRATED: self._frustrated_tone,
            ANALYTICAL: self._analytical_tone,
            LATE_NIGHT: self._late_night_tone,
            POSITIVE: self._positive_tone,
        }
        formatter = tone_map.get(mood.mood_type, self._neutral_tone)
        return formatter(action_type, message, action_description)

    # ── Mood Tone Formatters ─────────────────────────────────────────────

    def _neutral_tone(self, action_type: str, message: str, description: str) -> str:
        action_phrase = self._action_phrase(action_type, description)
        return (
            f"{action_phrase}, Sir.\n"
            f"{message}\n"
            f"Is there anything else I can assist you with?"
        )

    def _urgent_tone(self, action_type: str, message: str, description: str) -> str:
        action_phrase = self._action_phrase(action_type, description)
        return (
            f"{action_phrase}, Sir.\n"
            f"{message}\n"
            f"Next task?"
        )

    def _frustrated_tone(self, action_type: str, message: str, description: str) -> str:
        action_phrase = self._action_phrase(action_type, description)
        return (
            f"Understood, Sir. Let me handle that right away.\n"
            f"{action_phrase}.\n"
            f"{message}\n"
            f"Would you like me to verify the result?"
        )

    def _analytical_tone(self, action_type: str, message: str, description: str) -> str:
        action_phrase = self._action_phrase(action_type, description)
        return (
            f"{action_phrase}, Sir.\n"
            f"Details:\n"
            f"  • Result: {message}\n"
            f"  • Action: {action_type}\n"
            f"Would you like a deeper analysis?"
        )

    def _late_night_tone(self, action_type: str, message: str, description: str) -> str:
        action_phrase = self._action_phrase(action_type, description)
        return (
            f"{action_phrase}, Sir.\n"
            f"{message}\n"
            f"Anything else before you wrap up for the night?"
        )

    def _positive_tone(self, action_type: str, message: str, description: str) -> str:
        action_phrase = self._action_phrase(action_type, description)
        return (
            f"{action_phrase}, Sir.\n"
            f"{message}\n"
            f"Glad to help! What's next?"
        )

    # ── Risk Tone Formatters ─────────────────────────────────────────────

    def _critical_tone(self, action_type: str, message: str, description: str) -> str:
        return (
            f"Sir, this is a CRITICAL action.\n"
            f"{description or action_type}: {message}\n"
            f"Please confirm to proceed by typing: YES I CONFIRM"
        )

    def _high_risk_tone(self, action_type: str, message: str, success: bool, description: str) -> str:
        if success:
            return (
                f"Sir, the high-risk action has been executed successfully.\n"
                f"{description or action_type}: {message}\n"
                f"Please verify the outcome at your earliest convenience."
            )
        else:
            return (
                f"Sir, the high-risk action encountered an issue.\n"
                f"{description or action_type}: {message}\n"
                f"I recommend we review before proceeding further."
            )

    # ── Failure Tone ─────────────────────────────────────────────────────

    def _failure_tone(self, action_type: str, message: str, mood: MoodProfile, description: str) -> str:
        if mood.mood_type == FRUSTRATED:
            return (
                f"I understand the concern, Sir.\n"
                f"The action '{description or action_type}' did not succeed: {message}\n"
                f"Let me investigate and suggest an alternative approach."
            )
        return (
            f"Sir, the action '{description or action_type}' encountered an issue.\n"
            f"Details: {message}\n"
            f"Would you like me to retry or try a different approach?"
        )

    # ── Helpers ───────────────────────────────────────────────────────────

    @staticmethod
    def _action_phrase(action_type: str, description: str) -> str:
        """Generate a natural-language action phrase."""
        if description:
            return description.rstrip(".")
        
        phrases = {
            "open_application": "Opening the application now",
            "focus_application": "Switching focus to the application now",
            "type_text": "Typing the requested text now",
            "press_keys": "Sending the key combination now",
            "search_online": "Searching online now",
            "prompt_next_action": "Ready for your next instruction",
            "run_powershell": "Executing the command now",
            "organize_files": "Organizing files now",
            "find_duplicates": "Scanning for duplicates now",
        }
        return phrases.get(action_type, f"Executing {action_type}")

    def format_plan_summary(self, plan_summary: str, mood: MoodProfile | None = None) -> str:
        """Format the plan presentation to the user."""
        if mood and mood.mood_type == URGENT:
            return f"Sir, here is the plan. Awaiting your approval."
        return f"Sir, I've prepared the following plan for your review."

    def format_social_response(self, mood: MoodProfile | None = None) -> str:
        """Format a social/greeting response."""
        if mood and mood.mood_type == LATE_NIGHT:
            return "Good evening, Sir. Working late tonight? How may I assist you?"
        return "Hello, Sir. I am Aegis, your Executive Assistant. How can I assist you today?"

    def format_rejection(self) -> str:
        """Format the rejection acknowledgement."""
        return "Understood, Sir. The plan has been cancelled. Your feedback has been noted."

    def format_completion(self, mood: MoodProfile | None = None) -> str:
        """Format the plan completion message."""
        if mood and mood.mood_type == URGENT:
            return "Task completed, Sir. What is our next objective?"
        return "What would you like me to do next, Sir?"

    def format_what_next(self) -> str:
        """Standard professional follow-up prompt."""
        return "What would you like me to do next, Sir?"
