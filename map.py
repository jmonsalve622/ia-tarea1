import numpy as np

ROWS = 10
COLUMS = 20

EMPTY = 0
WALL = 1
EXIT = 2
FIRE = 3

class Map:
    def __init__(self, id: int, rows: int, cols: int):
        # Matriz de celdas, indexada [fila][columna]
        self.cells: list[list[Cell]] = [
            [Cell(r, c) for c in range(cols)]
            for r in range(rows)
        ]
        self.rows = rows
        self.cols = cols
        self.exit_cell: tuple[int, int] = None
        self.fire_start: tuple[int, int] = None
        self.id = None

    def get_cell(self, row: int, col: int):
        return self.cells[row][col]

    def orthogonal_neighbors(self, row: int, col: int):
        # Movimientos en las cuatro driecciones
        candidates = [(row + 1, col), (row - 1, col), (row, col + 1), (row, col - 1)]
        return [
            (nr, nc) for nr, nc in candidates
            if 0 <= nr < self.rows and 0 <= nc < self.cols
        ]

    @classmethod
    def from_file(cls, path: str):
        with open(path) as f:
            lines = [line.strip() for line in f.readlines()]
        rows, cols = len(lines), len(lines[0])

        id = None
        if path.count('1'):
            id = 1
        elif path.count('2'):
            id = 2
        elif path.count('3'):
            id = 3
        else:
            id = 0
        
        map = cls(id, rows, cols)
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
    def __init__(self, row: int, col: int):
        self.row = row
        self.col = col
        self.is_burned = False
        self.base_cost = 1.0
        self.is_wall = False

class OccupancyTable:
    def __init__(self):
        pass



