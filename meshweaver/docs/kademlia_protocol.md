# Kademlia DHT Protocol Research

## What is Kademlia?
Kademlia is a distributed hash table (DHT) protocol designed by Petar Maymounkov and David Mazières in 2002. It provides efficient peer-to-peer node lookup and data storage in decentralized networks.

## XOR Distance Metric

### Why XOR?
Kademlia uses XOR (exclusive OR) to calculate distance between node IDs:
####

### Properties:
- **Symmetric**: distance(A, B) = distance(B, A)
- **Identity**: distance(A, A) = 0
- **Triangle inequality**: distance(A, C) ≤ distance(A, B) + distance(B, C)
- **Unidirectional**: For any point and distance, exactly one point exists at that distance

### Example:
####



## Node IDs
- Each node has a 160-bit unique identifier
- Generated using SHA-1 hash of random data
- IDs uniformly distributed across the ID space

## K-Buckets (Routing Table)

### Structure:
- 160 buckets (one per bit position in 160-bit ID space)
- Bucket i contains nodes at distance range [2^i, 2^(i+1))
- Each bucket holds up to k nodes (typically k=20)

### Bucket Management:
- **Insertion**: Add new node if bucket has space
- **Full bucket**: PING least-recently-seen (LRS) node
  - If LRS responds: keep it, discard new node
  - If LRS fails: remove it, add new node
- **Why LRS?**: Older nodes are more stable and reliable

## Four Core Operations

### 1. PING
- Check if a node is alive
- Request: `PING(sender_id)`
- Response: `PONG(receiver_id)`

### 2. STORE
- Store key-value pair on a node
- Request: `STORE(key, value)`
- Keys hashed to 160-bit IDs
- Stored on k closest nodes to key

### 3. FIND_NODE
- Locate k closest nodes to target ID
- Request: `FIND_NODE(target_id)`
- Response: k closest nodes from routing table

### 4. FIND_VALUE
- Retrieve value for a key
- Request: `FIND_VALUE(key)`
- Response: value if stored, or k closest nodes

## Lookup Algorithm

### Process:
1. Start with α closest nodes from local routing table (α=3 typically)
2. Send FIND_NODE requests in parallel
3. Receive k closest nodes from each response
4. Add new nodes to shortlist
5. Query closer nodes iteratively
6. Stop when k closest nodes queried and no closer nodes found

### Complexity:
- **Time**: O(log n) hops
- **Messages**: O(log n) parallel requests
- **Space**: O(log n) routing table entries per node

## Key Properties

### Decentralization
- No central authority
- All nodes equal
- Self-organizing network

### Fault Tolerance
- Data replicated on k nodes
- Network continues if nodes fail
- Automatic recovery

### Scalability
- Logarithmic lookup time
- Minimal routing state per node
- Handles millions of nodes

### Load Balancing
- Keys uniformly distributed
- XOR metric ensures balanced tree
- No hot spots

## Real-World Usage
- **BitTorrent**: Mainline DHT for peer discovery
- **IPFS**: Content addressing and routing
- **Ethereum**: Node discovery protocol
- **Storj**: Distributed cloud storage

## References
- Original Paper: "Kademlia: A Peer-to-Peer Information System Based on the XOR Metric" (2002)
- Authors: Petar Maymounkov, David Mazières
- Link: https://pdos.csail.mit.edu/~petar/papers/maymounkov-kademlia-lncs.pdf



