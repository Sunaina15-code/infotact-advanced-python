# MeshWeaver - Task Serializer - Aug 3 - Athrva
# Serializes Python functions using cloudpickle

import cloudpickle
import hashlib
import json
from datetime import datetime

class TaskSerializer:
    def __init__(self):
        self.serialized_tasks = {}

    def serialize_task(self, func, *args, **kwargs):
        """Serialize a Python function and its arguments"""
        try:
            task_data = {
                'function': cloudpickle.dumps(func),
                'args': cloudpickle.dumps(args),
                'kwargs': cloudpickle.dumps(kwargs),
                'func_name': func.__name__,
                'timestamp': datetime.now().isoformat()
            }
            # Create unique task ID
            task_id = hashlib.md5(
                f"{func.__name__}{datetime.now()}".encode()
            ).hexdigest()[:8]

            self.serialized_tasks[task_id] = task_data
            print(f"✅ Task serialized: {func.__name__} (ID: {task_id})")
            return task_id, cloudpickle.dumps(task_data)

        except Exception as e:
            print(f"❌ Serialization error: {e}")
            return None, None

    def deserialize_task(self, serialized_data):
        """Deserialize and execute a task"""
        try:
            task_data = cloudpickle.loads(serialized_data)
            func = cloudpickle.loads(task_data['function'])
            args = cloudpickle.loads(task_data['args'])
            kwargs = cloudpickle.loads(task_data['kwargs'])
            print(f"✅ Task deserialized: {task_data['func_name']}")
            return func, args, kwargs
        except Exception as e:
            print(f"❌ Deserialization error: {e}")
            return None, None, None

    def execute_serialized(self, serialized_data):
        """Deserialize and immediately execute"""
        func, args, kwargs = self.deserialize_task(serialized_data)
        if func:
            result = func(*args, **kwargs)
            print(f"✅ Task executed! Result: {result}")
            return result
        return None

def demo_task(x, y):
    """Example task to serialize"""
    return x + y

def ml_task(data):
    """Example ML-like task"""
    total = sum(data)
    mean = total / len(data)
    return {'sum': total, 'mean': mean, 'count': len(data)}

if __name__ == "__main__":
    print("=== Task Serializer Demo ===\n")
    serializer = TaskSerializer()

    # Test 1: Simple function
    print("Test 1: Simple addition task")
    task_id, serialized = serializer.serialize_task(demo_task, 10, 20)
    result = serializer.execute_serialized(serialized)

    # Test 2: ML-like function
    print("\nTest 2: ML task")
    task_id2, serialized2 = serializer.serialize_task(
        ml_task, [1, 2, 3, 4, 5]
    )
    result2 = serializer.execute_serialized(serialized2)
    print(f"ML Result: {result2}")

    print("\n=== Serialization Complete! ===")
# Aug 3 update
