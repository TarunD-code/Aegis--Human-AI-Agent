import logging
from typing import List, Any
from brain.intent_engine import IntentMetadata
from brain.planner import Action, ActionPlan
from core.state import working_memory

logger = logging.getLogger(__name__)

class ExecutionRouter:
    """
    Routes simple intents (MATH, BROWSER, SYSTEM) to specialized engines
    to bypass the expensive LLM planning phase.
    """
    def __init__(self, planner):
        self.planner = planner

    def route(self, user_input: str, intent: IntentMetadata, context: dict) -> ActionPlan:
        """
        Route the command based on detected intent.
        """
        import re as _re

        # 0a. Drive Open Detection (v6.3) — "open d drive", "open c:"
        drive_match = _re.search(r"open\s+([a-zA-Z])\s*(?:drive|:)", user_input, _re.I)
        if drive_match:
            letter = drive_match.group(1).upper()
            path = f"{letter}:\\"
            logger.info(f"Router: Drive open detected → {path}")
            return ActionPlan(
                summary=f"Opening drive {letter}:",
                reasoning="Direct drive path routing.",
                actions=[Action(type="open_application", value="explorer.exe", params={"application_name": f"explorer.exe {path}"})],
                requires_approval=False
            )

        # 0b. Known web shortcuts — gmail, figma, etc.
        web_shortcuts = {
            "gmail": "https://mail.google.com",
            "figma": "https://www.figma.com",
            "github": "https://github.com",
            "chatgpt": "https://chat.openai.com",
            "copilot": "https://copilot.microsoft.com",
        }
        if user_input.lower().startswith("open "):
            target = user_input[5:].strip().lower()
            if target in web_shortcuts:
                url = web_shortcuts[target]
                logger.info(f"Router: Web shortcut detected → {url}")
                return ActionPlan(
                    summary=f"Opening {target}",
                    reasoning="Direct web shortcut routing.",
                    actions=[Action(type="browse_to", value=url, params={"query": url})],
                    requires_approval=False
                )

        # 0c. App Registry Bypass (Jarvis v5.4)
        if user_input.lower().startswith("open "):
            app_name = user_input[5:].strip()
            from core.app_registry import registry
            path = registry.resolve(app_name)
            
            browser_keywords = ["youtube", "google", "facebook", "website", "http", "www"]
            is_browser_target = any(k in app_name.lower() for k in browser_keywords)
            
            if path and not is_browser_target:
                logger.info(f"Router: Directed app launch (registry): {app_name}")
                return ActionPlan(
                    summary=f"Launching {app_name}",
                    reasoning="Direct bypass via static/dynamic registry.",
                    actions=[Action(type="open_application", value=path, params={"application_name": app_name})],
                    requires_approval=False
                )

        primary_intent = intent.intent_types[0] if intent.intent_types else "EXECUTE"
        
        # 1. MATH Routing
        if primary_intent == "MATH" or any(op in user_input for op in ["+", "-", "*", "/"]):
            from brain.math_engine import math_engine
            # Extract expression (simple heuristic)
            expr = user_input.replace("calculate", "").replace("compute", "").strip()
            res = math_engine.evaluate(expr)
            if res is not None:
                working_memory.set("last_result", res)
                logger.info(f"Router: Directed math evaluation: {expr} = {res}")
                return ActionPlan(
                    summary=f"Calculated {expr} = {res}",
                    reasoning="Direct routing to MathEngine.",
                    actions=[Action(type="compute_result", value=str(res), params={"expression": expr, "result": res})],
                    requires_approval=False
                )

        # 2. BROWSER Routing (Jarvis v5.4 Fix)
        if primary_intent == "BROWSER" or "copilot" in user_input.lower():
            logger.info("Router: Directed browser routing.")
            # route_browser in the action handler (which we'll use in the plan)
            # but we need to ensure the action type is browse_to
            query = user_input
            if user_input.lower().startswith("open "):
                query = user_input[5:].strip()
                
            if "copilot" in query.lower():
                query = "https://copilot.microsoft.com"
            
            return ActionPlan(
                summary=f"Routing browser for: {query}",
                reasoning="Direct routing to BrowserRouter.",
                actions=[Action(type="browse_to", value=query, params={"query": query})],
                requires_approval=False
            )

        # 2b. VISION Control Intercepts (Aegis v6.2)
        ui_keywords = ["click", "press", "scroll", "find", "skip", "button"]
        if any(kw in user_input.lower() for kw in ui_keywords):
            cmd = user_input.lower()
            logger.info(f"Router: Vision Interaction Intercepted: {cmd}")
            
            # Translate 'scroll down/up'
            if "scroll" in cmd:
                return ActionPlan(
                    summary=f"Scrolling screen: {cmd}",
                    actions=[Action(type="vision_scroll", value=cmd, params={"direction": cmd})],
                    reasoning="Visual scroll instruction detected.",
                    requires_approval=False
                )
                
            # Assume it's a clicking instruction
            element_name = cmd.replace("click", "").replace("press", "").replace("button", "").strip()
            return ActionPlan(
                summary=f"Visually searching and clicking: '{element_name}'",
                actions=[Action(type="vision_click", value=element_name, params={"target": element_name})],
                reasoning="Visual element interaction detected.",
                requires_approval=False
            )

        # 3. MEMORY Routing (Jarvis v5.4)
        if primary_intent == "MEMORY":
            from memory.user_memory import user_memory
            import re
            
            # Pattern: "remember my X is Y" or "remember that X is Y"
            rem_match = re.search(r"remember (?:my|that) (.*?) is (.*)", user_input, re.I)
            if rem_match:
                key, val = rem_match.groups()
                user_memory.remember(key.strip(), val.strip())
                return ActionPlan(
                    summary=f"Memory updated: {key} remembered.",
                    actions=[], # No system action needed, internal state updated
                    reasoning="Internal UserMemory update."
                )
            
            # Pattern: "what is my X"
            rec_match = re.search(r"what is my (.*)", user_input, re.I)
            if rec_match:
                key = rec_match.group(1).strip()
                val = user_memory.recall(key)
                if val:
                    return ActionPlan(
                        summary=f"Recalled {key}: {val}",
                        actions=[],
                        reasoning="Internal UserMemory recall."
                    )
            
        # 4. SYSTEM Routing (Monitor, Stats, List Apps)
        if primary_intent in ["MONITOR", "SYSTEM"]:
            logger.info("Router: Directed system monitoring.")
            action_type = "system_stats"
            if "list" in user_input or "apps" in user_input or "windows" in user_input:
                action_type = "list_running_apps"
                
            return ActionPlan(
                summary="Retrieving system metrics." if action_type == "system_stats" else "Listing running applications.",
                reasoning="Direct routing to SystemActions.",
                actions=[Action(type=action_type, value="all", params={})],
                requires_approval=False
            )

        # 4b. SYSTEM_APPS Routing (Installed Inventory)
        if primary_intent == "SYSTEM_APPS":
            from core.app_registry import get_installed_applications
            apps = get_installed_applications()
            summary = f"Sir, I have found {len(apps)} installed applications."
            return ActionPlan(
                summary=summary,
                reasoning="Direct routing to AppRegistry.",
                actions=[Action(type="respond_text", params={"text": f"{summary}\n\n" + "\n".join(apps[:20]) + ("\n...and more." if len(apps) > 20 else "")})],
                requires_approval=False
            )

        # 5. MUSIC Routing (v5.5) / Overridden with Vision Workflow
        if primary_intent == "MUSIC":
            return self._route_music(user_input)

        # Fallback to LLM Planner
        logger.info(f"Router: Falling back to LLM Planner for intent: {primary_intent}")
        return self.planner.generate_plan(user_input, context)

    def _route_music(self, command: str) -> ActionPlan:
        """Routes music intent visual browser interactions (v6.2 Vision Flow)."""
        # Extract song name
        clean = command.lower().replace("play", "").replace("music", "").replace("song", "").replace("some", "").strip()
        query = f"{clean} music video" if clean else "music"
        from urllib.parse import quote
        url = f"https://www.youtube.com/results?search_query={quote(query)}"
        
        logger.info(f"Router: Directed visual music playback path: {query}")
        return ActionPlan(
            summary=f"Playing music visually: {query}",
            reasoning="Direct visual search layout interaction.",
            actions=[
                Action(type="respond_text", params={"text": f"Playing music: {query}, Sir."}),
                Action(type="open_application", value="chrome.exe", params={"application_name": "chrome"}),
                Action(type="wait", value=2.0),
                Action(type="browse_to", value=url, params={"query": url}),
                Action(type="wait", value=3.0),
                Action(type="vision_click", value="video-title", params={"target": "video"}), # Click the first video object
                Action(type="wait", value=2.0),
                Action(type="vision_click", value="play", params={"target": "play"}) # Hit play visually if halted
            ],
            requires_approval=False
        )
