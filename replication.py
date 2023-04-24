from queue import Queue
import grpc
import threading
import time
import pickle

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

    def incr_max_size(self):
        """Incrementing by 2 so the queue can hold 2*node_count pings."""
        self.max_size += 2

class ViewServer(rpc.ReplicationServicer):
    def __init__(self):
        self.node_id_counter = 0
        self.view_id_counter = 0
        self.nodes = {}
        self.recent_pings = CustomQueue()
        self.nodes_updated = {}
        self.primary_id = None
        self.backup_id = None

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
            del self.nodes[self.backup_id]
            self.backup_id = live_nodes.pop()
            self._handle_view_update()
        
        # Check primary
        if self.primary_id not in live_nodes:
            del self.nodes[self.primary_id]
            self.primary_id = self.backup_id
            self.backup_id = live_nodes.pop()
            self._handle_view_update()
    
    def _handle_view_update(self):
        self.nodes_updated = {id: False for id in self.nodes.keys()}

    def RegisterNode(self, request, context):
        """
        Register the node.
        """
        id = self.node_id_counter
        node = Node(id, request.address, request.port)
        self.nodes[id] = node
        self.node_id_counter += 1
        self.nodes_updated[id] = True
        self.recent_pings.incr_max_size()

        return replica.NodeID(val=self.node_id_counter)

    def GetNodeAddress(self, request, context):
        node = self.nodes[request.val]
        return replica.NodeAddress(address=node.address, port=node.port)
    
    def Heartbeat(self, request, context):
        ping_id = request.node_id
        self.recent_pings.append(ping_id)
        self._check_active_connections()

        if not self.nodes_updated[ping_id]:
            msg = replica.ViewState(primary_id=self.primary_id, backup_id=self.backup_id)
            # Flag that this node has been updated with newest view state
            self.nodes_updated[ping_id] = True
            return msg
    

class ServerNode(Server, rpc.PrimaryBackupServicer):
    """TODO: Right now this does not enforce that only the primary processes requests."""
    def __init__(self, view_address, view_port, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Create a connection to the view server
        channel = grpc.insecure_channel(view_address + ':' + str(view_port))
        self.view_conn = rpc.ReplicationStub(channel)
        # Register node with view server
        msg = replica.NodeAddress(address=self.address, port=self.port)
        res = self.view_conn.RegisterNode(msg)
        self.node_id = res.val
        self.last_view_id = None
        self.is_primary = False
        self.is_backup = False
        # Create a thread for listening to view changes
        threading.Thread(target=self._listen_for_view_changes, daemon=True).start()

    def _listen_for_view_changes(self):
        """TODO: Handle exceptions."""
        # Send a ping every 0.5 seconds
        while True:
            res = self.view_conn.Heartbeat(self.node_id)
            # If the view has changed, update
            if res.view_id != self.last_view_id:
                if res.primary_id == self.node_id:
                    self.is_primary = True
                if res.backup_id == self.node_id:
                    self._assume_backup(res.primary_id)
            time.sleep(0.5)

    def _listen_for_state_updates(self):
        """TODO: Handle exceptions."""
        for msg in self.primary_conn.StateUpdateStream(replica.Empty()):
            self.model = pickle.loads(msg.state)

    def _assume_backup(self, primary_id):
        self.is_backup = True
        # Get primary address from view
        msg = replica.NodeID(val=primary_id)
        res = self.view_conn.GetNodeAddress(msg)
        # Connect to primary for state updates
        channel = grpc.insecure_channel(res.address + ":" + res.port)
        self.primary_conn = rpc.PrimaryBackupStub(channel)
        # Start a thread for listening to updates from primary
        # threading.Thread(target)

    def StateUpdateStream(self, request, context):
        while True:
            if self.is_primary:
                # Pickle the model
                state_pkl = pickle.dumps(self.model)
                yield replica.StateUpdate(state=state_pkl)
                time.sleep(0.1)