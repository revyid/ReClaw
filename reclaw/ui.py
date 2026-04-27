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
[bold white]ReClaw[/bold white] [dim]v2.1[/dim]
[dim]AI Agentic Coding Assistant[/dim]

[cyan]•[/cyan] [white]Model:[/white] [dim]kimi-k2-instruct[/dim]
[cyan]•[/cyan] [white]Status:[/white] [green]Ready (Real-time Streaming)[/green]
[cyan]•[/cyan] [white]Type [bold red]exit[/bold red] to quit[/white]
"""

def print_welcome():
    console.print("\n")
    console.print(Panel(
        WELCOME_TEXT.strip(),
        border_style=STYLE["border"],
        padding=(1, 2),
        subtitle="[dim]Minimalist & Real-time[/dim]"
    ))
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

class StreamingDisplay:
    """Handles real-time display of AI responses and tool calls."""
    def __init__(self):
        self.content = ""
        self.live = None
        self.current_tool = None

    def __enter__(self):
        self.live = Live(Text(""), refresh_per_second=10, transient=False)
        self.live.start()
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        if self.live:
            self.live.stop()
        # Final print to ensure Markdown is rendered properly after streaming
        if self.content:
            console.print(Markdown(self.content))
            console.print("\n")

    def update_content(self, delta: str):
        self.content += delta
        # We don't render Markdown in real-time for performance and stability,
        # instead we show the raw text and render Markdown at the end.
        self.live.update(Text(self.content, style="white"))

    def show_tool_start(self, name: str, args: dict):
        # Print tool calls above the streaming content
        msg = Text()
        msg.append(" ⚙ ", style="cyan")
        msg.append(f"{name}: ", style="bold white")
        msg.append(str(args), style="dim white")
        console.print(msg)

    def show_tool_end(self, name: str, result: str):
        # Optional: show tool result summary
        pass

class StatusManager:
    """Helper to show a clean loading spinner during AI processing."""
    def __init__(self, message="Thinking..."):
        self.live = Live(Spinner("dots", text=Text(message, style="dim white")), refresh_per_second=10, transient=True)

    def __enter__(self):
        self.live.start()
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.live.stop()
