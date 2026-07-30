# Week 4 - Test Watch Variables Feature
# Test script to verify watch variables functionality

from ui.watch_variables import WatchVariables, WatchVariablesUI
from pychronicle.tracer.optimized_tracer import OptimizedTracer
from pychronicle.storage import StateStorage
import os


def setup_test_data():
    """Create test data for watch variables"""
    print("🔧 Setting up test data...")
    
    # Remove old database
    if os.path.exists("test_watch.db"):
        os.remove("test_watch.db")
    
    # Create test script
    test_script_content = """
# Test script for watch variables
def calculate_fibonacci(n):
    a = 0
    b = 1
    result = []
    
    for i in range(n):
        result.append(a)
        temp = a + b
        a = b
        b = temp
    
    total = sum(result)
    return total

# Run calculation
fibonacci_result = calculate_fibonacci(10)
print(f"Result: {fibonacci_result}")
"""
    
    with open("test_watch_script.py", "w") as f:
        f.write(test_script_content)
    
    # Trace it
    tracer = OptimizedTracer(db_path="test_watch.db")
    tracer.start_trace("test_watch_script.py")
    
    print("✅ Test data created!")


def test_cli_watcher():
    """Test CLI-based watcher"""
    print("\n" + "="*60)
    print("TEST 1: CLI Watcher")
    print("="*60)
    
    watcher = WatchVariables(db_path="test_watch.db")
    
    # Add watches
    watcher.add_watch("a")
    watcher.add_watch("b")
    watcher.add_watch("total")
    
    # Get history
    watcher.get_watch_history()
    
    # Show timeline
    watcher.display_timeline()
    
    # Compare variables
    watcher.compare_variables("a", "b")


def test_variable_queries():
    """Test database queries for watch variables"""
    print("\n" + "="*60)
    print("TEST 2: Variable Queries")
    print("="*60)
    
    storage = StateStorage("test_watch.db")
    
    # Get all unique variables
    cursor = storage.conn.execute(
        '''SELECT DISTINCT variable_name, COUNT(*) as changes
           FROM variable_states 
           GROUP BY variable_name
           ORDER BY changes DESC'''
    )
    
    print("\nAvailable Variables:")
    for row in cursor.fetchall():
        print(f"  {row[0]:<20} | {row[1]:4} changes")
    
    # Test specific variable query
    print("\nDetailed info for 'result':")
    cursor = storage.conn.execute(
        '''SELECT line_number, serialized_value, timestamp
           FROM variable_states 
           WHERE variable_name = 'result'
           ORDER BY id'''
    )
    
    for row in cursor.fetchall():
        print(f"  Line {row[0]:3} | {row[1][:50]:<50} | {row[2][:19]}")


def test_watch_statistics():
    """Test watch variable statistics"""
    print("\n" + "="*60)
    print("TEST 3: Watch Statistics")
    print("="*60)
    
    storage = StateStorage("test_watch.db")
    
    variables = ["a", "b", "result", "total"]
    
    for var in variables:
        cursor = storage.conn.execute(
            '''SELECT 
                   COUNT(*) as changes,
                   MIN(line_number) as first_line,
                   MAX(line_number) as last_line
               FROM variable_states 
               WHERE variable_name = ?''',
            (var,)
        )
        
        stats = cursor.fetchone()
        if stats and stats[0] > 0:
            print(f"\n{var}:")
            print(f"  Total changes: {stats[0]}")
            print(f"  First appearance: Line {stats[1]}")
            print(f"  Last appearance: Line {stats[2]}")
            print(f"  Span: {stats[2] - stats[1]} lines")


if __name__ == "__main__":
    # Setup
    setup_test_data()
    
    # Run tests
    test_cli_watcher()
    test_variable_queries()
    test_watch_statistics()
    
    print("\n" + "="*60)
    print("✅ All tests completed!")
    print("="*60)
    print("\nTo test interactive UI, run:")
    print("  python -m ui.watch_variables")
    print("  python -m ui.integrated_timeline")
