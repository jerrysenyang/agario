"""
TODO: Do we need a time component in calculating move distance? Maybe not necessary.
TODO: We will need to keep in mind that the game window will be different from the application window.
"""
import numpy as np
import random
import math


GAME_WINDOW_WIDTH = 1500
GAME_WINDOW_HEIGHT = 800
FOOD_AMOUNT = 100
INITIAL_SPEED = 5.5
RED = (255, 0, 0)
BLUE = (0, 0, 255)
BLACK = (0, 0, 0)
GROWTH_FACTOR = 1


class Cell():

    CELL_COLORS = [
    (80,252,54),
    (36,244,255),
    (243,31,46),
    (4,39,243),
    (254,6,178),
    (255,211,7),
    (216,6,254),
    (145,255,7),
    (7,255,182),
    (255,6,86),
    (147,7,255)]

    """Base class for cells and players."""
    def __init__(self, pos, radius, color, speed, direction):
        self.pos = pos
        self.radius = radius
        self.color = color
        self.speed = speed
        self.direction = direction # In radians

    def _clip_to_bounds(self):
        """Clip position to the boundaries of the screen."""
        if self.pos[0] < 0 + self.radius:
            self.pos[0] = self.radius
        elif self.pos[0] > GAME_WINDOW_WIDTH - self.radius:
            self.pos[0] = GAME_WINDOW_WIDTH - self.radius
        if self.pos[1] < 0 + self.radius:
            self.pos[1] = self.radius
        elif self.pos[1] > GAME_WINDOW_HEIGHT - self.radius:
            self.pos[1] = GAME_WINDOW_HEIGHT - self.radius

    
    def print_cell(self):
        print("The cell is at position: " + str(self.pos))


class Player(Cell):

    def __init__(self, username, pos, radius=10, color= BLACK, speed=INITIAL_SPEED, direction=0):
        self.username = username
        super().__init__(pos, radius, color, speed, direction)
    
    def move(self, x, y):
        """Updates players current position depending on player's mouse relative position.
        """
        rotation = math.atan2(y - float(GAME_WINDOW_HEIGHT)/2, x - float(GAME_WINDOW_WIDTH)/2)
        rotation *= 180/math.pi
        normalized = (90 - math.fabs(rotation))/90
        vx = self.speed*normalized
        vy = 0
        if rotation < 0:
            vy = -self.speed + math.fabs(vx)
        else:
            vy = self.speed - math.fabs(vx)
        tmpX = self.pos[0] + vx
        tmpY = self.pos[1] + vy
        self.pos[0] = tmpX
        self.pos[1] = tmpY

        self._clip_to_bounds()
    

class Model():
    """Represents the game state."""
    def __init__(self, players=None):
        self._players = players if players else {}
        self._food = {}
        for i in range(0,FOOD_AMOUNT):
            self.add_food(i)
            
    def move(self, username, x, y):
        player = self._players.get(username, None)
        if not player:
            raise ValueError
        
        player.move(x, y)


    def detect_food_collisions(self, username):
        """Detects cells being inside the radius of current player.
        Those cells are eaten.
        """
        player = self._players.get(username, None)
        if not player:
            raise ValueError

        for key in self._food:
            f = self._food[key]
            if(self.getDistance(f.pos[0], f.pos[1], player.pos[0], player.pos[1]) <= player.radius *.75):
                player.radius+=GROWTH_FACTOR
                del self._food[key]
                print("COLLISION DETECTED! Food: " + key)
                self.add_food(key)
                return
    
    def detect_player_collisions(self, username):
        """Detects cells being inside the radius of current player.
        Those cells are eaten.
        """

        try:
            player = self._players.get(username, None)
            if not player:
                raise ValueError

            for key in self._players:
                if key != username:
                    p = self._players[key]
                    if(self.getDistance(p.pos[0], p.pos[1], player.pos[0], player.pos[1]) <= p.radius *.75):
                        if player.radius < p.radius:
                            del self._players[username]
                            print("COLLISION DETECTED! Player died! Player: " + username)
                            return False
            
            return True
        
        except: 
            print("Couldn't finish iteration, dictionary changed size.")
            return True
    
    def getDistance(self, ax, ay, bx, by):
        """Calculates Euclidean distance between given points.
        """
        diffX = math.fabs(ax-bx)
        diffY = math.fabs(ay-by)
        return ((diffX**2)+(diffY**2))**(0.5)

    
    def add_player(self, username):
        """TODO: Add checking for username, choosing spawn location, etc."""
        pos = np.array([GAME_WINDOW_WIDTH // 2, GAME_WINDOW_HEIGHT // 2])
        player = Player(username, pos)
        self._players[username] = player

    def add_food(self, index):
        pos = np.array([random.randint(20, GAME_WINDOW_WIDTH-20), random.randint(20,GAME_WINDOW_HEIGHT-20)])
        food = Cell(pos, radius = 7, speed = 0.0, color = random.choice(Cell.CELL_COLORS), direction=0)
        self._food[str(index)] = food
    
    @property
    def players(self):
        """All players in the game."""
        return self._players.values()
    
    @property
    def food(self):
        return self._food.values()