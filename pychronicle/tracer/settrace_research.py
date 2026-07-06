# Noah - Week 1: sys.settrace Research & Demo
import sys

"""
RESEARCH NOTES: sys.settrace
=============================

What is sys.settrace?
- Python built-in function to set a trace function
- Called for every line, function call, and return
- Used by debuggers like pdb

How it works:
- sys.settrace(trace_function) sets the tracer
- trace_function receives 3 args: frame, event, arg
- Returns itself to continue tracing

Events:
- 'call'   : function called
- 'line'   : about to execute a line
- 'return' : function about to return
- 'exception': exception occurred

Frame Object Contains:
- f_locals  : local variables dict
- f_globals : global variables dict
- f_lineno  : current line number
- f_code    : code object
"""

class SettraceDemo:
    def __init__(self):
        self.trace_log = []

    def trace_function(self, frame, event, arg):
        """Main trace function called by Python interpreter"""
        if event == 'line':
            line_no = frame.f_lineno
            local_vars = frame.f_locals.copy()
            filename = frame.f_code.co_filename
            
            self.trace_log.append({
                'event': event,
                'line': line_no,
                'vars': local_vars,
                'file': filename
            })
        return self.trace_function

    def run_demo(self):
        """Demo: trace a simple calculation"""
        print("=== sys.settrace Demo ===\n")
        
        sys.settrace(self.trace_function)
        
        # Simple code to trace
        a = 100
        b = 200
        c = a + b
        result = c * 2
        
        sys.settrace(None)
        
        print(f"Traced {len(self.trace_log)} line events\n")
        print("=== Trace Log ===")
        for entry in self.trace_log:
            if entry['vars']:
                vars_str = ', '.join([
                    f"{k}={v}" for k, v in entry['vars'].items()
                    if not k.startswith('__')
                ])
                print(f"Line {entry['line']:3} | vars: {vars_str}")

    def display_research(self):
        print("\n=== Key Findings ===")
        print("1. sys.settrace hooks into Python interpreter")
        print("2. 'line' event fires before each line executes")
        print("3. frame.f_locals gives current variable state")
        print("4. Must return trace function to continue tracing")
        print("5. sys.settrace(None) stops tracing")
        print("\nThis is the foundation of PyChronicle!")

if __name__ == "__main__":
    demo = SettraceDemo()
    demo.run_demo()
    demo.display_research()