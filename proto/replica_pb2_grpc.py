# Generated by the gRPC Python protocol compiler plugin. DO NOT EDIT!
"""Client and server classes corresponding to protobuf-defined services."""
import grpc

from . import replica_pb2 as replica__pb2


class ReplicationStub(object):
    """Missing associated documentation comment in .proto file."""

    def __init__(self, channel):
        """Constructor.

        Args:
            channel: A grpc.Channel.
        """
        self.RegisterNode = channel.unary_unary(
                '/replica.Replication/RegisterNode',
                request_serializer=replica__pb2.NodeAddress.SerializeToString,
                response_deserializer=replica__pb2.NodeID.FromString,
                )
        self.GetNodeAddress = channel.unary_unary(
                '/replica.Replication/GetNodeAddress',
                request_serializer=replica__pb2.NodeID.SerializeToString,
                response_deserializer=replica__pb2.NodeAddress.FromString,
                )
        self.Heartbeat = channel.unary_unary(
                '/replica.Replication/Heartbeat',
                request_serializer=replica__pb2.PingMessage.SerializeToString,
                response_deserializer=replica__pb2.ViewState.FromString,
                )


class ReplicationServicer(object):
    """Missing associated documentation comment in .proto file."""

    def RegisterNode(self, request, context):
        """Missing associated documentation comment in .proto file."""
        context.set_code(grpc.StatusCode.UNIMPLEMENTED)
        context.set_details('Method not implemented!')
        raise NotImplementedError('Method not implemented!')

    def GetNodeAddress(self, request, context):
        """Missing associated documentation comment in .proto file."""
        context.set_code(grpc.StatusCode.UNIMPLEMENTED)
        context.set_details('Method not implemented!')
        raise NotImplementedError('Method not implemented!')

    def Heartbeat(self, request, context):
        """Missing associated documentation comment in .proto file."""
        context.set_code(grpc.StatusCode.UNIMPLEMENTED)
        context.set_details('Method not implemented!')
        raise NotImplementedError('Method not implemented!')


def add_ReplicationServicer_to_server(servicer, server):
    rpc_method_handlers = {
            'RegisterNode': grpc.unary_unary_rpc_method_handler(
                    servicer.RegisterNode,
                    request_deserializer=replica__pb2.NodeAddress.FromString,
                    response_serializer=replica__pb2.NodeID.SerializeToString,
            ),
            'GetNodeAddress': grpc.unary_unary_rpc_method_handler(
                    servicer.GetNodeAddress,
                    request_deserializer=replica__pb2.NodeID.FromString,
                    response_serializer=replica__pb2.NodeAddress.SerializeToString,
            ),
            'Heartbeat': grpc.unary_unary_rpc_method_handler(
                    servicer.Heartbeat,
                    request_deserializer=replica__pb2.PingMessage.FromString,
                    response_serializer=replica__pb2.ViewState.SerializeToString,
            ),
    }
    generic_handler = grpc.method_handlers_generic_handler(
            'replica.Replication', rpc_method_handlers)
    server.add_generic_rpc_handlers((generic_handler,))


 # This class is part of an EXPERIMENTAL API.
class Replication(object):
    """Missing associated documentation comment in .proto file."""

    @staticmethod
    def RegisterNode(request,
            target,
            options=(),
            channel_credentials=None,
            call_credentials=None,
            insecure=False,
            compression=None,
            wait_for_ready=None,
            timeout=None,
            metadata=None):
        return grpc.experimental.unary_unary(request, target, '/replica.Replication/RegisterNode',
            replica__pb2.NodeAddress.SerializeToString,
            replica__pb2.NodeID.FromString,
            options, channel_credentials,
            insecure, call_credentials, compression, wait_for_ready, timeout, metadata)

    @staticmethod
    def GetNodeAddress(request,
            target,
            options=(),
            channel_credentials=None,
            call_credentials=None,
            insecure=False,
            compression=None,
            wait_for_ready=None,
            timeout=None,
            metadata=None):
        return grpc.experimental.unary_unary(request, target, '/replica.Replication/GetNodeAddress',
            replica__pb2.NodeID.SerializeToString,
            replica__pb2.NodeAddress.FromString,
            options, channel_credentials,
            insecure, call_credentials, compression, wait_for_ready, timeout, metadata)

    @staticmethod
    def Heartbeat(request,
            target,
            options=(),
            channel_credentials=None,
            call_credentials=None,
            insecure=False,
            compression=None,
            wait_for_ready=None,
            timeout=None,
            metadata=None):
        return grpc.experimental.unary_unary(request, target, '/replica.Replication/Heartbeat',
            replica__pb2.PingMessage.SerializeToString,
            replica__pb2.ViewState.FromString,
            options, channel_credentials,
            insecure, call_credentials, compression, wait_for_ready, timeout, metadata)


class PrimaryBackupStub(object):
    """Missing associated documentation comment in .proto file."""

    def __init__(self, channel):
        """Constructor.

        Args:
            channel: A grpc.Channel.
        """
        self.StateUpdateStream = channel.unary_stream(
                '/replica.PrimaryBackup/StateUpdateStream',
                request_serializer=replica__pb2.Empty.SerializeToString,
                response_deserializer=replica__pb2.StateUpdate.FromString,
                )


class PrimaryBackupServicer(object):
    """Missing associated documentation comment in .proto file."""

    def StateUpdateStream(self, request, context):
        """Missing associated documentation comment in .proto file."""
        context.set_code(grpc.StatusCode.UNIMPLEMENTED)
        context.set_details('Method not implemented!')
        raise NotImplementedError('Method not implemented!')


def add_PrimaryBackupServicer_to_server(servicer, server):
    rpc_method_handlers = {
            'StateUpdateStream': grpc.unary_stream_rpc_method_handler(
                    servicer.StateUpdateStream,
                    request_deserializer=replica__pb2.Empty.FromString,
                    response_serializer=replica__pb2.StateUpdate.SerializeToString,
            ),
    }
    generic_handler = grpc.method_handlers_generic_handler(
            'replica.PrimaryBackup', rpc_method_handlers)
    server.add_generic_rpc_handlers((generic_handler,))


 # This class is part of an EXPERIMENTAL API.
class PrimaryBackup(object):
    """Missing associated documentation comment in .proto file."""

    @staticmethod
    def StateUpdateStream(request,
            target,
            options=(),
            channel_credentials=None,
            call_credentials=None,
            insecure=False,
            compression=None,
            wait_for_ready=None,
            timeout=None,
            metadata=None):
        return grpc.experimental.unary_stream(request, target, '/replica.PrimaryBackup/StateUpdateStream',
            replica__pb2.Empty.SerializeToString,
            replica__pb2.StateUpdate.FromString,
            options, channel_credentials,
            insecure, call_credentials, compression, wait_for_ready, timeout, metadata)
