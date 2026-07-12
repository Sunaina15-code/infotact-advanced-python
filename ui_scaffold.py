"""
Week 2 — TUI Scaffolding
John's Task: Initialize Textual App, create basic layout with
             code-view pane and timeline slider.
"""

from textual.app import App, ComposeResult
from textual.widgets import Header, Footer, Static, DataTable, Label
from textual.containers import Horizontal, Vertical
from textual.binding import Binding
from textual.reactive import reactive
from rich.text import Text


class TimelineSlider(Static):
    """Basic timeline slider showing current position in event history."""

    def render_bar(self, current: int, total: int) -> Text:
        text = Text()
        if total == 0:
            text.append("  No events recorded.", style="dim italic")
            return text

        pct       = current / max(total - 1, 1)
        bar_width = 36
        filled    = int(pct * bar_width)

        text.append("  ⏮ ", style="dim")
        text.append("█" * filled,                    style="bold cyan")
        text.append("▓",                             style="bold bright_cyan")
        text.append("░" * max(0, bar_width - filled - 1), style="dim")
        text.append(" ⏭  ", style="dim")
        text.append(f"Step {current + 1}", style="bold cyan")
        text.append(" / ", style="dim")
        text.append(str(total), style="white")
        return text


class PyChronicleScaffold(App):
    """
    Week 2 scaffold — basic Textual layout with:
      - Timeline slider (top)
      - Code-view pane (left)
      - Variable/delta panels (right)
      - Status bar (bottom)
    """

    CSS = """
    Screen { background: #0d1117; }

    #timeline {
        height: 3;
        background: #161b22;
        border: solid #30363d;
        padding: 0 1;
        content-align: left middle;
    }
    #main { height: 1fr; }

    #left-panel {
        width: 58%;
        border: solid #30363d;
        background: #0d1117;
        padding: 1;
    }
    #code-view {
        height: 1fr;
        overflow-y: auto;
    }

    #right-panel {
        width: 42%;
        border: solid #30363d;
        background: #0d1117;
        padding: 1;
    }
    #event-info {
        height: 6;
        background: #161b22;
        border: solid #21262d;
        padding: 0 1;
        margin-bottom: 1;
    }
    #var-table  { height: 1fr; }
    #delta-table { height: 8; }

    #status-bar {
        height: 3;
        background: #161b22;
        border: solid #30363d;
        padding: 0 2;
        content-align: left middle;
    }
    """

    BINDINGS = [
        Binding("left,h",  "prev_event",  "◀ Prev",  show=True),
        Binding("right,l", "next_event",  "▶ Next",  show=True),
        Binding("home",    "first_event", "⏮ First", show=True),
        Binding("end",     "last_event",  "⏭ Last",  show=True),
        Binding("q",       "quit",        "Quit",    show=True),
    ]

    current_index: reactive[int] = reactive(0)

    def __init__(self, events: list):
        super().__init__()
        self.events  = events
        self._slider = TimelineSlider()

    def compose(self) -> ComposeResult:
        yield Header(show_clock=True)
        yield Static("", id="timeline")
        with Horizontal(id="main"):
            with Vertical(id="left-panel"):
                yield Label("[bold]📄 Source[/bold]")
                yield Static("[dim italic]  Source file will appear here.[/dim italic]", id="code-view")
            with Vertical(id="right-panel"):
                yield Label("[bold]⚡ Event Info[/bold]")
                yield Static("", id="event-info")
                yield Label("[bold]🔢 Variables[/bold]")
                yield DataTable(id="var-table")
                yield Label("[bold]🔀 Deltas[/bold]")
                yield DataTable(id="delta-table")
        yield Static("", id="status-bar")
        yield Footer()

    def on_mount(self):
        vt: DataTable = self.query_one("#var-table")
        vt.add_columns("Variable", "Type", "Value")

        dt: DataTable = self.query_one("#delta-table")
        dt.add_columns("Variable", "Before", "After")

        self._refresh_view()

    def watch_current_index(self, _old: int, _new: int):
        self._refresh_view()

    def _refresh_view(self):
        total = len(self.events)
        idx   = self.current_index

        # Update timeline slider
        timeline: Static = self.query_one("#timeline")
        timeline.update(self._slider.render_bar(idx, total))

        # Update status bar
        status: Static = self.query_one("#status-bar")
        status.update(
            f" [dim]◀/▶ navigate  ⏮/⏭ jump  |  "
            f"[white]{total}[/white] total events[/dim]"
        )

    def action_next_event(self):
        if self.current_index < len(self.events) - 1:
            self.current_index += 1

    def action_prev_event(self):
        if self.current_index > 0:
            self.current_index -= 1

    def action_first_event(self):
        self.current_index = 0

    def action_last_event(self):
        self.current_index = max(0, len(self.events) - 1)


if __name__ == "__main__":
    # Demo with dummy events
    dummy_events = [{"id": i, "filename": "demo.py", "lineno": i + 1,
                     "func_name": "main", "event": "line"} for i in range(20)]
    PyChronicleScaffold(dummy_events).run()
