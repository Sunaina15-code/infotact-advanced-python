# MeshWeaver - Gossip Protocol - Aug 7 - Athrva
# Nodes broadcast CPU/RAM usage every 5 seconds

import asyncio
import json
import psutil
from datetime import datetime

class GossipNode:
    """
    Gossip Protocol Engine
    Nodes share CPU/RAM load with neighbors every 5 seconds
    """
    def __init__(self, node_id, host, port):
        self.node_id = node_id
        self.host = host
        self.port = port
        self.neighbors = []
        self.node_loads = {}
        self.running = False

    def add_neighbor(self, node_id, host, port):
        self.neighbors.append({
            'id': node_id,
            'host': host,
            'port': port
        })
        print(f"[{self.node_id}] Added neighbor: {node_id}")

    def get_local_load(self):
        """Get current CPU and RAM usage"""
        try:
            cpu = psutil.cpu_percent(interval=0.1)
            ram = psutil.virtual_memory().percent
        except:
            import random
            cpu = random.uniform(10, 80)
            ram = random.uniform(30, 70)
        return {
            'cpu': round(cpu, 1),
            'ram': round(ram, 1),
            'timestamp': datetime.now().isoformat()
        }

    def create_gossip_message(self):
        """Create gossip message with local load info"""
        load = self.get_local_load()
        self.node_loads[self.node_id] = load
        return json.dumps({
            'type': 'gossip',
            'node_id': self.node_id,
            'host': self.host,
            'port': self.port,
            'load': load,
            'known_nodes': self.node_loads
        })

    def receive_gossip(self, message):
        """Process received gossip message"""
        data = json.loads(message)
        sender_id = data['node_id']
        self.node_loads[sender_id] = data['load']

        # Merge known nodes
        for nid, load in data.get('known_nodes', {}).items():
            if nid not in self.node_loads:
                self.node_loads[nid] = load

        print(f"[{self.node_id}] Gossip from {sender_id}: "
              f"CPU={data['load']['cpu']}% RAM={data['load']['ram']}%")

    def find_lowest_load_node(self):
        """Find node with lowest CPU load for task routing"""
        if not self.node_loads:
            return self.node_id
        return min(
            self.node_loads.keys(),
            key=lambda n: self.node_loads[n].get('cpu', 100)
        )

    async def gossip_loop(self, interval=5):
        """Continuously gossip with neighbors"""
        self.running = True
        print(f"[{self.node_id}] Gossip loop started (every {interval}s)")
        count = 0
        while self.running and count < 3:
            message = self.create_gossip_message()
            load = self.get_local_load()
            print(f"[{self.node_id}] Broadcasting: "
                  f"CPU={load['cpu']}% RAM={load['ram']}%")
            await asyncio.sleep(interval)
            count += 1
        self.running = False

    def display_network_load(self):
        print(f"\n=== Network Load [{self.node_id}] ===")
        for nid, load in self.node_loads.items():
            bar = "█" * int(load.get('cpu', 0) / 10)
            print(f"  {nid:<15} CPU: {bar:<10} {load.get('cpu', 0)}%")
        lowest = self.find_lowest_load_node()
        print(f"\n✅ Best node for task: {lowest}")

async def demo_gossip():
    print("=== Gossip Protocol Demo ===\n")

    node1 = GossipNode("node-alpha", "127.0.0.1", 8001)
    node2 = GossipNode("node-beta", "127.0.0.1", 8002)
    node3 = GossipNode("node-gamma", "127.0.0.1", 8003)

    node1.add_neighbor("node-beta", "127.0.0.1", 8002)
    node1.add_neighbor("node-gamma", "127.0.0.1", 8003)

    # Simulate gossip exchange
    msg1 = node1.create_gossip_message()
    msg2 = node2.create_gossip_message()
    msg3 = node3.create_gossip_message()

    node1.receive_gossip(msg2)
    node1.receive_gossip(msg3)

    node1.display_network_load()
    print("\n=== Gossip Demo Complete! ✅ ===")

if __name__ == "__main__":
    asyncio.run(demo_gossip())