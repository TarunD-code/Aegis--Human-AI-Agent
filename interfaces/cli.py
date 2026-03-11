"""
Aegis v5.4 — Professional AI Command Center
===========================================
Advanced interactive CLI with dynamic status, fuzzy auto-complete, 
and professional AI behavioral layers.
"""

from __future__ import annotations

import logging
from colorama import init as colorama_init
from brain.contextual_planner import ContextualPlanner
from brain.mood_detector import detect_mood
from brain.tone_controller import ToneController
from brain.greeting_engine import generate_greeting
from execution.engine import ExecutionEngine
from memory.memory_manager import MemoryManager
from conversation.dialog_controller import DialogController
from security.approval_gate import display_plan, request_approval
from security.validator import validate_plan
from core.state import session_memory as global_session
from interfaces.repl_controller import REPLController

logger = logging.getLogger(__name__)

class AegisCLI:
    """
    Primary interface for Aegis, now as a professional command center.
    Acts as a thin wrapper around REPLController for session management.
    """
    def __init__(self, engine=None, memory=None, session=None, planner=None):
        colorama_init(autoreset=True)
        self._engine = engine or ExecutionEngine()
        self._memory = memory or MemoryManager()
        self._session = session or global_session
        self._tone = ToneController()
        self._dialog = DialogController(tone_controller=self._tone)
        self._planner = planner or ContextualPlanner(memory=self._memory)
        
        # New Jarvis v5.4 Components
        self._repl = REPLController(self)
        self.debug_mode = False

        if not self._session.conversation_context_id:
            import uuid
            self._session.conversation_context_id = str(uuid.uuid4())[:8]

    def run(self):
        """Standard entry point for the CLI."""
        self._display_header()
        print(f"\n  {generate_greeting()}, Sir.\n")
        self._repl.start()
        
    def _display_header(self):
        """Displays the JARVIS-style Command Center Header."""
        try:
            from core import system_inspector
            summary = system_inspector.get_system_summary()
            cpu = summary.get("cpu_percent", "N/A")
            mem = summary.get("memory", {}).get("percent", "N/A")
            agents = 3 # Hardcoded placeholder for now as per design
            
            print(f"╔══════════════════════════════════════╗")
            print(f"║ AEGIS COMMAND CENTER                ║")
            print(f"║ Session: Active                     ║")
            print(f"║ CPU: {cpu}%{ ' ' * (27 - len(str(cpu))) }║")
            print(f"║ Memory: {mem}%{ ' ' * (24 - len(str(mem))) }║")
            print(f"║ Agents Running: {agents}{ ' ' * (20 - len(str(agents))) }║")
            print(f"║ Active Task: System Ready           ║")
            print(f"╚══════════════════════════════════════╝")
        except Exception:
            pass

    def _process_command(self, user_input: str):
        # 1. Retrieve Mood State (Detection moved to command_processor)
        try:
            from brain.mood_detector import MoodProfile
            current_mood_type = self._session.get_metadata("current_mood")
            if not current_mood_type:
                current_mood_type = "neutral"
            mood = MoodProfile(mood_type=current_mood_type)
        except Exception as e:
            logger.error(f"Mood fallback failed: {e}")
            from brain.mood_detector import MoodProfile
            mood = MoodProfile(mood_type="neutral")
            
        # 2. Intent & Routing
        from brain.intent_engine import IntentClassifier
        from brain.execution_router import ExecutionRouter
        from core.state import working_memory
        
        # Session Awareness: Handle "previous result"
        if "previous result" in user_input.lower():
            last_res = working_memory.get("last_result")
            if last_res is not None:
                user_input = user_input.lower().replace("previous result", str(last_res))
                self._repl.display_output(f"Using previous result: {last_res}", type="info")
        
        classifier = IntentClassifier()
        intent = classifier.classify(user_input)
        
        context = self._gather_context()
        router = ExecutionRouter(planner=self._planner)
        
        # Interaction Layer: Conversational Response (Jarvis Style)
        if intent.intent_types and intent.intent_types[0] == "EXECUTE":
             self._repl.display_output(f"Certainly, Sir. I'll get started on that right away.", type="ai")
        else:
             self._repl.display_output(f"Of course. Let me look into that for you.", type="ai")
        
        plan = router.route(user_input, intent, context)

        # 3. Security & Risk Approval (v6.0 Jarvis)
        from security.risk_assessor import requires_approval as check_risk
        
        is_safe, warnings = validate_plan(plan)
        if not is_safe:
            self._repl.display_output("Sir, the plan failed security validation:", type="error")
            for w in warnings: self._repl.display_output(f"• {w}", type="error")
            return

        if plan.actions:
            display_plan(plan)
            
            # v6.0 Risk Approval Check
            if plan.requires_approval or check_risk(intent):
                self._repl.display_output("Sir, this is a high-risk command.", type="warn")
                approved, _ = request_approval()
                if not approved:
                    self._repl.display_output("Operation cancelled, Sir.", type="warn")
                    return

        # Developer Debug Mode
        if self.debug_mode:
            self._repl.display_output("\n[DEBUG] Intent: " + str(intent.intent_types), type="warn")
            self._repl.display_output("[DEBUG] Summary: " + plan.summary, type="warn")

        # 5. Execution Loop
        for idx, action in enumerate(plan.actions, 1):
            res = self._engine.execute(action)
            
            # Audit and Result Tracking
            if not res.success:
                self._repl.display_output(f"Action {idx} failed: {res.message}", type="error")
                break
            
            # Professional Execution Feedback
            toned_output = self._tone.format_response(
                action_type=action.type,
                message=res.message,
                success=res.success,
                risk_level=getattr(action, "risk_level", "LOW") or "LOW",
                mood=mood,
                action_description=getattr(action, "description", "") or "",
            )
            print(f"  {toned_output}")

        # 6. Smooth Conclusion & Proactive Follow-up
        completion_msg = self._tone.format_completion(mood)
        self._repl.display_output(completion_msg, type="success")
        
        # Follow-up question loop based on context
        if intent.intent_types and "MUSIC" in intent.intent_types:
             self._repl.display_output("Would you like me to queue another song, Sir?", type="ai")
        elif plan.actions and res and getattr(res, "success", False):
             self._repl.display_output("Anything else I can assist with, Sir?", type="ai")
        else:
             self._repl.display_output("How else may I be of service, Sir?", type="ai")

    def _gather_context(self):
        """
        Aggregates system and session context for the planner. 
        Aegis v5.6: Mandatory fault tolerance.
        """
        from datetime import datetime
        try:
            from core import system_inspector
            from core.window_tracker import tracker as window_tracker
            
            # Safe metrics gathering
            system_summary = system_inspector.get_system_summary()
            window_context = window_tracker.get_context()
            
            return {
                "system_snapshot": system_summary,
                "running_apps": system_inspector.get_running_apps(),
                "installed_apps_count": system_summary.get("installed_count", 0),
                "foreground_app": window_context.get("active_window_title", "Unknown"),
                "foreground_process": window_context.get("active_window_process", "Unknown"),
                "daily_history": self._memory.get_daily_history(datetime.now().strftime("%Y-%m-%d")),
                "session_state": {
                    "current_mood": self._session.get_metadata("current_mood")
                }
            }
        except Exception as e:
            logger.error(f"CLI: Failed to gather context: {e}")
            # Robust fallback to empty/safe context
            return {
                "system_snapshot": {},
                "running_apps": [],
                "foreground_app": "Unknown",
                "daily_history": [],
                "session_state": {"current_mood": "neutral"}
            }
