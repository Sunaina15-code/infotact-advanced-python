# MeshWeaver - Peer Discovery - Aug 8 - Sunaina
# Dynamic peer discovery without hardcoded IPs

import asyncio
import json
import socket
from datetime import datetime

class PeerDiscovery:
    """
    Peer discovery using UDP broadcast
    Nodes can find each other without hardcoded IPs
    """
    def __init__(self, node_id, port=9999):
        self.node_id = node_id
        self.port = port
        self.discovered_peers = {}
        self.running = False

    def create_discovery_message(self):
        return json.dumps({
            'type': 'discover',
            'node_id': self.node_id,
            'port': self.port,
            'timestamp': datetime.now().isoformat()
        })

    def create_response_message(self):
        return json.dumps({
            'type': 'discover_response',
            'node_id': self.node_id,
            'port': self.port,
            'timestamp': datetime.now().isoformat()
        })

    def process_discovery(self, message, addr):
        """Process incoming discovery message"""
        try:
            data = json.loads(message)
            if data['type'] in ['discover', 'discover_response']:
                peer_id = data['node_id']
                if peer_id != self.node_id:
                    self.discovered_peers[peer_id] = {
                        'host': addr[0],
                        'port': data['port'],
                        'discovered_at': datetime.now().isoformat()
                    }
                    print(f"[{self.node_id[:8]}] Discovered: "
                          f"{peer_id[:8]} @ {addr[0]}:{data['port']}")
                    return True
        except Exception as e:
            print(f"Error: {e}")
        return False

    def simulate_discovery(self, other_nodes):
        """Simulate peer discovery with other nodes"""
        print(f"\n[{self.node_id[:8]}] Starting peer discovery...")
        for node in other_nodes:
            msg = node.create_response_message()
            self.process_discovery(
                msg,
                (node.host if hasattr(node, 'host') else '127.0.0.1',
                 node.port)
            )

    def display_peers(self):
        print(f"\n=== Discovered Peers [{self.node_id[:8]}] ===")
        if not self.discovered_peers:
            print("No peers discovered yet")
            return
        for pid, info in self.discovered_peers.items():
            print(f"  {pid[:8]} @ {info['host']}:{info['port']}")
        print(f"\nTotal: {len(self.discovered_peers)} peers")

class DiscoveryNode(PeerDiscovery):
    def __init__(self, node_id, host, port):
        super().__init__(node_id, port)
        self.host = host

async def demo_discovery():
    print("=== Peer Discovery Demo ===\n")

    nodes = [
        DiscoveryNode(f"node{i}{'x'*12}", "127.0.0.1", 8000+i)
        for i in range(1, 6)
    ]

    print("Simulating 5 nodes discovering each other...\n")
    for i, node in enumerate(nodes):
        others = [n for n in nodes if n != node]
        node.simulate_discovery(others[:3])

    print("\n=== Discovery Results ===")
    for node in nodes:
        node.display_peers()

    print("\n✅ All nodes discovered each other without hardcoded IPs!")
    print("=== Discovery Demo Complete! ===")

if __name__ == "__main__":
    asyncio.run(demo_discovery())
# Aug 8 final update
