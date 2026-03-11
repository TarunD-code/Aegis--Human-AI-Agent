"""
Aegis v6.3 — Command Decomposition Engine
==========================================
Slices compound user requests into atomic, actionable steps
using NLP-aware segmentation on conjunctions and sequence markers.
"""

import re
import logging
from typing import List

logger = logging.getLogger(__name__)

class CommandDecomposer:
    """
    Identifies multi-step intents and breaks them down for sequential planning.
    Uses regex-based NLP segmentation instead of naive string splitting.
    """

    # Ordered by specificity (longest first to avoid partial matches)
    SPLIT_PATTERN = re.compile(
        r'\s+(?:and\s+then|after\s+that|and\s+next|then\s+also|then\s+open|and\s+also|'
        r'then|after|next|and)\s+',
        re.IGNORECASE
    )

    # Protected phrases that should NOT be split (e.g., "search and rescue")
    PROTECTED_PHRASES = [
        "search and rescue", "copy and paste", "cut and paste",
        "drag and drop", "bread and butter", "black and white"
    ]

    def decompose(self, text: str) -> List[str]:
        """
        Segments a command into individual tasks using NLP markers.
        Example: "open notepad and write hello then save" -> ["open notepad", "write hello", "save"]
        """
        if not text:
            return []

        text = text.strip()

        # Check if the text contains a protected phrase — don't split
        text_lower = text.lower()
        for phrase in self.PROTECTED_PHRASES:
            if phrase in text_lower:
                return [text]

        # Split on NLP markers
        parts = self.SPLIT_PATTERN.split(text)
        result = [p.strip() for p in parts if p.strip()]

        if len(result) > 1:
            logger.info(f"Decomposer: Split '{text}' into {len(result)} tasks: {result}")
        
        return result if result else [text]

decomposer = CommandDecomposer()
