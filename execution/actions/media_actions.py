"""
Aegis v5.6 — Media Actions
===========================
Handlers for music and media playback.
"""

import webbrowser
import logging
from execution.actions.app_actions import ExecutionResult

logger = logging.getLogger(__name__)

def play_music(action=None) -> ExecutionResult:
    """
    Opens YouTube Music in the default browser.
    """
    url = "https://music.youtube.com"
    logger.info("Aegis: Opening YouTube Music.")
    try:
        webbrowser.open(url)
        return ExecutionResult(
            success=True,
            message="Sir, I have opened YouTube Music for you.",
            data={"url": url, "action_type": "play_music"}
        )
    except Exception as e:
        logger.error(f"Failed to play music: {e}")
        return ExecutionResult(
            success=False,
            message=f"I encountered an error while trying to open the music player: {e}",
            data={"error": str(e), "action_type": "play_music"}
        )
