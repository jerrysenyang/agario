from concurrent import futures
import grpc

import proto.game_pb2_grpc as game_rpc
import proto.replica_pb2_grpc as replica_rpc
from replication import ViewServer, ServerNode
from config import config


if __name__ == "__main__":
    port = str(config["PORT"])
    address = config["SERVER_HOST"]
    view_server = grpc.server(futures.ThreadPoolExecutor(max_workers=10))
    replica_rpc.add_ReplicationServicer_to_server(ViewServer(), view_server)
    print(f"View server started. Listening on {address}:{port}...")
    view_server.add_insecure_port(address + ":" + port)
    view_server.start()
    view_server.wait_for_termination()
