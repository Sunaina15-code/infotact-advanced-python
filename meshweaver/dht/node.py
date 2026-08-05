# MeshWeaver - DHT Node - Aug 4 - Sunaina
# Kademlia-inspired node discovery protocol

import hashlib
import asyncio
import json
from datetime import datetime

class KademliaNode:
    def __init__(self, node_id=None, host='127.0.0.1', port=8888):
        self.node_id = node_id or self._generate_id()
        self.host = host
        self.port = port
        self.routing_table = {}
        self.data_store = {}
        self.created_at = datetime.now().isoformat()

    def _generate_id(self):
        """Generate unique node ID"""
        import random
        return hashlib.sha1(
            str(random.randint(0, 999999)).encode()
        ).hexdigest()[:16]

    def distance(self, other_id):
        """XOR distance between two node IDs"""
        return int(self.node_id, 16) ^ int(other_id, 16)

    def add_peer(self, peer_id, host, port):
        """Add a peer to routing table"""
        self.routing_table[peer_id] = {
            'host': host,
            'port': port,
            'last_seen': datetime.now().isoformat(),
            'distance': self.distance(peer_id)
        }
        print(f"[{self.node_id[:8]}] Added peer: {peer_id[:8]}")

    def find_closest_peers(self, target_id, k=3):
        """Find k closest peers to target"""
        peers = list(self.routing_table.items())
        peers.sort(key=lambda x: self.distance(x[0]))
        return peers[:k]

    def store(self, key, value):
        """Store data in DHT"""
        hashed_key = hashlib.sha1(key.encode()).hexdigest()[:16]
        self.data_store[hashed_key] = {
            'value': value,
            'timestamp': datetime.now().isoformat()
        }
        print(f"[{self.node_id[:8]}] Stored: {key}")
        return hashed_key

    def retrieve(self, key):
        """Retrieve data from DHT"""
        hashed_key = hashlib.sha1(key.encode()).hexdigest()[:16]
        return self.data_store.get(hashed_key)

    def display_info(self):
        print(f"\n=== Node Info ===")
        print(f"ID:      {self.node_id}")
        print(f"Address: {self.host}:{self.port}")
        print(f"Peers:   {len(self.routing_table)}")
        print(f"Data:    {len(self.data_store)} items")

        if self.routing_table:
            print("\nRouting Table:")
            for peer_id, info in self.routing_table.items():
                print(f"  {peer_id[:8]} @ {info['host']}:{info['port']}")

if __name__ == "__main__":
    print("=== MeshWeaver DHT Demo ===\n")

    # Create nodes
    node1 = KademliaNode("node1abc12345678", "127.0.0.1", 8001)
    node2 = KademliaNode("node2def12345678", "127.0.0.1", 8002)
    node3 = KademliaNode("node3ghi12345678", "127.0.0.1", 8003)

    # Connect nodes
    node1.add_peer(node2.node_id, node2.host, node2.port)
    node1.add_peer(node3.node_id, node3.host, node3.port)
    node2.add_peer(node1.node_id, node1.host, node1.port)

    # Store and retrieve data
    node1.store("task_1", {"function": "add", "args": [10, 20]})
    node1.store("task_2", {"function": "multiply", "args": [5, 6]})

    # Display info
    node1.display_info()

    # Find closest peers
    closest = node1.find_closest_peers("node2def12345678")
    print(f"\nClosest peers to node2: {len(closest)}")

    print("\n=== DHT Demo Complete! ===")
# Aug 4 update
