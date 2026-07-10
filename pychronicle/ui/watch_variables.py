# Week 2 - Watch Variables - July 11 - Sunaina
# Track specific variables across timeline

from pychronicle.storage import StateStorage

class WatchVariables:
    def __init__(self, db_path="pychronicle.db"):
        self.storage = StateStorage(db_path)
        self.watched = []

    def add_watch(self, variable_name):
        """Add a variable to watch list"""
        self.watched.append(variable_name)
        print(f"✅ Watching: {variable_name}")

    def get_watch_history(self):
        """Get history of all watched variables"""
        print("\n=== Watch Variables Report ===")
        for var in self.watched:
            cursor = self.storage.conn.execute(
                '''SELECT line_number, serialized_value, timestamp 
                   FROM variable_states 
                   WHERE variable_name = ?
                   ORDER BY id''',
                (var,)
            )
            rows = cursor.fetchall()
            print(f"\n📌 {var} ({len(rows)} changes):")
            for row in rows:
                print(f"   Line {row[0]:3} | Value: {row[1]:<15} | {row[2][:19]}")

    def display_timeline(self):
        """Show timeline of watched variables"""
        print("\n=== Variable Timeline ===")
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
                values = [f"Line {r[0]}:{r[1]}" for r in rows]
                print(" → ".join(values))

if __name__ == "__main__":
    watcher = WatchVariables()
    watcher.add_watch("total")
    watcher.add_watch("result")
    watcher.get_watch_history()
    watcher.display_timeline()