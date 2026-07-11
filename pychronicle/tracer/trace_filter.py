# Week 3 - Trace Filter - July 12 - Sunaina
# Filters out unwanted variables from trace

class TraceFilter:
    def __init__(self):
        self.skip_vars = [
            '__name__', '__doc__', '__package__',
            '__loader__', '__spec__', '__builtins__',
            '__file__', '__cached__'
        ]
        self.skip_types = ['builtin_function_or_method']

    def should_track(self, var_name, value):
        """Check if variable should be tracked"""
        if var_name in self.skip_vars:
            return False
        if var_name.startswith('__'):
            return False
        if type(value).__name__ in self.skip_types:
            return False
        return True

    def filter_locals(self, local_vars):
        """Filter local variables dict"""
        return {
            k: v for k, v in local_vars.items()
            if self.should_track(k, v)
        }

    def display_filtered(self, local_vars):
        filtered = self.filter_locals(local_vars)
        print(f"Original: {len(local_vars)} vars → "
              f"Filtered: {len(filtered)} vars "
              f"(removed {len(local_vars)-len(filtered)})")
        return filtered

if __name__ == "__main__":
    f = TraceFilter()
    test_vars = {
        'x': 10, 'y': 20, '__name__': '__main__',
        '__builtins__': {}, 'result': 30, '__doc__': None
    }
    print("=== Trace Filter Test ===")
    filtered = f.display_filtered(test_vars)
    print(f"Kept variables: {list(filtered.keys())}")
    