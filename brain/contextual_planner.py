"""
Aegis v2.0 — Contextual Planner
==================================
Enhanced planner that injects system context, memory history, and
environment state into the Gemini prompt for smarter planning.

CRITICAL RULES:
- Output schema is IDENTICAL to v1 planner (ActionPlan).
- Pre-processing is logged but NEVER creates execution plans directly.
- Gemini still generates the final JSON plan.
- Output passes UNCHANGED to the validator.
- This module contains NO execution logic.
"""

from __future__ import annotations

import json
import logging
import time
import re
from datetime import datetime, timedelta
from typing import Any

from brain.llm.llm_client import LLMClient
from brain.planner import parse_plan, ActionPlan, Action
from brain.intent_engine import IntentClassifier, IntentMetadata
from brain.proactive_engine import ProactiveEngine
from brain.command_normalizer import normalizer
from brain.math_engine import math_engine
from core.state import working_memory
from brain.conversation_engine import ConversationEngine
from brain.plan_validator import normalize_and_validate
from config import CONTEXTUAL_SYSTEM_PROMPT, GROQ_MODEL, get_action_list

logger = logging.getLogger(__name__)


class ContextualPlanner:
    """
    Context-aware planner that enriches Groq prompts with system state,
    running processes, memory history, and environment information.

    Maintains the same interface and output contract as the v1 planner:
    ``generate_plan(user_input) → dict``
    """

    def __init__(self, client: LLMClient | None = None, memory: Any | None = None) -> None:
        """Initialize the contextual Groq client and memory link."""
        self._client = client or LLMClient(system_prompt=CONTEXTUAL_SYSTEM_PROMPT)
        self._memory = memory
        self._intent_engine = IntentClassifier()
        self._proactive_engine = ProactiveEngine()
        self._conversation_engine = ConversationEngine(memory=self._memory)
        logger.info("ContextualPlanner (v5.2) Conversation Intelligence initialized.")

    def generate_plan(
        self,
        user_input: str,
        context: dict[str, Any] | None = None,
    ) -> ActionPlan:
        """
        Orchestrate prompt assembly, Groq call, and v3.1 parsing.
        Now includes v5.7 Normalization and Math routing.
        """
        # 1. Normalize Input (v5.7)
        original_input = user_input
        normalized_input = normalizer.normalize(user_input)
        logger.info(f"Normalized input: '{original_input}' -> '{normalized_input}'")

        # 2. Direct Math Routing (v5.7)
        # Check if it looks like a calculation (e.g. "calculate 5+5" or "5+5")
        math_match = re.search(r"(?:calculate\s+)?([\d\.\s\+\-\*\/\(\)\^x]+)$", normalized_input, re.I)
        if math_match:
            expr = math_match.group(1).strip()
            if len(expr) > 2 and any(op in expr for op in "+-*/^"):
                res = math_engine.evaluate(expr)
                if res is not None:
                    # Update WorkingMemory
                    working_memory.set("last_result", res)
                    logger.info(f"Math Engine evaluated: {expr} = {res}")
                    return ActionPlan(
                        summary=f"Calculated {expr} = {res}",
                        reasoning="Direct math evaluation via MathEngine.",
                        actions=[Action(type="compute_result", value=str(res), params={"expression": expr, "result": res})],
                        requires_approval=False
                    )

        # 3. Contextual Expansion (v5.2)
        session_state = (context or {}).get("session_state") or {}
        intent_metadata = self._intent_engine.classify(user_input)
        
        # If ambiguity is high, ask for clarification immediately
        if intent_metadata.requires_clarification or intent_metadata.ambiguity_score > 0.4:
            # Check if there's a specific clarification question provided
            clarification_msg = intent_metadata.clarification_question
            
            # v6.0 Jarvis Upgrade: Specific clarification logic
            if "MUSIC" in intent_metadata.intent_types and original_input.strip().lower() in ["play music", "play some music"]:
                 clarification_msg = "What type of music would you like?\n\n1. Chill\n2. Pop\n3. Instrumental\n4. Specific song"

            if not clarification_msg:
                 clarification_msg = f"Sir, '{original_input}' is a bit ambiguous. Could you please clarify your intent?"

            return ActionPlan(
                summary="Clarification required.",
                actions=[Action(type="respond_text", params={"text": clarification_msg})],
                requires_approval=False,
                reasoning="Command was ambiguous or lacked necessary parameters."
            )

        # Build the enriched prompt with intent metadata and multi-input visibility
        enriched_prompt = self._build_enriched_prompt(
            original_input=original_input,
            expanded_input=normalized_input,
            context=context or {},
            intent_metadata=intent_metadata
        )
        
        # Aegis v5.0: Unique Plan Tracking
        plan_id = f"plan_{int(time.time())}"
        logger.info(f"[{plan_id}] Starting plan generation for: {user_input[:50]}...")

        from config import SystemConfig
        # GroqClient handles network retries. We handle logic/schema retries here.
        raw_result = self._client.generate_plan(enriched_prompt, max_retries=SystemConfig.MAX_RETRIES)
        
        # Aegis v5.0: Enhanced Plan Validation & Multi-Attempt Regeneration
        is_valid, errors = normalize_and_validate(raw_result)
        
        if not is_valid:
            error_str = ", ".join(errors)
            logger.warning(f"[{plan_id}] Attempt 1 validation failed: {error_str}. Regenerating...")
            
            retry_prompt = (
                f"{enriched_prompt}\n\n"
                f"### CRITICAL SCHEMA VIOLATION DETECTED ###\n"
                f"Your previous plan violated the strict execution contract: {error_str}\n"
                f"REMEDY: Every action MUST contain required parameters in the 'params' block.\n"
                f"Example: 'open_application' requires {{\"application_name\": \"...\"}}.\n"
                f"Please regenerate a valid JSON plan now."
            )
            
            raw_result = self._client.generate_plan(retry_prompt, max_retries=1)
            is_valid, errors = normalize_and_validate(raw_result)
            
            if not is_valid:
                error_str = ", ".join(errors)
                logger.error(f"[{plan_id}] Attempt 2 validation failed: {error_str}. Falling back to safe response.")
                # Aegis v5.0: Graceful fallback instead of crashing
                return ActionPlan(
                    summary="Execution Strategy Error",
                    actions=[Action(
                        type="prompt_next_action",
                        description=f"Sir, I encountered a structural error while planning ({error_str}). How should I proceed?",
                        params={}
                    )],
                    requires_approval=False,
                    reasoning="Strategic validation loop failed twice."
                )

        logger.info(f"[{plan_id}] Plan successfully validated and accepted.")
        # Aegis v3.1+: Use parse_plan to ensure typed Action objects
        return parse_plan(raw_result)


    # ── Prompt construction ──────────────────────────────────────────────

    def _build_enriched_prompt(
        self,
        original_input: str,
        expanded_input: str,
        context: dict[str, Any],
        intent_metadata: IntentMetadata | None = None,
    ) -> str:
        """
        Build a prompt enriched with system context for Groq.
        Includes a safety guard to prevent crashes during prompt construction.
        """
        try:
            parts: list[str] = []
            state = context.get("session_state") or {}

            # Aegis v5.5: Explicit User Message Pillar
            msg_parts = [f"  Original: {original_input}"]
            if expanded_input != original_input:
                msg_parts.append(f"  Expanded (Contextual): {expanded_input}")
            parts.append("[USER MESSAGE]\n" + "\n".join(msg_parts))

            # Aegis v5.5: Conversation Context Pillar
            if intent_metadata:
                parts.append(
                    f"[CONVERSATION CONTEXT]\n"
                    f"  Primary Intents: {', '.join(intent_metadata.intent_types)}\n"
                    f"  Ambiguity Score: {intent_metadata.ambiguity_score:.2f}"
                )
                logger.debug("Context injected: intent metadata.")

            # System metrics
            snapshot = context.get("system_snapshot")
            if snapshot:
                cpu = snapshot.get("cpu_percent", "N/A")
                mem = snapshot.get("memory", {})
                disk = snapshot.get("disk", {})
                parts.append(
                    f"[SYSTEM STATE]\n"
                    f"  CPU: {cpu}%\n"
                    f"  Memory: {mem.get('percent', 'N/A')}% used "
                    f"({self._format_bytes(mem.get('available', 0))} available)\n"
                    f"  Disk: {disk.get('percent', 'N/A')}% used "
                    f"({self._format_bytes(disk.get('free', 0))} free)"
                )
                logger.debug("Context injected: system snapshot.")

            # Running processes
            running = context.get("running_apps")
            if running:
                proc_list = ", ".join(running[:20])
                parts.append(f"[RUNNING APPS]\n  {proc_list}")
                logger.debug("Context injected: %d running processes.", len(running))

            # Foreground app
            fg_app = context.get("foreground_app")
            if fg_app:
                parts.append(f"[FOREGROUND APP]\n  {fg_app}")
                logger.debug("Context injected: foreground app = %s.", fg_app)

            # Open windows
            windows = context.get("open_windows")
            if windows:
                win_list = ", ".join(windows[:15])
                parts.append(f"[OPEN WINDOWS]\n  {win_list}")
                logger.debug("Context injected: %d open windows.", len(windows))

            # Aegis v3.1+: Daily Memory (Persistence)
            daily = context.get("daily_history")
            if daily:
                events = []
                for e in daily[-15:]:
                    cat = e.get('app_category')
                    cat_str = f" ({cat})" if cat else ""
                    events.append(f"  - {e['timestamp'].split('T')[1][:5]} [{e['app']}{cat_str}] {e['action_type']}: {e['command']} -> {e['result']}")
                
                parts.append("[DAILY HISTORY (TODAY)]\n" + "\n".join(events))
                logger.debug("Context injected: %d daily history events with categories.", len(daily))

            # Aegis v3.1: Past History Retrieval
            # v5.7: Fixed NameError (user_input -> original_input)
            if self._memory and any(k in original_input.lower() for k in ["yesterday", "last week", "date", "202"]):
                target_date = None
                if "yesterday" in original_input.lower():
                    target_date = (datetime.now() - timedelta(days=1)).strftime("%Y-%m-%d")
                else:
                    match = re.search(r"\d{4}-\d{2}-\d{2}", original_input)
                    if match:
                        target_date = match.group(0)
                
                if target_date:
                    past_history = self._memory.get_daily_history(target_date)
                    if past_history:
                        events = [
                            f"  - [{e['app']}] {e['action_type']}: {e['command']} -> {e['result']}"
                            for e in past_history[-15:]
                        ]
                        parts.append(f"[PAST HISTORY ({target_date})]\n" + "\n".join(events))
                        logger.debug("Context injected: past history for %s.", target_date)

            # Aegis v3.1: Autonomous Learning & Preferences
            rejected = context.get("recent_rejected")
            learning_parts = []
            
            if rejected:
                reasons = [r.get("reason", "").lower() for r in rejected if r.get("reason")]
                if any("clear" in r or "esc" in r for r in reasons):
                    learning_parts.append("  - LEARNED: User often prefers skipping screen clearing (ESC) in Calculator/CLI.")
                if any("tab" in r or "window" in r for r in reasons):
                    learning_parts.append("  - LEARNED: User prefers reusing existing tabs/windows when possible.")
                
                recent_feedback = [r.get("reason") for r in rejected if r.get("reason")][:3]
                for rf in recent_feedback:
                    learning_parts.append(f"  - LEARNED: User previously rejected a plan because: \"{rf}\"")

            # Aegis v3.2: Macro Detection Logic
            if daily:
                from collections import Counter
                commands = [f"{e['app']}:{e['command']}" for e in daily if e['command']]
                counts = Counter(commands)
                for cmd, count in counts.items():
                    if count >= 3:
                        app, val = cmd.split(":", 1)
                        learning_parts.append(f"  - MACRO SUGGESTION: User repeats '{val}' in {app} frequently ({count} times). Suggest direct macro optimization.")

            if learning_parts:
                parts.append("[LEARNING & PREFERENCES]\n" + "\n".join(learning_parts))
                logger.debug("Context injected: autonomous learning & macro patterns.")

            # Aegis v3.5: User Behavioral Profile
            if self._memory:
                profile = self._memory.get_user_profile()
                if profile:
                    profile_parts = [
                        f"  Organization Preference: {profile.get('organization_preference')}",
                        f"  Email Tone: {profile.get('email_tone_preference')}",
                        f"  Risk Tolerance: {profile.get('risk_tolerance')}",
                        f"  Frequently Rejected: {', '.join(profile.get('frequently_rejected_actions', []))}"
                    ]
                    parts.append("[USER PROFILE]\n" + "\n".join(profile_parts))
                    logger.debug("Context injected: behavioral user profile.")

            # Aegis v3.0: Session State (Result Chaining)
            if state:
                state_parts = []
                last_res = state.get("last_result")
                last_app = state.get("last_app")
                if last_res is not None:
                    state_parts.append(f"  Last calculation result: {last_res}")
                if last_app:
                    state_parts.append(f"  Last active app: {last_app}")
                
                active_app = state.get("active_application")
                if active_app:
                    state_parts.append(f"  CURRENTLY ACTIVE APPLICATION: {active_app}")
                    
                if state_parts:
                    parts.append("[SESSION STATE]\n" + "\n".join(state_parts))
                    logger.debug("Context injected: session state (chaining).")

            # Aegis v5.3: Working Memory Injection
            try:
                from core.state import working_memory
                wm_data = working_memory.get_all()
                if any(wm_data.values()):
                    wm_parts = [f"  {k}: {v}" for k, v in wm_data.items() if v is not None]
                    if wm_parts:
                        parts.append("[WORKING MEMORY]\n" + "\n".join(wm_parts))
            except Exception: pass

            # Aegis v5.4: Task State Injection
            try:
                from core.state import task_manager
                task_context = task_manager.get_context()
                if task_context["active_task"]:
                    task_block = [f"  ACTIVE WORKFLOW: {task_context['active_task']}"]
                    if task_context["task_state"]:
                        task_block.append(f"  Current State: {task_context['task_state']}")
                    if task_context["associated_app"]:
                        task_block.append(f"  Primary App: {task_context['associated_app']}")
                    parts.append("[ACTIVE TASK]\n" + "\n".join(task_block))
            except Exception: pass

            # Last action error
            last_error = state.get("last_error")
            if last_error:
                parts.append(f"[LAST ACTION ERROR]\n  The action '{last_error['action']}' failed with error: \"{last_error['message']}\".")

            # Knowledge Base
            kb = state.get("knowledge_base")
            if kb and (kb["summaries"] or kb["facts"]):
                kb_parts = []
                if kb["summaries"]:
                    kb_parts.append("  Known Summaries:")
                    kb_parts.extend([f"    - {s}" for s in kb["summaries"][-3:]])
                if kb["facts"]:
                    kb_parts.append("  Established Facts:")
                    kb_parts.extend([f"    - {k}: {v}" for k, v in kb["facts"].items()])
                parts.append("[CONVERSATION KNOWLEDGE]\n" + "\n".join(kb_parts))

            # Proactive suggestions
            suggestions = self._proactive_engine.generate_suggestions(context)
            if suggestions:
                s_parts = [f"  - [{s.type}] {s.content}" for s in suggestions]
                parts.append("[PROACTIVE SUGGESTIONS]\n" + "\n".join(s_parts))

            # Assemble final prompt
            context_block = "\n\n".join(parts)
            return (
                f"--- CURRENT CONTEXT ---\n{context_block}\n"
                f"--- END CONTEXT ---\n\n"
                f"User request: {expanded_input}"
            )

        except Exception as exc:
            logger.error(f"Planner Hardening: Prompt construction failed: {exc}")
            # v5.7 Safe Fallback
            return f"[SYSTEM] Context construction failed. Falling back to safe prompt.\nUser request: {expanded_input}"

    @staticmethod
    def _format_bytes(num_bytes: int) -> str:
        """Format byte count to human-readable string."""
        if num_bytes <= 0:
            return "N/A"
        for unit in ("B", "KB", "MB", "GB", "TB"):
            if abs(num_bytes) < 1024.0:
                return f"{num_bytes:.1f} {unit}"
            num_bytes /= 1024.0
        return f"{num_bytes:.1f} PB"
