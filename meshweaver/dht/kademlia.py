# MeshWeaver - Kademlia DHT - Aug 7 - Sunaina
# Lightweight Kademlia node discovery protocol

import hashlib
import asyncio
import json
from datetime import datetime

class KBucket:
    """K-bucket for storing peers at a specific distance"""
    def __init__(self, k=20):
        self.k = k
        self.peers = []

    def add(self, peer):
        if peer not in self.peers:
            if len(self.peers) < self.k:
                self.peers.append(peer)
                return True
        return False

    def remove(self, peer):
        if peer in self.peers:
            self.peers.remove(peer)

class KademliaNetwork:
    """
    Lightweight Kademlia DHT implementation
    Allows nodes to dynamically join mesh and find peers
    without hardcoded IPs
    """
    def __init__(self, node_id, host, port):
        self.node_id = node_id
        self.host = host
        self.port = port
        self.buckets = [KBucket() for _ in range(160)]
        self.data = {}
        self.bootstrap_nodes = []

    def _distance(self, id1, id2):
        """XOR metric for node distance"""
        return int(id1, 16) ^ int(id2, 16)

    def _bucket_index(self, other_id):
        """Find which bucket a peer belongs to"""
        dist = self._distance(self.node_id, other_id)
        if dist == 0:
            return 0
        return dist.bit_length() - 1

    def add_peer(self, peer_id, host, port):
        """Add peer to appropriate k-bucket"""
        idx = self._bucket_index(peer_id)
        peer = {'id': peer_id, 'host': host, 'port': port,
                'last_seen': datetime.now().isoformat()}
        added = self.buckets[idx].add(peer)
        if added:
            print(f"[{self.node_id[:8]}] Peer added to bucket {idx}: {peer_id[:8]}")
        return added

    def find_node(self, target_id, k=3):
        """Find k closest nodes to target"""
        all_peers = []
        for bucket in self.buckets:
            all_peers.extend(bucket.peers)

        all_peers.sort(
            key=lambda p: self._distance(p['id'], target_id)
        )
        return all_peers[:k]

    def store(self, key, value):
        """Store key-value in DHT"""
        hkey = hashlib.sha1(key.encode()).hexdigest()
        self.data[hkey] = {
            'value': value,
            'stored_at': datetime.now().isoformat()
        }
        print(f"[{self.node_id[:8]}] Stored key: {key[:20]}")
        return hkey

    def get(self, key):
        """Retrieve value from DHT"""
        hkey = hashlib.sha1(key.encode()).hexdigest()
        result = self.data.get(hkey)
        if result:
            print(f"[{self.node_id[:8]}] Found: {key[:20]}")
        return result

    async def join_network(self, bootstrap_host, bootstrap_port):
        """Join existing network via bootstrap node"""
        print(f"[{self.node_id[:8]}] Joining network via {bootstrap_host}:{bootstrap_port}")
        self.bootstrap_nodes.append({
            'host': bootstrap_host,
            'port': bootstrap_port
        })
        await asyncio.sleep(0.1)
        print(f"[{self.node_id[:8]}] Successfully joined network!")

    def display_routing_table(self):
        print(f"\n=== Routing Table [{self.node_id[:8]}] ===")
        total = 0
        for i, bucket in enumerate(self.buckets):
            if bucket.peers:
                print(f"Bucket {i:3}: {len(bucket.peers)} peers")
                for p in bucket.peers:
                    print(f"  → {p['id'][:8]} @ {p['host']}:{p['port']}")
                total += len(bucket.peers)
        print(f"Total peers: {total}")

async def demo_kademlia():
    print("=== Kademlia DHT Demo ===\n")

    # Create 3 nodes
    node1 = KademliaNetwork("aaaa1111bbbb2222", "127.0.0.1", 8001)
    node2 = KademliaNetwork("cccc3333dddd4444", "127.0.0.1", 8002)
    node3 = KademliaNetwork("eeee5555ffff6666", "127.0.0.1", 8003)

    # Node 2 and 3 join via node 1
    await node2.join_network("127.0.0.1", 8001)
    await node3.join_network("127.0.0.1", 8001)

    # Add peers to routing tables
    node1.add_peer(node2.node_id, node2.host, node2.port)
    node1.add_peer(node3.node_id, node3.host, node3.port)
    node2.add_peer(node1.node_id, node1.host, node1.port)
    node3.add_peer(node1.node_id, node1.host, node1.port)

    # Store and retrieve
    node1.store("task_cpu_heavy", {"func": "matrix_multiply", "size": 1000})
    result = node1.get("task_cpu_heavy")
    print(f"\nRetrieved: {result['value']}")

    # Find closest nodes
    closest = node1.find_node(node2.node_id)
    print(f"\nClosest to node2: {len(closest)} nodes found")

    node1.display_routing_table()
    print("\n=== Kademlia Demo Complete! ✅ ===")

if __name__ == "__main__":
    asyncio.run(demo_kademlia())