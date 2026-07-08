import sqlite3
from datetime import datetime

connection = sqlite3.connect("pychronicle.db")

cursor = connection.cursor()

def save_variable(line_number, variable_name, serialized_value):

    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    cursor.execute("""
        INSERT INTO variable_history
        (timestamp,line_number,variable_name,serialized_value)
        VALUES(?,?,?,?)
    """,(timestamp,line_number,variable_name,serialized_value))

    connection.commit()

save_variable(1,"a","10")
save_variable(2,"b","20")
save_variable(3,"a","30")

connection.close()

print("Records inserted successfully")