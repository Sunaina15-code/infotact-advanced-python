# Week 2 - Query Engine - July 11 - Athrva
# Advanced querying for state storage

from pychronicle.storage import StateStorage

class QueryEngine:
    def __init__(self, db_path="pychronicle.db"):
        self.storage = StateStorage(db_path)

    def search_by_value(self, value):
        """Search all states with specific value"""
        cursor = self.storage.conn.execute(
            '''SELECT * FROM variable_states 
               WHERE serialized_value LIKE ?
               ORDER BY line_number''',
            (f'%{value}%',)
        )
        return cursor.fetchall()

    def get_line_range(self, start_line, end_line):
        """Get all states between two lines"""
        cursor = self.storage.conn.execute(
            '''SELECT * FROM variable_states 
               WHERE line_number BETWEEN ? AND ?
               ORDER BY line_number''',
            (start_line, end_line)
        )
        return cursor.fetchall()

    def get_latest_state(self):
        """Get the most recent state of all variables"""
        cursor = self.storage.conn.execute(
            '''SELECT variable_name, serialized_value, line_number
               FROM variable_states
               GROUP BY variable_name
               HAVING MAX(id)
               ORDER BY line_number'''
        )
        results = cursor.fetchall()
        print("\n=== Latest Variable States ===")
        for row in results:
            print(f"Line {row[2]:3} | {row[0]:<15} = {row[1]}")
        return results

if __name__ == "__main__":
    engine = QueryEngine()
    print("=== Search for value '15' ===")
    results = engine.search_by_value("15")
    for r in results:
        print(f"Line {r[2]} | {r[3]} = {r[4]}")
    engine.get_latest_state()