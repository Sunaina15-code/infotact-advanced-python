# Week 3 - Memory Profiler - July 13 - Noah
# Measures memory usage of tracer

import sys
import time
from pychronicle.storage import StateStorage

class MemoryProfiler:
    def __init__(self):
        self.baseline = 0
        self.peak = 0

    def get_size(self, obj):
        """Get size of object in bytes"""
        return sys.getsizeof(obj)

    def profile_storage(self):
        print("=== Memory Profiler ===\n")

        # Test without compression
        db1 = StateStorage(":memory:")
        start_time = time.time()
        test_vars = {
            'x': 10, 'y': 20, 'result': 30,
            'total': 0, 'name': 'PyChronicle'
        }
        # Simulate 100 lines without compression
        for line in range(100):
            for var, val in test_vars.items():
                db1.insert_state(line, var, val)
        states1 = db1.get_all_states()
        time1 = time.time() - start_time
        print(f"Without compression:")
        print(f"  States stored: {len(states1)}")
        print(f"  Time taken:    {time1:.4f}s")
        db1.close()

        # Test with compression (only changes)
        db2 = StateStorage(":memory:")
        start_time = time.time()
        prev = {}
        saved = 0
        for line in range(100):
            # Simulate only x changing every 10 lines
            if line % 10 == 0:
                test_vars['x'] = line
            for var, val in test_vars.items():
                if prev.get(var) != str(val):
                    db2.insert_state(line, var, val)
                    prev[var] = str(val)
                    saved += 1
        states2 = db2.get_all_states()
        time2 = time.time() - start_time
        print(f"\nWith compression:")
        print(f"  States stored: {len(states2)}")
        print(f"  Time taken:    {time2:.4f}s")

        # Results
        reduction = ((len(states1)-len(states2))/len(states1))*100
        print(f"\n=== Results ===")
        print(f"Memory reduced by: {reduction:.1f}%")
        print(f"Speed improved by: {((time1-time2)/time1)*100:.1f}%")
        db2.close()

if __name__ == "__main__":
    profiler = MemoryProfiler()
    profiler.profile_storage()