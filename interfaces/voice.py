"""
Aegis v7.0 — Voice Interface
============================
Provides Text-to-Speech (TTS) and Speech-to-Text (STT) capabilities.
Supports pluggable backends (pyttsx3, VOSK, Whisper).
"""

import logging
import threading

logger = logging.getLogger(__name__)

class AegisVoiceInterface:
    def __init__(self):
        self.tts_engine = None
        self.stt_recognizer = None
        self._init_tts()
        self._init_stt()

    def _init_tts(self):
        try:
            import pyttsx3
            self.tts_engine = pyttsx3.init()
            # Configure voice properties
            self.tts_engine.setProperty('rate', 170)
            self.tts_engine.setProperty('volume', 0.9)
            logger.info("Voice: TTS engine (pyttsx3) initialized.")
        except Exception as e:
            logger.warning(f"Voice: Failed to initialize TTS: {e}")

    def _init_stt(self):
        try:
            import speech_recognition as sr
            self.stt_recognizer = sr.Recognizer()
            logger.info("Voice: STT recognizer (speech_recognition) initialized.")
        except Exception as e:
            logger.warning(f"Voice: Failed to initialize STT: {e}")

    def speak(self, text: str, wait: bool = False):
        """Convert text to speech."""
        if not self.tts_engine or not text:
            return
        
        logger.info(f"Voice: Speaking: {text}")
        
        def _run():
            try:
                self.tts_engine.say(text)
                self.tts_engine.runAndWait()
            except Exception as e:
                logger.error(f"Voice: TTS speaking failed: {e}")

        if wait:
            _run()
        else:
            threading.Thread(target=_run, daemon=True).start()

    def listen(self, timeout: int = 5) -> str:
        """Listen for audio and convert to text."""
        if not self.stt_recognizer:
            return ""

        try:
            import speech_recognition as sr
            with sr.Microphone() as source:
                logger.info("Voice: Listening...")
                self.stt_recognizer.adjust_for_ambient_noise(source, duration=0.5)
                audio = self.stt_recognizer.listen(source, timeout=timeout, phrase_time_limit=10)
                
                logger.info("Voice: Processing speech...")
                # Default to Google Web Speech API (requires internet)
                # For offline, use vosk or whisper-local
                text = self.stt_recognizer.recognize_google(audio)
                logger.info(f"Voice: Recognized: {text}")
                return text
        except Exception as e:
            logger.debug(f"Voice: STT failed or timed out: {e}")
            return ""

# Singleton
voice_interface = AegisVoiceInterface()
