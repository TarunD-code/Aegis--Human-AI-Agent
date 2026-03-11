"""
Aegis v3.9 — Mood Detection Engine
=====================================
Detects user mood from input text analysis: sentence length, capitalization,
punctuation intensity, keywords, and command frequency.

Returns a MoodProfile with mood_type, confidence, and urgency_score.
"""

from __future__ import annotations

import re
import logging
from dataclasses import dataclass
from datetime import datetime, timezone
from typing import TYPE_CHECKING
from enum import Enum

class MoodState(Enum):
    NEUTRAL = "neutral"
    POSITIVE = "positive"
    NEGATIVE = "negative"


if TYPE_CHECKING:
    from memory.session_memory import SessionMemory

logger = logging.getLogger(__name__)

# ── Mood Categories ──────────────────────────────────────────────────────

NEUTRAL = "NEUTRAL"
URGENT = "URGENT"
FRUSTRATED = "FRUSTRATED"
ANALYTICAL = "ANALYTICAL"
LATE_NIGHT = "LATE_NIGHT"
POSITIVE = "POSITIVE"


@dataclass
class MoodProfile:
    """Detected mood state for the current interaction."""
    mood_type: str = NEUTRAL
    confidence: float = 0.5
    urgency_score: float = 0.0


# ── Keywords ─────────────────────────────────────────────────────────────

_URGENT_KEYWORDS = {
    "now", "asap", "immediately", "hurry", "quick", "fast",
    "urgent", "right now", "emergency", "quickly",
}
_FRUSTRATED_KEYWORDS = {
    "why", "wrong", "broken", "fail", "error", "crash", "again",
    "not working", "doesn't work", "can't", "frustrated", "stupid",
    "useless", "terrible", "annoying", "fix",
}
_POSITIVE_KEYWORDS = {
    "thanks", "great", "awesome", "good", "nice", "perfect",
    "love", "excellent", "well done", "appreciate", "brilliant",
}
_ANALYTICAL_KEYWORDS = {
    "explain", "analyze", "compare", "detail", "breakdown",
    "statistics", "metrics", "report", "data", "how does",
    "show me", "list", "describe",
}


def detect_mood(
    user_input: str,
    session: SessionMemory | None = None,
    current_hour: int | None = None,
) -> MoodProfile:
    """
    Analyze user input and return a MoodProfile.

    Detection signals (weighted):
    - Capitalization ratio
    - Punctuation intensity (!!!, ???)
    - Keyword matching
    - Sentence length
    - Time of day
    - Command frequency (rapid-fire detection)
    """
    text = user_input.strip()
    lower = text.lower()
    profile = MoodProfile()

    if not text:
        profile.mood_type = MoodState.NEUTRAL.value
        return profile

    scores: dict[str, float] = {
        MoodState.NEUTRAL.value: 0.3,
        URGENT: 0.0,
        FRUSTRATED: 0.0,
        ANALYTICAL: 0.0,
        LATE_NIGHT: 0.0,
        POSITIVE: 0.0,
    }

    # ── Signal 1: Capitalization ──────────────────────────────────────
    alpha_chars = [c for c in text if c.isalpha()]
    if alpha_chars:
        caps_ratio = sum(1 for c in alpha_chars if c.isupper()) / len(alpha_chars)
        if caps_ratio > 0.6 and len(text) > 3:
            scores[URGENT] += 0.3
            scores[FRUSTRATED] += 0.2

    # ── Signal 2: Punctuation intensity ──────────────────────────────
    excl_count = text.count("!")
    quest_count = text.count("?")
    if excl_count >= 1:
        scores[URGENT] += 0.2
        scores[FRUSTRATED] += 0.1
    if quest_count >= 2:
        scores[FRUSTRATED] += 0.3
    if excl_count >= 3:
        scores[FRUSTRATED] += 0.2

    # ── Signal 3: Keyword matching ───────────────────────────────────
    for kw in _URGENT_KEYWORDS:
        if kw in lower:
            scores[URGENT] += 0.45
            break

    for kw in _FRUSTRATED_KEYWORDS:
        if kw in lower:
            scores[FRUSTRATED] += 0.45
            break

    for kw in _POSITIVE_KEYWORDS:
        if kw in lower:
            scores[POSITIVE] += 0.5
            break

    for kw in _ANALYTICAL_KEYWORDS:
        if kw in lower:
            scores[ANALYTICAL] += 0.45
            break

    # ── Signal 4: Sentence length ────────────────────────────────────
    word_count = len(text.split())
    if word_count <= 3:
        scores[URGENT] += 0.15  # Short commands feel urgent
    elif word_count >= 15:
        scores[ANALYTICAL] += 0.2  # Lengthy requests are analytical

    # ── Signal 5: Late night detection ───────────────────────────────
    hour = current_hour if current_hour is not None else datetime.now().hour
    if hour >= 22 or hour < 5:
        scores[LATE_NIGHT] += 0.4

    # ── Signal 6: Rapid-fire detection ───────────────────────────────
    if session:
        try:
            last_activity = datetime.fromisoformat(session.last_activity)
            now = datetime.now(tz=timezone.utc)
            # Ensure timezone awareness
            if last_activity.tzinfo is None:
                from datetime import timezone as tz
                last_activity = last_activity.replace(tzinfo=tz.utc)
            delta_seconds = (now - last_activity).total_seconds()
            if delta_seconds < 5 and session.command_count > 2:
                scores[URGENT] += 0.2
                scores[FRUSTRATED] += 0.1
        except Exception:
            pass

    # ── Determine the winner ─────────────────────────────────────────
    best_mood = max(scores, key=scores.get)
    best_score = scores[best_mood]

    # Confidence: how much the winner leads over the baseline
    confidence = min(1.0, best_score / max(sum(scores.values()), 0.01))

    # Urgency is a composite score
    urgency = min(1.0, scores[URGENT] + (0.1 if scores[FRUSTRATED] > 0.2 else 0.0))

    profile.mood_type = best_mood
    profile.confidence = round(confidence, 2)
    profile.urgency_score = round(urgency, 2)

    logger.debug("Mood detected: %s (confidence=%.2f, urgency=%.2f)", 
                 profile.mood_type, profile.confidence, profile.urgency_score)
    return profile
