# Week 2 - Timeline UI - July 10 - Sunaina
# Connects SQLite database to Textual timeline slider

from textual.app import App, ComposeResult
from textual.widgets import Header, Footer, Static, ProgressBar
from textual.containers import Horizontal, Vertical
from textual import events
from pychronicle.storage import StateStorage

class TimelineUI(App):
    """PyChronicle Timeline - Time Travel Debugger"""

    CSS = """
    #timeline_panel {
        height: 100%;
        border: solid green;
        width: 40%;
    }
    #code_panel {
        height: 100%;
        border: solid blue;
        width: 60%;
    }
    #status_bar {
        height: 3;
        background: $accent;
        content-align: center middle;
    }
    #current_state {
        height: auto;
        padding: 1;
    }
    """

    def __init__(self, db_path="pychronicle.db"):
        super().__init__()
        self.storage = StateStorage(db_path)
        self.history = self.storage.get_all_states()
        self.current_index = 0

    def compose(self) -> ComposeResult:
        yield Header(show_clock=True)
        yield Static(
            f"PyChronicle | Total States: {len(self.history)} | "
            f"Use ← → to travel through time | Q to quit",
            id="status_bar"
        )
        with Horizontal():
            with Vertical(id="timeline_panel"):
                yield Static("=== TIMELINE ===")
                for i, state in enumerate(self.history[:30]):
                    marker = "► " if i == self.current_index else "  "
                    yield Static(
                        f"{marker}[{i}] Line {state[2]} | "
                        f"{state[3]} = {state[4][:20]}"
                    )
            with Vertical(id="code_panel"):
                yield Static("=== CURRENT STATE ===")
                if self.history:
                    state = self.history[self.current_index]
                    yield Static(f"📍 Line Number : {state[2]}", id="line")
                    yield Static(f"📦 Variable    : {state[3]}", id="var")
                    yield Static(f"💾 Value       : {state[4]}", id="val")
                    yield Static(f"🕐 Timestamp   : {state[1][:19]}", id="time")
                    yield Static(f"🔄 Event Type  : {state[5]}", id="event")
        yield Footer()

    def on_key(self, event: events.Key) -> None:
        if event.key == "q":
            self.exit()

if __name__ == "__main__":
    app = TimelineUI()
    app.run()