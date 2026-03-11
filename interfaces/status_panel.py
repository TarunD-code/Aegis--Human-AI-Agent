import psutil
from colorama import Fore, Style

class StatusPanel:
    """
    Renders a dynamic system status header for the Aegis Command Center.
    """
    @staticmethod
    def render() -> str:
        cpu = psutil.cpu_percent()
        mem = psutil.virtual_memory().percent
        
        # Mocking active agents for now, would integrate with a real agent registry
        active_agents = 1 
        
        panel = [
            f"{Fore.CYAN}╔══════════════════════════════════════╗",
            f"║ {Fore.WHITE}AEGIS COMMAND CENTER{Fore.CYAN}                ║",
            f"║ {Fore.WHITE}Session: Active{Fore.CYAN}                     ║",
            f"║ {Fore.WHITE}CPU: {cpu:>3}%{Fore.CYAN}                            ║",
            f"║ {Fore.WHITE}Memory: {mem:>3}%{Fore.CYAN}                         ║",
            f"║ {Fore.WHITE}Agents Running: {active_agents}{Fore.CYAN}                    ║",
            f"╚══════════════════════════════════════╝{Style.RESET_ALL}"
        ]
        return "\n".join(panel)

# Global instance for easy access
status_panel = StatusPanel()
