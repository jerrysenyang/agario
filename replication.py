from queue import Queue

import proto.replica_pb2 as replica
import proto.replica_pb2_grpc as rpc
from server import Server


class Node:
    def __init__(self, id, address, port):
        self.id = id
        self.address = address
        self.port = port


class CustomQueue(Queue):
    """A FIFO queue that will pop an item when max size is reached."""
    def __init__(self, max_size, *args):
        super().__init__(args)
        self.max_size = max_size

    def put(self, item):
        """Overwrite the put() function to pop the first item if max_size is reached."""
        if len(self) == self.max_size:
            self.get() # Pop first element
        self.put(item)


class ViewServer(rpc.ReplicationServicer):
    def __init__(self):
        self.node_id_counter = 0
        self.nodes = {}
        self.recent_pings = CustomQueue()
        self.primary_id = None
        self.backup_id = None
        self.view_has_changed = False

    def _check_active_connections(self):
        """
        TODO: Make more efficent and robust.
        TODO: Does this work in the case that the primary and backup
        fail at the same time?
        """
        live_nodes = set()
        for id in self.recent_pings:
            live_nodes.add(id)

        # Check backup ID is in recent pings
        if self.backup_id not in live_nodes:
            self.backup_id = live_nodes.pop()
            self.view_has_changed = True
        
        # Check primary
        if self.primary_id not in live_nodes:
            self.primary_id = self.backup_id
            self.backup_id = live_nodes.pop()
            self.view_has_changed = True

    def RegisterNode(self, request, context):
        """
        Register the node.
        """
        id = self.node_id_counter
        node = Node(id, request.address, request.port)
        self.nodes[id] = node
        self.node_id_counter += 1

        return replica.NodeID(val=self.node_id_counter)

    def GetNodeAddress(self, request, context):
        node = self.nodes[request.val]
        return replica.NodeAddress(address=node.address, port=node.port)
    
    def HeartbeatStream(self, request, context):
        ping_id = request.node_id
        self.recent_pings.append(ping_id)
        self._check_active_connections()

        if self.view_has_changed:
            msg = replica.ViewState(primary_id=self.primary_id, backup_id=self.backup_id)
            yield msg
    
    
class ServerReplica(Server):
    pass