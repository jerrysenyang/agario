from concurrent import futures
import grpc
import sys

import proto.game_pb2_grpc as game_rpc
import proto.replica_pb2_grpc as replica_rpc
from replication import ServerNode
from config import config


if __name__ == "__main__":
    view_port = str(config["PORT"])
    address = config["SERVER_HOST"]
    port = str(int(view_port) + int(sys.argv[1]))
    server = grpc.server(futures.ThreadPoolExecutor(max_workers=10))
    instance = ServerNode(address=address, port=port, view_address=address, view_port=view_port)
    replica_rpc.add_PrimaryBackupServicer_to_server(instance, server)
    game_rpc.add_GameServicer_to_server(instance, server)
    print("Game server started. Listening...")
    server.add_insecure_port(address + ":" + port)
    server.start()
    server.wait_for_termination()
