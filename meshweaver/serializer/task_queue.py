# MeshWeaver - Task Queue - Aug 8 - Noah
# Distributed task queue with priority support

import asyncio
import cloudpickle
import hashlib
from datetime import datetime
from enum import Enum

class TaskStatus(Enum):
    PENDING = "pending"
    RUNNING = "running"
    COMPLETE = "complete"
    FAILED = "failed"

class Task:
    def __init__(self, func, args=(), kwargs={}, priority=1):
        self.task_id = hashlib.md5(
            f"{func.__name__}{datetime.now()}".encode()
        ).hexdigest()[:8]
        self.func = func
        self.args = args
        self.kwargs = kwargs
        self.priority = priority
        self.status = TaskStatus.PENDING
        self.result = None
        self.created_at = datetime.now().isoformat()
        self.func_name = func.__name__

    def serialize(self):
        return cloudpickle.dumps({
            'task_id': self.task_id,
            'func': self.func,
            'args': self.args,
            'kwargs': self.kwargs,
            'priority': self.priority,
            'func_name': self.func_name
        })

    @staticmethod
    def deserialize(data):
        return cloudpickle.loads(data)

class DistributedTaskQueue:
    def __init__(self, node_id):
        self.node_id = node_id
        self.queue = asyncio.PriorityQueue()
        self.completed = []
        self.failed = []
        self.running = {}

    async def submit(self, func, *args, priority=1, **kwargs):
        task = Task(func, args, kwargs, priority)
        await self.queue.put((priority, task))
        print(f"[{self.node_id}] Task submitted: "
              f"{task.func_name} (ID: {task.task_id})")
        return task.task_id

    async def execute_next(self):
        if self.queue.empty():
            return None
        priority, task = await self.queue.get()
        task.status = TaskStatus.RUNNING
        self.running[task.task_id] = task
        print(f"[{self.node_id}] Executing: {task.func_name}")
        try:
            if asyncio.iscoroutinefunction(task.func):
                task.result = await task.func(*task.args, **task.kwargs)
            else:
                task.result = task.func(*task.args, **task.kwargs)
            task.status = TaskStatus.COMPLETE
            self.completed.append(task)
            print(f"[{self.node_id}] ✅ Complete: "
                  f"{task.func_name} → {task.result}")
        except Exception as e:
            task.status = TaskStatus.FAILED
            self.failed.append(task)
            print(f"[{self.node_id}] ❌ Failed: {task.func_name} → {e}")
        finally:
            del self.running[task.task_id]
        return task

    async def run_all(self):
        while not self.queue.empty():
            await self.execute_next()

    def display_stats(self):
        print(f"\n=== Queue Stats [{self.node_id}] ===")
        print(f"Pending:   {self.queue.qsize()}")
        print(f"Running:   {len(self.running)}")
        print(f"Completed: {len(self.completed)}")
        print(f"Failed:    {len(self.failed)}")
        if self.completed:
            print("\nCompleted Tasks:")
            for t in self.completed:
                print(f"  {t.task_id} | {t.func_name} → {t.result}")

# Demo functions
def add_numbers(x, y): return x + y
def multiply(x, y): return x * y
def compute_stats(data):
    return {'sum': sum(data), 'mean': sum(data)/len(data)}

async def demo_queue():
    print("=== Distributed Task Queue Demo ===\n")
    queue = DistributedTaskQueue("node-alpha")

    await queue.submit(add_numbers, 10, 20, priority=1)
    await queue.submit(multiply, 5, 6, priority=2)
    await queue.submit(compute_stats, [1,2,3,4,5], priority=1)

    print("\nExecuting all tasks...")
    await queue.run_all()
    queue.display_stats()
    print("\n=== Queue Demo Complete! ✅ ===")

if __name__ == "__main__":
    asyncio.run(demo_queue())