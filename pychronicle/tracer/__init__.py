import sys
import sqlite3
from datetime import datetime
from pychronicle.storage import StateStorage

class ExecutionTracer:
    def __init__(self, db_path="pychronicle.db"):
        self.storage = StateStorage(db_path)
        self.is_tracing = False

    def _trace_calls(self, frame, event, arg):
        if event == 'line':
            local_vars = frame.f_locals.copy()
            line_no = frame.f_lineno
            for var_name, value in local_vars.items():
                try:
                    self.storage.insert_state(
                        line_number=line_no,
                        variable_name=var_name,
                        value=value,
                        event_type=event
                    )
                except Exception:
                    pass
        return self._trace_calls

    def start_trace(self, target_script):
        print(f"\n=== PyChronicle Tracer Started ===")
        print(f"Tracing: {target_script}\n")
        self.is_tracing = True
        sys.settrace(self._trace_calls)
        try:
            with open(target_script) as f:
                code = compile(f.read(), target_script, 'exec')
                exec(code, {'__name__': '__main__'})
        finally:
            sys.settrace(None)
            self.is_tracing = False
            print("\n=== Tracing Complete ===")

    def get_history(self):
        return self.storage.get_all_states()

    def display_history(self):
        history = self.get_history()
        print(f"\n=== Execution History ({len(history)} states) ===")
        for row in history:
            print(f"ID:{row[0]} | Line:{row[2]} | Var:{row[3]} | Value:{row[4]}")

if __name__ == "__main__":
    import sys
    script = sys.argv[1] if len(sys.argv) > 1 else "test_script.py"
    tracer = ExecutionTracer()
    tracer.start_trace(script)
    tracer.display_history()