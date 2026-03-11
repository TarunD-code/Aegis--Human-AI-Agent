"""
Aegis v3.9 — Greeting Engine
===============================
Dynamic startup greeting that adapts based on time of day and session context.
Always addresses the user as "Sir".
"""

from __future__ import annotations

import logging
from datetime import datetime, timezone

logger = logging.getLogger(__name__)


def generate_greeting(
    current_hour: int | None = None,
    is_returning_session: bool = False,
) -> str:
    """
    Generate a context-aware greeting.

    Parameters
    ----------
    current_hour : int | None
        Override for the current hour (0-23). Uses system time if None.
    is_returning_session : bool
        True if user is returning within 2 hours of last session.
    """
    hour = current_hour if current_hour is not None else datetime.now().hour

    if is_returning_session:
        return "Welcome back, Sir. How can I assist you now?"

    if 5 <= hour < 12:
        return "Good Morning, Sir. I'm Aegis, your AI assistant. How may I assist you today?"
    elif 12 <= hour < 17:
        return "Good Afternoon, Sir. I'm Aegis, your AI assistant. How may I assist you?"
    elif 17 <= hour < 22:
        return "Good Evening, Sir. I'm Aegis, your AI assistant. How may I assist you tonight?"
    else:
        return "Good Evening, Sir. Working late tonight? How may I assist you?"
