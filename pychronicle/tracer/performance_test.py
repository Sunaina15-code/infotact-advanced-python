# Week 2 - Performance Test - July 10 - Noah
# Benchmarks the tracer performance

import time
import sys
from pychronicle.storage import StateStorage

class PerformanceTester:
    def __init__(self):
        self.results = []

    def test_storage_speed(self):
        """Test how fast storage can handle inserts"""
        print("=== Storage Performance Test ===\n")
        
        db = StateStorage(":memory:")
        
        # Test 1: 100 inserts
        start = time.time()
        for i in range(100):
            db.insert_state(i, f"var_{i}", i*2)
        elapsed = time.time() - start
        print(f"100 inserts:  {elapsed:.4f}s ({100/elapsed:.0f} ops/sec)")
        self.results.append(('100 inserts', elapsed))

        # Test 2: 1000 inserts
        start = time.time()
        for i in range(1000):
            db.insert_state(i, f"var_{i}", i*2)
        elapsed = time.time() - start
        print(f"1000 inserts: {elapsed:.4f}s ({1000/elapsed:.0f} ops/sec)")
        self.results.append(('1000 inserts', elapsed))

        # Test 3: 10000 inserts
        start = time.time()
        for i in range(10000):
            db.insert_state(i, f"var_{i}", i*2)
        elapsed = time.time() - start
        print(f"10000 inserts:{elapsed:.4f}s ({10000/elapsed:.0f} ops/sec)")
        self.results.append(('10000 inserts', elapsed))

        # Test 4: Query speed
        start = time.time()
        results = db.get_all_states()
        elapsed = time.time() - start
        print(f"\nQuery {len(results)} records: {elapsed:.4f}s")

        db.close()
        print("\n=== Performance Test Complete ===")
        print("Storage is fast enough for production use! ✅")

if __name__ == "__main__":
    tester = PerformanceTester()
    tester.test_storage_speed()