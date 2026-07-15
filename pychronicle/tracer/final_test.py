# Week 4 - Final Test - July 15 - Noah
# Complete end-to-end test of PyChronicle

import sys
import os
from pychronicle.tracer.compressed_tracer import CompressedTracer
from pychronicle.storage import StateStorage
from pychronicle.tracer.trace_filter import TraceFilter
from pychronicle.tracer.delta_tracker import DeltaTracker

def run_final_test():
    print("=" * 50)
    print("  PyChronicle - Final End-to-End Test")
    print("=" * 50)

    # Test 1: Filter
    print("\n[1/4] Testing Trace Filter...")
    f = TraceFilter()
    test_vars = {'x': 10, '__name__': '__main__', 'y': 20}
    filtered = f.filter_locals(test_vars)
    assert '__name__' not in filtered
    assert 'x' in filtered
    print("✅ Filter working correctly!")

    # Test 2: Delta Tracker
    print("\n[2/4] Testing Delta Tracker...")
    d = DeltaTracker()
    changes1 = d.compute_delta(1, {'x': 10})
    changes2 = d.compute_delta(2, {'x': 10, 'y': 20})
    changes3 = d.compute_delta(3, {'x': 10, 'y': 20})
    assert len(changes1) == 1
    assert len(changes2) == 1
    assert len(changes3) == 0
    print("✅ Delta tracking working correctly!")

    # Test 3: Storage
    print("\n[3/4] Testing Storage...")
    db = StateStorage(":memory:")
    db.insert_state(1, "x", 10)
    db.insert_state(2, "y", 20)
    states = db.get_all_states()
    assert len(states) == 2
    print("✅ Storage working correctly!")

    # Test 4: Full trace
    print("\n[4/4] Testing Full Tracer...")
    tracer = CompressedTracer(":memory:")
    tracer.run("test_script.py")
    print("✅ Full tracer working correctly!")

    print("\n" + "=" * 50)
    print("  ALL TESTS PASSED! PyChronicle is ready! 🎉")
    print("=" * 50)

if __name__ == "__main__":
    run_final_test()