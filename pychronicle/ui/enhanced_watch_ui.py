# Week 4 - Enhanced Watch Variables UI
# Interactive terminal UI for tracking specific variables across timeline

from textual.app import App, ComposeResult
from textual.widgets import Header, Footer, Static, DataTable, Input, Button
from textual.containers import Horizontal, Vertical, Container
from textual.binding import Binding
from textual import events
from pychronicle.storage import StateStorage
import json


class WatchVariablesUI(App):
    """Interactive Watch Variables UI - Track specific variables across timeline"""

    BINDINGS = [
        Binding("q", "quit", "Quit"),
        Binding("a", "add_watch", "Add Watch"),
        Binding("r", "remove_watch", "Remove Watch"),
        Binding("c", "clear_all", "Clear All"),
        Binding("e", "export_csv", "Export CSV"),
    ]

    CSS = """
    #watch_list {
        height: 40%;
        border: solid green;
        padding: 1;
    }
    
    #variable_history {
        height: 60%;
        border: solid blue;
        padding: 1;
    }
    
    #status_bar {
        height: 3;
        background: $accent;
        content-align: center middle;
    }
    
    #input_container {
        height: auto;
        padding: 1;
        background: $panel;
    }
    
    .watch_item {
        padding: 1;
        background: $surface;
        margin: 1;
    }
    
    DataTable {
        height: 100%;
    }
    """

    def __init__(self, db_path="pychronicle.db"):
        super().__init__()
        self.storage = StateStorage(db_path)
        self.watched_variables = []
        self.selected_variable = None

    def compose(self) -> ComposeResult:
        yield Header(show_clock=True)
        yield Static(
            "PyChronicle Watch Variables | [A]dd [R]emove [C]lear [E]xport [Q]uit",
            id="status_bar"
        )
        
        with Vertical():
            # Watch List Section
            with Container(id="watch_list"):
                yield Static("=== WATCHED VARIABLES ===", classes="section_title")
                yield DataTable(id="watch_table")
            
            # Variable History Section
            with Container(id="variable_history"):
                yield Static("=== VARIABLE HISTORY ===", classes="section_title")
                yield DataTable(id="history_table")
        
        yield Footer()

    def on_mount(self) -> None:
        """Initialize tables when app mounts"""
        # Setup watch table
        watch_table = self.query_one("#watch_table", DataTable)
        watch_table.add_columns("Variable", "Current Value", "Changes")
        watch_table.cursor_type = "row"
        
        # Setup history table
        history_table = self.query_one("#history_table", DataTable)
        history_table.add_columns("Line #", "Value", "Timestamp", "Event")
        
        # Load initial data if any
        self._refresh_watch_list()

    def _refresh_watch_list(self):
        """Refresh the watch list table"""
        watch_table = self.query_one("#watch_table", DataTable)
        watch_table.clear()
        
        for var_name in self.watched_variables:
            # Get variable info
            cursor = self.storage.conn.execute(
                '''SELECT serialized_value, COUNT(*) as changes
                   FROM variable_states 
                   WHERE variable_name = ?
                   GROUP BY variable_name''',
                (var_name,)
            )
            row = cursor.fetchone()
            
            if row:
                current_value = json.loads(row[0]) if row[0] else "N/A"
                change_count = row[1]
                watch_table.add_row(var_name, str(current_value)[:30], str(change_count))
            else:
                watch_table.add_row(var_name, "Not found", "0")

    def _refresh_history(self, variable_name):
        """Refresh the history table for selected variable"""
        history_table = self.query_one("#history_table", DataTable)
        history_table.clear()
        
        cursor = self.storage.conn.execute(
            '''SELECT line_number, serialized_value, timestamp, event_type
               FROM variable_states 
               WHERE variable_name = ?
               ORDER BY id''',
            (variable_name,)
        )
        
        for row in cursor.fetchall():
            line_num = row[0]
            value = json.loads(row[1]) if row[1] else "N/A"
            timestamp = row[2][:19] if row[2] else "N/A"
            event = row[3] or "assignment"
            
            history_table.add_row(
                str(line_num),
                str(value)[:30],
                timestamp,
                event
            )

    def action_add_watch(self):
        """Add a new variable to watch list"""
        self.push_screen(AddWatchScreen(), self._handle_add_watch)

    def _handle_add_watch(self, variable_name: str | None):
        """Callback when adding a watch"""
        if variable_name and variable_name not in self.watched_variables:
            self.watched_variables.append(variable_name)
            self._refresh_watch_list()
            self.notify(f"✅ Now watching: {variable_name}")

    def action_remove_watch(self):
        """Remove selected variable from watch list"""
        watch_table = self.query_one("#watch_table", DataTable)
        if watch_table.cursor_row is not None:
            row_key = watch_table.cursor_row
            if 0 <= row_key < len(self.watched_variables):
                removed = self.watched_variables.pop(row_key)
                self._refresh_watch_list()
                self.notify(f"🗑️ Removed: {removed}")

    def action_clear_all(self):
        """Clear all watched variables"""
        self.watched_variables.clear()
        self._refresh_watch_list()
        history_table = self.query_one("#history_table", DataTable)
        history_table.clear()
        self.notify("🗑️ All watches cleared")

    def action_export_csv(self):
        """Export watch data to CSV"""
        import csv
        filename = f"watch_export_{len(self.watched_variables)}_vars.csv"
        
        with open(filename, 'w', newline='') as f:
            writer = csv.writer(f)
            writer.writerow(['Variable', 'Line', 'Value', 'Timestamp', 'Event'])
            
            for var_name in self.watched_variables:
                cursor = self.storage.conn.execute(
                    '''SELECT line_number, serialized_value, timestamp, event_type
                       FROM variable_states 
                       WHERE variable_name = ?
                       ORDER BY id''',
                    (var_name,)
                )
                for row in cursor.fetchall():
                    value = json.loads(row[1]) if row[1] else "N/A"
                    writer.writerow([var_name, row[0], value, row[2], row[3]])
        
        self.notify(f"📄 Exported to {filename}")

    def on_data_table_row_selected(self, event: DataTable.RowSelected):
        """Handle row selection in watch table"""
        if event.data_table.id == "watch_table":
            row_index = event.cursor_row
            if 0 <= row_index < len(self.watched_variables):
                var_name = self.watched_variables[row_index]
                self.selected_variable = var_name
                self._refresh_history(var_name)


