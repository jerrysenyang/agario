from concurrent import futures
import grpc

import proto.game_pb2 as game
import proto.game_pb2_grpc as rpc
from config import config
from model import Model


HOST = config["SERVER_HOST"]
PORT = config["PORT"]


class Server(rpc.GameServicer):
    def __init__(self, address=None, port=None):
        self.address = address
        self.port = port
        self.model = Model()

    def _game_state_error(self, alive):
        msg = game.GameState()
        player_msgs = []
        food_msgs = []
        msg.players.extend(player_msgs)
        msg.food.extend(food_msgs)
        msg.alive = alive
        msg.error = True
        
    def _game_state_to_proto(self, alive):
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
            food_msgs.append(_cell_to_proto_msg(food))
        msg.food.extend(food_msgs)
        msg.alive = alive
        msg.error = False

        return msg
    
    def RegisterUser(self, request, context):
        """TODO: Add checking for username, etc."""
        self.model.add_player(request.username)
        msg = self._game_state_to_proto(True)
        print(msg)
        return msg
    
    def GameUpdate(self, request, context):
        """
        Receive player actions and yield game state. Updates player position based on the mouse position.
        """
        # Update player velocity
        #self.model.update_velocity(request.username, request.mouse_pos.angle, request.mouse_pos.length)
        # TODO: Add code for emission action
        try: 
            self.model.move(request.username, request.x, request.y)
            self.model.detect_food_collisions(request.username)
            alive = self.model.detect_player_collisions(request.username)
            msg = self._game_state_to_proto(alive)
           # print(msg)
            return msg
        except:
            msg = self._game_state_error(alive)
            print(msg)
            return msg


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
    msg = game.Cell()
    msg.x_pos = int(cell.pos[0])
    msg.y_pos = int(cell.pos[1])
    msg.size = cell.radius
    msg.r = cell.color[0]
    msg.g = cell.color[1]
    msg.b = cell.color[2]
    return msg


####################
### Run
####################

if __name__ == "__main__":
    port = 11912  # a random port for the server to run on

    server = grpc.server(futures.ThreadPoolExecutor(max_workers=10))
    rpc.add_GameServicer_to_server(Server(), server)
    #server.add_insecure_port(HOST + ":"+ str(PORT))
    connectionString = HOST +":" + str(PORT)
    server.add_insecure_port(connectionString)
    print("Server listening on " + connectionString)
    server.start()
    server.wait_for_termination()