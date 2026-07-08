# Week 2 - Delta Tracker - July 8
# Tracks only CHANGES in variables (not every state)

class DeltaTracker:
    def __init__(self):
        self.previous_state = {}
        self.deltas = []

    def compute_delta(self, line_no, local_vars):
        """Only save what CHANGED since last line"""
        changes = {}
        
        for var_name, value in local_vars.items():
            # Skip built-in variables
            if var_name.startswith('__'):
                continue
            
            str_value = str(value)
            
            # Only record if value is NEW or CHANGED
            if var_name not in self.previous_state:
                changes[var_name] = {
                    'old': None,
                    'new': str_value,
                    'type': 'new_variable'
                }
            elif self.previous_state[var_name] != str_value:
                changes[var_name] = {
                    'old': self.previous_state[var_name],
                    'new': str_value,
                    'type': 'changed'
                }
            
            # Update previous state
            self.previous_state[var_name] = str_value
        
        if changes:
            self.deltas.append({
                'line': line_no,
                'changes': changes
            })
        
        return changes

    def display_deltas(self):
        print(f"\n=== Delta Report ({len(self.deltas)} changes) ===")
        for delta in self.deltas:
            print(f"\nLine {delta['line']}:")
            for var, info in delta['changes'].items():
                if info['type'] == 'new_variable':
                    print(f"  NEW     {var} = {info['new']}")
                else:
                    print(f"  CHANGED {var}: {info['old']} → {info['new']}")

if __name__ == "__main__":
    tracker = DeltaTracker()
    # Simulate variable changes
    tracker.compute_delta(2, {'x': 10})
    tracker.compute_delta(3, {'x': 10, 'y': 20})
    tracker.compute_delta(5, {'x': 10, 'y': 20, 'result': 30})
    tracker.compute_delta(8, {'x': 10, 'y': 20, 'result': 30, 'total': 0})
    tracker.compute_delta(10, {'x': 10, 'y': 20, 'result': 30, 'total': 1})
    tracker.compute_delta(10, {'x': 10, 'y': 20, 'result': 30, 'total': 3})
    tracker.display_deltas()