"""
Aegis v3.5 — Intent Intelligence Engine
=======================================
Classifies user commands into functional intents and assesses ambiguity.
"""

import logging
from typing import List, Dict, Any
from dataclasses import dataclass, field

logger = logging.getLogger(__name__)

@dataclass
class IntentMetadata:
    intent_types: List[str] = field(default_factory=list)
    intent_confidence: float = 0.0
    ambiguity_score: float = 0.0
    requires_clarification: bool = False
    clarification_question: str | None = None

class IntentClassifier:
    """
    Analyzes user input to determine the underlying intent and risk/ambiguity.
    """
    
    INTENTS = [
        "EXECUTE", "RESEARCH", "ORGANIZE", "DECIDE", 
        "STRATEGIZE", "ANALYZE", "OPTIMIZE", "MONITOR", 
        "CREATE", "AUTOMATE", "SOCIAL"
    ]

    def classify(self, user_input: str) -> IntentMetadata:
        """
        Heuristic-based intent classification with compound command detection.
        """
        from brain.command_decomposer import decomposer
        tasks = decomposer.decompose(user_input)
        
        if len(tasks) > 1:
            logger.info(f"Decomposer split input into {len(tasks)} tasks.")
            # For multi-tasks, we flag as compound
            metadata = IntentMetadata()
            metadata.intent_types = ["COMPOUND"]
            metadata.intent_confidence = 0.9
            metadata.data = {"sub_tasks": tasks}
            return metadata

        user_input_lower = user_input.lower()
        metadata = IntentMetadata()
        
        # Heuristic 0: Explicit Launch Commands (Jarvis v5.4 Priority)
        if user_input_lower.startswith("open "):
            metadata.intent_types.append("EXECUTE")
            metadata.intent_confidence = 0.95
            return metadata

        # 1. Social Intent (Greetings)
        greetings = ["hi", "hello", "hey", "good morning", "good afternoon", "good evening", "howdy", "sups", "yo"]
        if any(word == user_input_lower or user_input_lower.startswith(word + " ") for word in greetings):
            metadata.intent_types.append("SOCIAL")
            metadata.intent_confidence = 1.0
            return metadata

        # 2. Functional Key Words
        if any(word in user_input_lower for word in ["search", "find", "who is", "what is", "research", "lookup"]):
            metadata.intent_types.append("RESEARCH")
        if any(word in user_input_lower for word in ["chrome", "browser", "edge", "firefox", "website", "url", "tab"]):
            metadata.intent_types.append("BROWSER")
        if any(word in user_input_lower for word in ["organize", "sort", "clean", "scan"]):
            metadata.intent_types.append("ORGANIZE")
        if any(word in user_input_lower for word in ["delete", "remove", "kill", "terminate", "stop"]):
            metadata.intent_types.append("EXECUTE")
        if any(word in user_input_lower for word in ["add", "calculate", "compute", "+", "-", "*", "/", "calc"]):
            # Aegis v5.3: Separate MATH intent for routing
            metadata.intent_types.append("MATH")
        if any(word in user_input_lower for word in ["play music", "play song", "play some music"]):
            metadata.intent_types.append("MUSIC")
        if any(word in user_input_lower for word in ["remember", "forget", "recall", "what is my"]):
            metadata.intent_types.append("MEMORY")
        if any(word in user_input_lower for word in ["list running", "show windows", "running apps"]):
            metadata.intent_types.append("SYSTEM")
        if user_input_lower in ["status", "system", "performance", "metrics"]:
            metadata.intent_types.append("MONITOR")
        if any(word in user_input_lower for word in ["installed apps", "installed applications", "installed programs", "what apps are installed", "list programs", "applications on my computer"]):
            metadata.intent_types.append("SYSTEM_APPS")
        
        # Simple commands should have higher confidence
        if not metadata.intent_types:
            metadata.intent_types.append("EXECUTE")
            metadata.intent_confidence = 0.8 # Higher baseline
            metadata.ambiguity_score = 0.2
        else:
            metadata.intent_confidence = 0.95 # Very high for clear keywords
            metadata.ambiguity_score = 0.05

        # Refined Ambiguity check
        known_commands = ["status", "clear", "exit", "quit", "help"]
        if len(user_input.split()) < 2 and user_input_lower not in known_commands:
            metadata.ambiguity_score = 0.7
            metadata.requires_clarification = True
            metadata.clarification_question = f"Sir, '{user_input}' is a very brief command. Could you please elaborate on what you'd like me to do?"
        else:
            metadata.requires_clarification = False

        logger.info(f"Intent classified (v4.1): {metadata}")
        return metadata
