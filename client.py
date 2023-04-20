import contextlib
import math
with contextlib.redirect_stdout(None):
    import pygame
import grpc 
import os
import logging

import proto.game_pb2 as game
import proto.game_pb2_grpc as rpc
from model import Player

address = 'localhost'
port = 11912

logging.basicConfig(level=logging.INFO)

class Client():
    def __init__(self, window, username, height, width):
        self.window = window
        self.username = username
        self.height = height
        self.width = width
        self.food = None
        self.players = None

        # Set up channel
        channel = grpc.insecure_channel(address + ':' + str(port))
        self.conn = rpc.GameStub(channel)

    def redraw_window(self):
        self.window.fill((255, 255, 255))
        
        # TODO: Using this because I don't know what the pygame colors are
        tmp_color = (37,7,255)
        # Draw players
        for p in self.players:
            pygame.draw.circle(self.window, tmp_color, p.pos, p.radius)

        pygame.display.update()
        
    def mouse_pos_to_polar(self):
        """Convert mouse position to polar vector."""
        x, y = pygame.mouse.get_pos()
        # center offset 
        x -= self.width/2
        y = self.height/2 - y
        # get angle and length(speed) of vector
        angle = math.atan2(y, x)
        speed = math.sqrt(x**2 + y**2)
        # setting radius of speed change zone
        speed_bound = 0.8*min(self.width/2, self.height/2)
        # normalize speed
        speed = 1 if speed >= speed_bound else speed/speed_bound
        return angle, speed

    def handle_response(self, res):
        """Parse response and update players etc."""
        tmp = []
        for p in res.players:
            pos = (p.cell.x_pos, p.cell.y_pos)
            radius, color = p.cell.size, p.cell.color
            player = Player(username=p.username, pos=pos, radius=radius, color=color)
            tmp.append(player)

        self.players = tmp

    def run(self):

        # First create user
        msg = game.RegisterRequest(username=self.username)
        res = self.conn.RegisterUser(msg)
        self.handle_response(res)
        self.redraw_window()

        # Continue updating 
        while True:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    exit()
            
            angle, speed = self.mouse_pos_to_polar()
            mouse_pos = game.PolarVector(angle=angle, length=speed)
            msg = game.PlayerAction(action_type=game.PlayerActionType.MOVE, username=self.username)
            msg.mouse_pos.CopyFrom(mouse_pos)
            print(msg)
            res = self.conn.GameUpdate(msg)
            self.handle_response(res)
            print(res)
            self.redraw_window()


if __name__ == "__main__":
    # make window start in top left hand corner
    os.environ['SDL_VIDEO_WINDOW_POS'] = "%d,%d" % (0,30)

    W, H = 1600, 830

    # setup pygame window
    WIN = pygame.display.set_mode((W,H))
    pygame.display.set_caption("Blobs")
    
    c = Client(WIN, "John", W, H)
    c.run()