from rich.console import Console
from rich.panel import Panel
from rich.text import Text
from rich.markdown import Markdown
from rich.live import Live
from prompt_toolkit import PromptSession
from prompt_toolkit.styles import Style as PromptStyle
from prompt_toolkit.formatted_text import HTML
import datetime
import asyncio

# Use standard color system and disable complex layout features for stability
console = Console(color_system="standard")

class ProfessionalUI:
    def __init__(self):
        self.current_tool = None
        self.status = "Idle"
        self.session = PromptSession(style=PromptStyle.from_dict({
            'prompt': 'cyan bold',
            'arrow': 'white',
        }))

    def print_welcome(self):
        welcome_text = Text.assemble(
            (" RECLAW PRO v3.6 ", "bold white on cyan"),
            ("\n Professional Coding Assistant ", "white"),
            ("\n" + "─" * 40, "bright_black"),
            ("\n Mode: ", "white"), ("Ultra-Stable", "green bold"),
            ("\n Type 'exit' to quit.", "bright_black")
        )
        console.print("\n")
        console.print(Panel(welcome_text, border_style="cyan", expand=False))
        console.print("\n")

    def set_status(self, status):
        self.status = status

    def print_user_message(self, content):
        console.print(f"\n[bold cyan]ReClaw[/bold cyan] [white]❯[/white] [bold white]{content}[/bold white]")

    async def stream_content(self, delta):
        """Stream content directly to the console for maximum stability."""
        # We use a simple print for streaming to avoid layout corruption
        console.print(delta, end="", style="white")
        # Small sleep to allow terminal to catch up
        await asyncio.sleep(0.01)

    def finalize_content(self, full_content):
        """Render the final Markdown after streaming is complete."""
        # Clear the line and render properly
        console.print("\n")
        console.print(Markdown(full_content))
        console.print("\n" + "─" * 50, style="bright_black")

    def show_tool_start(self, name, args):
        msg = Text()
        msg.append("\n ⚙ ", style="yellow")
        msg.append(f"Tool: {name} ", style="bold white")
        msg.append(f"({str(args)})", style="dim white")
        console.print(msg)

    def show_tool_end(self, name, result):
        # Optional: show a small success indicator
        pass

    def print_error(self, text):
        console.print(f"\n[bold red]![/bold red] [red]ERROR:[/red] {text}\n")

    async def get_input_async(self):
        try:
            return await self.session.prompt_async(HTML('<cyan><b>ReClaw</b></cyan> ❯ '))
        except (KeyboardInterrupt, EOFError):
            return "exit"

# Global UI instance
ui = ProfessionalUI()

# Compatibility wrappers
def print_welcome():
    ui.print_welcome()

def print_error(text):
    ui.print_error(text)
