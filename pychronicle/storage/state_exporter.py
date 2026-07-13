# Week 3 - State Exporter - July 13 - Athrva
# Export stored states to different formats

import json
import csv
from pychronicle.storage import StateStorage

class StateExporter:
    def __init__(self, db_path="pychronicle.db"):
        self.storage = StateStorage(db_path)

    def export_to_json(self, output_file="states.json"):
        states = self.storage.get_all_states()
        data = []
        for s in states:
            data.append({
                'id': s[0],
                'timestamp': s[1],
                'line_number': s[2],
                'variable_name': s[3],
                'value': s[4],
                'event_type': s[5]
            })
        with open(output_file, 'w') as f:
            json.dump(data, f, indent=2)
        print(f"✅ Exported {len(data)} states to {output_file}")

    def export_to_csv(self, output_file="states.csv"):
        states = self.storage.get_all_states()
        with open(output_file, 'w', newline='') as f:
            writer = csv.writer(f)
            writer.writerow([
                'id', 'timestamp', 'line_number',
                'variable_name', 'value', 'event_type'
            ])
            writer.writerows(states)
        print(f"✅ Exported {len(states)} states to {output_file}")

    def export_summary(self):
        states = self.storage.get_all_states()
        print(f"\n=== Export Summary ===")
        print(f"Total states: {len(states)}")
        vars = set(s[3] for s in states)
        print(f"Variables tracked: {', '.join(vars)}")

if __name__ == "__main__":
    exporter = StateExporter()
    exporter.export_to_json()
    exporter.export_to_csv()
    exporter.export_summary()
    