# Generated by the gRPC Python protocol compiler plugin. DO NOT EDIT!
"""Client and server classes corresponding to protobuf-defined services."""
import grpc

import game_pb2 as game__pb2


class GameStub(object):
    """**
    Service

    TODO: Might want to have RegisterUser return RegisterResponse, and then 
    have another unary call that loads in the initial game state.
    *
    """

    def __init__(self, channel):
        """Constructor.

        Args:
            channel: A grpc.Channel.
        """
        self.GameUpdate = channel.unary_unary(
                '/game.Game/GameUpdate',
                request_serializer=game__pb2.PlayerAction.SerializeToString,
                response_deserializer=game__pb2.GameState.FromString,
                )
        self.RegisterUser = channel.unary_unary(
                '/game.Game/RegisterUser',
                request_serializer=game__pb2.RegisterRequest.SerializeToString,
                response_deserializer=game__pb2.GameState.FromString,
                )


class GameServicer(object):
    """**
    Service

    TODO: Might want to have RegisterUser return RegisterResponse, and then 
    have another unary call that loads in the initial game state.
    *
    """

    def GameUpdate(self, request, context):
        """Missing associated documentation comment in .proto file."""
        context.set_code(grpc.StatusCode.UNIMPLEMENTED)
        context.set_details('Method not implemented!')
        raise NotImplementedError('Method not implemented!')

    def RegisterUser(self, request, context):
        """Missing associated documentation comment in .proto file."""
        context.set_code(grpc.StatusCode.UNIMPLEMENTED)
        context.set_details('Method not implemented!')
        raise NotImplementedError('Method not implemented!')


def add_GameServicer_to_server(servicer, server):
    rpc_method_handlers = {
            'GameUpdate': grpc.unary_unary_rpc_method_handler(
                    servicer.GameUpdate,
                    request_deserializer=game__pb2.PlayerAction.FromString,
                    response_serializer=game__pb2.GameState.SerializeToString,
            ),
            'RegisterUser': grpc.unary_unary_rpc_method_handler(
                    servicer.RegisterUser,
                    request_deserializer=game__pb2.RegisterRequest.FromString,
                    response_serializer=game__pb2.GameState.SerializeToString,
            ),
    }
    generic_handler = grpc.method_handlers_generic_handler(
            'game.Game', rpc_method_handlers)
    server.add_generic_rpc_handlers((generic_handler,))


 # This class is part of an EXPERIMENTAL API.
class Game(object):
    """**
    Service

    TODO: Might want to have RegisterUser return RegisterResponse, and then 
    have another unary call that loads in the initial game state.
    *
    """

    @staticmethod
    def GameUpdate(request,
            target,
            options=(),
            channel_credentials=None,
            call_credentials=None,
            insecure=False,
            compression=None,
            wait_for_ready=None,
            timeout=None,
            metadata=None):
        return grpc.experimental.unary_unary(request, target, '/game.Game/GameUpdate',
            game__pb2.PlayerAction.SerializeToString,
            game__pb2.GameState.FromString,
            options, channel_credentials,
            insecure, call_credentials, compression, wait_for_ready, timeout, metadata)

    @staticmethod
    def RegisterUser(request,
            target,
            options=(),
            channel_credentials=None,
            call_credentials=None,
            insecure=False,
            compression=None,
            wait_for_ready=None,
            timeout=None,
            metadata=None):
        return grpc.experimental.unary_unary(request, target, '/game.Game/RegisterUser',
            game__pb2.RegisterRequest.SerializeToString,
            game__pb2.GameState.FromString,
            options, channel_credentials,
            insecure, call_credentials, compression, wait_for_ready, timeout, metadata)
