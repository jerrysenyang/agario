"""
TODO: Do we need a time component in calculating move distance? Maybe not necessary.
TODO: We will need to keep in mind that the game window will be different from the application window.
"""
import numpy as np
import random
import math


GAME_WINDOW_WIDTH = 1500
GAME_WINDOW_HEIGHT = 800
FOOD_AMOUNT = 50


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

    # def move(self):
    #     """Move in the given direction at object's velocity."""
    #     # Compute direction vector and add to position
    #     dx = int(self.speed * np.cos(self.direction))
    #     dy = int(self.speed * np.sin(self.direction))
    #     print(dx)
    #     print(dy)
    #     self.pos += np.array([dx, dy])
        
        # # Clip the cell to the boundaries of the screen
        # self._clip_to_bounds()


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
    
    def print_cell(self):
        print("The cell is at position: " + str(self.pos))


class Player(Cell):
    def __init__(self, username, pos, radius=10, color="r", speed=10.0, direction=0):
        self.username = username
        super().__init__(pos, radius, color, speed, direction)
    
    def update_velocity(self, angle, speed):
        """
        Update the velocity with a given polar vector.
        
        TODO: Not sure if this is sufficient, may need to fix this.
        """
        self.direction = angle
        self.speed = speed



class Model():
    """Represents the game state."""
    def __init__(self, players=None):
        self._players = players if players else {}
        self._food = {}
        for i in range(0,FOOD_AMOUNT):
            self.add_food(i)
        
    def update(self):
        """
        Call `move` on every player.
        
        TODO: Should update to handle ejections since these will move.
        """
        for player in self._players.values():
            # player.move()
            pass
            # Check collisions with food and players

    def update_velocity(self, username, angle, speed):
        """
        Return Player instance by username or raise exception.
        """
        player = self._players.get(username, None)

        # Change exception 
        if not player:
            raise ValueError
        
        player.update_velocity(angle, speed)
    
    def move(self, username, x, y):
        player = self._players.get(username, None)
        if not player:
            raise ValueError
        
        player.move(x, y)
    
    def add_player(self, username):
        """TODO: Add checking for username, choosing spawn location, etc."""
        pos = np.array([GAME_WINDOW_WIDTH // 2, GAME_WINDOW_HEIGHT // 2])
        player = Player(username, pos)
        self._players[username] = player

    def add_food(self, index):
        pos = np.array([random.randint(20, GAME_WINDOW_WIDTH-20), random.randint(20,GAME_WINDOW_HEIGHT-20)])
        food = Cell(pos, radius = 7, speed = 0, color = "b", direction=0)
        self._food[str(index)] = food
    
    @property
    def players(self):
        """All players in the game."""
        return self._players.values()
    
    @property
    def food(self):
        return self._food.values()