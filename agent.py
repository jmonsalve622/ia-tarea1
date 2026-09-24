from map import Map, OccupancyTable
from search import Search
from enum import Enum, auto

class Moves(Enum):
    UP = auto()
    DOWN = auto()
    LEFT = auto()
    RIGHT = auto()

class Agent:
    def __init__(self, row: int, col: int):
        self.row = row
        self.col = col
        self.is_alive = True

    def decide_next_step(map: Map, occ: OccupancyTable, turn: int):
        pass

    def apply_move(move: Moves):
        pass
        