import sqlite3

connection = sqlite3.connect("pychronicle.db")

cursor = connection.cursor()

create_table_query = """
CREATE TABLE IF NOT EXISTS variable_history (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    timestamp TEXT NOT NULL,
    line_number INTEGER NOT NULL,
    variable_name TEXT NOT NULL,
    serialized_value TEXT NOT NULL
);
"""

cursor.execute(create_table_query)

connection.commit()

connection.close()

print("Database created successfully")