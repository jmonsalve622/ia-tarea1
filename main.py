import numpy as np # type: ignore
from enum import Enum, auto
import random

K = 5
ROWS = 20
COLUMS = 30

EMPTY = 0
WALL = -1
EXIT = -2
FIRE = -3   

class Actions(Enum):
    UP = auto()
    DOWN = auto()
    LEFT = auto()
    RIGHT = auto()

class Map:
    def __init__(self, grid, exit):
        self.turn = 0
        self.grid = grid
        self.exit = exit
        self.fire = []

    @classmethod
    def from_file(cls, filepath):
        grid = np.loadtxt(filepath, dtype=int)

        exit = None
        for i in range(ROWS):
            for j in range(COLUMS):
                if grid[i,j] == -2:
                    exit = (i, j)
                    break

        return cls(grid, exit)

    def fire_expand(self):
        if (self.turn % K == 0):
            for cell in self.fire:
                r = cell[0]
                c = cell[1]
            
    def update(self):
        self.turn += 1

    # Inicio del incendio en posición aleatorio, evitando iniciar en la salida o en una casilla con una persona
    def fire_start(self):
        # Asegurarse de que el mapa este bien hecho para que no quede en un bucle sin salida
        while(True):
            r = random.randint(0, ROWS - 1)
            c = random.randint(0, COLUMS - 1)
            if (self.grid[r,c] > 0 or self.grid[r,c] == EXIT):
                break

        self.grid[r,c] = FIRE
        self.fire.append((r,c))

class Agent:
    def __init__(self, id, pos):
        self.id = id
        self.pos = pos
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
        






