from rapidfuzz import process, fuzz
import logging

logger = logging.getLogger(__name__)

COMMON_MISTAKES = {
    "opne": "open",
    "wright": "write",
    "calcualtor": "calculator",
    "serch": "search",
    "googl": "google",
    "notepd": "notepad",
    "claculate": "calculate",
    "calulate": "calculate",
}

import logging
from brain.normalizer_rules import rules_engine

logger = logging.getLogger(__name__)

class CommandNormalizer:
    """
    Corrects typing mistakes and unifies command verbs using deterministic 
    rules and fuzzy matching for application names.
    """
    def __init__(self):
        self.rules = rules_engine

    def normalize(self, text: str) -> str:
        if not text: return text
        cmd = text.strip().lower()

        # 0. Fuzzy Typo Correction for primary verbs
        parts = cmd.split(maxsplit=1)
        if len(parts) > 0:
            verb = parts[0]
            known_verbs = ["open", "write", "calculate", "search", "close", "focus", "play", "list", "launch", "shutdown", "restart"]
            from rapidfuzz import process, fuzz
            match = process.extractOne(verb, known_verbs, scorer=fuzz.ratio)
            if match and match[1] >= 75:  # Tolerance threshold
                corrected_verb = match[0]
                if verb != corrected_verb:
                    logger.debug(f"Normalizer: Corrected typo '{verb}' -> '{corrected_verb}'")
                    cmd = corrected_verb + (" " + parts[1] if len(parts) > 1 else "")

        # 1. Apply synonym replacement (e.g., "launch" -> "open")
        cmd = self.rules.apply_synonyms(cmd)

        # 2. Intent-specific deterministic handling
        # If it's an "open <app>" command, fuzzy correct only the app name
        if cmd.startswith("open "):
            parts = cmd.split(maxsplit=1)
            if len(parts) > 1:
                app_candidate = parts[1].strip()
                corrected_app = self.rules.fuzzy_match_app(app_candidate)
                if corrected_app:
                    logger.debug(f"Normalizer: '{app_candidate}' matched to '{corrected_app}'")
                    return f"open {corrected_app}"

        # 3. Deterministic Screenshot Rule
        if "take screenshot" in cmd or "capture screen" in cmd:
            return "press_key win+shift+s"

        # 4. Preserve multi-step intent (e.g., "open youtube and play music")
        # Rule: if 'and' is present, don't over-simplify the whole command
        # if it's not a simple command.
        
        return cmd

# Global instance
normalizer = CommandNormalizer()

# Global instance
normalizer = CommandNormalizer()
