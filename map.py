EMPTY = 0
WALL = 1
EXIT = 2
FIRE = 3

K_TURN = 3
CAPACITY = 3

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
        self.occupancy_table: list[list[int]] = [[0] * cols for _ in range(rows)]

    @classmethod
    def from_file(cls, path: str):
        with open(path) as f:
            grid = [[int(v) for v in line.split()] for line in f if line.strip()]
        rows, cols = len(grid), len(grid[0])
        map = cls(rows, cols)
        for r, row in enumerate(grid):
            for c, value in enumerate(row):
                cell = map.cells[r][c]
                if value == WALL:
                    cell.is_wall = True
                elif value == EXIT:
                    map.exit_cell = (r, c)
                elif value == FIRE:
                    cell.is_burned = True
        return map
        
    def orthogonal_neighbors(self, row: int, col: int):
        # Movimientos en las cuatro driecciones
        candidates = [(row + 1, col), (row - 1, col), (row, col + 1), (row, col - 1)]
        return [
            (nr, nc) for nr, nc in candidates
            if 0 <= nr < self.rows and 0 <= nc < self.cols and not self.cells[nr][nc].is_burned and not self.cells[nr][nc].is_wall 
        ]

    def spread_fire(self, turn: int):
        if (turn % K_TURN == 0):
            fire_positions = [(r, c) for r in range(self.rows) for c in range(self.cols) if self.cells[r][c].is_burned]
            for r, c in fire_positions:
                for nr, nc in self.orthogonal_neighbors(r, c):
                    self.cells[nr][nc].is_burned = True
        pass

    def dynamic_cost(self, row: int, col: int):
        if self.occupancy_table[row][col] >= CAPACITY:
            return float('inf')

        if self.occupancy_table[row][col] == 0:
            return 1
        
        return 1 + self.occupancy_table[row][col] ** 2
            
class Cell:
    def __init__(self, row: int, col: int):
        self.row = row
        self.col = col
        self.is_burned = False
        self.is_wall = False