from rich.console import Console
from rich.panel import Panel
from rich.markdown import Markdown
from rich.text import Text
from rich.live import Live
from rich.spinner import Spinner
from prompt_toolkit import PromptSession
from prompt_toolkit.styles import Style as PromptStyle
from prompt_toolkit.formatted_text import HTML
import time

console = Console()

# Modern Minimalist Style
STYLE = {
    "primary": "bold white",
    "secondary": "dim white",
    "accent": "bold cyan",
    "error": "bold red",
    "success": "bold green",
    "warning": "bold yellow",
    "border": "dim white"
}

WELCOME_TEXT = """
[bold white]ReClaw[/bold white] [dim]v2.0[/dim]
[dim]AI Agentic Coding Assistant[/dim]

[cyan]•[/cyan] [white]Model:[/white] [dim]kimi-k2-instruct[/dim]
[cyan]•[/cyan] [white]Status:[/white] [green]Ready[/green]
[cyan]•[/cyan] [white]Type [bold red]exit[/bold red] to quit[/white]
"""

def print_welcome():
    console.print("\n")
    console.print(Panel(
        WELCOME_TEXT.strip(),
        border_style=STYLE["border"],
        padding=(1, 2),
        subtitle="[dim]Minimalist & Powerful[/dim]"
    ))
    console.print("\n")

def print_response(text: str):
    if text.startswith("[Tool]"):
        # Format tool calls more cleanly
        tool_name = text.split("]")[0].replace("[", "")
        content = text.split("->")[1].strip() if "->" in text else ""
        
        msg = Text()
        msg.append(" ⚙ ", style="cyan")
        msg.append(f"{tool_name}: ", style="bold white")
        msg.append(content, style="dim white")
        console.print(msg)
    else:
        # Markdown response with a bit of padding
        console.print("\n")
        console.print(Markdown(text))
        console.print("\n")

def print_error(text: str):
    console.print(f"\n[bold red]![/bold red] {text}\n")

def print_info(text: str):
    console.print(f"[dim]ℹ {text}[/dim]")

# Prompt Toolkit Session for better input
prompt_style = PromptStyle.from_dict({
    'prompt': 'bold #ffffff',
    'arrow': '#00ffff',
})

session = PromptSession(style=prompt_style)

def get_input() -> str:
    try:
        return session.prompt(HTML('<b>ReClaw</b> <arrow>❯</arrow> '))
    except KeyboardInterrupt:
        raise
    except EOFError:
        raise

class StatusManager:
    """Helper to show a clean loading spinner during AI processing."""
    def __init__(self, message="Thinking..."):
        self.live = Live(Spinner("dots", text=Text(message, style="dim white")), refresh_per_second=10, transient=True)

    def __enter__(self):
        self.live.start()
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.live.stop()
