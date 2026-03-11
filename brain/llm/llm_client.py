"""
Aegis v3.6 — Resilient LLM Client
==================================
Handles API calls with backoff, circuit-breaking, telemetry, and offline mock mode.
"""

import json
import logging
import time
import os
from typing import Any
import backoff
import pybreaker
from groq import Groq, RateLimitError, APIError
from config import GROQ_MODEL, LLM_URL, get_action_list
from logs.logger import get_logger

logger = get_logger(__name__)

# Circuit Breaker: Open after 5 failures in 60s, stay open for 30s
llm_breaker = pybreaker.CircuitBreaker(fail_max=5, reset_timeout=30)

class Telemetry:
    def __init__(self):
        self.total_calls = 0
        self.errors = 0
        self.total_latency_ms = 0.0

    def record(self, latency_ms: float, error: bool = False):
        self.total_calls += 1
        self.total_latency_ms += latency_ms
        if error:
            self.errors += 1

telemetry = Telemetry()

class LLMClient:
    """
    Production-Ready LLM Client for Aegis v3.6.
    Supports offline mocks, retries, circuit breaking, and telemetry.
    """

    def __init__(self, system_prompt: str) -> None:
        self.offline_mode = os.environ.get("AEGIS_OFFLINE_MODE", "false").lower() == "true"
        self.system_prompt = system_prompt
        self.model = GROQ_MODEL
        
        if self.offline_mode:
            logger.warning("Initializing LLMClient in OFFLINE mock mode.")
            self.client = None
        else:
            api_key = os.environ.get("GROQ_API_KEY")
            if not api_key:
                logger.error("GROQ_API_KEY is not set. Switching to offline mode automatically to avoid crash.")
                self.offline_mode = True
                self.client = None
            else:
                self.client = Groq(api_key=api_key, base_url=LLM_URL if LLM_URL else None)
                
        logger.info("LLMClient v3.6 initialized.")

    @llm_breaker
    @backoff.on_exception(backoff.expo, (RateLimitError, APIError), max_tries=5)
    def _call_api(self, messages: list) -> str:
        """Internal physical call with circuit breaker and backoff."""
        start_time = time.time()
        try:
            completion = self.client.chat.completions.create(
                model=self.model,
                messages=messages,
                temperature=0.1,
                max_tokens=2048,
                response_format={"type": "json_object"},
            )
            latency = (time.time() - start_time) * 1000
            telemetry.record(latency)
            return completion.choices[0].message.content.strip()
        except Exception as e:
            latency = (time.time() - start_time) * 1000
            telemetry.record(latency, error=True)
            raise e

    def _mock_fallback(self) -> dict[str, Any]:
        """Provides deterministic safe JSON for offline mode / CI testing."""
        return {
            "summary": "MOCK MODE ACTIVE",
            "reasoning": "Offline mode triggered this mock response.",
            "actions": [{
                "type": "prompt_next_action",
                "parameters": {"message": "Aegis is operating in offline mode. This is a mock response."},
                "risk_level": "LOW",
                "requires_confirmation": False
            }],
            "requires_approval": True
        }

    def generate_plan(self, user_input: str, max_retries: int = 3, correction_hint: str = None) -> dict[str, Any]:
        """v3.6 Safe Plan Generation."""
        if self.offline_mode:
            return self._mock_fallback()
            
        messages = [
            {"role": "system", "content": self.system_prompt},
            {"role": "user", "content": user_input},
        ]
        
        if correction_hint:
             messages.append({"role": "user", "content": f"Correction hint: {correction_hint}"})
        
        last_error = None
        for attempt in range(1, max_retries + 1):
            try:
                raw_text = self._call_api(messages)
                return json.loads(raw_text)
            
            except json.JSONDecodeError as e:
                last_error = e
                logger.warning(f"LLM returned invalid JSON (attempt {attempt}).")
                messages.append({"role": "assistant", "content": raw_text})
                messages.append({
                    "role": "user", 
                    "content": f"JSON Error: {e}. Fix and return ONLY valid JSON."
                })
            
            except pybreaker.CircuitBreakerError:
                logger.error("LLM Circuit Breaker is OPEN. Aborting.")
                raise RuntimeError("LLM service is currently unavailable (circuit breaker).")
            
            except Exception as e:
                last_error = e
                logger.error(f"API failure (attempt {attempt}): {e}")
                if attempt < max_retries:
                    time.sleep(1)
                
        raise RuntimeError(f"LLM exhausted retries. Last error: {last_error}")

def safe_llm_generate(client: LLMClient, prompt: str) -> dict:
    """Convenience wrapper for safe generation."""
    try:
        return client.generate_plan(prompt)
    except Exception as e:
        logger.error(f"Safe LLM generation failed: {e}")
        return {
            "summary": "Failure",
            "reasoning": str(e),
            "actions": [{"action_type": "prompt_next_action", "parameters": {"message": "Service unavailable."}}]
        }
