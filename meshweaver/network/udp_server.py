# MeshWeaver - UDP Server - Aug 1 - Sunaina
# Base asyncio UDP server for peer communication

import asyncio
import json
import socket
from datetime import datetime

class MeshNode(asyncio.DatagramProtocol):
    def __init__(self, node_id, host='127.0.0.1', port=8888):
        self.node_id = node_id
        self.host = host
        self.port = port
        self.peers = {}
        self.transport = None
        self.message_log = []

    def connection_made(self, transport):
        self.transport = transport
        print(f"[{self.node_id}] Node started on {self.host}:{self.port}")

    def datagram_received(self, data, addr):
        try:
            message = json.loads(data.decode())
            self.message_log.append({
                'from': addr,
                'message': message,
                'time': datetime.now().isoformat()
            })
            self._handle_message(message, addr)
        except Exception as e:
            print(f"[{self.node_id}] Error: {e}")

    def _handle_message(self, message, addr):
        msg_type = message.get('type')

        if msg_type == 'ping':
            print(f"[{self.node_id}] Ping from {addr}")
            response = json.dumps({
                'type': 'pong',
                'node_id': self.node_id,
                'timestamp': datetime.now().isoformat()
            }).encode()
            self.transport.sendto(response, addr)

        elif msg_type == 'pong':
            print(f"[{self.node_id}] Pong received from {addr}")
            self.peers[str(addr)] = {
                'node_id': message.get('node_id'),
                'last_seen': datetime.now().isoformat()
            }

        elif msg_type == 'join':
            print(f"[{self.node_id}] New peer joined: {addr}")
            self.peers[str(addr)] = {
                'node_id': message.get('node_id'),
                'last_seen': datetime.now().isoformat()
            }

    def send_ping(self, target_host, target_port):
        message = json.dumps({
            'type': 'ping',
            'node_id': self.node_id,
            'timestamp': datetime.now().isoformat()
        }).encode()
        self.transport.sendto(message, (target_host, target_port))
        print(f"[{self.node_id}] Ping sent to {target_host}:{target_port}")

    def display_peers(self):
        print(f"\n[{self.node_id}] Known peers: {len(self.peers)}")
        for addr, info in self.peers.items():
            print(f"  {addr} → {info['node_id']}")

async def run_node(node_id, host, port):
    loop = asyncio.get_event_loop()
    transport, protocol = await loop.create_datagram_endpoint(
        lambda: MeshNode(node_id, host, port),
        local_addr=(host, port)
    )
    return transport, protocol

if __name__ == "__main__":
    async def main():
        print("=== MeshWeaver UDP Server ===")
        transport, node = await run_node("Node-1", "127.0.0.1", 8888)
        print(f"Node running... Press Ctrl+C to stop")
        try:
            await asyncio.sleep(30)
        finally:
            transport.close()

    asyncio.run(main())
# Aug 1 update
