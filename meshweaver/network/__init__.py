# MeshWeaver - Task Router - Aug 9 - Sunaina
# Routes tasks to node with lowest CPU load

import asyncio
import json
from datetime import datetime
from meshweaver.network.gossip import GossipNode

class TaskRouter:
    """
    Routes submitted tasks to the peer with lowest CPU load
    Uses gossip protocol data to make routing decisions
    """
    def __init__(self, node_id):
        self.node_id = node_id
        self.node_loads = {}
        self.routing_history = []

    def update_load(self, node_id, cpu, ram):
        """Update known load for a node"""
        self.node_loads[node_id] = {
            'cpu': cpu,
            'ram': ram,
            'updated_at': datetime.now().isoformat()
        }

    def find_best_node(self):
        """Find node with lowest CPU load"""
        if not self.node_loads:
            print(f"[{self.node_id}] No peers known — routing to self")
            return self.node_id

        best = min(
            self.node_loads.keys(),
            key=lambda n: self.node_loads[n]['cpu']
        )
        print(f"[{self.node_id}] Best node: {best} "
              f"(CPU: {self.node_loads[best]['cpu']}%)")
        return best

    def route_task(self, task_name, task_data):
        """Route a task to the best available node"""
        target = self.find_best_node()
        routing_entry = {
            'task': task_name,
            'routed_to': target,
            'cpu_at_routing': self.node_loads.get(
                target, {}
            ).get('cpu', 0),
            'timestamp': datetime.now().isoformat()
        }
        self.routing_history.append(routing_entry)
        print(f"[{self.node_id}] Routing '{task_name}' → {target}")
        return target, routing_entry

    def display_network_status(self):
        print(f"\n=== Network Status [{self.node_id}] ===")
        print(f"{'Node':<20} {'CPU%':<10} {'RAM%':<10} {'Status'}")
        print("-" * 50)
        for nid, load in self.node_loads.items():
            cpu = load['cpu']
            status = "✅ Available" if cpu < 70 else "⚠️ High Load"
            bar = "█" * int(cpu/10)
            print(f"{nid:<20} {cpu:<10} {load['ram']:<10} {status}")

    def display_routing_history(self):
        print(f"\n=== Routing History ===")
        for entry in self.routing_history:
            print(f"  {entry['task']:<20} → {entry['routed_to']:<15} "
                  f"(CPU: {entry['cpu_at_routing']}%)")

if __name__ == "__main__":
    print("=== Task Router Demo ===\n")

    router = TaskRouter("coordinator")

    # Simulate node loads from gossip
    router.update_load("node-alpha", cpu=75, ram=60)
    router.update_load("node-beta",  cpu=23, ram=45)
    router.update_load("node-gamma", cpu=45, ram=50)
    router.update_load("node-delta", cpu=12, ram=30)

    router.display_network_status()

    # Route tasks
    print("\nRouting tasks...")
    router.route_task("matrix_multiply", {"size": 1000})
    router.route_task("ml_inference", {"model": "bert"})
    router.route_task("data_process", {"rows": 50000})
    router.route_task("image_resize", {"count": 100})

    router.display_routing_history()
    print("\n✅ Task routing complete!")
    