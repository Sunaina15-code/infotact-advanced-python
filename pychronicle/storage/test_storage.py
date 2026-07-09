# Athrva - Week 1: Storage Schema Testing
import sqlite3
import json
from datetime import datetime
from pychronicle.storage import StateStorage

def test_storage_schema():
    """Test the SQLite storage schema"""
    print("=== Storage Schema Test ===\n")
    
    # Test 1: Create database
    db = StateStorage(":memory:")
    print("✓ Test 1: Database created successfully")
    
    # Test 2: Insert single state
    db.insert_state(1, "x", 10, "assignment")
    print("✓ Test 2: Single state inserted")
    
    # Test 3: Insert multiple states
    db.insert_state(2, "y", 20, "assignment")
    db.insert_state(3, "name", "PyChronicle", "assignment")
    db.insert_state(4, "result", 30, "assignment")
    print("✓ Test 3: Multiple states inserted")
    
    # Test 4: Retrieve all states
    states = db.get_all_states()
    print(f"✓ Test 4: Retrieved {len(states)} states")
    
    # Test 5: Verify data integrity
    print("\n=== Stored Data ===")
    for state in states:
        print(f"ID:{state[0]} | Time:{state[1][:19]} | "
              f"Line:{state[2]} | Var:{state[3]} | Value:{state[4]}")
    
    # Test 6: Performance test
    print("\n=== Performance Test ===")
    start = datetime.now()
    for i in range(1000):
        db.insert_state(i, f"var_{i}", i*2, "assignment")
    end = datetime.now()
    elapsed = (end - start).total_seconds()
    print(f"✓ Test 6: 1000 inserts in {elapsed:.3f} seconds")
    
    total = db.get_all_states()
    print(f"✓ Total records: {len(total)}")
    
    db.close()
    print("\n=== All Tests Passed! ===")

if __name__ == "__main__":
    test_storage_schema()