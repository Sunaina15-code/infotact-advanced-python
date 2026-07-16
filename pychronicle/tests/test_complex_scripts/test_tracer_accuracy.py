# test_tracer_accuracy.py — Week 2 Testing & Validation
# Tests the OptimizedTracer against complex scripts and validates accuracy

import sys
import os
import sqlite3

# Make sure project root is in path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../../..')))

from pychronicle.tracer.optimized_tracer import OptimizedTracer
from pychronicle.storage import StateStorage

# ── Helpers ──────────────────────────────────────────────────────────────────

SCRIPTS_DIR = os.path.join(os.path.dirname(__file__), 'test_complex_scripts')

def get_script(name):
    return os.path.join(SCRIPTS_DIR, name)

def get_all_states(db_path):
    conn = sqlite3.connect(db_path)
    rows = conn.execute('SELECT * FROM variable_states ORDER BY id').fetchall()
    conn.close()
    return rows

def run_tracer(script_name, db_name):
    """Run the OptimizedTracer on a script, return (tracer, states)"""
    db_path = db_name
    # Remove old db if exists so results are clean
    if os.path.exists(db_path):
        os.remove(db_path)
    tracer = OptimizedTracer(db_path=db_path)
    tracer.start_trace(get_script(script_name))
    states = get_all_states(db_path)
    return tracer, states

# ── Test 1: Loop Script ───────────────────────────────────────────────────────

def test_loop_script():
    print("\n=== TEST 1: loop_script.py ===")
    tracer, states = run_tracer('loop_script.py', 'test_loop.db')

    # Validate: 'total' should have been recorded and its final value should be 45
    total_states = [s for s in states if s[3] == 'total']
    final_total = total_states[-1][4] if total_states else None  # serialized_value column

    print(f"  'total' recorded {len(total_states)} time(s)")
    print(f"  Final value of 'total': {final_total}")

    assert len(total_states) > 0, "FAIL: 'total' was never recorded"
    assert '"45"' in final_total or '45' in final_total, f"FAIL: expected 45, got {final_total}"
    print("  ✓ total = 45 confirmed")

    # Validate: countdown should reach 0
    countdown_states = [s for s in states if s[3] == 'countdown']
    final_countdown = countdown_states[-1][4] if countdown_states else None
    assert '0' in str(final_countdown), f"FAIL: countdown didn't reach 0, got {final_countdown}"
    print(f"  ✓ countdown reached 0 ({len(countdown_states)} changes recorded)")

    # Validate: matrix_sum
    matrix_states = [s for s in states if s[3] == 'matrix_sum']
    print(f"  'matrix_sum' recorded {len(matrix_states)} time(s)")
    assert len(matrix_states) > 0, "FAIL: matrix_sum was never recorded"
    print("  ✓ matrix_sum tracked")

    # Validate delta efficiency: skip_count should be > 0
    assert tracer.skip_count > 0, "FAIL: delta tracker never skipped anything — not working"
    print(f"  ✓ Delta tracker skipped {tracer.skip_count} unchanged lines")

    print("  TEST 1 PASSED\n")
    return len(states), tracer.trace_count, tracer.skip_count

# ── Test 2: Nested Script ─────────────────────────────────────────────────────

def test_nested_script():
    print("=== TEST 2: nested_script.py ===")
    tracer, states = run_tracer('nested_script.py', 'test_nested.db')

    # Validate fibonacci — fib list should grow
    fib_states = [s for s in states if s[3] == 'fib']
    print(f"  'fib' recorded {len(fib_states)} time(s)")
    assert len(fib_states) > 0, "FAIL: fib was never recorded"
    print("  ✓ fib tracked")

    # max_val should end at 9
    max_states = [s for s in states if s[3] == 'max_val']
    final_max = max_states[-1][4] if max_states else None
    assert '9' in str(final_max), f"FAIL: max_val should be 9, got {final_max}"
    print(f"  ✓ max_val = 9 confirmed ({len(max_states)} changes)")

    # word should end as 'PyChronicle'
    word_states = [s for s in states if s[3] == 'word']
    final_word = word_states[-1][4] if word_states else None
    assert 'PyChronicle' in str(final_word), f"FAIL: word should be PyChronicle, got {final_word}"
    print(f"  ✓ word = 'PyChronicle' confirmed ({len(word_states)} changes)")

    print("  TEST 2 PASSED\n")
    return len(states), tracer.trace_count, tracer.skip_count

# ── Test 3: Edge Cases ────────────────────────────────────────────────────────

def test_edge_cases():
    print("=== TEST 3: edge_cases_script.py ===")
    tracer, states = run_tracer('edge_cases_script.py', 'test_edge.db')

    # x changes type multiple times — all should be recorded
    x_states = [s for s in states if s[3] == 'x']
    print(f"  'x' recorded {len(x_states)} time(s)")
    assert len(x_states) >= 5, f"FAIL: x should have at least 5 changes, got {len(x_states)}"
    print("  ✓ type-changing variable tracked correctly")

    # big_total stress test — should reach 124750
    big_states = [s for s in states if s[3] == 'big_total']
    final_big = big_states[-1][4] if big_states else None
    assert '124750' in str(final_big), f"FAIL: big_total should be 124750, got {final_big}"
    print(f"  ✓ big_total = 124750 confirmed (stress test passed, {len(big_states)} changes)")

    # flag should have toggled
    flag_states = [s for s in states if s[3] == 'flag']
    print(f"  'flag' toggled {len(flag_states)} time(s)")
    assert len(flag_states) >= 2, "FAIL: flag never toggled"
    print("  ✓ boolean toggling tracked")

    print("  TEST 3 PASSED\n")
    return len(states), tracer.trace_count, tracer.skip_count

# ── Summary Report ────────────────────────────────────────────────────────────

def print_summary(results):
    print("=" * 50)
    print("VALIDATION SUMMARY")
    print("=" * 50)
    labels = ['loop_script', 'nested_script', 'edge_cases']
    for label, (total_states, saved, skipped) in zip(labels, results):
        total_lines = saved + skipped
        efficiency = (skipped / total_lines * 100) if total_lines > 0 else 0
        print(f"\n  {label}:")
        print(f"    Total DB records : {total_states}")
        print(f"    Changes saved    : {saved}")
        print(f"    Lines skipped    : {skipped}")
        print(f"    Delta efficiency : {efficiency:.1f}%")
    print("\n  All tests passed ✓")
    print("=" * 50)

# ── Run ───────────────────────────────────────────────────────────────────────

if __name__ == "__main__":
    results = []
    results.append(test_loop_script())
    results.append(test_nested_script())
    results.append(test_edge_cases())
    print_summary(results)
