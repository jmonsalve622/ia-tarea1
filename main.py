import numpy as np
from enum import Enum, auto

K = 5
ROWS = 20
COLUMS = 30

class Actions(Enum):
    UP = auto()
    DOWN = auto()
    LEFT = auto()
    RIGHT = auto()

class Map:
    def __init__(self, grid):
        self.turn = 0
        self.grid = grid

    @classmethod
    def from_file(cls, filepath):
        grid = np.loadtxt(filepath, dtype=int)
        return cls(grid)

    def fire_expand(self):
        if (self.turn % K == 0):
            new_grid = np.zeros(shape=(ROWS, COLUMS), dtype=int)
            
    def update(self):
        self.turn += 1

class Agent:
    def __init__(self, row, column):
        self.row = row
        self.column = column
        self.alive = True

    def actions(self, grid):
        actions = []

        # Moverse arriba
        if (self.row > 0):
            if (grid[self.row - 1,self.column] != 1 and grid[self.row - 1,self.column] != 3):
                actions.append(Actions.UP)
        # Moverse abajo
        if (self.row < ROWS - 1):
            if (grid[self.row + 1,self.column] != 1 and grid[self.row + 1,self.column] != 3):
                actions.append(Actions.DOWN)
        # Moverse a la izquierda
        if (self.column > 0):
            if (grid[self.row,self.column - 1] != 1 and grid[self.row,self.column - 1] != 3):
                actions.append(Actions.LEFT)
        # Moverse a la izquierda
        if (self.column < COLUMS - 1):
            if (grid[self.row,self.column + 1] != 1 and grid[self.row,self.column + 1] != 3):
                actions.append(Actions.RIGHT)

        return actions
        






