"""
Aegis v5.5 — Command Normalizer Rules
======================================
Deterministic transformation rules for user commands.
"""

import json
import os
from rapidfuzz import process, fuzz
import logging

logger = logging.getLogger(__name__)

class NormalizerRules:
    def __init__(self, synonym_file="d:\\Aegis\\config\\synonyms.json"):
        self.synonyms = {}
        if os.path.exists(synonym_file):
            try:
                with open(synonym_file, "r") as f:
                    self.synonyms = json.load(f)
            except Exception as e:
                logger.error(f"Failed to load synonyms: {e}")
        
        # Load app names for fuzzy matching
        self.app_names = []
        app_registry_path = "d:\\Aegis\\config\\app_registry.json"
        if os.path.exists(app_registry_path):
             try:
                with open(app_registry_path, "r") as f:
                    registry = json.load(f)
                    self.app_names = list(registry.keys())
             except Exception as e:
                logger.error(f"Failed to load app registry: {e}")

    def apply_synonyms(self, command: str) -> str:
        """Replaces command verbs with canonical ones."""
        words = command.split()
        if not words: return command
        
        first_word = words[0].lower()
        if first_word in self.synonyms:
            replacement = self.synonyms[first_word]
            words[0] = replacement
            
        return " ".join(words)

    def fuzzy_match_app(self, app_candidate: str) -> str | None:
        """Matches app name against the registry with high confidence."""
        if not self.app_names: return None
        
        match = process.extractOne(app_candidate, self.app_names, scorer=fuzz.ratio)
        if match and match[1] > 80:
            return match[0]
        return None

rules_engine = NormalizerRules()
