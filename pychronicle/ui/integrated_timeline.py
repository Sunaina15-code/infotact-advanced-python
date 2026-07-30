# Week 4 - Integrated Timeline with Watch Variables
# Combines timeline view with watch variables in split-screen

from textual.app import App, ComposeResult
from textual.widgets import Header, Footer, Static, DataTable, TabbedContent, TabPane
from textual.containers import Horizontal, Vertical, Container
from textual.binding import Binding
from pychronicle.storage import StateStorage
import json


class IntegratedTimelineUI(App):
    """Integrated Timeline + Watch Variables UI"""

    BINDINGS = [
        Binding("q", "quit", "Quit"),
        Binding("w", "toggle_watch", "Toggle Watch"),
        Binding("left", "prev_state", "Previous"),
        Binding("right", "next_state", "Next"),
        Binding("home", "first_state", "First"),
        Binding("end", "last_state", "Last"),
    ]

    CSS = """
    #main_container {
        height: 100%;
    }
    
    #timeline_panel {
        width: 50%;
        border: solid green;
        padding: 1;
    }
    
    #watch_panel {
        width: 50%;
        border: solid blue;
        padding: 1;
    }
    
    #status_bar {
        height: 3;
        background: $accent;
        content-align: center middle;
    }
    
    #state_info {
        height: auto;
        padding: 1;
        background: $panel;
    }
    
    DataTable {
        height: 100%;
    }
    
    .highlight {
        background: $accent;
    }
    """

    def __init__(self, db_path="pychronicle.db"):
        super().__init__()
        self.storage = StateStorage(db_path)
        self.all_states = self.storage.get_all_states()
        self.current_index = 0
        self.watched_variables = set()

    def compose(self) -> ComposeResult:
        yield Header(show_clock=True)
        yield Static(
            f"PyChronicle Integrated View | States: {len(self.all_states)} | "
            f"[←→] Navigate [W] Watch [Q] Quit",
            id="status_bar"
        )
        
        with Horizontal(id="main_container"):
            # Timeline Panel
            with Vertical(id="timeline_panel"):
                yield Static("=== EXECUTION TIMELINE ===")
                yield DataTable(id="timeline_table")
                
            # Watch Variables Panel
            with Vertical(id="watch_panel"):
                yield Static("=== WATCHED VARIABLES ===")
                yield DataTable(id="watch_table")
        
        # Current State Info
        with Container(id="state_info"):
            yield Static("Select a state to view details", id="current_state")
        
        yield Footer()

    def on_mount(self) -> None:
        """Initialize UI"""
        # Setup timeline table
        timeline_table = self.query_one("#timeline_table", DataTable)
        timeline_table.add_columns("ID", "Line", "Variable", "Value", "Event")
        timeline_table.cursor_type = "row"
        
        # Setup watch table
        watch_table = self.query_one("#watch_table", DataTable)
        watch_table.add_columns("Variable", "Current", "Changes")
        
        # Load data
        self._populate_timeline()
        self._update_current_state()

    def _populate_timeline(self):
        """Populate timeline table with all states"""
        timeline_table = self.query_one("#timeline_table", DataTable)
        timeline_table.clear()
        
        for state in self.all_states[:100]:  # Limit to first 100 for performance
            state_id = state[0]
            line_num = state[2]
            var_name = state[3]
            value = json.loads(state[4]) if state[4] else "N/A"
            event = state[5] or "assignment"
            
            timeline_table.add_row(
                str(state_id),
                str(line_num),
                var_name,
                str(value)[:25],
                event
            )

    def _update_watch_panel(self):
        """Update watch variables panel"""
        watch_table = self.query_one("#watch_table", DataTable)
        watch_table.clear()
        
        for var_name in self.watched_variables:
            cursor = self.storage.conn.execute(
                '''SELECT serialized_value, COUNT(*)
                   FROM variable_states 
                   WHERE variable_name = ?
                   GROUP BY variable_name''',
                (var_name,)
            )
            row = cursor.fetchone()
            
            if row:
                current_value = json.loads(row[0]) if row[0] else "N/A"
                watch_table.add_row(var_name, str(current_value)[:20], str(row[1]))

    def _update_current_state(self):
        """Update current state info display"""
        if 0 <= self.current_index < len(self.all_states):
            state = self.all_states[self.current_index]
            value = json.loads(state[4]) if state[4] else "N/A"
            
            info_text = (
                f"State #{state[0]} | "
                f"Line {state[2]} | "
                f"{state[3]} = {value} | "
                f"{state[1][:19]} | "
                f"{state[5]}"
            )
            
            current_state = self.query_one("#current_state", Static)
            current_state.update(info_text)

    def action_toggle_watch(self):
        """Toggle watch on current variable"""
        if 0 <= self.current_index < len(self.all_states):
            state = self.all_states[self.current_index]
            var_name = state[3]
            
            if var_name in self.watched_variables:
                self.watched_variables.remove(var_name)
                self.notify(f"🗑️ Stopped watching: {var_name}")
            else:
                self.watched_variables.add(var_name)
                self.notify(f"✅ Now watching: {var_name}")
            
            self._update_watch_panel()

    def action_next_state(self):
        """Navigate to next state"""
        if self.current_index < len(self.all_states) - 1:
            self.current_index += 1
            self._update_current_state()

    def action_prev_state(self):
        """Navigate to previous state"""
        if self.current_index > 0:
            self.current_index -= 1
            self._update_current_state()

    def action_first_state(self):
        """Jump to first state"""
        self.current_index = 0
        self._update_current_state()

    def action_last_state(self):
        """Jump to last state"""
        self.current_index = len(self.all_states) - 1
        self._update_current_state()

    def on_data_table_row_selected(self, event: DataTable.RowSelected):
        """Handle row selection"""
        if event.data_table.id == "timeline_table":
            self.current_index = event.cursor_row
            self._update_current_state()


if __name__ == "__main__":
    app = IntegratedTimelineUI()
    app.run()
