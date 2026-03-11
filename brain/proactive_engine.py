"""
Aegis v3.5 — Proactive Intelligence Engine
==========================================
Analyzes session history and daily logs to suggest optimizations.
"""

import logging
from typing import List, Dict, Any
from dataclasses import dataclass

logger = logging.getLogger(__name__)

@dataclass
class Suggestion:
    type: str  # OPTIMIZATION, MACRO, CLEANUP, SECURITY
    content: str
    benefit: str
    impact: str  # LOW, MEDIUM, HIGH

class ProactiveEngine:
    """
    Suggests improvements to the user's workflow based on behavioral patterns.
    """

    def generate_suggestions(self, context: dict) -> List[Suggestion]:
        suggestions = []
        
        # 1. Macro Suggestions (Repeated actions)
        daily_history = context.get("daily_history", [])
        if len(daily_history) >= 3:
            from collections import Counter
            commands = [f"{e['app']}:{e['command']}" for e in daily_history if e.get('command')]
            counts = Counter(commands)
            for cmd, count in counts.items():
                if count >= 4:
                    app, val = cmd.split(":", 1)
                    suggestions.append(Suggestion(
                        type="MACRO",
                        content=f"Create a direct macro for '{val}' in {app}.",
                        benefit="Reduces manual typing and speeds up execution.",
                        impact="MEDIUM"
                    ))

        # 2. Window/Tab Reuse Suggestions
        session_state = context.get("session_state", {})
        if session_state.get("last_tab"):
            suggestions.append(Suggestion(
                type="OPTIMIZATION",
                content="Reuse the current browser tab instead of opening a new one.",
                benefit="Reduces system resource usage and tab clutter.",
                impact="LOW"
            ))

        # 3. Security/Risk Suggestions
        recent_rejected = context.get("recent_rejected", [])
        for rej in recent_rejected:
            reason = rej.get("reason", "").lower()
            if "delete" in reason or "remove" in reason:
                suggestions.append(Suggestion(
                    type="SECURITY",
                    content="Always archive files before deletion for safe recovery.",
                    benefit="Prevents accidental data loss.",
                    impact="HIGH"
                ))

        # 4. Behavioral Pattern Suggestions (v5.6)
        from core.state import working_memory, memory_manager
        last_action_key = working_memory.get("last_action_key")
        
        if last_action_key:
            patterns = memory_manager.get_top_patterns(last_action_key, limit=1)
            if patterns:
                top_pattern = patterns[0]
                # High confidence threshold: Suggest if transition has occurred at least 3 times
                if top_pattern["count"] >= 3:
                    suggestion_action = top_pattern["suggested_action"]
                    # Format suggestion content nicely: "youtube:search_web" -> "Search Web in Youtube"
                    if ":" in suggestion_action:
                        app, act = suggestion_action.split(":", 1)
                        display_name = f"{act.replace('_', ' ')} in {app}".title()
                    else:
                        display_name = suggestion_action.replace("_", " ").title()
                    
                    suggestions.append(Suggestion(
                        type="PROACTIVE",
                        content=f"Would you like me to {display_name}?",
                        benefit="Proactively automates your habitual multi-step workflows.",
                        impact="HIGH"
                    ))

        logger.info(f"Generated {len(suggestions)} proactive suggestions.")
        return suggestions
