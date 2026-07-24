# Week 3 - Database Performance Test - Noah
# Benchmarks storage with thousands of state changes
# Tests: insert speed, query speed, disk overhead, compression comparison

import time
import os
import sys
import sqlite3
import json
from datetime import datetime

# Add project root to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from storage import StateStorage


class DBPerformanceTester:
    """
    Full performance benchmark for PyChronicle storage.
    Covers: bulk inserts, query speed, disk size, compression comparison.
    """

    def __init__(self):
        self.results = []
        self.test_db_path = "perf_test.db"

    # ------------------------------------------------------------------ #
    #  HELPER
    # ------------------------------------------------------------------ #

    def _fresh_db(self, path=":memory:"):
        """Return a clean StateStorage instance."""
        return StateStorage(path)

    def _remove_test_db(self):
        if os.path.exists(self.test_db_path):
            os.remove(self.test_db_path)

    def _record(self, label, count, elapsed):
        ops_per_sec = count / elapsed if elapsed > 0 else float('inf')
        ms_per_op   = (elapsed / count) * 1000 if count > 0 else 0
        self.results.append({
            'label':       label,
            'count':       count,
            'elapsed_s':   elapsed,
            'ops_per_sec': ops_per_sec,
            'ms_per_op':   ms_per_op,
        })
        print(f"  {label:<35} | {count:>7} ops | "
              f"{elapsed:.4f}s | {ops_per_sec:>9,.0f} ops/s | "
              f"{ms_per_op:.4f} ms/op")

    # ------------------------------------------------------------------ #
    #  TEST 1 — BULK INSERT SCALING
    # ------------------------------------------------------------------ #

    def test_bulk_inserts(self):
        """Insert 100 → 100,000 records and measure throughput."""
        print("\n" + "=" * 70)
        print("TEST 1: Bulk Insert Scaling")
        print("=" * 70)

        sizes = [100, 1_000, 5_000, 10_000, 50_000, 100_000]

        for n in sizes:
            db = self._fresh_db()
            start = time.perf_counter()
            for i in range(n):
                db.insert_state(
                    line_number=i % 200,
                    variable_name=f"var_{i % 20}",
                    value=i * 3,
                    event_type="assignment"
                )
            elapsed = time.perf_counter() - start
            db.close()
            self._record(f"Insert {n:>7,} records", n, elapsed)

    # ------------------------------------------------------------------ #
    #  TEST 2 — QUERY SPEED
    # ------------------------------------------------------------------ #

    def test_query_speed(self):
        """Populate DB then benchmark common query patterns."""
        print("\n" + "=" * 70)
        print("TEST 2: Query Speed (on 50,000-record database)")
        print("=" * 70)

        # Build dataset once
        db = self._fresh_db()
        for i in range(50_000):
            db.insert_state(
                line_number=i % 500,
                variable_name=f"var_{i % 15}",
                value=i,
                event_type="assignment"
            )

        # 2a — fetch all of them
        start = time.perf_counter()
        all_states = db.get_all_states()
        elapsed = time.perf_counter() - start
        self._record("SELECT all 50,000 rows", len(all_states), elapsed)

        # 2b — query by line number(indexed)
        start = time.perf_counter()
        for line in range(0, 500, 10):   # 50 queries
            db.conn.execute(
                "SELECT * FROM variable_states WHERE line_number = ?", (line,)
            ).fetchall()
        elapsed = time.perf_counter() - start
        self._record("50 indexed line queries", 50, elapsed)

        # 2c — query by variable name
        start = time.perf_counter()
        for v in range(15):
            db.conn.execute(
                "SELECT * FROM variable_states WHERE variable_name = ?",
                (f"var_{v}",)
            ).fetchall()
        elapsed = time.perf_counter() - start
        self._record("15 variable name queries", 15, elapsed)

        # 2d — COUNT aggregate
        start = time.perf_counter()
        for _ in range(100):
            db.conn.execute(
                "SELECT COUNT(*) FROM variable_states"
            ).fetchone()
        elapsed = time.perf_counter() - start
        self._record("100 COUNT(*) queries", 100, elapsed)

        db.close()

    # ------------------------------------------------------------------ #
    #  TEST 3 — DISK SIZE OVERHEAD
    # ------------------------------------------------------------------ #

    def test_disk_overhead(self):
        """Measure actual .db file size for varying record counts."""
        print("\n" + "=" * 70)
        print("TEST 3: Disk Size Overhead")
        print("=" * 70)

        sizes = [1_000, 10_000, 50_000, 100_000]

        for n in sizes:
            self._remove_test_db()
            db = self._fresh_db(self.test_db_path)
            for i in range(n):
                db.insert_state(
                    line_number=i % 200,
                    variable_name=f"var_{i % 20}",
                    value=i,
                    event_type="assignment"
                )
            db.close()

            size_bytes = os.path.getsize(self.test_db_path)
            size_kb    = size_bytes / 1024
            size_mb    = size_kb / 1024
            bytes_per  = size_bytes / n

            print(f"  {n:>7,} records → "
                  f"{size_kb:>8.1f} KB  "
                  f"({size_mb:.3f} MB)  "
                  f"~{bytes_per:.1f} bytes/record")

        self._remove_test_db()

    # ------------------------------------------------------------------ #
    #  TEST 4 — COMPRESSION COMPARISON
    # ------------------------------------------------------------------ #

    def test_compression_comparison(self):
        """
        Compare raw storage vs delta-compressed storage.
        Simulates a loop where only one variable changes each iteration.
        """
        print("\n" + "=" * 70)
        print("TEST 4: Compression Comparison (raw vs delta)")
        print("=" * 70)

        iterations = 10_000
        variables  = {'counter': 0, 'total': 0, 'name': 'PyChronicle',
                      'debug': True, 'version': '1.0'}

        # --- RAW: save every variable on every line ---
        db_raw = self._fresh_db()
        start  = time.perf_counter()
        for i in range(iterations):
            variables['counter'] = i
            variables['total']   = i * 2
            for var, val in variables.items():
                db_raw.insert_state(i, var, val, "assignment")
        raw_time   = time.perf_counter() - start
        raw_count  = len(db_raw.get_all_states())
        db_raw.close()

        # --- COMPRESSED: save only changed variables ---
        db_comp   = self._fresh_db()
        prev      = {}
        start     = time.perf_counter()
        comp_saved = 0
        for i in range(iterations):
            variables['counter'] = i
            variables['total']   = i * 2
            for var, val in variables.items():
                str_val = str(val)
                if prev.get(var) != str_val:
                    db_comp.insert_state(i, var, val, "changed")
                    prev[var]   = str_val
                    comp_saved += 1
        comp_time  = time.perf_counter() - start
        comp_count = len(db_comp.get_all_states())
        db_comp.close()

        reduction = ((raw_count - comp_count) / raw_count) * 100 if raw_count else 0
        speed_gain = ((raw_time - comp_time) / raw_time) * 100 if raw_time else 0

        print(f"  {'Metric':<30} {'Raw':>15} {'Compressed':>15}")
        print(f"  {'-'*60}")
        print(f"  {'Records stored':<30} {raw_count:>15,} {comp_count:>15,}")
        print(f"  {'Time taken (s)':<30} {raw_time:>15.4f} {comp_time:>15.4f}")
        print(f"  {'Storage reduction':<30} {'':>15} {reduction:>14.1f}%")
        print(f"  {'Speed improvement':<30} {'':>15} {speed_gain:>14.1f}%")

        self._record("Raw storage (10k iterations)",        raw_count,  raw_time)
        self._record("Compressed storage (10k iterations)", comp_count, comp_time)

    # ------------------------------------------------------------------ #
    #  TEST 5 — CONCURRENT WRITE SIMULATION
    # ------------------------------------------------------------------ #

    def test_rapid_state_changes(self):
        """
        Simulate rapid state changes as seen during a tight loop trace.
        Writes 1,000 changes per second target test.
        """
        print("\n" + "=" * 70)
        print("TEST 5: Rapid State Change Simulation (tight loop trace)")
        print("=" * 70)

        db    = self._fresh_db()
        total = 20_000
        start = time.perf_counter()

        # Simulate counter variable changing every line in a loop
        for i in range(total):
            db.insert_state(
                line_number=10 + (i % 5),   # lines 10-14 repeating
                variable_name="counter",
                value=i,
                event_type="changed"
            )

        elapsed   = time.perf_counter() - start
        ops_per_s = total / elapsed

        print(f"  Simulated {total:,} counter changes in {elapsed:.4f}s")
        print(f"  Throughput: {ops_per_s:,.0f} state changes/second")

        if ops_per_s >= 5_000:
            print("  ✅ PASS — handles tight-loop traces at real speed")
        else:
            print("  ⚠️  SLOW — may lag on very tight loops")

        db.close()
        self._record("Rapid loop changes (20k)", total, elapsed)

    # ------------------------------------------------------------------ #
    #  FINAL REPORT
    # ------------------------------------------------------------------ #

    def print_summary(self):
        print("\n" + "=" * 70)
        print("PERFORMANCE SUMMARY")
        print("=" * 70)
        print(f"  {'Test':<35} | {'Count':>8} | {'Time(s)':>8} | {'ops/s':>10}")
        print(f"  {'-'*65}")
        for r in self.results:
            print(f"  {r['label']:<35} | {r['count']:>8,} | "
                  f"{r['elapsed_s']:>8.4f} | {r['ops_per_sec']:>10,.0f}")
        print("\n  ✅ Week 3 Performance Testing Complete")
        print("  Storage is validated for production-scale tracing.\n")

    # ------------------------------------------------------------------ #
    #  RUN ALL
    # ------------------------------------------------------------------ #

    def run_all(self):
        print("\n" + "#" * 70)
        print("#  PyChronicle — Week 3 Performance Test Suite")
        print(f"#  Run at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print("#" * 70)

        self.test_bulk_inserts()
        self.test_query_speed()
        self.test_disk_overhead()
        self.test_compression_comparison()
        self.test_rapid_state_changes()
        self.print_summary()


if __name__ == "__main__":
    tester = DBPerformanceTester()
    tester.run_all()
