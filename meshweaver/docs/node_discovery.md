# Node Discovery in Kademlia

## Bootstrap Process

### Initial Join:
1. New node generates random 160-bit ID
2. Connects to one or more bootstrap nodes (known addresses)
3. Inserts bootstrap node into routing table
4. Performs node lookup on its own ID
5. Populates routing table with discovered nodes

### Example Flow:
###


## Active Discovery (FIND_NODE)

### Process:
1. Node needs to find target ID (or closest nodes)
2. Selects α closest nodes from routing table (α=3)
3. Sends parallel FIND_NODE(target) requests
4. Each queried node responds with k closest nodes it knows
5. Adds new nodes to candidate list
6. Queries newly discovered closer nodes
7. Repeats until converged to k closest nodes

### Convergence:
- Each hop gets closer to target (XOR distance decreases)
- Typically converges in log(n) steps
- No infinite loops possible due to XOR properties

### Example:
###


## Passive Discovery

### Learning from Traffic:
- Node receives PING → Add sender to routing table
- Node receives FIND_NODE → Add sender to routing table
- Node receives STORE → Add sender to routing table
- Opportunistic learning from all incoming messages

### Benefits:
- No extra network traffic
- Continuous routing table updates
- Learns about active nodes naturally

## Peer Selection Strategy

### Least Recently Seen (LRS) Policy:
- Prefer long-lived nodes
- Recently contacted nodes moved to bucket tail
- Evict least recently seen nodes first
- Assumption: older nodes more stable

### Why This Works:
- Nodes online longer likely to stay online
- Reduces routing table churn
- Better network stability

## Network Join Flow

#####


## Network Leave/Failure

### Graceful Leave:
- No explicit leave protocol needed
- Node stops responding to requests
- Other nodes detect timeout and remove from routing table

### Failure Handling:
- Data replicated on k nodes
- If node fails, data still available on k-1 nodes
- Network automatically routes around failed nodes
- Self-healing through bucket refresh

### Timeout Detection:
- Nodes that don't respond to PING removed
- Failed lookups trigger re-routing
- Stale entries replaced during refresh

## Distance-Based Routing

### XOR Properties for Discovery:
- Always move closer to target with each hop
- Distance decreases monotonically
- No backtracking needed
- Guaranteed convergence

### Routing Efficiency:
- First hop: narrow search to half the ID space
- Second hop: narrow to 1/4 of ID space
- Each hop divides search space by 2
- Log(n) hops to reach any node

## Bucket Refresh Mechanism

### Purpose:
- Keep routing table fresh
- Discover new nodes in sparse buckets
- Remove stale entries

### Process:
1. For each bucket not queried in last hour:
   - Pick random ID in bucket's range
   - Perform FIND_NODE(random_id)
   - Update bucket with discovered nodes
2. Ensures all buckets stay populated
3. Maintains network connectivity

## Optimization Techniques

### Parallel Lookups:
- Query α nodes simultaneously (α=3 typically)
- Reduces lookup latency
- Faster convergence

### Shortlist Management:
- Track all discovered nodes during lookup
- Sort by distance to target
- Always query closest unqueried nodes

### Caching:
- Cache popular key-value pairs
- Reduces lookup overhead
- Improves response time

## MeshWeaver Implementation Mapping

### Current Code (node.py):
```python
# Distance calculation
def distance(self, other_id):
    return int(self.node_id, 16) ^ int(other_id, 16)

# Add discovered peer
def add_peer(self, peer_id, host, port):
    self.routing_table[peer_id] = {
        'host': host,
        'port': port,
        'last_seen': datetime.now(),
        'distance': self.distance(peer_id)
    }

# Find closest peers (active discovery)
def find_closest_peers(self, target_id, k=3):
    peers = sorted(
        self.routing_table.items(),
        key=lambda x: self.distance(x[0])
    )
    return peers[:k]
