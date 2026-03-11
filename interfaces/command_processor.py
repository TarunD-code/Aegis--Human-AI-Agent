import logging
import sys
from colorama import Fore, Style
from typing import Optional

logger = logging.getLogger(__name__)

class CommandProcessor:
    """
    Handles built-in CLI commands and routes system/AI requests.
    """
    def __init__(self, cli_context):
        self.cli = cli_context
        self.commands = {
            "help": self._cmd_help,
            "status": self._cmd_status,
            "memory": self._cmd_memory,
            "history": self._cmd_history,
            "clear": self._cmd_clear,
            "exit": self._cmd_exit,
            "quit": self._cmd_exit,
            "debug": self._cmd_debug,
            "config": self._cmd_config,
            "agents": self._cmd_agents,
            "tasks": self._cmd_tasks,
        }

    def process(self, user_input: str) -> bool:
        """
        Process a user command. Returns True if CLI should continue, False to exit.
        """
        parts = user_input.strip().split()
        if not parts:
            return True

        cmd = parts[PartIdx := 0].lower()
        args = parts[PartIdx + 1:]

        if cmd in self.commands:
            res = self.commands[cmd](args)
            import gc
            gc.collect()
            return res

        # If not a built-in command, it's an AI/Pipeline command
        self.cli._process_command(user_input)
        import gc
        gc.collect()
        return True

    def _cmd_help(self, args) -> bool:
        if args and args[0].lower() == "memory":
            print(f"\n  {Fore.CYAN}Aegis Memory System Help{Style.RESET_ALL}")
            print(f"  Aegis uses a persistent SQLite-backed Fact Store.")
            print(f"  - Use 'remember my [X] is [Y]' to store a fact.")
            print(f"  - Use 'what is my [X]' to recall it.")
            print(f"  - Built-in command 'memory' lists all known facts.\n")
            return True
        
        if args and args[0].lower() == "status":
            print(f"\n  {Fore.CYAN}Aegis Status Help{Style.RESET_ALL}")
            print(f"  Displays real-time system metrics and Aegis health.")
            print(f"  - CPU/Memory usage monitoring.")
            print(f"  - Active background agents state.")
            print(f"  - Planner and Routing availability.\n")
            return True

        print(f"\n  {Fore.CYAN}Aegis Command Center — Intelligent Help System{Style.RESET_ALL}")
        print(f"  Available Commands:")
        print(f"    {Fore.YELLOW}status{Style.RESET_ALL}   - View system health and hardware metrics")
        print(f"    {Fore.YELLOW}memory{Style.RESET_ALL}   - View/Manage persistent user context")
        print(f"    {Fore.YELLOW}history{Style.RESET_ALL}  - Inspect session interaction logs")
        print(f"    {Fore.YELLOW}clear{Style.RESET_ALL}    - Reset conversational and session context")
        print(f"    {Fore.YELLOW}debug{Style.RESET_ALL}    - Toggle dev mode: prompt/routing transparency")
        print(f"    {Fore.YELLOW}config{Style.RESET_ALL}   - Inspect core system parameters")
        print(f"    {Fore.YELLOW}agents{Style.RESET_ALL}   - List active autonomous agents")
        print(f"    {Fore.YELLOW}tasks{Style.RESET_ALL}    - Monitor pending background operations")
        print(f"    {Fore.YELLOW}exit{Style.RESET_ALL}     - Securely shutdown the Aegis interface")
        print(f"\n  Type 'help [command]' for specialized documentation.\n")
        return True

    def _cmd_status(self, args) -> bool:
        from interfaces.status_panel import status_panel
        print(f"\n{status_panel.render()}")
        return True

    def _cmd_memory(self, args) -> bool:
        from memory.user_memory import user_memory
        facts = user_memory.list_all()
        print(f"\n  {Fore.CYAN}Persistent User Memory:{Style.RESET_ALL}")
        if not facts:
            print(f"    No facts stored yet, Sir.")
        for k, v in facts.items():
            print(f"    • {Fore.WHITE}{k}{Style.RESET_ALL}: {v}")
        print()
        return True

    def _cmd_history(self, args) -> bool:
        print(f"\n  {Fore.CYAN}Command History:{Style.RESET_ALL}")
        # Command history is handled by prompt_toolkit, but we could list internal logs here
        print(f"    Use arrow keys to navigate history, Sir.\n")
        return True

    def _cmd_clear(self, args) -> bool:
        self.cli._session.reset()
        print(f"  {Fore.GREEN}✔ Session context reset, Sir.{Style.RESET_ALL}\n")
        return True

    def _cmd_exit(self, args) -> bool:
        print(f"\n  {Fore.WHITE}Shutting down Aegis. Goodbye, Sir.{Style.RESET_ALL}")
        sys.exit(0)

    def _cmd_debug(self, args) -> bool:
        if not args:
            state = "ON" if getattr(self.cli, "debug_mode", False) else "OFF"
            print(f"  Debug mode is currently {state}.")
            return True
        
        if args[0].lower() == "on":
            self.cli.debug_mode = True
            print(f"  {Fore.GREEN}Debug mode ENABLED.{Style.RESET_ALL}")
        else:
            self.cli.debug_mode = False
            print(f"  {Fore.YELLOW}Debug mode DISABLED.{Style.RESET_ALL}")
        return True

    def _cmd_config(self, args) -> bool:
        from config import SystemConfig
        print(f"\n  {Fore.CYAN}Aegis System Configuration (v{SystemConfig.VERSION}):{Style.RESET_ALL}")
        print(f"    Max Retries: {SystemConfig.MAX_RETRIES}")
        print(f"    Retry Delay: {SystemConfig.RETRY_DELAY}s")
        print(f"    Window Tracking: {SystemConfig.WINDOW_TRACKING_ENABLED}")
        print(f"    Fuzzy Normalizer: {SystemConfig.FUZZY_NORMALIZER_ENABLED}\n")
        return True

    def _cmd_agents(self, args) -> bool:
        print(f"\n  {Fore.CYAN}Active Agents:{Style.RESET_ALL}")
        print(f"    • {Fore.WHITE}Core Orchestrator{Style.RESET_ALL} (Primary)")
        print(f"    • {Fore.WHITE}Window Tracker{Style.RESET_ALL} (Active)\n")
        return True

    def _cmd_tasks(self, args) -> bool:
        print(f"\n  {Fore.CYAN}Background Tasks:{Style.RESET_ALL}")
        print(f"    No active tasks, Sir.\n")
        return True

    def _cmd_plugin(self, args) -> bool:
        """Stub for future plugin gateway."""
        print(f"  {Fore.YELLOW}Plugin Gateway is not yet implemented in v5.4.{Style.RESET_ALL}")
        return True
