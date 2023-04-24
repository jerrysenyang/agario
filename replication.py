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
        self.view_id = 0
        self.nodes = {}
        self.recent_pings = deque()
        self.primary_id = None
        self.backup_id = None

    def _check_active_connections(self):
        """
        Check which nodes are alive and set a new primary or backup if either is down.
        `self.recent_pings` the last (2*number of live nodes) pings, so we can use this
        to determine which nodes have not pinged in a while.

        TODO: Make more efficent and robust.
        TODO: Does this work in the case that the primary and backup
        fail at the same time?
        """
        live_nodes = set()
        for id in self.recent_pings:
            live_nodes.add(id)

        # Remove any nodes that have not pinged recently. If the primary or
        # backup has not pinged, set those fields to None as well.
        for id in list(self.nodes.keys()):
            if id not in live_nodes:
                del self.nodes[id]
                if id == self.backup_id:
                    self.backup_id = None
                if id == self.primary_id:
                    self.primary_id = None

        # Change the view if necessary
        self._update_view(live_nodes)
        # Reset the size of self.recent_pings
        self._update_recent_pings_maxlen()

    def _update_view(self, live_nodes):
        """Update the view."""
        # If both primary and backup are alive, view stays the same
        if self.primary_id and self.backup_id:
            return
        # If the primary is down, set the backup to primary and choose a new backup
        elif self.backup_id:
            self.primary_id = self.backup_id
            live_nodes.remove(self.backup_id)
            self.backup_id = live_nodes.pop() if live_nodes else None
        # If the backup is down, set a new backup
        elif self.primary_id:
            self.backup_id = live_nodes.pop() if live_nodes else None
        # If both are down, try to select two nodes from live_nodes
        else:
            self.primary_id = live_nodes.pop() if live_nodes else None
            self.backup_id = live_nodes.pop() if live_nodes else None
        
        # Increment the view ID since it has changed
        self.view_id += 1

    def _current_view(self):
        """Return ViewState instance."""
        vs = replica.ViewState()
        vs.view_id = self.view_id
        if self.primary_id:
            vs.primary_id = self.primary_id
        if self.backup_id:
            vs.backup_id = self.backup_id

        return vs
    
    def _update_recent_pings_maxlen(self):
        new_len = len(self.nodes.keys()) * 2
        # We have to initialize a new `deque()` instance since maxlen cannot be overwritten
        self.recent_pings = deque(self.recent_pings, maxlen=new_len)

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
        self._update_recent_pings_maxlen()

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