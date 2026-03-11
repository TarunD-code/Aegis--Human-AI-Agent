"""
Aegis v5.4 — CLI Response Engine
================================
Centralized logic for rendering clinical and professional AI feedback
directly to the terminal, bypassing UI automation.
"""

from colorama import Fore, Style

class CLIRenderer:
    """
    Handles all direct terminal output for the Aegis Command Center.
    """
    
    @staticmethod
    def display_message(text: str, type: str = "info"):
        """Displays a formatted message to the user."""
        color = Fore.WHITE
        prefix = " "
        
        if type == "success":
            color = Fore.GREEN
            prefix = "  ✅ "
        elif type == "error":
            color = Fore.RED
            prefix = "  ❌ "
        elif type == "warn":
            color = Fore.YELLOW
            prefix = "  ⚠️ "
        elif type == "ai":
            color = Fore.CYAN
            prefix = "  Aegis: "
            
        print(f"{prefix}{color}{text}{Style.RESET_ALL}")

    @staticmethod
    def display_plan(plan_summary: str, actions: list):
        """Displays the proposed execution plan in a professional format."""
        print()
        print(f"{Fore.CYAN}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━{Style.RESET_ALL}")
        print(f"{Fore.CYAN}  PROPOSED STRATEGY: {plan_summary}{Style.RESET_ALL}")
        print(f"{Fore.CYAN}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━{Style.RESET_ALL}")
        print()
        for idx, action in enumerate(actions, 1):
            print(f"    {Fore.WHITE}{idx}. {action.get('description', action.get('type'))}{Style.RESET_ALL}")
        print()
        print(f"{Fore.CYAN}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━{Style.RESET_ALL}")

    @staticmethod
    def display_system_status(status_data: dict):
        """Renders a detailed system status breakdown."""
        print(f"\n  {Fore.CYAN}Aegis System Status:{Style.RESET_ALL}")
        for key, value in status_data.items():
            print(f"    • {Fore.WHITE}{key:20}{Style.RESET_ALL}: {value}")
        print()

renderer = CLIRenderer()