class AddWatchScreen(App):
    """Modal screen for adding a watch variable"""
    
    CSS = """
    Screen {
        align: center middle;
    }
    
    #dialog {
        width: 60;
        height: 11;
        border: thick $background 80%;
        background: $surface;
        padding: 1;
    }
    
    Input {
        margin: 1 0;
    }
    
    Button {
        margin: 1;
    }
    """

    def compose(self) -> ComposeResult:
        with Container(id="dialog"):
            yield Static("Enter variable name to watch:")
            yield Input(placeholder="variable_name", id="var_input")
            with Horizontal():
                yield Button("Add", variant="primary", id="add_btn")
                yield Button("Cancel", variant="default", id="cancel_btn")

    def on_button_pressed(self, event: Button.Pressed):
        if event.button.id == "add_btn":
            var_input = self.query_one("#var_input", Input)
            self.dismiss(var_input.value.strip())
        else:
            self.dismiss(None)


# Standalone CLI-style watcher (non-interactive)
class WatchVariables:
    """Simple CLI-based variable watcher"""
    
    def __init__(self, db_path="pychronicle.db"):
        self.storage = StateStorage(db_path)
        self.watched = []

    def add_watch(self, variable_name):
        """Add a variable to watch list"""
        if variable_name not in self.watched:
            self.watched.append(variable_name)
            print(f"✅ Watching: {variable_name}")

    def remove_watch(self, variable_name):
        """Remove a variable from watch list"""
        if variable_name in self.watched:
            self.watched.remove(variable_name)
            print(f"🗑️ Removed: {variable_name}")

    def get_watch_history(self):
        """Get history of all watched variables"""
        print("\n" + "="*60)
        print("📊 WATCH VARIABLES REPORT")
        print("="*60)
        
        for var in self.watched:
            cursor = self.storage.conn.execute(
                '''SELECT line_number, serialized_value, timestamp, event_type
                   FROM variable_states 
                   WHERE variable_name = ?
                   ORDER BY id''',
                (var,)
            )
            rows = cursor.fetchall()
            
            print(f"\n📌 Variable: {var}")
            print(f"   Total Changes: {len(rows)}")
            print(f"   {'-'*56}")
            
            for i, row in enumerate(rows, 1):
                value = json.loads(row[1]) if row[1] else "N/A"
                print(f"   [{i:3}] Line {row[0]:4} | {str(value):<20} | {row[2][:19]}")

    def display_timeline(self):
        """Show timeline of watched variables"""
        print("\n" + "="*60)
        print("📈 VARIABLE TIMELINE")
        print("="*60)
        
        for var in self.watched:
            cursor = self.storage.conn.execute(
                '''SELECT line_number, serialized_value 
                   FROM variable_states 
                   WHERE variable_name = ?
                   ORDER BY id''',
                (var,)
            )
            rows = cursor.fetchall()
            
            if rows:
                print(f"\n{var}:")
                values = []
                for r in rows:
                    value = json.loads(r[1]) if r[1] else "N/A"
                    values.append(f"L{r[0]}:{value}")
                print("  " + " → ".join(values[:10]))
                if len(rows) > 10:
                    print(f"  ... and {len(rows) - 10} more changes")

    def compare_variables(self, var1, var2):
        """Compare two watched variables"""
        print(f"\n🔄 Comparing {var1} vs {var2}")
        print("="*60)
        
        for var in [var1, var2]:
            cursor = self.storage.conn.execute(
                '''SELECT AVG(LENGTH(serialized_value)), 
                          COUNT(*),
                          MIN(line_number),
                          MAX(line_number)
                   FROM variable_states 
                   WHERE variable_name = ?''',
                (var,)
            )
            stats = cursor.fetchone()
            print(f"\n{var}:")
            print(f"  Avg Value Length: {stats[0]:.1f}" if stats[0] else "N/A")
            print(f"  Total Changes: {stats[1]}")
            print(f"  Line Range: {stats[2]} - {stats[3]}")


if __name__ == "__main__":
    # Run interactive UI
    app = WatchVariablesUI()
    app.run()
