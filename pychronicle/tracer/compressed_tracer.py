# Week 3 - Compressed Tracer - July 13 - Sunaina
# Full implementation with filter + delta + storage

import sys
from pychronicle.tracer.trace_filter import TraceFilter
from pychronicle.tracer.delta_tracker import DeltaTracker
from pychronicle.storage import StateStorage

class CompressedTracer:
    def __init__(self, db_path="pychronicle.db"):
        self.filter = TraceFilter()
        self.delta = DeltaTracker()
        self.storage = StateStorage(db_path)
        self.saved = 0
        self.skipped = 0

    def _trace(self, frame, event, arg):
        if event == 'line':
            line_no = frame.f_lineno
            # Step 1: Filter unwanted variables
            filtered = self.filter.filter_locals(frame.f_locals)
            # Step 2: Get only changes
            changes = self.delta.compute_delta(line_no, filtered)
            # Step 3: Save only changes
            if changes:
                for var, info in changes.items():
                    self.storage.insert_state(
                        line_no, var,
                        info['new'], info['type']
                    )
                    self.saved += 1
            else:
                self.skipped += 1
        return self._trace

    def run(self, script_path):
        print(f"=== Compressed Tracer ===")
        print(f"Script: {script_path}\n")
        sys.settrace(self._trace)
        try:
            with open(script_path) as f:
                exec(compile(f.read(), script_path, 'exec'),
                     {'__name__': '__main__'})
        finally:
            sys.settrace(None)
        total = self.saved + self.skipped
        if total > 0:
            savings = (self.skipped/total)*100
            print(f"\n=== Compression Results ===")
            print(f"States saved:   {self.saved}")
            print(f"States skipped: {self.skipped}")
            print(f"Memory saved:   {savings:.1f}%")

if __name__ == "__main__":
    import sys
    script = sys.argv[1] if len(sys.argv) > 1 else "test_script.py"
    tracer = CompressedTracer()
    tracer.run(script)