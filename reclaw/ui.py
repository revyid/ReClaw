from rich.console import Console
from rich.panel import Panel
from rich.layout import Layout
from rich.live import Live
from rich.text import Text
from rich.markdown import Markdown
from rich.table import Table
from rich.spinner import Spinner
from prompt_toolkit import PromptSession
from prompt_toolkit.styles import Style as PromptStyle
from prompt_toolkit.formatted_text import HTML
import datetime

console = Console()

# Professional Theme
THEME = {
    "bg": "on #121212",
    "primary": "#ffffff",
    "secondary": "#888888",
    "accent": "#00d7ff",
    "success": "#00ff00",
    "error": "#ff0000",
    "tool": "#ffaf00"
}

class ProfessionalUI:
    def __init__(self):
        self.history = []
        self.current_content = ""
        self.current_tool = None
        self.status = "Idle"
        self.layout = self._create_layout()
        self.live = None

    def _create_layout(self):
        layout = Layout()
        layout.split_column(
            Layout(name="header", size=3),
            Layout(name="body"),
            Layout(name="footer", size=3)
        )
        layout["body"].split_row(
            Layout(name="chat", ratio=3),
            Layout(name="sidebar", ratio=1)
        )
        return layout

    def _get_header(self):
        grid = Table.grid(expand=True)
        grid.add_column(justify="left", ratio=1)
        grid.add_column(justify="right", ratio=1)
        grid.add_row(
            Text(" RECLAW PRO v3.0", style=f"bold {THEME['accent']}"),
            Text(datetime.datetime.now().strftime("%H:%M:%S"), style=THEME["secondary"])
        )
        return Panel(grid, style=f"white {THEME['bg']}", border_style=THEME["secondary"])

    def _get_footer(self):
        status_color = THEME["success"] if self.status == "Idle" else THEME["accent"]
        return Panel(
            Text(f" STATUS: {self.status}", style=f"bold {status_color}"),
            style=f"white {THEME['bg']}",
            border_style=THEME["secondary"]
        )

    def _get_sidebar(self):
        table = Table(show_header=False, expand=True, box=None)
        table.add_row(Text("TOOLS ACTIVE", style="bold white"))
        table.add_row(Text("─" * 15, style=THEME["secondary"]))
        
        if self.current_tool:
            table.add_row(Text(f"⚙ {self.current_tool}", style=THEME["tool"]))
        else:
            table.add_row(Text("None", style=THEME["secondary"]))
            
        return Panel(table, title="System", border_style=THEME["secondary"])

    def _get_chat(self):
        chat_renderable = Table.grid(expand=True)
        chat_renderable.add_column()
        
        # Show last 5 interactions for context in the live view
        for msg in self.history[-5:]:
            if msg["role"] == "user":
                chat_renderable.add_row(Text(f"\n❯ {msg['content']}", style=f"bold {THEME['accent']}"))
            else:
                chat_renderable.add_row(Markdown(msg["content"]))
        
        # Show current streaming content
        if self.current_content:
            chat_renderable.add_row(Text("\n" + self.current_content, style="white"))
            
        return Panel(chat_renderable, title="Workspace", border_style=THEME["secondary"])

    def update_display(self):
        self.layout["header"].update(self._get_header())
        self.layout["footer"].update(self._get_footer())
        self.layout["sidebar"].update(self._get_sidebar())
        self.layout["chat"].update(self._get_chat())

    def __enter__(self):
        self.live = Live(self.layout, refresh_per_second=10, screen=True)
        self.live.start()
        self.update_display()
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        if self.live:
            self.live.stop()

    def set_status(self, status):
        self.status = status
        self.update_display()

    def add_user_message(self, content):
        self.history.append({"role": "user", "content": content})
        self.update_display()

    def update_content(self, delta):
        self.current_content += delta
        self.update_display()

    def finalize_content(self):
        if self.current_content:
            self.history.append({"role": "assistant", "content": self.current_content})
            self.current_content = ""
        self.update_display()

    def set_tool(self, name):
        self.current_tool = name
        self.update_display()

# Global UI instance for simple access
ui = ProfessionalUI()

def print_welcome():
    # We use a clean splash screen before entering the TUI
    welcome_panel = Panel(
        Text.assemble(
            ("RECLAW ", f"bold {THEME['accent']}"),
            ("Professional Coding Assistant\n", "white"),
            ("─" * 40 + "\n", THEME["secondary"]),
            ("Type ", THEME["secondary"]),
            ("exit", "bold red"),
            (" to quit.", THEME["secondary"])
        ),
        border_style=THEME["accent"],
        padding=(1, 2)
    )
    console.print("\n")
    console.print(welcome_panel, justify="center")
    console.print("\n")

def get_input() -> str:
    prompt_style = PromptStyle.from_dict({
        'prompt': f"bold {THEME['accent']}",
        'arrow': THEME['primary'],
    })
    session = PromptSession(style=prompt_style)
    try:
        return session.prompt(HTML(f'<prompt>ReClaw</prompt> <arrow>❯</arrow> '))
    except (KeyboardInterrupt, EOFError):
        return "exit"

def print_error(text: str):
    console.print(f"\n[bold red]ERROR:[/bold red] {text}\n")
