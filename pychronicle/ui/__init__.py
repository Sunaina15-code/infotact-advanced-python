from textual.app import App, ComposeResult
from textual.widgets import Header, Footer, Static, ListView, ListItem
from textual.containers import Horizontal, Vertical
from textual import events

class PyChronicleUI(App):
    """PyChronicle - Time Travel Debugger TUI"""

    CSS = """
    Screen {
        layout: grid;
        grid-size: 2;
        grid-gutter: 1;
    }

    #timeline {
        height: 100%;
        border: solid green;
        background: $surface;
    }

    #code_view {
        height: 100%;
        border: solid blue;
        background: $surface;
    }

    #status {
        height: 3;
        background: $accent;
        color: $text;
        content-align: center middle;
    }
    """

    def __init__(self, history=None):
        super().__init__()
        self.history = history or []
        self.current_index = 0

    def compose(self) -> ComposeResult:
        yield Header(show_clock=True)
        yield Static("PyChronicle - Time Travel Debugger", id="status")
        with Horizontal():
            with Vertical(id="timeline"):
                yield Static("=== Timeline ===")
                for i, state in enumerate(self.history[:20]):
                    yield Static(
                        f"[{i}] Line {state[2]} | {state[3]} = {state[4]}"
                    )
            with Vertical(id="code_view"):
                yield Static("=== Variable State ===")
                if self.history:
                    state = self.history[self.current_index]
                    yield Static(f"Line:     {state[2]}")
                    yield Static(f"Variable: {state[3]}")
                    yield Static(f"Value:    {state[4]}")
                    yield Static(f"Time:     {state[1]}")
        yield Footer()

    def on_key(self, event: events.Key) -> None:
        if event.key == "q":
            self.exit()

if __name__ == "__main__":
    app = PyChronicleUI()
    app.run()