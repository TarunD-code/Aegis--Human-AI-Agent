"""
Aegis v1.0 — Action Planner
============================
Defines data structures for action plans and provides parsing/validation
of raw JSON output from the AI brain into typed ActionPlan objects.
"""

from __future__ import annotations

import logging
from dataclasses import dataclass, field
from typing import Any

from config import ACTION_WHITELIST

logger = logging.getLogger(__name__)


@dataclass
class Action:
    """Represents a single action within an Aegis plan."""

    type: str
    value: str | None = None
    target: str | None = None
    description: str | None = None
    thought: str = ""           # v7.0: Reasoning BEFORE execution
    reflect: str = ""           # v7.0: Verification AFTER execution
    use_last_result: bool = False
    date_memory_hook: str | None = None
    confidence_score: float = 1.0
    risk_level: str = "LOW"  # LOW, MEDIUM, HIGH, CRITICAL
    requires_confirmation: bool = False
    suggested_safer_alternative: str | None = None
    params: dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> dict[str, Any]:
        """Convert to a JSON-serializable dictionary."""
        return {
            "action_type": self.type,
            "parameters": {
                "value": self.value,
                "target": self.target,
                **self.params
            },
            "risk_level": self.risk_level,
            "requires_confirmation": self.requires_confirmation,
            "suggested_safer_alternative": self.suggested_safer_alternative
        }

    def __str__(self) -> str:
        parts = [f"[{self.type}]"]
        if self.thought:
            parts.append(f"💭 {self.thought}")
        if self.description:
            parts.append(f"({self.description})")
        if self.risk_level != "LOW":
            parts.append(f"[{self.risk_level} RISK]")
        if self.use_last_result:
            parts.append("[CHAIN]")
        if self.confidence_score < 1.0:
            parts.append(f"[CONF={self.confidence_score}]")
        if self.value:
            parts.append(f"value={self.value!r}")
        if self.target:
            parts.append(f"target={self.target!r}")
        if self.date_memory_hook:
            parts.append(f"hook={self.date_memory_hook}")
        if self.params:
            parts.append(f"params={self.params}")
        if self.reflect:
            parts.append(f"🔍 {self.reflect}")
        return " ".join(parts)


@dataclass
class ActionPlan:
    """
    Structured container for an AI-generated action plan.

    Attributes
    ----------
    summary : str
        Human-readable explanation of the plan.
    actions : list[Action]
        Ordered list of actions to execute.
    requires_approval : bool
        Whether the plan needs user confirmation before execution.
    reasoning : str
        The logic behind why this strategy was chosen.
    """

    summary: str
    actions: list[Action]
    requires_approval: bool = True
    reasoning: str = ""

    def to_dict(self) -> dict[str, Any]:
        """Convert to a JSON-serializable dictionary."""
        return {
            "summary": self.summary,
            "reasoning": self.reasoning,
            "actions": [a.to_dict() for a in self.actions],
            "requires_approval": self.requires_approval
        }

    @property
    def is_conversational(self) -> bool:
        """Return True if this plan has no actions (just a chat response)."""
        return len(self.actions) == 0

    def __str__(self) -> str:
        lines = [
            f"Plan: {self.summary}",
            f"Reasoning: {self.reasoning}",
            f"Actions ({len(self.actions)}):",
        ]
        for i, action in enumerate(self.actions, 1):
            lines.append(f"  {i}. {action}")
        lines.append(
            f"Requires approval: {'Yes' if self.requires_approval else 'No'}"
        )
        return "\n".join(lines)


def parse_plan(raw: dict | list) -> ActionPlan:
    """
    Parse and validate a raw JSON dictionary or list into an ActionPlan.
    (Supports v3.1+ JSON array format).
    """
    # Aegis v3.1: Support raw JSON array directly
    if isinstance(raw, list):
        raw = {
            "summary": "Executing structured plan",
            "actions": raw,
            "requires_approval": True
        }

    # --- Validate top-level keys ---
    if not isinstance(raw, dict):
        raise ValueError(f"Expected a JSON object, got {type(raw).__name__}.")

    summary = raw.get("summary")
    if not summary or not isinstance(summary, str):
        raise ValueError("Plan must contain a non-empty 'summary' string.")

    reasoning = raw.get("reasoning", "")
    raw_actions = raw.get("actions", [])
    if not isinstance(raw_actions, list):
        raise ValueError("'actions' must be a list.")

    requires_approval = raw.get("requires_approval", True)

    # --- Parse individual actions ---
    actions: list[Action] = []
    unknown_types: list[str] = []

    for idx, raw_action in enumerate(raw_actions):
        if not isinstance(raw_action, dict):
            raise ValueError(f"Action at index {idx} must be a JSON object.")

        # Aegis v3.5.1: Support both 'type' and 'action_type'
        action_type = (raw_action.get("type") or raw_action.get("action_type") or "").strip()
        if not action_type:
            raise ValueError(f"Action at index {idx} is missing 'type' or 'action_type'.")

        # Check against whitelist
        if action_type not in ACTION_WHITELIST:
            unknown_types.append(action_type)

        # Aegis v3.5.1: Support 'parameters' block
        params_block = raw_action.get("parameters", {})
        merged_params = {**raw_action.get("params", {}), **params_block}
        
        # Extract value/target from either top-level or parameters block
        val = raw_action.get("value") or params_block.get("value")
        tgt = raw_action.get("target") or params_block.get("target")

        # v7.0: Extract cognitive fields
        thought = raw_action.get("thought", "")
        reflect = raw_action.get("reflect", "")
        
        risk = raw_action.get("risk_level", "LOW").upper()
        needs_confirm = bool(raw_action.get("requires_confirmation", False))
        # v7.0 Safety: Force confirmation for HIGH/CRITICAL
        if risk in ("HIGH", "CRITICAL"):
            needs_confirm = True

        actions.append(
            Action(
                type=action_type,
                value=val,
                target=tgt,
                description=raw_action.get("description"),
                thought=thought,
                reflect=reflect,
                use_last_result=raw_action.get("use_last_result", False),
                date_memory_hook=raw_action.get("date_memory_hook"),
                confidence_score=float(raw_action.get("confidence_score", 1.0)),
                risk_level=risk,
                requires_confirmation=needs_confirm,
                suggested_safer_alternative=raw_action.get("suggested_safer_alternative"),
                params=merged_params,
            )
        )

    # v7.0: Warn about unknown types instead of hard-failing
    if unknown_types:
        logger.warning(
            f"Plan contains unknown action type(s): {', '.join(unknown_types)}. "
            f"These may fail at execution time."
        )

    plan = ActionPlan(
        summary=summary,
        actions=actions,
        requires_approval=bool(requires_approval),
        reasoning=reasoning,
    )
    logger.info("Parsed plan with %d action(s).", len(actions))
    return plan
