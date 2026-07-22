# Week 3 - Tracer Accuracy + Performance Validation - Noah
# Validates that the storage is accurate AND fast under load

import sys
import os
import time

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from storage import StateStorage


# ------------------------------------------------------------------ #
#  ACCURACY TESTS
# ------------------------------------------------------------------ #

def test_insert_and_retrieve():
    """Records stored must match records retrieved exactly."""
    db = StateStorage(":memory:")
    db.insert_state(1, "x", 42,        "assignment")
    db.insert_state(2, "name", "hello", "assignment")
    db.insert_state(3, "flag", True,    "assignment")

    rows = db.get_all_states()
    assert len(rows) == 3, f"Expected 3 rows, got {len(rows)}"
    assert rows[0][3] == "x"
    assert rows[1][3] == "name"
    assert rows[2][3] == "flag"
    db.close()
    print("✅ test_insert_and_retrieve passed")


def test_line_number_ordering():
    """Rows should come back ordered by line_number."""
    db = StateStorage(":memory:")
    db.insert_state(30, "c", 3, "assignment")
    db.insert_state(10, "a", 1, "assignment")
    db.insert_state(20, "b", 2, "assignment")

    rows = db.get_all_states()
    lines = [r[2] for r in rows]
    assert lines == sorted(lines), f"Not sorted: {lines}"
    db.close()
    print("✅ test_line_number_ordering passed")


def test_value_integrity():
    """Stored value string must survive round-trip."""
    db = StateStorage(":memory:")
    db.insert_state(5, "pi", 3.14159, "assignment")

    rows = db.get_all_states()
    # value is json-dumped in StateStorage, so '3.14159' is inside the json string
    assert "3.14159" in rows[0][4], f"Value not preserved: {rows[0][4]}"
    db.close()
    print("✅ test_value_integrity passed")


# ------------------------------------------------------------------ #
#  PERFORMANCE THRESHOLDS
# ------------------------------------------------------------------ #

def test_10k_inserts_under_5_seconds():
    """10,000 inserts must complete in under 5 seconds."""
    db    = StateStorage(":memory:")
    start = time.perf_counter()
    for i in range(10_000):
        db.insert_state(i % 100, f"var_{i%10}", i, "assignment")
    elapsed = time.perf_counter() - start
    db.close()
    assert elapsed < 5.0, f"10k inserts took {elapsed:.2f}s — too slow"
    print(f"✅ test_10k_inserts_under_5_seconds passed ({elapsed:.3f}s)")


def test_50k_inserts_under_20_seconds():
    """50,000 inserts must complete in under 20 seconds."""
    db    = StateStorage(":memory:")
    start = time.perf_counter()
    for i in range(50_000):
        db.insert_state(i % 500, f"var_{i%20}", i, "assignment")
    elapsed = time.perf_counter() - start
    db.close()
    assert elapsed < 20.0, f"50k inserts took {elapsed:.2f}s — too slow"
    print(f"✅ test_50k_inserts_under_20_seconds passed ({elapsed:.3f}s)")


def test_query_all_under_2_seconds():
    """Fetching all 10,000 rows should take under 2 seconds."""
    db = StateStorage(":memory:")
    for i in range(10_000):
        db.insert_state(i % 100, f"var_{i%10}", i, "assignment")

    start = time.perf_counter()
    rows  = db.get_all_states()
    elapsed = time.perf_counter() - start
    db.close()

    assert len(rows) == 10_000, f"Expected 10000, got {len(rows)}"
    assert elapsed < 2.0, f"Query took {elapsed:.2f}s — too slow"
    print(f"✅ test_query_all_under_2_seconds passed ({elapsed:.4f}s)")


def test_delta_compression_saves_records():
    """Compressed storage must store fewer records than raw storage."""
    iterations = 5_000
    variables  = {'x': 0, 'name': 'test', 'flag': True}

    # Raw
    db_raw = StateStorage(":memory:")
    for i in range(iterations):
        variables['x'] = i
        for var, val in variables.items():
            db_raw.insert_state(i, var, val, "assignment")
    raw_count = len(db_raw.get_all_states())
    db_raw.close()

    # Compressed
    db_comp = StateStorage(":memory:")
    prev = {}
    for i in range(iterations):
        variables['x'] = i
        for var, val in variables.items():
            sv = str(val)
            if prev.get(var) != sv:
                db_comp.insert_state(i, var, val, "changed")
                prev[var] = sv
    comp_count = len(db_comp.get_all_states())
    db_comp.close()

    assert comp_count < raw_count, (
        f"Compression didn't reduce records: {comp_count} >= {raw_count}"
    )
    reduction = ((raw_count - comp_count) / raw_count) * 100
    print(f"✅ test_delta_compression_saves_records passed "
          f"(reduction: {reduction:.1f}%)")


# ------------------------------------------------------------------ #
#  RUNNER
# ------------------------------------------------------------------ #

if __name__ == "__main__":
    print("\n=== PyChronicle — Week 3 Tracer Accuracy & Performance Tests ===\n")

    # Accuracy
    test_insert_and_retrieve()
    test_line_number_ordering()
    test_value_integrity()

    # Performance
    test_10k_inserts_under_5_seconds()
    test_50k_inserts_under_20_seconds()
    test_query_all_under_2_seconds()
    test_delta_compression_saves_records()

    print("\n=== All Tests Passed ✅ ===")
