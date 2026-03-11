import logging
from prompt_toolkit import PromptSession
from prompt_toolkit.history import FileHistory
from prompt_toolkit.auto_suggest import AutoSuggestFromHistory
from prompt_toolkit.completion import WordCompleter
from prompt_toolkit.styles import Style as PromptStyle
from colorama import Fore, Style
from interfaces.command_processor import CommandProcessor
from interfaces.status_panel import status_panel

logger = logging.getLogger(__name__)

# Aegis-specific styling for prompt_toolkit
AEGIS_STYLE = PromptStyle.from_dict({
    'prompt': 'cyan bold',
    'completion-menu.completion': 'bg:#008888 #ffffff',
    'completion-menu.completion.current': 'bg:#00aaaa #000000',
    'scrollbar.background': 'bg:#888888',
    'scrollbar.button': 'bg:#222222',
})

class REPLController:
    """
    Advanced REPL Engine using prompt_toolkit for a professional terminal experience.
    """
    def __init__(self, cli_context):
        self.cli = cli_context
        self.processor = CommandProcessor(cli_context)
        
        # Commands for auto-completion
        self.completer = WordCompleter([
            "help", "status", "memory", "history", "clear", "exit", 
            "debug on", "debug off", "config", "agents", "tasks",
            "open notepad", "open chrome", "open calculator",
            "search", "calculate", "remember that", "what is my"
        ], ignore_case=True)

        self.session = PromptSession(
            history=FileHistory('logs/aegis_cli_history.txt'),
            auto_suggest=AutoSuggestFromHistory(),
            completer=self.completer,
            style=AEGIS_STYLE
        )

    def start(self):
        """Starts the interactive REPL loop."""
        print(f"\n{status_panel.render()}")
        
        while True:
            try:
                # Use prompt_toolkit for the input line
                user_input = self.session.prompt([
                    ('class:prompt', '  Aegis ❯ ')
                ]).strip()

                if not user_input:
                    continue

                # Immunity Layer: Wrap execution in try-except
                try:
                    should_continue = self.processor.process(user_input)
                    if not should_continue:
                        break
                except Exception as e:
                    logger.exception("Internal command processing error")
                    print(f"\n  {Fore.RED}Sir, a pipeline error occurred: {e}{Style.RESET_ALL}")
                    print(f"  {Fore.WHITE}I am still standing by for your next request.{Style.RESET_ALL}\n")

            except KeyboardInterrupt:
                continue # User pressed Ctrl+C, just clear line
            except EOFError:
                break # User pressed Ctrl+D, exit
            except Exception as e:
                logger.exception("REPL Controller critical failure")
                print(f"\n  {Fore.RED}Critical Interface Error: {e}{Style.RESET_ALL}")
                break

        print(f"\n  {Fore.WHITE}Session terminated. Goodbye, Sir.{Style.RESET_ALL}")

    def display_output(self, text: str, type: str = "info"):
        """Displays formatted output to the console."""
        color = Fore.WHITE
        if type == "success": color = Fore.GREEN
        elif type == "error": color = Fore.RED
        elif type == "warn": color = Fore.YELLOW
        elif type == "ai": color = Fore.CYAN
        
        print(f"  {color}{text}{Style.RESET_ALL}")
