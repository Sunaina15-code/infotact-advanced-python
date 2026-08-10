# MeshWeaver - Heartbeat Monitor - Aug 9 - Athrva
# Detects node failures and re-routes tasks

import asyncio
from datetime import datetime, timedelta

class HeartbeatMonitor:
    """
    Monitors node health via heartbeats
    If a node drops offline → task is marked failed and re-routed
    """
    def __init__(self, node_id, timeout=10):
        self.node_id = node_id
        self.timeout = timeout
        self.heartbeats = {}
        self.failed_nodes = set()
        self.pending_tasks = {}

    def register_node(self, peer_id):
        """Register a new peer for monitoring"""
        self.heartbeats[peer_id] = datetime.now()
        print(f"[{self.node_id}] Monitoring: {peer_id}")

    def receive_heartbeat(self, peer_id):
        """Record heartbeat from peer"""
        self.heartbeats[peer_id] = datetime.now()
        if peer_id in self.failed_nodes:
            self.failed_nodes.remove(peer_id)
            print(f"[{self.node_id}] ✅ Node recovered: {peer_id}")

    def check_nodes(self):
        """Check all nodes for timeout"""
        now = datetime.now()
        newly_failed = []

        for peer_id, last_beat in self.heartbeats.items():
            elapsed = (now - last_beat).seconds
            if elapsed > self.timeout:
                if peer_id not in self.failed_nodes:
                    self.failed_nodes.add(peer_id)
                    newly_failed.append(peer_id)
                    print(f"[{self.node_id}] ❌ Node FAILED: {peer_id} "
                          f"(no heartbeat for {elapsed}s)")

        return newly_failed

    def assign_task(self, task_id, node_id, task_data):
        """Assign task to a node"""
        self.pending_tasks[task_id] = {
            'node': node_id,
            'data': task_data,
            'assigned_at': datetime.now().isoformat(),
            'status': 'running'
        }
        print(f"[{self.node_id}] Task {task_id} assigned to {node_id}")

    def handle_node_failure(self, failed_node):
        """Re-route tasks from failed node"""
        affected = {
            tid: task for tid, task in self.pending_tasks.items()
            if task['node'] == failed_node and task['status'] == 'running'
        }

        print(f"\n[{self.node_id}] Handling failure of {failed_node}")
        print(f"  Affected tasks: {len(affected)}")

        for task_id, task in affected.items():
            task['status'] = 'failed'
            print(f"  ❌ Task {task_id} marked FAILED — needs re-routing")

        return list(affected.keys())

    def get_active_nodes(self):
        """Get list of currently active nodes"""
        return [
            nid for nid in self.heartbeats.keys()
            if nid not in self.failed_nodes
        ]

    def display_status(self):
        print(f"\n=== Heartbeat Monitor [{self.node_id}] ===")
        now = datetime.now()
        for peer_id, last_beat in self.heartbeats.items():
            elapsed = (now - last_beat).seconds
            status = "❌ FAILED" if peer_id in self.failed_nodes else "✅ Active"
            print(f"  {peer_id:<20} Last: {elapsed}s ago  {status}")
        print(f"\nActive: {len(self.get_active_nodes())} | "
              f"Failed: {len(self.failed_nodes)}")

async def demo_heartbeat():
    print("=== Heartbeat Monitor Demo ===\n")

    monitor = HeartbeatMonitor("coordinator", timeout=3)

    # Register nodes
    monitor.register_node("node-alpha")
    monitor.register_node("node-beta")
    monitor.register_node("node-gamma")

    # Assign tasks
    monitor.assign_task("t001", "node-alpha", {"func": "ml_task"})
    monitor.assign_task("t002", "node-beta", {"func": "data_task"})
    monitor.assign_task("t003", "node-gamma", {"func": "compute_task"})

    # Simulate heartbeats
    monitor.receive_heartbeat("node-alpha")
    monitor.receive_heartbeat("node-beta")
    # node-gamma doesn't send heartbeat (simulating failure)

    print("\nWaiting for timeout...")
    await asyncio.sleep(4)

    # Check nodes
    failed = monitor.check_nodes()
    for node in failed:
        monitor.handle_node_failure(node)

    monitor.display_status()
    print("\n✅ Heartbeat monitoring complete!")

if __name__ == "__main__":
    asyncio.run(demo_heartbeat())