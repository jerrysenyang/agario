from concurrent import futures
import grpc

import proto.game_pb2 as game
import proto.game_pb2_grpc as rpc

from model import Model


class Server(rpc.GameServicer):
    def __init__(self):
        self.model = Model()
        
    def _game_state_to_proto(self):
        """Convert the game state to game.GameState."""
        msg = game.GameState()
        player_msgs = []
        food_msgs = []

        # Add all players
        for player in self.model.players:
            player_msgs.append(_player_to_proto_msg(player))
        msg.players.extend(player_msgs)
        

        # Add all food cells
        for food in self.model.food:
            food.print_cell()
            food_msgs.append(_cell_to_proto_msg(food))
        msg.food.extend(food_msgs)

        return msg
    
    def RegisterUser(self, request, context):
        """TODO: Add checking for username, etc."""
        self.model.add_player(request.username)
        msg = self._game_state_to_proto()
        print(msg)
        return msg
    
    def GameUpdate(self, request, context):
        """
        Receive player actions and yield game state.
        
        NOTE: `action.mouse_pos` is the polar vector that starts from player center and normalized to game.GAME_WINDOW size. 
        """
        # Update player velocity
        #self.model.update_velocity(request.username, request.mouse_pos.angle, request.mouse_pos.length)
        # TODO: Add code for emission action
        self.model.move(request.username, request.x, request.y)
        msg = self._game_state_to_proto()
        print(msg)
        return msg

class ReplicatedServer(Server):
    """Extends Server with replication (communication between servers)."""
    pass


####################
### Protobuf Messages
####################

def _player_to_proto_msg(player):
    """
    Return a game.Player instance from Player instance.
    """
    msg = game.Player()
    msg.cell.CopyFrom(_cell_to_proto_msg(player))
    msg.username = player.username

    return msg


def _cell_to_proto_msg(cell):
    """
    Return a game.Cell instance from Cell instance.
    """

    print("In cell to proto!")
    msg = game.Cell()
    print("the cell is " + str(msg))
    msg.x_pos = int(cell.pos[0])
    msg.y_pos = int(cell.pos[1])
    msg.size = cell.radius
    msg.color = cell.color
    return msg


####################
### Run
####################

if __name__ == "__main__":
    port = 11912  # a random port for the server to run on

    server = grpc.server(futures.ThreadPoolExecutor(max_workers=10))
    rpc.add_GameServicer_to_server(Server(), server)
    server.add_insecure_port('[::]:' + str(port))
    server.start()
    server.wait_for_termination()