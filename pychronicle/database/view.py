import sqlite3

connection = sqlite3.connect("pychronicle.db")

cursor = connection.cursor()

cursor.execute("SELECT * FROM variable_history")

rows = cursor.fetchall()

for row in rows:
    print(row)

connection.close()