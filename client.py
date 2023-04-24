"""
TODO: Set up client to get current primary from view server.
TODO: If the current connection fails, ask view server for new primary.
"""

import contextlib
import math
with contextlib.redirect_stdout(None):
    import pygame
import grpc 
import sys
import os
import logging
from time import sleep

import proto.game_pb2 as game
import proto.game_pb2_grpc as rpc
import proto.replica_pb2_grpc as replica_rpc
import proto.replica_pb2 as replica
from model import Player
from model import Cell
from config import config

PORT = config["PORT"]
ADDRESS = config["SERVER_HOST"]
local_address = "localhost"
port = 11912
#GAME_WIDTH, GAME_HEIGHT = (3000,1600)
VIEW_WIDTH, VIEW_HEIGHT = (1500, 800)
WHITE = (255,255,255)
BLACK= (0,0,0)
GREEN = (0, 255, 0)
BLUE = (0, 0, 255)
FPS = 60

logging.basicConfig(level=logging.INFO)

class Client():
    def __init__(self, window, username, width, height):
        self.window = window
        self.username = username
        self.height = height
        self.width = width
        self.food = None
        self.players = None

        # Set up connection to view server
        channel = grpc.insecure_channel("localhost" + ':' + str(PORT))
        self.view_server = replica_rpc.ReplicationStub(channel)
        res = self.view_server.GetPrimaryAddress(replica.Empty())
        # Set up connection to primary
        # TODO: Handle exceptions
        channel = grpc.insecure_channel(res.address + ":" + res.port)
        self.conn = rpc.GameStub(channel)
        logging.info(f"Connected to {res.address}:{res.port}")

    def redraw_window(self):
        self.window.fill(WHITE)
        
        # Draw players
        for p in self.players:
            pygame.draw.circle(self.window, p.color, p.pos, p.radius)
            self.write_name(p.username,p.pos, p.radius)
        for f in self.food:
            pygame.draw.circle(self.window, f.color, f.pos, f.radius)

        self.write_username()
        pygame.display.update()
    
    def write_game_over(self):
        self.window.fill(WHITE)
        
        # Draw players
        for p in self.players:
            pygame.draw.circle(self.window, p.color, p.pos, p.radius)
        for f in self.food:
            pygame.draw.circle(self.window, f.color, f.pos, f.radius)
        
        pygame.font.init()
        font = pygame.font.Font(None, 65)
        text1 = font.render('GAME OVER!', True, GREEN, BLUE)
        text2 = font.render('YOU WERE EATEN...', True, GREEN, BLUE)
        textRect1 = text1.get_rect()
        textRect1.center = (VIEW_WIDTH// 2, VIEW_HEIGHT // 2 + 100)
        textRect2 = text2.get_rect()
        textRect2.center = (VIEW_WIDTH// 2, VIEW_HEIGHT // 2 - 100)
        
        self.window.blit(text1, textRect1)
        self.window.blit(text2, textRect2)

        pygame.display.update()

    
    def write_username(self):
        pygame.font.init()
        font = pygame.font.Font(None, 30)
        text1 = font.render("Player: "+ self.username, True, BLACK, WHITE)
        textRect1 = text1.get_rect()
        textRect1.topleft = (20, 20)
        self.window.blit(text1, textRect1)

    def write_name(self, username, pos, radius):
        pygame.font.init()
        font = pygame.font.Font(None, 25)
        text1 = font.render(username, True, BLACK, WHITE)
        textRect1 = text1.get_rect()
        textRect1.bottomleft = (pos[0] + radius, pos[1] + radius)
        self.window.blit(text1, textRect1)

    def get_mouse_position(self):
        return pygame.mouse.get_pos()
    

    def handle_response(self, res):
        """Parse response and update players etc."""
        if not res.error:
            tmp = []
            for p in res.players:
                pos = (p.cell.x_pos, p.cell.y_pos)
                radius, color = p.cell.size, (p.cell.r, p.cell.g, p.cell.b)
                player = Player(username=p.username, pos=pos, radius=radius, color=color)
                tmp.append(player)
            self.players = tmp
            print(self.players)

            food = []
            for f in res.food:
                pos = (f.x_pos, f.y_pos)
                radius, color = f.size, (f.r, f.g, f.b)
                fd = Cell(pos=pos, radius=radius, color=color, speed = 0, direction = 0)
                food.append(fd)
            self.food = food
            print(self.food)

    def run(self):

        clock = pygame.time.Clock()

        # First create user
        msg = game.RegisterRequest(username=self.username)
        res = self.conn.RegisterUser(msg)
        print(res)
        self.handle_response(res)
        self.redraw_window()
        alive = True

        while alive:
            clock.tick(FPS)
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    exit()
            
            x, y = self.get_mouse_position()
            msg = game.PlayerAction(x= x, y= y, action_type=game.PlayerActionType.MOVE, username=self.username)
            print(msg)
            res = self.conn.GameUpdate(msg)
            
            ## if the player has died, show GAME OVER and exit
            if res.alive == False:
                print("YOU DIED!")
                self.write_game_over()
                alive = False
                sleep(3)

            else:
                self.handle_response(res)
                print(res)
                self.redraw_window()



if __name__ == "__main__":
    # make window start in top left hand corner
    os.environ['SDL_VIDEO_WINDOW_POS'] = "%d,%d" % (0,30)
    if len(sys.argv) != 2:
        print("Incorrect usage: Please enter a username as the first argument.")
    
    username = sys.argv[1]

    # setup pygame window
    WIN = pygame.display.set_mode((VIEW_WIDTH, VIEW_HEIGHT))
    pygame.display.set_caption("Agario -- Player: " + username)
    c = Client(WIN, username, VIEW_WIDTH, VIEW_HEIGHT)
    c.run()