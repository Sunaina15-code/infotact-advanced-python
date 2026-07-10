# Week 2 - Advanced Storage - July 10 - Athrva
# Advanced query functions for state storage

import sqlite3
import json
from pychronicle.storage import StateStorage

class AdvancedStorage(StateStorage):
    def __init__(self, db_path="pychronicle.db"):
        super().__init__(db_path)

    def get_variable_history(self, variable_name):
        """Get all states of a specific variable"""
        cursor = self.conn.execute(
            '''SELECT * FROM variable_states 
               WHERE variable_name = ? 
               ORDER BY line_number''',
            (variable_name,)
        )
        return cursor.fetchall()

    def get_states_at_line(self, line_number):
        """Get all variable states at a specific line"""
        cursor = self.conn.execute(
            '''SELECT * FROM variable_states 
               WHERE line_number = ? 
               ORDER BY id''',
            (line_number,)
        )
        return cursor.fetchall()

    def get_summary(self):
        """Get summary of all tracked variables"""
        cursor = self.conn.execute(
            '''SELECT variable_name, COUNT(*) as changes,
               MIN(line_number) as first_seen,
               MAX(line_number) as last_seen
               FROM variable_states
               GROUP BY variable_name
               ORDER BY changes DESC'''
        )
        return cursor.fetchall()

    def display_summary(self):
        print("\n=== Variable Summary ===")
        print(f"{'Variable':<15} {'Changes':<10} {'First Line':<12} {'Last Line'}")
        print("-" * 50)
        for row in self.get_summary():
            print(f"{row[0]:<15} {row[1]:<10} {row[2]:<12} {row[3]}")

if __name__ == "__main__":
    db = AdvancedStorage("pychronicle.db")
    db.display_summary()