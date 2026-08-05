# MeshWeaver - UDP Client - Aug 2 - Sunaina
# Client for connecting to mesh network

import asyncio
import json
from datetime import datetime

class MeshClient:
    def __init__(self, client_id):
        self.client_id = client_id
        self.transport = None
        self.protocol = None

    async def connect(self, server_host, server_port):
        loop = asyncio.get_event_loop()
        
        class ClientProtocol(asyncio.DatagramProtocol):
            def __init__(self, client):
                self.client = client

            def connection_made(self, transport):
                self.client.transport = transport
                print(f"[{self.client.client_id}] Connected!")

            def datagram_received(self, data, addr):
                message = json.loads(data.decode())
                print(f"[{self.client.client_id}] Received: {message}")

        self.transport, self.protocol = await loop.create_datagram_endpoint(
            lambda: ClientProtocol(self),
            remote_addr=(server_host, server_port)
        )

    def send_message(self, msg_type, data=None):
        message = json.dumps({
            'type': msg_type,
            'client_id': self.client_id,
            'data': data or {},
            'timestamp': datetime.now().isoformat()
        }).encode()
        self.transport.sendto(message)
        print(f"[{self.client_id}] Sent: {msg_type}")

    def disconnect(self):
        if self.transport:
            self.transport.close()

async def demo_client():
    print("=== MeshWeaver Client Demo ===")
    client = MeshClient("Client-1")
    await client.connect("127.0.0.1", 8888)
    client.send_message("ping")
    await asyncio.sleep(2)
    client.disconnect()

if __name__ == "__main__":
    asyncio.run(demo_client())