"""
TODO: Do we need a time component in calculating move distance? Maybe not necessary.
TODO: We will need to keep in mind that the game window will be different from the application window.
"""
import numpy as np


GAME_WINDOW_WIDTH = 100
GAME_WINDOW_HEIGHT = 100


class Cell():
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

    def move(self):
        """Move in the given direction at object's velocity."""
        # Compute direction vector and add to position
        dx = int(self.speed * np.cos(self.direction))
        dy = int(self.speed * np.sin(self.direction))
        print(dx)
        print(dy)
        self.pos += np.array([dx, dy])
        
        # Clip the cell to the boundaries of the screen
        self._clip_to_bounds()


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


class Food(Cell):
    """TODO: Add default initialization."""
    pass


class Model():
    """Represents the game state."""
    def __init__(self, players=None, food=None):
        self._players = players if players else {}
        self.food = food if food else []

    def update(self):
        """
        Call `move` on every player.
        
        TODO: Should update to handle ejections since these will move.
        """
        for player in self._players.values():
            player.move()
            
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
    
    def add_player(self, username):
        """TODO: Add checking for username, choosing spawn location, etc."""
        pos = np.array([GAME_WINDOW_WIDTH // 2, GAME_WINDOW_HEIGHT // 2])
        player = Player(username, pos)
        self._players[username] = player
    
    @property
    def players(self):
        """All players in the game."""
        return self._players.values()