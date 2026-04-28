from rich.console import Console
from rich.panel import Panel
from rich.text import Text
from rich.markdown import Markdown
from rich.syntax import Syntax
from prompt_toolkit import PromptSession
from prompt_toolkit.styles import Style as PromptStyle
from prompt_toolkit.formatted_text import HTML
import datetime
import asyncio
import sys

# Use standard color system for maximum stability
console = Console(color_system="standard")

class ProfessionalUI:
    def __init__(self):
        self.status = "Idle"
        self.session = PromptSession(style=PromptStyle.from_dict({
            'prompt': 'cyan bold',
            'arrow': 'white',
        }))

    def print_welcome(self):
        welcome_text = Text.assemble(
            (" RECLAW PRO v3.8 ", "bold white on cyan"),
            ("\n Professional Coding Assistant ", "white"),
            ("\n" + "─" * 40, "bright_black"),
            ("\n Mode: ", "white"), ("Direct Action & Code Visibility", "green bold"),
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
        """Stream content directly to the console."""
        sys.stdout.write(delta)
        sys.stdout.flush()
        await asyncio.sleep(0.005)

    def finalize_content(self, full_content):
        """Render the final Markdown properly."""
        console.print("\n")
        console.print(Markdown(full_content))
        console.print("\n" + "─" * 50, style="bright_black")

    def show_tool_start(self, name, args):
        if name == "write_file":
            path = args.get("path", "unknown")
            content = args.get("content", "")
            console.print(Panel(f"[yellow]Writing to:[/yellow] [bold white]{path}[/bold white]", border_style="yellow", title="FILE WRITE"))
            # Show the code being written
            syntax = Syntax(content, "python" if path.endswith(".py") else "javascript" if path.endswith(".js") else "html", theme="monokai", line_numbers=True)
            console.print(Panel(syntax, border_style="bright_black"))
        elif name == "edit_file":
            path = args.get("path", "unknown")
            console.print(Panel(f"[yellow]Editing:[/yellow] [bold white]{path}[/bold white]", border_style="yellow", title="FILE EDIT"))
        elif name == "run_shell":
            cmd = args.get("command", "")
            console.print(Panel(f"[cyan]Executing:[/cyan] [bold white]{cmd}[/bold white]", border_style="cyan", title="SHELL"))
        else:
            console.print(f"\n [yellow]⚙[/yellow] [bold white]{name}[/bold white] {str(args)}")

    def show_tool_end(self, name, result, args=None):
        if name == "run_shell":
            console.print("\n[dim white]Command Output:[/dim white]")
            console.print(Panel(result, border_style="bright_black", padding=(0, 1)))
        elif name in ["read_file", "view_file"]:
            path = args.get("path", "unknown") if args else "unknown"
            console.print(Panel(f"[green]Reading:[/green] [bold white]{path}[/bold white]", border_style="green", title="FILE READ"))
            # Show the content read
            syntax = Syntax(result, "python" if path.endswith(".py") else "javascript" if path.endswith(".js") else "html", theme="monokai", line_numbers=True)
            console.print(Panel(syntax, border_style="bright_black"))

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
