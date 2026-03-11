"""
Aegis v2.0 — Groq Client
========================
Wraps the Groq SDK to send structured prompts to Groq (llama-3.3-70b-versatile)
and receive JSON action plans.
"""

import json
import logging
import time
from typing import Any
import backoff
import pybreaker
from groq import Groq, RateLimitError, APIError
from config import GROQ_API_KEY, GROQ_MODEL, LLM_URL
from logs.logger import get_logger

logger = get_logger(__name__)

# Circuit Breaker: Open after 5 failures in 60s, stay open for 30s
llm_breaker = pybreaker.CircuitBreaker(fail_max=5, reset_timeout=30)

class GroqClient:
    """
    Production-Ready Groq Client with Resilience.
    """

    def __init__(self, system_prompt: str) -> None:
        if not GROQ_API_KEY:
            raise ValueError("GROQ_API_KEY is not set.")
        self.client = Groq(api_key=GROQ_API_KEY, base_url=LLM_URL if LLM_URL else None)
        self.model = GROQ_MODEL
        self.system_prompt = system_prompt
        logger.info("GroqClient v3.5.4 initialized.")

    @llm_breaker
    @backoff.on_exception(backoff.expo, RateLimitError, max_tries=5)
    def _call_groq(self, messages: list) -> str:
        """Internal call with circuit breaker and backoff."""
        completion = self.client.chat.completions.create(
            model=self.model,
            messages=messages,
            temperature=0.1,
            max_tokens=2048,
            response_format={"type": "json_object"},
        )
        return completion.choices[0].message.content.strip()

    def generate_plan(self, user_input: str, max_retries: int = 3) -> dict[str, Any]:
        """v3.5.4 Safe Plan Generation."""
        messages = [
            {"role": "system", "content": self.system_prompt},
            {"role": "user", "content": user_input},
        ]
        
        last_error = None
        for attempt in range(1, max_retries + 1):
            try:
                raw_text = self._call_groq(messages)
                return json.loads(raw_text)
            
            except json.JSONDecodeError as e:
                last_error = e
                logger.warning(f"Groq returned invalid JSON (attempt {attempt}).")
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
                logger.error(f"Groq API failure (attempt {attempt}): {e}")
                if attempt < max_retries:
                    time.sleep(1)
                
        raise RuntimeError(f"LLM exhausted retries. Last error: {last_error}")

def safe_llm_generate(client: GroqClient, prompt: str) -> dict:
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
