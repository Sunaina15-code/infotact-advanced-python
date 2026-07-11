# Week 3 - Storage Stats - July 12 - Athrva
# Statistics and analytics for stored states

from pychronicle.storage import StateStorage
from datetime import datetime

class StorageStats:
    def __init__(self, db_path="pychronicle.db"):
        self.storage = StateStorage(db_path)

    def get_total_states(self):
        cursor = self.storage.conn.execute(
            'SELECT COUNT(*) FROM variable_states'
        )
        return cursor.fetchone()[0]

    def get_unique_variables(self):
        cursor = self.storage.conn.execute(
            'SELECT COUNT(DISTINCT variable_name) FROM variable_states'
        )
        return cursor.fetchone()[0]

    def get_most_changed(self):
        cursor = self.storage.conn.execute(
            '''SELECT variable_name, COUNT(*) as changes
               FROM variable_states
               GROUP BY variable_name
               ORDER BY changes DESC
               LIMIT 5'''
        )
        return cursor.fetchall()

    def display_stats(self):
        print("\n=== Storage Statistics ===")
        print(f"Total states:      {self.get_total_states()}")
        print(f"Unique variables:  {self.get_unique_variables()}")
        print(f"\nMost Changed Variables:")
        for row in self.get_most_changed():
            print(f"  {row[0]:<15} → {row[1]} changes")

if __name__ == "__main__":
    stats = StorageStats()
    stats.display_stats()