"""
Aegis v1.0 — Approval Gate
===========================
Displays proposed action plans in a human-readable format and
requires explicit user confirmation before any execution proceeds.
"""

from __future__ import annotations

import logging
from typing import TYPE_CHECKING

from colorama import Fore, Style

if TYPE_CHECKING:
    from brain.planner import ActionPlan

logger = logging.getLogger(__name__)


# ── Display helpers ──────────────────────────────────────────────────────

def display_plan(plan: ActionPlan) -> None:
    """Pretty-print an ActionPlan to the console with color coding."""
    print()
    print(f"{Fore.CYAN}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━{Style.RESET_ALL}")
    print(f"{Fore.CYAN}  PROPOSED STRATEGY: {plan.summary}{Style.RESET_ALL}")
    print(f"{Fore.CYAN}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━{Style.RESET_ALL}")
    print()

    if not plan.actions:
        print(f"  {Fore.YELLOW}(No actions — informational response){Style.RESET_ALL}")
    else:
        print(f"  {Fore.WHITE}Actions:{Style.RESET_ALL}")
        for i, action in enumerate(plan.actions, 1):
            icon = _action_icon(action.type)
            print(
                f"    {Fore.GREEN}{i}. {icon}  {action.type}{Style.RESET_ALL}"
            )
            if action.value:
                print(f"       └─ value : {Fore.YELLOW}{action.value}{Style.RESET_ALL}")
            if action.target:
                print(f"       └─ target: {Fore.YELLOW}{action.target}{Style.RESET_ALL}")
            if action.params:
                print(f"       └─ params: {Fore.YELLOW}{action.params}{Style.RESET_ALL}")
        print()

    print(f"{Fore.CYAN}{'━' * 60}{Style.RESET_ALL}")


def _action_icon(action_type: str) -> str:
    """Return a Unicode icon for a given action type."""
    icons = {
        "open_application": "🚀",
        "organize_files": "📂",
        "list_duplicates": "🔍",
        "create_file": "📝",
        "rename_file": "✏️",
        "run_powershell": "⚡",
    }
    return icons.get(action_type, "▶️")


# ── Approval prompts ────────────────────────────────────────────────────

def request_approval() -> tuple[bool, str | None]:
    """
    Prompt the user for explicit yes/no approval and capture feedback
    if the plan is rejected.

    Returns
    -------
    tuple[bool, str | None]
        (Approved, Rejection Reason)
    """
    while True:
        response = input(
            f"\n  {Fore.WHITE}Approve this plan? "
            f"({Fore.GREEN}yes{Style.RESET_ALL}/{Fore.RED}no{Style.RESET_ALL}): "
        ).strip().lower()

        if response in ("yes", "y"):
            logger.info("User APPROVED the plan.")
            print(f"  {Fore.GREEN}✔ Plan approved — executing...{Style.RESET_ALL}\n")
            return True, None
            
        if response in ("no", "n"):
            logger.info("User REJECTED the plan.")
            feedback = input(f"  {Fore.YELLOW}Please provide a reason for rejecting the plan: {Style.RESET_ALL}").strip()
            print(f"  {Fore.RED}✘ Plan rejected — no actions taken.{Style.RESET_ALL}\n")
            return False, feedback or "No reason provided"

        print(f"  {Fore.YELLOW}Please type 'yes' or 'no'.{Style.RESET_ALL}")


def request_delete_confirmation(target: str) -> bool:
    """
    Secondary confirmation required for any delete-related action.

    Parameters
    ----------
    target : str
        Description or path of what would be deleted.

    Returns
    -------
    bool
        True if user confirms the deletion, False otherwise.
    """
    print(
        f"\n  {Fore.RED}⚠  DELETION WARNING ⚠{Style.RESET_ALL}"
    )
    print(f"  Target: {Fore.YELLOW}{target}{Style.RESET_ALL}")

    while True:
        response = input(
            f"  {Fore.RED}Confirm deletion? (type 'DELETE' to confirm): {Style.RESET_ALL}"
        ).strip()

        if response == "DELETE":
            logger.info("User confirmed deletion of: %s", target)
            return True
        if response.lower() in ("no", "n", "cancel", ""):
            logger.info("User cancelled deletion of: %s", target)
            return False

        print(f"  {Fore.YELLOW}Type 'DELETE' to confirm or 'no' to cancel.{Style.RESET_ALL}")


def ask_inline_confirmation(summary: str) -> bool:
    """
    v7.0: Prompts for confirmation mid-execution of a plan.
    Used by the 'ask_confirmation' action and high-risk triggers.
    """
    print()
    print(f"  {Fore.MAGENTA}╔══════════════════════════════════════════════════════════╗{Style.RESET_ALL}")
    print(f"  {Fore.MAGENTA}║ {Fore.WHITE}ACTION CONFIRMATION REQUIRED {Fore.MAGENTA}║{Style.RESET_ALL}")
    print(f"  {Fore.MAGENTA}╠══════════════════════════════════════════════════════════╣{Style.RESET_ALL}")
    print(f"  {Fore.MAGENTA}║ {Fore.YELLOW}{summary[:58]:<58} {Fore.MAGENTA}║{Style.RESET_ALL}")
    print(f"  {Fore.MAGENTA}╚══════════════════════════════════════════════════════════╝{Style.RESET_ALL}")
    
    while True:
        choice = input(f"  {Fore.CYAN}Proceed? (y/n): {Style.RESET_ALL}").strip().lower()
        if choice in ('y', 'yes'):
            print(f"  {Fore.GREEN}✔ Proceeding...{Style.RESET_ALL}\n")
            return True
        if choice in ('n', 'no'):
            print(f"  {Fore.RED}✘ Aborted by user.{Style.RESET_ALL}\n")
            return False
        print(f"  {Fore.YELLOW}Please type 'y' or 'n'.{Style.RESET_ALL}")
