import contextlib
import math
with contextlib.redirect_stdout(None):
    import pygame
import grpc 
import os
import logging
from time import sleep

import proto.game_pb2 as game
import proto.game_pb2_grpc as rpc
from model import Player
from model import Cell

address = 'localhost'
port = 11912
PLATFORM_WIDTH, PLATFORM_HEIGHT = (1500,800)
WHITE = (255,255,255)

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
        self.window.fill(WHITE)
        
        # Draw players
        for p in self.players:
            pygame.draw.circle(self.window, (255,0,0), p.pos, p.radius)
        for f in self.food:
            pygame.draw.circle(self.window, (0,0,255), f.pos, f.radius)

        pygame.display.update()
        
    # def mouse_pos_to_polar(self):
    #     """Convert mouse position to polar vector."""
    #     x, y = pygame.mouse.get_pos()
    #     # center offset 
    #     x -= self.width/2
    #     y = self.height/2 - y
    #     # get angle and length(speed) of vector
    #     angle = math.atan2(y, x)
    #     speed = math.sqrt(x**2 + y**2)
    #     # setting radius of speed change zone
    #     speed_bound = 0.8*min(self.width/2, self.height/2)
    #     # normalize speed
    #     speed = 1 if speed >= speed_bound else speed/speed_bound
    #     return angle, speed

    def get_mouse_position(self):
        return pygame.mouse.get_pos()

    def handle_response(self, res):
        """Parse response and update players etc."""
        tmp = []
        for p in res.players:
            pos = (p.cell.x_pos, p.cell.y_pos)
            radius, color = p.cell.size, p.cell.color
            player = Player(username=p.username, pos=pos, radius=radius, color=color)
            tmp.append(player)
        self.players = tmp
        print(self.players)

        food = []
        for f in res.food:
            pos = (f.x_pos, f.y_pos)
            radius, color = f.size, f.color
            fd = Cell(pos=pos, radius=radius, color=color, speed = 0, direction = 0)
            food.append(fd)
        self.food = food
        print(self.food)

    def run(self):

        # First create user
        msg = game.RegisterRequest(username=self.username)
        res = self.conn.RegisterUser(msg)
        print(res)
        self.handle_response(res)
        self.redraw_window()

        # # Continue updating 
        # while True:
        #     for event in pygame.event.get():
        #         if event.type == pygame.QUIT:
        #             exit()
            
        #     angle, speed = self.mouse_pos_to_polar()
        #     mouse_pos = game.PolarVector(angle=angle, length=speed)
        #     msg = game.PlayerAction(action_type=game.PlayerActionType.MOVE, username=self.username)
        #     msg.mouse_pos.CopyFrom(mouse_pos)
        #     print(msg)
        #     res = self.conn.GameUpdate(msg)
        #     self.handle_response(res)
        #     print(res)
        #     self.redraw_window()

        while True:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    exit()
            
            x, y = self.get_mouse_position()
            msg = game.PlayerAction(x= x, y= y, action_type=game.PlayerActionType.MOVE, username=self.username)
            print(msg)
            res = self.conn.GameUpdate(msg)
            self.handle_response(res)
            print(res)
            self.redraw_window()



if __name__ == "__main__":
    # make window start in top left hand corner
    os.environ['SDL_VIDEO_WINDOW_POS'] = "%d,%d" % (0,30)

    # setup pygame window
    WIN = pygame.display.set_mode((PLATFORM_WIDTH, PLATFORM_HEIGHT))
    pygame.display.set_caption("Agario")
    c = Client(WIN, "John", PLATFORM_WIDTH, PLATFORM_HEIGHT)
    c.run()