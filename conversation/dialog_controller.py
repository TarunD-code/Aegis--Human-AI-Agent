"""
Aegis v5.0 — Dialog Controller
===============================
Manages interactive dialogue, follow-up questions, and outcome presentation.
Ensures Aegis sounds like a proactive digital employee.
"""

from __future__ import annotations
import logging
from typing import Optional, Dict, Any
from brain.mood_detector import MoodProfile
from brain.tone_controller import ToneController

logger = logging.getLogger(__name__)

class DialogController:
    """
    Governs the interactive flow between Aegis and the User.
    """

    def __init__(self, tone_controller: Optional[ToneController] = None):
        self._tone = tone_controller or ToneController()

    def present_research_findings(self, topic: str, summary: str, mood: MoodProfile) -> str:
        """
        Formats and presents research findings professionally.
        """
        # Jarvis-style presentation
        header = f"Sir, I have completed the research on '{topic}'."
        body = f"\n\n{summary}\n\n"
        footer = "I have committed these findings to my long-term memory. Would you like me to perform any further analysis?"
        
        # Apply tone modulation based on mood
        if mood.mood_type == "URGENT":
            return f"Sir, research into '{topic}' is complete. Brief summary follows:\n{summary[:500]}..."
        
        return f"{header}{body}{footer}"

    def ask_for_clarification(self, ambiguity_reason: str) -> str:
        """
        Asks the user for clarification when intent is ambiguous.
        """
        return f"Sir, I'm slightly unclear on your requirement regarding '{ambiguity_reason}'. Could you please elaborate so I can assist you more effectively?"

    def confirm_sensitive_action(self, action_description: str) -> str:
        """
        Asks for confirmation for high-risk actions.
        """
        return f"Sir, the following action has high risk potential: '{action_description}'. Do I have your executive approval to proceed?"

    def get_greeting(self, time_of_day: str = "day") -> str:
        """
        Returns a time-aware executive greeting.
        """
        if time_of_day == "morning":
            return "Good morning, Sir. Aegis is online and ready for service."
        if time_of_day == "evening":
            return "Good evening, Sir. How may I assist you with your tasks tonight?"
        return "At your service, Sir. What is our objective?"
