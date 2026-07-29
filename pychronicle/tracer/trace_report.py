# Week 4 - Trace Report - July 19 - Noah
# Generates final report of execution trace

from pychronicle.storage import StateStorage
from datetime import datetime

class TraceReport:
    def __init__(self, db_path="pychronicle.db"):
        self.storage = StateStorage(db_path)
        self.states = self.storage.get_all_states()

    def generate_report(self):
        print("=" * 60)
        print("         PyChronicle Execution Report")
        print(f"         Generated: {datetime.now().strftime('%Y-%m-%d %H:%M')}")
        print("=" * 60)

        # Summary
        vars = set(s[3] for s in self.states)
        lines = set(s[2] for s in self.states)
        print(f"\n📊 Summary:")
        print(f"   Total states recorded : {len(self.states)}")
        print(f"   Unique variables      : {len(vars)}")
        print(f"   Lines traced          : {len(lines)}")

        # Variable changes
        print(f"\n📈 Variable Change Count:")
        var_counts = {}
        for s in self.states:
            var_counts[s[3]] = var_counts.get(s[3], 0) + 1
        for var, count in sorted(
            var_counts.items(),
            key=lambda x: x[1],
            reverse=True
        ):
            bar = "█" * min(count, 20)
            print(f"   {var:<15} {bar} ({count})")

        # Timeline
        print(f"\n⏱️  Execution Timeline:")
        prev_line = None
        for s in self.states[:15]:
            if s[2] != prev_line:
                print(f"\n   Line {s[2]}:")
                prev_line = s[2]
            print(f"      {s[3]} = {s[4][:30]}")

        print("\n" + "=" * 60)
        print("         Report Complete ✅")
        print("=" * 60)

if __name__ == "__main__":
    report = TraceReport()
    report.generate_report()