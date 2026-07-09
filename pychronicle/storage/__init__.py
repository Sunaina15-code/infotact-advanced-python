import sqlite3
import json
from datetime import datetime

class StateStorage:
    def __init__(self, db_path=":memory:"):
        self.db_path = db_path
        self.conn = sqlite3.connect(db_path)
        self._create_schema()

    def _create_schema(self):
        self.conn.execute('''
            CREATE TABLE IF NOT EXISTS variable_states (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                timestamp TEXT NOT NULL,
                line_number INTEGER NOT NULL,
                variable_name TEXT NOT NULL,
                serialized_value TEXT,
                event_type TEXT
            )
        ''')
        self.conn.execute('''
            CREATE INDEX IF NOT EXISTS idx_line 
            ON variable_states(line_number)
        ''')
        self.conn.commit()
        print("Storage schema created successfully!")

    def insert_state(self, line_number, variable_name, value, event_type="assignment"):
        self.conn.execute('''
            INSERT INTO variable_states 
            (timestamp, line_number, variable_name, serialized_value, event_type)
            VALUES (?, ?, ?, ?, ?)
        ''', (
            datetime.now().isoformat(),
            line_number,
            variable_name,
            json.dumps(str(value)),
            event_type
        ))
        self.conn.commit()

    def get_all_states(self):
        cursor = self.conn.execute(
            'SELECT * FROM variable_states ORDER BY line_number'
        )
        return cursor.fetchall()

    def close(self):
        self.conn.close()

if __name__ == "__main__":
    db = StateStorage("pychronicle.db")
    db.insert_state(1, "x", 10)
    db.insert_state(2, "name", "hello")
    print("\nStored states:")
    for row in db.get_all_states():
        print(row)
    db.close()