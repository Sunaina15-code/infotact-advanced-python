# Week 2 - Optimized Tracer - July 9
# Combines sys.settrace with delta tracking

import sys
from pychronicle.tracer.delta_tracker import DeltaTracker
from pychronicle.storage import StateStorage

class OptimizedTracer:
    def __init__(self, db_path="pychronicle.db"):
        self.delta_tracker = DeltaTracker()
        self.storage = StateStorage(db_path)
        self.trace_count = 0
        self.skip_count = 0

    def _trace_calls(self, frame, event, arg):
        if event == 'line':
            line_no = frame.f_lineno
            local_vars = frame.f_locals.copy()
            
            # Only save CHANGES not everything
            changes = self.delta_tracker.compute_delta(line_no, local_vars)
            
            if changes:
                for var_name, info in changes.items():
                    self.storage.insert_state(
                        line_number=line_no,
                        variable_name=var_name,
                        value=info['new'],
                        event_type=info['type']
                    )
                self.trace_count += len(changes)
            else:
                self.skip_count += 1

        return self._trace_calls

    def start_trace(self, target_script):
        print(f"\n=== Optimized PyChronicle Tracer ===")
        print(f"Tracing: {target_script}")
        
        sys.settrace(self._trace_calls)
        try:
            with open(target_script) as f:
                code = compile(f.read(), target_script, 'exec')
                exec(code, {'__name__': '__main__'})
        finally:
            sys.settrace(None)
        
        print(f"\n=== Optimization Results ===")
        print(f"Changes saved:  {self.trace_count}")
        print(f"Lines skipped:  {self.skip_count}")
        if self.trace_count + self.skip_count > 0:
            savings = (self.skip_count/(self.trace_count + self.skip_count))*100
            print(f"Memory saved:   {savings:.1f}%")

    def display_history(self):
        self.delta_tracker.display_deltas()

if __name__ == "__main__":
    import sys
    script = sys.argv[1] if len(sys.argv) > 1 else "test_script.py"
    tracer = OptimizedTracer()
    tracer.start_trace(script)
    tracer.display_history()