"""
Aegis v4.0 — Execution Engine
===============================
Dispatches validated and approved action plans to the appropriate
action handlers and collects results. Now with verification integration.
"""

from __future__ import annotations

import logging
from typing import TYPE_CHECKING
from colorama import Fore, Style
from execution.actions import ACTION_REGISTRY
from execution.actions.app_actions import ExecutionResult

if TYPE_CHECKING:
    from brain.planner import Action, ActionPlan

logger = logging.getLogger(__name__)

class ExecutionEngine:
    """
    Executes approved action plans by dispatching actions to handlers.
    In v4.0, verification is handled within the action handlers themselves
    (see ui_actions.py) or via the VerificationEngine.
    """

    def _render_message(self, message: str, data: dict) -> str:
        """Replaces {{key}} placeholders with values from data."""
        if not message: return message
        import re
        for key, value in data.items():
            placeholder = f"{{{{{key}}}}}"
            if placeholder in message:
                message = message.replace(placeholder, str(value))
        return message

    def execute(self, action: Action, attempt: int = 1) -> ExecutionResult:
        """
        Execute a single action by dispatching to its registered handler.
        Includes v5.4 Resilience: Centralized Retry & Fallback.
        """
        if action.risk_level in ["HIGH", "CRITICAL"]:
            self._log_risk(action)

        # Aegis v5.5 Synchronized Registry
        from config import ACTION_ALIASES
        canonical_type = ACTION_ALIASES.get(action.type, action.type)
        handler = ACTION_REGISTRY.get(canonical_type)

        if handler is None:
            logger.warning(f"ACTION REGISTRY VALIDATION FAILED: No handler registered for '{action.type}'.")
            return ExecutionResult(
                success=False,
                message=f"Sir, I do not have a registered handler for the action '{action.type}'. I will fallback to a verbal explanation.",
                data={"action_type": action.type, "fallback_required": True}
            )

        from config import SystemConfig
        
        for attempt_idx in range(1, SystemConfig.MAX_RETRIES + 1):
            try:
                # v7.0 Security & Safety Validation
                from security.validator import validate_action
                is_allowed, needs_conf, err_msg = validate_action(action)
                
                if not is_allowed:
                    logger.error(f"SECURITY BLOCK: {err_msg}")
                    return ExecutionResult(success=False, message=f"Sir, for security reasons, I am not allowed to perform the action: {action.type}.")

                if needs_conf:
                    from security.approval_gate import ask_inline_confirmation
                    summary = action.params.get("description") or action.description or f"Perform {action.type}?"
                    if not ask_inline_confirmation(summary):
                        logger.warning(f"USER REJECTED action: {action.type}")
                        return ExecutionResult(success=False, message="Action cancelled by user, Sir.")

                logger.info(f"Dispatching action: {action.type} (Attempt {attempt_idx}/{SystemConfig.MAX_RETRIES})")
                
                # v7.0: Dynamic Variable Resolution from all Working Memory keys
                from execution.variable_resolver import resolve_variables
                from core.state import working_memory
                
                context = working_memory.get_all()
                # Ensure result1, result2, etc. are synced if missing from get_all
                count = working_memory.get("math_result_count", 0)
                for i in range(1, count + 1):
                    rk = f"result{i}"
                    if rk not in context:
                        context[rk] = working_memory.get(rk)

                if action.value and isinstance(action.value, str):
                    action.value = resolve_variables(action.value, context)
                if isinstance(action.params, dict):
                    for k, v in action.params.items():
                        if isinstance(v, str):
                            action.params[k] = resolve_variables(v, context)
                
                # v5.7: Resolve via registry if it's an app-related action
                if action.type in ["open_application", "focus_application", "switch_application"]:
                    from core.app_registry import registry
                    app_name = action.params.get("application_name") or action.value
                    if app_name:
                        resolved_path = registry.resolve(app_name)
                        if action.type == "open_application":
                            action.value = resolved_path
                        logger.debug(f"Resolved app via registry: {app_name} -> {resolved_path}")

                import time
                start_time = time.time()
                result = handler(action)
                duration = (time.time() - start_time) * 1000
                
                # --- v5.4 Conflict Resolution ---
                if result.message == "CONFLICT_REQUIRED":
                    from execution.conflict_resolver import handle_conflict_decision
                    # Default: reuse if not specified. In interactive mode, the CLI handles this.
                    decision = action.params.get("decision", "reuse")
                    logger.info(f"Conflict detected for {action.type}. Applying strategy: {decision}")
                    
                    if handle_conflict_decision(action.params.get("application_name") or action.value, decision):
                        # If reuse was successful, we consider it a success
                        if decision == "reuse":
                            result = ExecutionResult(success=True, message=f"Reused existing window for '{action.value}'.")
                        else:
                            # Re-run for 'new'
                            action.params["decision"] = "new"
                            result = handler(action)
                    else:
                        result = ExecutionResult(success=False, message="Operation cancelled due to conflict.")

                # v7.0: Context Buffer & Action Logging
                try:
                    from core.state import working_memory
                    working_memory.push_action(action.type, action.params, result.__dict__)
                    
                    from logs.action_logger import action_logger
                    import pyautogui
                    import pygetwindow as gw
                    
                    win_title = ""
                    try:
                        active_win = gw.getActiveWindow()
                        if active_win: win_title = active_win.title
                    except Exception: pass
                    
                    action_logger.log_action(
                        action_type=action.type,
                        params=action.params,
                        success=result.success,
                        message=result.message,
                        duration_ms=duration,
                        window_title=win_title,
                        cursor_position=pyautogui.position(),
                        error=result.message if not result.success else ""
                    )
                except Exception as e:
                    logger.error(f"Post-execution logging failed: {e}")

                if result.success:
                    result.message = self._render_message(result.message, result.data)
                    return self._process_success(action, result)

                # --- Resilience Logic ---
                if attempt_idx < SystemConfig.MAX_RETRIES:
                    logger.warning(f"Action '{action.type}' failed: {result.message}. Retrying...")
                    
                    # v7.0 Failure Diagnostics
                    try:
                        from agents.vision_agent import vision_agent
                        screenshot_path = vision_agent.hub.capture_screenshot()
                        result.data["diagnostic_screenshot"] = screenshot_path
                        
                        import psutil
                        procs = [p.name() for p in psutil.process_iter(['name'])][:20]
                        result.data["active_processes"] = procs
                    except Exception as e:
                        logger.debug(f"Diagnostic capture failed: {e}")

                    if action.type == "focus_application":
                        from brain.planner import Action as ActionClass
                        open_action = ActionClass(type="open_application", value=action.value, params=action.params)
                        return self.execute(open_action, attempt=attempt_idx + 1)
                    
                    if action.type in ["type_text", "click", "hotkey"]:
                        app_name = action.params.get("application_name")
                        if app_name:
                            logger.info(f"Refocusing {app_name} before retry {attempt_idx+1}")
                            from execution.ui_automation.window_focus import focus_window
                            focus_window(app_name)
                    
                    time.sleep(SystemConfig.RETRY_DELAY * attempt_idx)
                    continue
                
                return result

            except Exception as exc:
                logger.error("Unhandled exception in handler for '%s': %s", action.type, exc)
                if attempt_idx < SystemConfig.MAX_RETRIES:
                    import time
                    time.sleep(SystemConfig.RETRY_DELAY * attempt_idx)
                    continue
                
                return ExecutionResult(
                    success=False,
                    message=f"Sir, the action '{action.type}' encountered a serious error: {exc}",
                    data={"action_type": action.type}
                )
        
        return ExecutionResult(success=False, message="Max retries reached.")

    def _process_success(self, action: Action, result: ExecutionResult) -> ExecutionResult:
        """Centralized success processing for state tracking."""
        # Success tracking
        if result.success:
            if action.type in ["open_application", "focus_application"]:
                app_name = action.params.get("application_name") or action.value
                if app_name:
                    try:
                        from core.state import session_memory
                        session_memory.active_application = app_name
                        logger.info(f"Updated active application context: {app_name}")
                    except (ImportError, AttributeError): pass
            
            # v5.3 + v5.4: Formal Working Memory & Task Manager Integration
            try:
                from core.state import working_memory, task_manager
                # Update active_application from any action that specifies it
                app_name = action.params.get("application_name") or (action.value if action.type in ["open_application", "focus_application"] else None)
                if app_name:
                    working_memory.set("active_application", app_name)

                if action.type == "type_text":
                    text = action.params.get("text") or action.value
                    working_memory.set("last_text_written", text)
                    task_manager.update_task("Writing", state="typing", app=app_name)
                elif action.type == "search_web":
                    query = action.params.get("query") or action.value
                    working_memory.set("last_search_query", query)
                    task_manager.update_task("Research", state="searching")
                elif action.type == "compute_result":
                    res_val = result.data.get("result")
                    working_memory.set("last_result", res_val)
                    from core.state import session_memory
                    if res_val is not None: session_memory.last_result = res_val
                    task_manager.update_task("Calculation", state=f"result={res_val}")
                elif action.type in ["open_application", "focus_application"] and app_name:
                    task_manager.update_task("Navigation", state="focused", app=app_name)

                # v5.6: Behavioral Pattern Learning
                current_app = working_memory.get("active_application")
                action_key = f"{current_app}:{action.type}" if current_app else action.type
                
                last_action_key = working_memory.get("last_action_key")
                if last_action_key:
                    from core.state import memory_manager
                    memory_manager.record_transition(last_action_key, action_key)
                
                working_memory.set("last_action_key", action_key)
            except (ImportError, AttributeError):
                pass
            
            # Legacy Context Tracking (v5.2)
            try:
                from core.state import session_memory
                if action.type == "type_text":
                    text = action.params.get("text") or action.value
                    if text: session_memory.last_typed = text
                elif action.type == "compute_result":
                    query = action.params.get("query") or action.value
                    if query: session_memory.browser_context["last_search"] = query
                elif action.type == "compute_result":
                    res_val = result.data.get("result")
                    if res_val is not None: session_memory.last_result = res_val
            except (ImportError, AttributeError): pass

        return result

    def execute_action(self, action: Action) -> ExecutionResult:
        """Compatibility wrapper."""
        return self.execute(action)

    def execute_plan(self, plan: ActionPlan) -> list[ExecutionResult]:
        """Execute all actions in a plan sequentially."""
        results: list[ExecutionResult] = []
        
        print(f"  {Fore.CYAN}⏳ Executing Strategy: {plan.summary}{Style.RESET_ALL}\n")

        for idx, action in enumerate(plan.actions, 1):
            logger.info("Executing action %d/%d: %s", idx, len(plan.actions), action.type)
            
            result = self.execute(action)
            result.data["action_type"] = action.type
            results.append(result)
            self._print_result(idx, result)

            if not result.success:
                is_optional = action.params.get("optional", False)
                if is_optional:
                    logger.warning("Optional action %d failed, but plan continues.", idx)
                    continue
                
                logger.error(f"Stop sequence: Action {idx} failed.")
                break

        return results

    def _log_risk(self, action: Action) -> None:
        """Log HIGH/CRITICAL actions."""
        import os
        from datetime import datetime, timezone
        
        log_dir = "logs"
        if not os.path.exists(log_dir): os.makedirs(log_dir)
            
        log_file = os.path.join(log_dir, "risk_log.txt")
        timestamp = datetime.now(tz=timezone.utc).isoformat()
        
        try:
            with open(log_file, "a", encoding="utf-8") as f:
                f.write(f"[{timestamp}] [{action.risk_level}] {action.type}: {action.description}\n")
        except Exception as e:
            logger.error("Failed to write to risk_log: %s", e)

    @staticmethod
    def _print_result(idx: int, result: ExecutionResult) -> None:
        """Print a single action result."""
        if result.success:
            icon = f"{Fore.GREEN}✔{Style.RESET_ALL}"
            color = Fore.WHITE
        else:
            icon = f"{Fore.RED}✘{Style.RESET_ALL}"
            color = Fore.RED

        print(f"  {icon} [{idx}] {result.action_type}: {color}{result.message}{Style.RESET_ALL}")
