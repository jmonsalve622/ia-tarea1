from map import Map
from search import Search

class Agent:
    def __init__(self, id: int, row: int, col: int, search: Search):
        self.id = id
        self.row = row
        self.col = col
        self.is_alive = True
        self.has_evacuated = False
        self.search = search
        self.planned_path: list[tuple[int, int]] = []
        self.has_planned = False

    def decide_next_step(self, map: Map):
        should_replan = self.search.REPLAN_EVERY_TURN or not self.has_planned
        if should_replan:
            self.planned_path = self.search.plan(self, map)
            self.has_planned = True

        return self.planned_path[0] if self.planned_path else None
    
    def apply_move(self, next_cell: tuple[int, int]):
        self.row, self.col = next_cell

        if self.planned_path and self.planned_path[0] == next_cell:
            self.planned_path.pop(0)