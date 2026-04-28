from rich.console import Console
from rich.panel import Panel
from rich.layout import Layout
from rich.live import Live
from rich.text import Text
from rich.markdown import Markdown
from rich.table import Table
from prompt_toolkit import PromptSession
from prompt_toolkit.styles import Style as PromptStyle
from prompt_toolkit.formatted_text import HTML
from prompt_toolkit.patch_stdout import patch_stdout
import datetime
import asyncio
import time

# Force standard color system for maximum compatibility
console = Console(color_system="standard", force_terminal=True)

class ProfessionalUI:
    def __init__(self):
        self.history = []
        self.current_content = ""
        self.display_content = ""
        self.current_tool = None
        self.status = "Idle"
        self.layout = self._create_layout()
        self.live = None
        self.session = PromptSession(style=PromptStyle.from_dict({
            'prompt': 'cyan bold',
            'arrow': 'white',
        }))

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
            Text(" RECLAW PRO v3.5", style="bold cyan"),
            Text(datetime.datetime.now().strftime("%H:%M:%S"), style="white")
        )
        return Panel(grid, border_style="white")

    def _get_footer(self):
        status_color = "green" if self.status == "Idle" else "cyan"
        return Panel(
            Text(f" STATUS: {self.status} | Type 'exit' to quit", style=f"bold {status_color}"),
            border_style="white"
        )

    def _get_sidebar(self):
        table = Table(show_header=False, expand=True, box=None)
        table.add_row(Text("SYSTEM", style="bold white"))
        table.add_row(Text("-" * 10, style="white"))
        table.add_row(Text("\nTOOL:", style="white"))
        table.add_row(Text(f"{self.current_tool or 'None'}", style="yellow" if self.current_tool else "white"))
        table.add_row(Text("\nTURNS:", style="white"))
        table.add_row(Text(f"{len(self.history)//2}", style="white"))
        return Panel(table, border_style="white")

    def _get_chat(self):
        chat_renderable = Table.grid(expand=True)
        chat_renderable.add_column()
        
        # Show recent history
        for msg in self.history[-5:]:
            if msg["role"] == "user":
                chat_renderable.add_row(Text(f"\n> {msg['content']}", style="bold cyan"))
            else:
                chat_renderable.add_row(Markdown(msg["content"]))
        
        if self.display_content:
            chat_renderable.add_row(Text("\n" + self.display_content, style="white"))
            
        return Panel(chat_renderable, title="Workspace", border_style="white")

    def update_display(self):
        self.layout["header"].update(self._get_header())
        self.layout["footer"].update(self._get_footer())
        self.layout["sidebar"].update(self._get_sidebar())
        self.layout["chat"].update(self._get_chat())

    def start(self):
        # REMOVED screen=True to prevent ANSI mess on incompatible terminals
        self.live = Live(self.layout, refresh_per_second=4, auto_refresh=False)
        self.live.start()
        self.update_display()
        self.live.refresh()

    def stop(self):
        if self.live: self.live.stop()

    def set_status(self, status):
        self.status = status
        self.update_display()
        if self.live: self.live.refresh()

    def add_user_message(self, content):
        self.history.append({"role": "user", "content": content})
        self.update_display()
        if self.live: self.live.refresh()

    async def stream_content(self, delta):
        self.current_content += delta
        self.display_content += delta
        self.update_display()
        if self.live: self.live.refresh()
        await asyncio.sleep(0.01)

    def finalize_content(self):
        if self.current_content:
            self.history.append({"role": "assistant", "content": self.current_content})
            self.current_content = ""
            self.display_content = ""
        self.update_display()
        if self.live: self.live.refresh()

    def set_tool(self, name):
        self.current_tool = name
        self.update_display()
        if self.live: self.live.refresh()

    async def get_input_async(self):
        with patch_stdout():
            try:
                return await self.session.prompt_async("ReClaw > ")
            except (KeyboardInterrupt, EOFError):
                return "exit"

ui = ProfessionalUI()

def print_welcome():
    welcome_panel = Panel(
        Text.assemble(
            ("RECLAW ", "bold cyan"),
            ("PRO v3.5\n", "white"),
            ("-" * 30 + "\n", "white"),
            ("Compatibility Mode Active\n", "green"),
            ("Type 'exit' to quit.", "white")
        ),
        border_style="cyan",
        padding=(1, 2)
    )
    console.print("\n")
    console.print(welcome_panel, justify="center")
    console.print("\n")
