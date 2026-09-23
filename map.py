import numpy as np

ROWS = 10
COLUMS = 20

EMPTY = 0
WALL = 1
EXIT = 2
FIRE = 3

class Map:
    def __init__(self, rows: int, cols: int):
        # Matriz de celdas, indexada [fila][columna]
        self.cells: list[list[Cell]] = [
            [Cell(r, c) for c in range(cols)]
            for r in range(rows)
        ]
        self.rows = rows
        self.cols = cols
        self.exit_cell: tuple[int, int] = None

    def get_cell(self, r: int, c: int):
        return self.cells[r][c]

    def orthogonal_neighbors(self, r: int, c: int):
        # Movimientos en las cuatro driecciones
        candidates = [(r+1, c), (r-1, c), (r, c+1), (r, c-1)]
        return [
            (nr, nc) for nr, nc in candidates
            if 0 <= nr < self.rows and 0 <= nc < self.cols
        ]

    @classmethod
    def from_file(cls, path: str):
        with open(path) as f:
            lines = [line.strip() for line in f.readlines()]
        rows, cols = len(lines), len(lines[0])
        map = cls(rows, cols)
        for r, line in enumerate(lines):
            for c, char in enumerate(line):
                cell = map.get_cell(r, c)
                if char == WALL:
                    cell.is_wall = True
                elif char == EXIT:
                    map.exit_cell = (r, c)
        return map

    def spread_fire(self):
        pass


class Cell:
    def __init__(self, r: int, c: int):
        self.r = r
        self.c = c
        self.is_burned = False
        self.base_cost = 1.0
        self.is_wall = False

class OccupancyTable:
    def __init__(self):
        pass



