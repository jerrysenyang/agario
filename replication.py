from collections import deque
import grpc
import threading
import time
import pickle
import logging 

import proto.replica_pb2 as replica
import proto.replica_pb2_grpc as rpc
from server import Server


# Logging config
logging.basicConfig(level=logging.DEBUG,
                    format='(%(threadName)-9s) %(message)s',)


class Node:
    def __init__(self, id, address, port):
        self.id = id
        self.address = address
        self.port = port


### NOTE: This functionality is implemented in deque already with the maxlen argument.
# class CustomQueue(deque):
#     """A FIFO queue that will pop an item when max size is reached."""
#     def __init__(self, max_size=0, *args):
#         super().__init__(args)
#         self.max_size = max_size

#     def append(self, item):
#         """Overwrite the put() function to pop the first item if max_size is reached."""
#         if len(self) == self.max_size:
#             self.popleft() # Pop first element
#         super().append(item)

#     def incr_max_size(self):
#         """Incrementing by 2 so the queue can hold 2*node_count pings."""
#         self.max_size += 2


class ViewServer(rpc.ReplicationServicer):
    def __init__(self):
        self.node_id_counter = 0
        self.view_id_counter = 0
        self.nodes = {}
        self.recent_pings = deque()
        self.nodes_updated = {}
        self.primary_id = None
        self.backup_id = None

    def _check_active_connections(self):
        """
        Check which nodes are alive and set a new primary or backup if either is down.

        TODO: Make more efficent and robust.
        TODO: Does this work in the case that the primary and backup
        fail at the same time?
        """
        live_nodes = set()
        for id in self.recent_pings:
            live_nodes.add(id)

        # Check if backup ID is in recent pings. If not, choose a new 
        # backup from the active nodes.
        if self.backup_id and self.backup_id not in live_nodes:
            del self.nodes[self.backup_id]
            self.backup_id = live_nodes.pop()
            logging.info(f"Backup node is down. Setting backup to {self.backup_id}")
            self.view_id_counter += 1

        # Check if primary ID is in recent pings. If not, set the current
        # backup to primary and choose a new backup from active nodes.
        if self.primary_id and self.primary_id not in live_nodes:
            del self.nodes[self.primary_id]
            self.primary_id = self.backup_id
            # Remove the new primary from live_nodes so it isn't considered for
            # the new backup
            live_nodes.remove(self.primary_id)
            self.backup_id = live_nodes.pop() if live_nodes else None
            logging.info(f"Primary node is down. Setting primary to {self.primary_id} and backup to {self.backup_id}")
            self.view_id_counter += 1

    def _current_view(self):
        """Return ViewState instance."""
        vs = replica.ViewState()
        vs.view_id = self.view_id_counter
        if self.primary_id:
            vs.primary_id = self.primary_id
        if self.backup_id:
            vs.backup_id = self.backup_id

        return vs
    
    def RegisterNode(self, request, context):
        """
        Register the node.
        """
        logging.info(f"Registering node with address {request.address} and port {request.port}")
        id = str(self.node_id_counter)
        node = Node(id, request.address, request.port)
        self.nodes[id] = node
        self.node_id_counter += 1
        self.nodes_updated[id] = True
        prev_max_length = self.recent_pings.maxlen
        self.recent_pings = deque(self.recent_pings, maxlen=prev_max_length+2)

        if not self.primary_id:
            self.primary_id = id
        elif not self.backup_id:
            self.backup_id = id

        return replica.NodeID(val=id)

    def GetNodeAddress(self, request, context):
        node = self.nodes[request.val]
        return replica.NodeAddress(address=node.address, port=node.port)
    
    def Heartbeat(self, request, context):
        ping_id = request.node_id
        self.recent_pings.append(ping_id)
        self._check_active_connections()
        
        msg = self._current_view()
        return msg
    

class ServerNode(Server):
    """TODO: Right now this does not enforce that only the primary processes requests."""
    def __init__(self, view_address, view_port, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Create a connection to the view server
        channel = grpc.insecure_channel(view_address + ':' + str(view_port))
        self.view_conn = rpc.ReplicationStub(channel)
        # Register node with view server
        msg = replica.NodeAddress(address=self.address, port=self.port)
        print(msg)
        res = self.view_conn.RegisterNode(msg)
        logging.info("Connected to view server.")
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
            msg = replica.PingMessage(node_id=self.node_id)
            res = self.view_conn.Heartbeat(msg)
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